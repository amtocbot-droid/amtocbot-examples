"""Production LLM resilience patterns: retry budget, idempotency, negative
caching, and a rate-window circuit breaker.

Companion code for the AmtocSoft post
"Production AI Agent Patterns: Retry, Idempotency, Circuit Breakers".

The post uses Redis for the cache; this module keeps the identical interface
but backs it with an in-process dict so the example runs with zero
dependencies. Swap `DictStore` for a real `redis.Redis` in production.
"""

from __future__ import annotations

import hashlib
import json
import random
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


# --------------------------------------------------------------------------
# Retry budget: token-bucket in dollars. Refills over time, capped.
# --------------------------------------------------------------------------
@dataclass
class RetryBudget:
    refill_rate_per_sec: float          # dollars per second
    max_balance: float                  # dollars
    balance: float = 0.0
    last_refill: float = field(default_factory=time.monotonic)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def try_spend(self, cost_usd: float) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.balance = min(self.max_balance,
                               self.balance + elapsed * self.refill_rate_per_sec)
            self.last_refill = now
            if self.balance >= cost_usd:
                self.balance -= cost_usd
                return True
            return False


def retry_with_budget(
    fn: Callable[[], T],
    budget: RetryBudget,
    estimate_cost_usd: Callable[[Exception], float],
    max_attempts: int = 4,
    base_delay_sec: float = 1.0,
    cap_delay_sec: float = 20.0,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    last_exc: Optional[Exception] = None
    delay = base_delay_sec
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt + 1 == max_attempts:
                raise
            cost = estimate_cost_usd(exc)
            if not budget.try_spend(cost):
                raise
            delay = min(cap_delay_sec, random.uniform(base_delay_sec, delay * 3))
            sleep(delay)
    raise last_exc  # unreachable


# --------------------------------------------------------------------------
# Idempotency key: canonicalise the request so identical calls collide.
# --------------------------------------------------------------------------
def llm_idempotency_key(*, model: str, temperature: float, seed: Optional[int],
                        system: str, messages: list[dict],
                        tools: Optional[list[dict]]) -> str:
    canon = json.dumps(
        {"model": model, "temperature": round(temperature, 3), "seed": seed,
         "system": system, "messages": messages, "tools": tools or []},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "llm:v1:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Cache with negative caching. Redis-shaped interface, dict-backed here.
# --------------------------------------------------------------------------
class DictStore:
    """Minimal subset of redis.Redis: get / set(ex=)."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._d: dict[str, tuple[str, float]] = {}
        self._clock = clock

    def get(self, key: str) -> Optional[str]:
        v = self._d.get(key)
        if v is None:
            return None
        raw, expires = v
        if expires and self._clock() > expires:
            del self._d[key]
            return None
        return raw

    def set(self, key: str, raw: str, ex: Optional[int] = None) -> None:
        expires = self._clock() + ex if ex else 0.0
        self._d[key] = (raw, expires)


class LLMCache:
    SUCCESS_TTL = 3600
    FAILURE_TTL = 90

    def __init__(self, client: DictStore):
        self.r = client

    def get(self, key: str) -> Optional[dict]:
        raw = self.r.get(key)
        return json.loads(raw) if raw is not None else None

    def put_success(self, key: str, completion: dict) -> None:
        self.r.set(key, json.dumps({"ok": True, "data": completion}),
                   ex=self.SUCCESS_TTL)

    def put_failure(self, key: str, error: str) -> None:
        # negative caching prevents retry storms on hot-key failures
        self.r.set(key + ":fail", json.dumps({"ok": False, "error": error}),
                   ex=self.FAILURE_TTL)

    def get_failure(self, key: str) -> Optional[dict]:
        return self.get(key + ":fail")


# --------------------------------------------------------------------------
# Rate-window circuit breaker.
# --------------------------------------------------------------------------
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class LLMCircuitBreaker:
    window_sec: float = 30.0
    failure_rate_threshold: float = 0.5
    min_calls: int = 8
    cooldown_sec: float = 15.0
    state: CircuitState = CircuitState.CLOSED
    opened_at: float = 0.0
    events: deque = field(default_factory=deque)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    clock: Callable[[], float] = time.monotonic

    def _gc(self, now: float) -> None:
        while self.events and now - self.events[0][0] > self.window_sec:
            self.events.popleft()

    def allow(self) -> bool:
        with self._lock:
            now = self.clock()
            if self.state == CircuitState.OPEN:
                if now - self.opened_at >= self.cooldown_sec:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            return True

    def record(self, ok: bool) -> None:
        with self._lock:
            now = self.clock()
            self.events.append((now, ok))
            self._gc(now)
            if self.state == CircuitState.HALF_OPEN:
                if ok:
                    self.state = CircuitState.CLOSED
                    self.events.clear()
                else:
                    self.state = CircuitState.OPEN
                    self.opened_at = now
                return
            if len(self.events) >= self.min_calls:
                failures = sum(1 for _, e_ok in self.events if not e_ok)
                if failures / len(self.events) >= self.failure_rate_threshold:
                    self.state = CircuitState.OPEN
                    self.opened_at = now

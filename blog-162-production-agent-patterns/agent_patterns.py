"""Async production agent patterns: retry budget, idempotent replay, and a
multi-arm circuit breaker.

Companion code for the AmtocSoft post
"Production Agent Patterns: Retry, Idempotency, Circuit Breakers".

This is the asyncio variant: an agent step pre-checks each breaker arm,
computes an idempotency key, replays cached results, and retries transient
failures within a bounded budget. Pure standard library (asyncio).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, TypeVar

T = TypeVar("T")


# --------------------------------------------------------------------------
# Retry budget (attempts + wall-clock + token ceiling) with capped jitter.
# --------------------------------------------------------------------------
@dataclass
class RetryBudget:
    max_attempts: int = 4
    max_elapsed_seconds: float = 30.0
    max_input_tokens: int = 200_000
    base_delay: float = 1.0
    max_delay: float = 16.0
    tokens_used: int = 0
    started_at: float = field(default_factory=time.monotonic)

    def can_retry(self, attempt: int, last_call_tokens: int) -> bool:
        self.tokens_used += last_call_tokens
        if attempt >= self.max_attempts:
            return False
        if (time.monotonic() - self.started_at) > self.max_elapsed_seconds:
            return False
        if self.tokens_used >= self.max_input_tokens:
            return False
        return True

    def next_delay(self, attempt: int) -> float:
        cap = min(self.max_delay, self.base_delay * (2 ** attempt))
        return random.uniform(0, cap)


class TransientLLMError(Exception):
    pass


class FatalLLMError(Exception):
    pass


async def with_retry(call: Callable[[], Awaitable[T]], budget: RetryBudget,
                     on_retry: Optional[Callable[[int, float, Exception], None]] = None,
                     sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> T:
    attempt = 0
    last_tokens = 0
    while True:
        try:
            return await call()
        except FatalLLMError:
            raise
        except TransientLLMError as e:
            if not budget.can_retry(attempt, last_tokens):
                raise
            delay = budget.next_delay(attempt)
            if on_retry:
                on_retry(attempt, delay, e)
            await sleep(delay)
            attempt += 1


# --------------------------------------------------------------------------
# Idempotency: canonical prompt hash + replay cache.
# --------------------------------------------------------------------------
def canonical_prompt_hash(messages: list[dict], tools: list[dict],
                          temperature: float) -> str:
    canonical = {
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        "tools": sorted(t["name"] for t in tools),
        "temperature": round(temperature, 2),
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


class IdempotentLLMCache:
    def __init__(self, ttl_seconds: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    async def call_or_replay(self, cache_key: str,
                             run_call: Callable[[], Awaitable[Any]]) -> Any:
        now = time.monotonic()
        if cache_key in self._store:
            value, ts = self._store[cache_key]
            if (now - ts) < self._ttl:
                return value
        result = await run_call()
        self._store[cache_key] = (result, now)
        return result


# --------------------------------------------------------------------------
# Multi-arm circuit breaker: one arm per provider / tool / cost axis.
# --------------------------------------------------------------------------
class BreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitArm:
    name: str
    failure_threshold: int = 10
    success_threshold: int = 3
    cooldown_seconds: float = 30.0
    state: BreakerState = BreakerState.CLOSED
    failures: int = 0
    successes_in_half_open: int = 0
    opened_at: float = 0.0
    clock: Callable[[], float] = time.monotonic

    def record_success(self):
        if self.state == BreakerState.HALF_OPEN:
            self.successes_in_half_open += 1
            if self.successes_in_half_open >= self.success_threshold:
                self.state = BreakerState.CLOSED
                self.failures = 0
                self.successes_in_half_open = 0
        elif self.state == BreakerState.CLOSED:
            self.failures = max(0, self.failures - 1)

    def record_failure(self):
        if self.state == BreakerState.HALF_OPEN:
            self.state = BreakerState.OPEN
            self.opened_at = self.clock()
            self.successes_in_half_open = 0
        elif self.state == BreakerState.CLOSED:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = BreakerState.OPEN
                self.opened_at = self.clock()

    def can_proceed(self) -> bool:
        if self.state == BreakerState.CLOSED:
            return True
        if self.state == BreakerState.OPEN:
            if (self.clock() - self.opened_at) > self.cooldown_seconds:
                self.state = BreakerState.HALF_OPEN
                return True
            return False
        return True


class MultiArmBreaker:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self.arms = {
            "provider_anthropic": CircuitArm("provider_anthropic", clock=clock),
            "provider_openai": CircuitArm("provider_openai", clock=clock),
            "tool_database": CircuitArm("tool_database", clock=clock),
            "tool_search": CircuitArm("tool_search", clock=clock),
            "cost_per_task": CircuitArm("cost_per_task", failure_threshold=3,
                                        cooldown_seconds=120, clock=clock),
        }

    def precheck(self, axis: str) -> bool:
        return self.arms[axis].can_proceed()

    def report(self, axis: str, success: bool):
        if success:
            self.arms[axis].record_success()
        else:
            self.arms[axis].record_failure()

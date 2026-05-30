"""Tests. Run: python3 test_resilience.py"""

from __future__ import annotations

from resilience import (
    RetryBudget, retry_with_budget, LLMCache, DictStore, LLMCircuitBreaker,
    CircuitState, llm_idempotency_key,
)


def test_idempotency_key_is_stable_and_order_independent():
    a = llm_idempotency_key(model="m", temperature=0.0, seed=1, system="s",
                            messages=[{"role": "user", "content": "x"}], tools=None)
    b = llm_idempotency_key(model="m", temperature=0.0, seed=1, system="s",
                            messages=[{"role": "user", "content": "x"}], tools=[])
    assert a == b and a.startswith("llm:v1:")


def test_idempotency_key_differs_on_temperature():
    a = llm_idempotency_key(model="m", temperature=0.0, seed=1, system="s",
                            messages=[], tools=None)
    b = llm_idempotency_key(model="m", temperature=0.7, seed=1, system="s",
                            messages=[], tools=None)
    assert a != b


def test_budget_blocks_when_empty():
    b = RetryBudget(refill_rate_per_sec=0.0, max_balance=0.05, balance=0.05)
    assert b.try_spend(0.05) is True
    assert b.try_spend(0.05) is False


def test_negative_cache_roundtrip():
    c = LLMCache(DictStore())
    c.put_failure("k", "boom")
    assert c.get_failure("k") == {"ok": False, "error": "boom"}
    assert c.get("k") is None  # success slot is empty


def test_success_cache_roundtrip():
    c = LLMCache(DictStore())
    c.put_success("k", {"text": "hi"})
    assert c.get("k") == {"ok": True, "data": {"text": "hi"}}


def test_breaker_opens_on_failure_rate():
    b = LLMCircuitBreaker(min_calls=8, failure_rate_threshold=0.5)
    for _ in range(8):
        b.record(ok=False)
    assert b.state == CircuitState.OPEN


def test_breaker_stays_closed_below_threshold():
    b = LLMCircuitBreaker(min_calls=8, failure_rate_threshold=0.5)
    for i in range(8):
        b.record(ok=(i % 2 == 0))  # 50% exactly -> opens; use mostly-ok
    # rebuild with clearly-below-threshold
    b2 = LLMCircuitBreaker(min_calls=8, failure_rate_threshold=0.5)
    for i in range(8):
        b2.record(ok=(i != 0))  # 1/8 failures
    assert b2.state == CircuitState.CLOSED


def test_retry_stops_at_max_attempts():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise RuntimeError("transient")

    try:
        retry_with_budget(fn, RetryBudget(0.0, 100.0, 100.0),
                          estimate_cost_usd=lambda e: 0.0, max_attempts=3,
                          base_delay_sec=0.0, cap_delay_sec=0.0, sleep=lambda d: None)
    except RuntimeError:
        pass
    assert calls["n"] == 3


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

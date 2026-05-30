"""Simulate a provider outage and show the three layers cooperating:
retry budget absorbs transient blips, negative cache prevents retry storms
on a hot failing key, and the circuit breaker opens once the failure rate
crosses the window threshold.

    $ python3 simulate_outage.py
"""

from __future__ import annotations

from resilience import (
    RetryBudget, retry_with_budget, LLMCache, DictStore, LLMCircuitBreaker,
    llm_idempotency_key,
)


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def main() -> None:
    clock = FakeClock()
    breaker = LLMCircuitBreaker(min_calls=8, failure_rate_threshold=0.5,
                               cooldown_sec=15.0, clock=clock)

    # Drive 10 failing calls through the breaker.
    for _ in range(10):
        if breaker.allow():
            breaker.record(ok=False)
        clock.advance(1.0)
    print("after 10 failures, breaker state:", breaker.state.value)
    assert breaker.state.value == "open"
    assert breaker.allow() is False, "open breaker must shed load"

    # Cooldown elapses -> half-open -> a success closes it.
    clock.advance(16.0)
    assert breaker.allow() is True
    breaker.record(ok=True)
    print("after cooldown + success, breaker state:", breaker.state.value)
    assert breaker.state.value == "closed"

    # Negative caching: a known-bad key is served from cache, not retried.
    cache = LLMCache(DictStore(clock=clock))
    key = llm_idempotency_key(model="claude-opus-4-7", temperature=0.0,
                              seed=1, system="s", messages=[{"role": "user",
                              "content": "hi"}], tools=None)
    cache.put_failure(key, "provider 529 overloaded")
    assert cache.get_failure(key)["error"] == "provider 529 overloaded"
    print("negative cache hit:", cache.get_failure(key)["error"])

    # Retry budget caps the number of paid retries.
    budget = RetryBudget(refill_rate_per_sec=0.0, max_balance=0.10, balance=0.10)
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        raise RuntimeError("RateLimitError")

    try:
        retry_with_budget(flaky, budget, estimate_cost_usd=lambda e: 0.05,
                          max_attempts=10, base_delay_sec=0.0, cap_delay_sec=0.0,
                          sleep=lambda d: None)
    except RuntimeError:
        pass
    print("paid retries before budget exhausted:", attempts["n"])
    assert attempts["n"] == 3  # 2 paid retries ($0.10/$0.05) + final raise

    print("\nOK: retries bounded, breaker opens and recovers, no retry storm.")


if __name__ == "__main__":
    main()

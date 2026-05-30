"""Tests. Run: python3 test_agent_patterns.py"""

from __future__ import annotations

import asyncio

from agent_patterns import (
    RetryBudget, with_retry, TransientLLMError, FatalLLMError,
    IdempotentLLMCache, canonical_prompt_hash, MultiArmBreaker, BreakerState,
)


def run(coro):
    return asyncio.run(coro)


def test_canonical_hash_order_independent_tools():
    a = canonical_prompt_hash([{"role": "user", "content": "x"}],
                              [{"name": "b"}, {"name": "a"}], 0.0)
    b = canonical_prompt_hash([{"role": "user", "content": "x"}],
                              [{"name": "a"}, {"name": "b"}], 0.0)
    assert a == b and len(a) == 16


def test_fatal_not_retried():
    calls = {"n": 0}

    async def call():
        calls["n"] += 1
        raise FatalLLMError("bad request")

    async def go():
        try:
            await with_retry(call, RetryBudget(max_attempts=5))
        except FatalLLMError:
            return
        raise AssertionError("should have raised")

    run(go())
    assert calls["n"] == 1


def test_transient_retried_then_succeeds():
    calls = {"n": 0}

    async def call():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TransientLLMError("blip")
        return "ok"

    async def go():
        return await with_retry(call, RetryBudget(max_attempts=5, base_delay=0.0,
                                max_delay=0.0), sleep=lambda d: asyncio.sleep(0))

    assert run(go()) == "ok" and calls["n"] == 3


def test_budget_caps_attempts():
    calls = {"n": 0}

    async def call():
        calls["n"] += 1
        raise TransientLLMError("blip")

    async def go():
        try:
            await with_retry(call, RetryBudget(max_attempts=2, base_delay=0.0,
                             max_delay=0.0), sleep=lambda d: asyncio.sleep(0))
        except TransientLLMError:
            return

    run(go())
    # initial try + retries until attempt >= max_attempts
    assert calls["n"] == 3


def test_replay_cache_calls_once():
    cache = IdempotentLLMCache()
    calls = {"n": 0}

    async def run_call():
        calls["n"] += 1
        return {"v": 1}

    async def go():
        await cache.call_or_replay("k", run_call)
        await cache.call_or_replay("k", run_call)

    run(go())
    assert calls["n"] == 1


def test_breaker_opens_and_recovers():
    clock = {"t": 0.0}
    b = MultiArmBreaker(clock=lambda: clock["t"])
    for _ in range(10):
        b.report("provider_openai", success=False)
    assert b.arms["provider_openai"].state == BreakerState.OPEN
    assert b.precheck("provider_openai") is False
    clock["t"] += 31
    assert b.precheck("provider_openai") is True  # half-open
    for _ in range(3):
        b.report("provider_openai", success=True)
    assert b.arms["provider_openai"].state == BreakerState.CLOSED


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

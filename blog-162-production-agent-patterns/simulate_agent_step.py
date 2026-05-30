"""Run an agent step end-to-end: breaker pre-check -> idempotency key ->
replay cache -> bounded retry. Reproduces the post's decision flow.

    $ python3 simulate_agent_step.py
"""

from __future__ import annotations

import asyncio

from agent_patterns import (
    RetryBudget, with_retry, TransientLLMError, IdempotentLLMCache,
    canonical_prompt_hash, MultiArmBreaker,
)


async def main() -> None:
    breaker = MultiArmBreaker()
    cache = IdempotentLLMCache(ttl_seconds=300)

    messages = [{"role": "user", "content": "summarise Q3"}]
    tools = [{"name": "search"}, {"name": "fetch"}]
    key = canonical_prompt_hash(messages, tools, temperature=0.0)

    # 1. Cost arm must be closed before we spend anything.
    assert breaker.precheck("cost_per_task")

    # 2. A flaky provider call that fails twice then succeeds.
    attempts = {"n": 0}

    async def provider_call():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise TransientLLMError("529 overloaded")
        return {"text": "Q3 revenue up 12%"}

    async def run_call():
        budget = RetryBudget(max_attempts=5, base_delay=0.0, max_delay=0.0)
        return await with_retry(provider_call, budget, sleep=lambda d: asyncio.sleep(0))

    result = await cache.call_or_replay(key, run_call)
    breaker.report("provider_anthropic", success=True)
    print("result:", result, "after", attempts["n"], "attempts")
    assert result["text"].startswith("Q3") and attempts["n"] == 3

    # 3. Second identical step is served from the replay cache (no new call).
    again = await cache.call_or_replay(key, run_call)
    assert again == result and attempts["n"] == 3
    print("replayed from cache, provider not called again")

    # 4. The cost arm trips after 3 failures and sheds the next step.
    for _ in range(3):
        breaker.report("cost_per_task", success=False)
    assert breaker.precheck("cost_per_task") is False
    print("cost arm open -> step shed. OK")


if __name__ == "__main__":
    asyncio.run(main())

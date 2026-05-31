"""Show sticky bucketing converging on the target percentage, then a shadow
route that serves old while logging a new-vs-old diff.

    $ python3 demo.py
"""

from __future__ import annotations

import asyncio

from canary import route_decision, shadow_route


def main_sync() -> None:
    # Sticky: ~10% of users land on model-new at 10%.
    users = [f"user-{i}" for i in range(10_000)]
    new = sum(route_decision(u, 10.0) == "model-new" for u in users)
    print(f"at 10% rollout, {new}/{len(users)} users on model-new "
          f"({new/len(users):.1%})")
    assert 850 <= new <= 1150  # close to 10%

    # Stickiness: same user, same bucket across calls.
    assert route_decision("user-42", 10.0) == route_decision("user-42", 10.0)
    # Monotonic: a user on new at 10% is still on new at 50%.
    on_new_at_10 = [u for u in users[:200] if route_decision(u, 10.0) == "model-new"]
    assert all(route_decision(u, 50.0) == "model-new" for u in on_new_at_10)
    print("routing is sticky and monotonic in percent")


async def main_async() -> None:
    log: list[dict] = []

    async def call_model(name, prompt):
        await asyncio.sleep(0)
        return {"text": f"[{name}] answer", "usage": {"completion_tokens": 3}}

    async def shadow_log(rec):
        log.append(rec)

    out = await shadow_route("hello", "user-1", call_model, shadow_log)
    print(f"\nserved to user: {out}")
    for _ in range(10):       # let the background shadow-log task complete
        if log:
            break
        await asyncio.sleep(0)
    assert out["model"] == "model-old"
    assert log and log[0]["diverged"] is True
    print(f"shadow logged diff: diverged={log[0]['diverged']}")
    print("\nOK: sticky splits + non-blocking shadow logging.")


if __name__ == "__main__":
    main_sync()
    asyncio.run(main_async())

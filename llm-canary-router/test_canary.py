"""Tests. Run: python3 test_canary.py"""

from __future__ import annotations

import asyncio

from canary import route_decision, shadow_route


def test_zero_percent_all_old():
    assert all(route_decision(f"u{i}", 0.0) == "model-old" for i in range(100))


def test_hundred_percent_all_new():
    assert all(route_decision(f"u{i}", 100.0) == "model-new" for i in range(100))


def test_sticky_same_user():
    assert route_decision("u-42", 30.0) == route_decision("u-42", 30.0)


def test_monotonic_in_percent():
    new_at_10 = [f"u{i}" for i in range(500)
                 if route_decision(f"u{i}", 10.0) == "model-new"]
    assert all(route_decision(u, 60.0) == "model-new" for u in new_at_10)


def test_split_is_approximately_target():
    n = sum(route_decision(f"u{i}", 25.0) == "model-new" for i in range(5000))
    assert 0.22 <= n / 5000 <= 0.28


def test_shadow_serves_old_and_logs():
    log = []

    async def call_model(name, prompt):
        return {"text": f"[{name}]", "usage": {"completion_tokens": 1}}

    async def shadow_log(rec):
        log.append(rec)

    async def go():
        out = await shadow_route("p", "u1", call_model, shadow_log)
        await asyncio.sleep(0)
        return out

    out = asyncio.run(go())
    assert out["model"] == "model-old"
    assert log and "diverged" in log[0]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

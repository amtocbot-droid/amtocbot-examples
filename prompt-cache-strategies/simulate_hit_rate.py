"""Drive many tenants/users through both prompt builders and show the
fleet-wide cache hit rate. Reproduces the post's central claim: moving
volatile content out of the cached prefix lifts hit rate from near-zero
to near-one.

    $ python3 simulate_hit_rate.py
"""

from __future__ import annotations

from prefix_cache import build_prompt_broken, build_prompt_stable, cache_key


def simulate(builder, n_tenants=5, n_calls=20) -> float:
    seen = set()
    hits = total = 0
    for t in range(n_tenants):
        for c in range(n_calls):
            now = f"2026-05-30T10:{c:02d}:00"
            msgs = builder(f"tenant{t}", f"user{c}", "hello", now)
            key = cache_key(msgs)
            total += 1
            if key in seen:
                hits += 1
            else:
                seen.add(key)
    return hits / total


def main() -> None:
    broken = simulate(build_prompt_broken)
    stable = simulate(build_prompt_stable)
    print(f"broken builder hit rate: {broken:.0%}")
    print(f"stable builder hit rate: {stable:.0%}")
    assert broken == 0.0
    assert stable >= 0.98
    print("\nOK: one stable cache key across all tenants -> ~99% hit rate.")


if __name__ == "__main__":
    main()

"""Tests. Run: python3 test_prefix_cache.py"""

from __future__ import annotations

from prefix_cache import (
    build_prompt_broken, build_prompt_stable, cache_key, cache_stats, Usage,
)
from simulate_hit_rate import simulate


def test_stable_key_is_constant_across_tenants():
    k1 = cache_key(build_prompt_stable("a", "u1", "hi", "t1"))
    k2 = cache_key(build_prompt_stable("b", "u2", "hi", "t2"))
    assert k1 == k2


def test_broken_key_changes_per_call():
    k1 = cache_key(build_prompt_broken("a", "u1", "hi", "t1"))
    k2 = cache_key(build_prompt_broken("a", "u1", "hi", "t2"))
    assert k1 != k2


def test_cache_stats_high_hit_rate():
    s = cache_stats(Usage(input_tokens=50, cache_read_input_tokens=41_247))
    assert s["hit_rate"] > 0.99
    assert s["savings"] > 0.8


def test_cache_stats_empty():
    assert cache_stats(Usage(0))["hit_rate"] == 0.0


def test_simulation_separates_builders():
    assert simulate(build_prompt_broken) == 0.0
    assert simulate(build_prompt_stable) >= 0.98


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

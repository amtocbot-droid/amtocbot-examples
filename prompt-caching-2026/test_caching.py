"""Tests. Run: python3 test_caching.py"""

from __future__ import annotations

from estimate_cost import monthly_cost_no_cache, monthly_cost_cached
from cache_sim import simulate, prepare_document_broken, prepare_document_fixed


def test_post_headline_numbers():
    base = monthly_cost_no_cache(40_000, 15, 90)
    assert round(base, 2) == 810.00
    assert round(base * 0.90, 2) == 729.00


def test_caching_is_cheaper():
    base = monthly_cost_no_cache(40_000, 15, 90)
    cached = monthly_cost_cached(40_000, 15, 90)
    assert cached < base


def test_single_call_session_has_no_read_savings():
    # One call = pure cache write, costs slightly MORE than no-cache.
    base = monthly_cost_no_cache(40_000, 1, 10)
    cached = monthly_cost_cached(40_000, 1, 10)
    assert cached > base


def test_broken_prefix_never_hits():
    assert simulate(prepare_document_broken).hit_rate() == 0.0


def test_fixed_prefix_hits_after_first():
    c = simulate(prepare_document_fixed, calls=15)
    assert c.writes == 1 and c.reads == 14


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

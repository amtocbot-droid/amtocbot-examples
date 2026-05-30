"""Tests. Run: python3 test_rollup.py"""

from __future__ import annotations

from datetime import date

from rollup import rollup, quarter_bounds, load_known_tags


def test_quarter_bounds_q2():
    s, e = quarter_bounds(date(2026, 5, 30))
    assert s == date(2026, 4, 1) and e == date(2026, 6, 30)


def test_known_tags_loaded():
    tags = load_known_tags()
    assert "aggressive-timeout" in tags and "missing-canary" in tags


def test_recurring_factors_surface():
    rows = dict((tag, n) for tag, n, _ in rollup(date(2026, 5, 30)))
    assert rows["aggressive-timeout"] == 4
    assert rows["missing-canary"] == 4
    # eval-gap and runbook-miss appear once each -> below threshold, not listed
    assert "eval-gap" not in rows and "runbook-miss" not in rows


def test_empty_quarter():
    assert rollup(date(2025, 1, 15)) == []


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

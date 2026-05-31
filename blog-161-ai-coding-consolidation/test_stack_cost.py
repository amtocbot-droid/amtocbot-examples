"""Tests. Run: python3 test_stack_cost.py"""

from __future__ import annotations

from stack_cost import FIVE_TOOL, TWO_TOOL, compare, Stack, Tool


def test_license_cost_scales_with_seats():
    assert FIVE_TOOL.license_cost(10) == FIVE_TOOL.license_cost(1) * 10


def test_two_tool_cheaper_overall():
    r = compare(20)
    assert r["two_tool"] < r["five_tool"] and r["monthly_savings"] > 0


def test_switch_tax_lower_for_fewer_tools():
    assert TWO_TOOL.switch_cost(20) < FIVE_TOOL.switch_cost(20)


def test_zero_switches_means_no_tax():
    s = Stack("x", [Tool("a", 10)], switches_per_day=0)
    assert s.switch_cost(5) == 0.0
    assert s.total_monthly(5) == s.license_cost(5)


def test_switch_cost_formula():
    s = Stack("x", [Tool("a", 0)], switches_per_day=10, minutes_per_switch=6)
    # 10 switches * 6 min * 21 days * 1 seat = 1260 min = 21 hours * $90 = 1890
    assert abs(s.switch_cost(1, hourly_usd=90.0, working_days=21) - 1890.0) < 1e-6


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

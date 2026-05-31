"""Tests. Run: python3 test_score.py"""

from __future__ import annotations

from score import (
    CategoryReading, compliance, platform_health_score, per_tenant_scores,
    DEFAULT_WEIGHTS, _sample,
)


def test_full_compliance_when_meeting_target():
    assert compliance(CategoryReading(0.999, 0.999, True)) == 100.0


def test_zero_compliance_when_budget_blown():
    # availability 99.9% target, observed 99.8% -> 0.001 deficit on 0.001 budget
    assert compliance(CategoryReading(0.999, 0.998, True)) == 0.0


def test_lower_is_better_cost():
    # cost target 0.95 of budget, actual 0.88 -> under, full marks
    assert compliance(CategoryReading(0.95, 0.88, False)) == 100.0
    # over budget
    assert compliance(CategoryReading(0.95, 0.97, False)) < 100.0


def test_score_in_range():
    s = platform_health_score(_sample())
    assert 0.0 <= s <= 100.0


def test_weights_must_sum_to_one():
    try:
        platform_health_score(_sample(), {"availability": 0.5})
    except (ValueError, KeyError):
        return
    raise AssertionError("should reject weights not summing to 1.0")


def test_per_tenant_suppresses_low_traffic():
    readings = {"t1": _sample(), "t2": _sample()}
    traffic = {"t1": 50_000, "t2": 10}
    out = per_tenant_scores(readings, traffic, traffic_floor=1000)
    assert out["t2"] is None and out["t1"] is not None


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

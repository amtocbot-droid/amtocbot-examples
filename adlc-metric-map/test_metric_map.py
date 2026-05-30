"""Tests. Run: python3 test_metric_map.py"""

from __future__ import annotations

from metric_map import (
    PreDeployGate, decide_deploy, score_trajectory_diff, steady_state_drift,
)


def test_gate_ships_when_all_pass():
    ok, p = decide_deploy(PreDeployGate(0.94, 0.93, 0.09, 0.31), prev_bar=0.93)
    assert ok and all(p["checks"].values())


def test_gate_holds_on_low_golden():
    ok, p = decide_deploy(PreDeployGate(0.80, 0.93, 0.09, 0.31), prev_bar=0.93)
    assert not ok and p["checks"]["golden_pass_rate"] is False


def test_gate_holds_on_regression_below_prev_bar():
    ok, p = decide_deploy(PreDeployGate(0.94, 0.90, 0.09, 0.31), prev_bar=0.93)
    assert not ok and p["checks"]["regression_floor"] is False


def test_trajectory_flags_too_much_worse():
    r = score_trajectory_diff(["worse"] * 30 + ["same"] * 70)
    assert r["flag"] is True


def test_trajectory_clean_when_mostly_same():
    r = score_trajectory_diff(["same"] * 80 + ["better"] * 15 + ["worse"] * 5)
    assert r["flag"] is False


def test_drift_insufficient_history():
    assert steady_state_drift([0.9, 0.9])["status"] == "insufficient_history"


def test_drift_flags_sustained_drop():
    # baseline needs some variance for the z-score to be meaningful
    baseline = [0.89, 0.91] * 6  # mean 0.90, small stdev
    r = steady_state_drift(baseline + [0.84, 0.83])
    assert r["flag"] is True and r["drop"] > 0.03 and r["z"] > 1.5


def test_drift_clean_when_stable():
    r = steady_state_drift([0.90] * 14)
    assert r["flag"] is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

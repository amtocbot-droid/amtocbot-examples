"""Tests. Run: python3 test_alert_fatigue.py"""

from __future__ import annotations

from alert_fatigue import analyze, missing_runbooks


def test_token_alert_missing_runbook():
    assert "TokenUsageAboveAverage" in missing_runbooks()


def test_critical_alerts_have_runbooks():
    missing = set(missing_runbooks())
    assert "ADLCPreDeployRegressionFloorBroken" not in missing
    assert "PostDeployToolErrorSpike" not in missing


def test_fatigue_offender_flagged():
    by_alert = {r.alert: r for r in analyze()}
    token = by_alert["TokenUsageAboveAverage"]
    assert token.is_offender is True
    assert token.actionable_ratio < 0.30


def test_actionable_alert_not_flagged():
    by_alert = {r.alert: r for r in analyze()}
    spike = by_alert["PostDeployToolErrorSpike"]
    assert spike.is_offender is False
    assert spike.actionable_ratio > 0.30


def test_reports_sorted_worst_first():
    ratios = [r.actionable_ratio for r in analyze()]
    assert ratios == sorted(ratios)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

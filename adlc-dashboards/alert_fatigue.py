"""Alert-fatigue analyzer for ADLC dashboards.

Companion code for the AmtocSoft post
"ADLC Dashboards: Panel Queries, Layouts, PromQL, Grafana, Alert Fatigue".

The post's central operational claim: an alert that fires often but is
rarely actioned is noise, and noise trains the on-call to ignore the page.
Two checks here, runnable against a firing log:

1. Every alert rule must carry a `runbook` annotation (an alert with no
   runbook is unactionable by construction).
2. Each alert's *actionable ratio* (acked-and-acted / total fires) must clear
   a floor; below it, the alert is a fatigue offender and should be tuned,
   routed to a dashboard, or deleted.

Pure standard library — alert rules and the firing log are plain dicts,
mirroring an alertmanager rules file and an incident log.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

# Mirrors alertmanager rules: severity/stage labels + annotations.
ALERT_RULES = [
    {"alert": "ADLCPreDeployRegressionFloorBroken", "stage": "pre-deploy",
     "severity": "critical",
     "annotations": {"runbook": "https://internal/runbooks/adlc/pre-deploy-regression-floor"}},
    {"alert": "PostDeployToolErrorSpike", "stage": "post-deploy",
     "severity": "critical",
     "annotations": {"runbook": "https://internal/runbooks/adlc/post-deploy-tool-error"}},
    {"alert": "SteadyStateQualityDrift", "stage": "steady-state",
     "severity": "warning",
     "annotations": {"runbook": "https://internal/runbooks/adlc/steady-state-drift"}},
    # A classic fatigue offender: fires constantly, no runbook, rarely acted on.
    {"alert": "TokenUsageAboveAverage", "stage": "steady-state",
     "severity": "warning", "annotations": {}},
]

# Firing log: each fire is (alert, outcome). outcome in {acted, ignored, auto_resolved}.
FIRING_LOG = (
    [("ADLCPreDeployRegressionFloorBroken", "acted")] * 3
    + [("PostDeployToolErrorSpike", "acted")] * 8
    + [("PostDeployToolErrorSpike", "auto_resolved")] * 1
    + [("SteadyStateQualityDrift", "acted")] * 4
    + [("SteadyStateQualityDrift", "ignored")] * 2
    + [("TokenUsageAboveAverage", "ignored")] * 40
    + [("TokenUsageAboveAverage", "acted")] * 2
)

ACTIONABLE_FLOOR = 0.30


@dataclass
class AlertReport:
    alert: str
    fires: int
    actionable_ratio: float
    has_runbook: bool
    is_offender: bool


def missing_runbooks(rules=ALERT_RULES) -> list[str]:
    return [r["alert"] for r in rules if not r["annotations"].get("runbook")]


def analyze(rules=ALERT_RULES, log=FIRING_LOG,
            floor: float = ACTIONABLE_FLOOR) -> list[AlertReport]:
    runbook = {r["alert"]: bool(r["annotations"].get("runbook")) for r in rules}
    fires: Counter[str] = Counter(a for a, _ in log)
    acted: Counter[str] = Counter(a for a, o in log if o == "acted")
    reports = []
    for alert, n in fires.items():
        ratio = acted[alert] / n if n else 0.0
        has_rb = runbook.get(alert, False)
        offender = ratio < floor or not has_rb
        reports.append(AlertReport(alert, n, round(ratio, 3), has_rb, offender))
    return sorted(reports, key=lambda r: r.actionable_ratio)


if __name__ == "__main__":
    missing = missing_runbooks()
    print("alerts missing a runbook:", missing or "(none)")
    print(f"\n{'alert':<38}{'fires':>6}{'acted%':>8}  runbook  offender")
    print("-" * 70)
    for r in analyze():
        print(f"{r.alert:<38}{r.fires:>6}{r.actionable_ratio*100:>7.0f}%"
              f"  {'yes' if r.has_runbook else 'NO ':>7}  "
              f"{'TUNE' if r.is_offender else 'ok'}")

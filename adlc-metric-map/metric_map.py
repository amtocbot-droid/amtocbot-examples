"""ADLC metric map: pre-deploy gate, post-deploy trajectory diff, and
steady-state drift detection.

Companion code for the AmtocSoft post
"The Agent Development Lifecycle (ADLC): Pre-Deploy, Post-Deploy,
Steady-State Metrics".

Each lifecycle stage has one decision function. Pure standard library.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import mean, stdev


# --------------------------------------------------------------------------
# Pre-deploy: a four-check gate. All four must pass to ship.
# --------------------------------------------------------------------------
@dataclass
class PreDeployGate:
    golden_pass_rate: float        # tier 1 + tier 2 combined
    regression_floor: float        # never drop below previous bar
    judge_disagreement: float      # human-vs-judge sample
    eval_drift_kl: float           # eval vs production embedding KL


def decide_deploy(g: PreDeployGate, *, min_golden=0.92, max_regression_drop=0.01,
                  max_judge_disagreement=0.12, max_eval_drift=0.40,
                  prev_bar: float) -> tuple[bool, dict]:
    """Return (deploy_ok, reason_payload). All four checks must pass."""
    checks = {
        "golden_pass_rate": g.golden_pass_rate >= min_golden,
        "regression_floor": g.regression_floor >= prev_bar - max_regression_drop,
        "judge_disagreement": g.judge_disagreement <= max_judge_disagreement,
        "eval_drift_kl": g.eval_drift_kl <= max_eval_drift,
    }
    return all(checks.values()), {
        "checks": checks,
        "values": {
            "golden": round(g.golden_pass_rate, 3),
            "regression": round(g.regression_floor, 3),
            "disagreement": round(g.judge_disagreement, 3),
            "drift_kl": round(g.eval_drift_kl, 3),
            "prev_bar": round(prev_bar, 3),
        },
    }


# --------------------------------------------------------------------------
# Post-deploy: A/B trajectory diff. Asymmetric — tolerate "same", fear "worse".
# --------------------------------------------------------------------------
def score_trajectory_diff(judgements: list[str]) -> dict:
    c = Counter(judgements)
    total = sum(c.values()) or 1
    better, same, worse = c["better"] / total, c["same"] / total, c["worse"] / total
    rolling_worse_share = worse
    flag = rolling_worse_share > 0.20 or (better - worse) < -0.05
    return {"n": total, "better": round(better, 3), "same": round(same, 3),
            "worse": round(worse, 3), "flag": flag}


# --------------------------------------------------------------------------
# Steady-state: sustained drop vs a rolling baseline (z-scored).
# --------------------------------------------------------------------------
def steady_state_drift(weekly_scores: list[float], baseline_window: int = 12) -> dict:
    if len(weekly_scores) < baseline_window + 2:
        return {"status": "insufficient_history", "weeks": len(weekly_scores)}
    baseline = weekly_scores[-(baseline_window + 2):-2]
    recent = weekly_scores[-2:]
    mu = mean(baseline)
    sigma = stdev(baseline) if len(baseline) > 1 else 0.0
    drop_vs_baseline = mu - mean(recent)
    z = drop_vs_baseline / sigma if sigma > 0 else 0.0
    flag = drop_vs_baseline > 0.03 and z > 1.5
    return {"baseline_mean": round(mu, 3), "recent_mean": round(mean(recent), 3),
            "drop": round(drop_vs_baseline, 3), "z": round(z, 2), "flag": flag}


if __name__ == "__main__":
    ok, payload = decide_deploy(
        PreDeployGate(golden_pass_rate=0.94, regression_floor=0.93,
                      judge_disagreement=0.09, eval_drift_kl=0.31),
        prev_bar=0.93)
    print("pre-deploy:", "SHIP" if ok else "HOLD", payload["checks"])
    print("trajectory:", score_trajectory_diff(
        ["same"] * 60 + ["better"] * 30 + ["worse"] * 10))
    print("steady-state:", steady_state_drift(
        [0.90] * 12 + [0.84, 0.83]))

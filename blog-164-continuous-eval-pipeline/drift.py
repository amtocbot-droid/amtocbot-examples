"""Continuous evaluation: embedding-drift detection (MMD) and canary replay.

Companion code for the AmtocSoft post
"Continuous Evaluation for AI Agents: Drift Detection and Replay".

The post computes Maximum Mean Discrepancy with numpy. This reimplements MMD
with the RBF kernel in pure Python (fine for the small daily samples a drift
job actually compares), plus a canary replay harness graded against
required/preferred criteria. No dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# --------------------------------------------------------------------------
# Embedding drift via Maximum Mean Discrepancy (RBF kernel).
# --------------------------------------------------------------------------
def _rbf(a: list[float], b: list[float], sigma: float) -> float:
    d2 = sum((x - y) ** 2 for x, y in zip(a, b))
    return math.exp(-d2 / (2 * sigma ** 2))


def _mean_kernel(xs: list[list[float]], ys: list[list[float]], sigma: float) -> float:
    total = sum(_rbf(x, y, sigma) for x in xs for y in ys)
    return total / (len(xs) * len(ys))


def mmd_squared(x: list[list[float]], y: list[list[float]], sigma: float = 1.0) -> float:
    """Squared MMD between two samples. Higher = more different."""
    return (_mean_kernel(x, x, sigma) + _mean_kernel(y, y, sigma)
            - 2 * _mean_kernel(x, y, sigma))


@dataclass
class DriftResult:
    dimension: str
    score: float
    threshold: float
    direction: str
    sample_size: int
    fired: bool


def detect_embedding_drift(baseline: list[list[float]], recent: list[list[float]],
                           threshold: float = 0.05, sigma: float = 1.0,
                           min_sample: int = 50) -> DriftResult:
    if len(recent) < min_sample:
        return DriftResult("embeddings", 0.0, threshold, "insufficient",
                           len(recent), False)
    score = mmd_squared(baseline, recent, sigma)
    dim = len(baseline[0])
    base_centroid = [sum(v[i] for v in baseline) / len(baseline) for i in range(dim)]
    rec_centroid = [sum(v[i] for v in recent) / len(recent) for i in range(dim)]
    shift = math.sqrt(sum((a - b) ** 2 for a, b in zip(base_centroid, rec_centroid)))
    direction = "expanding" if shift > 0.1 else "stable"
    return DriftResult("embeddings", score, threshold, direction,
                       len(recent), score > threshold)


# --------------------------------------------------------------------------
# Canary replay: grade a fixed answer against required/preferred criteria.
# --------------------------------------------------------------------------
@dataclass
class Criterion:
    text: str
    severity: str  # "required" | "preferred"
    keyword: str   # what the grader looks for (stand-in for an LLM judge)


@dataclass
class CanaryResult:
    name: str
    passed: list[str]
    failed: list[str]
    fired: bool


def grade_canary(name: str, agent_answer: str, criteria: list[Criterion]) -> CanaryResult:
    passed, failed = [], []
    for c in criteria:
        if c.keyword.lower() in agent_answer.lower():
            passed.append(c.text)
        else:
            failed.append(c.text)
    # A canary fires if any *required* criterion failed.
    fired = any(c.severity == "required" and c.text in failed for c in criteria)
    return CanaryResult(name, passed, failed, fired)

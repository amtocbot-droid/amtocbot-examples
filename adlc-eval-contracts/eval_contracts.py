"""Codified eval contracts: turn ad-hoc cohort evals into versioned
regression bases with pinned tolerances and rationales.

Companion code for the AmtocSoft ADLC eval-contract series (posts 189-201):
eval contracts, drift detection, attestation-aware retrospectives, and the
manifest-ledger tooling those posts build on this foundation.

The post splits this across evals/base.py, evals/metrics.py, and
evals/contracts/customer_support.py. It's collapsed into one runnable module
here. Pure standard library.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
def kl_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """KL(p || q) over a shared support, with Laplace smoothing so that a
    category present in one distribution but not the other doesn't blow up."""
    keys = set(p) | set(q)
    eps = 1e-6
    total = 0.0
    for k in keys:
        pk = p.get(k, 0.0) + eps
        qk = q.get(k, 0.0) + eps
        total += pk * math.log(pk / qk)
    return total


# --------------------------------------------------------------------------
# contract primitives
# --------------------------------------------------------------------------
@dataclass
class Invariant:
    name: str
    metric: Callable[[list[dict]], Any]
    compare: str  # "delta_percent" | "delta_absolute" | "kl_divergence"
    tolerance: float
    rationale: str


@dataclass
class EvalContract:
    name: str
    baseline_traces_data: list[dict]
    invariants: list[Invariant]
    drift_check_model: str = "baseline_producer_v3"
    version: int = 1

    def evaluate(self, candidate_traces: list[dict]) -> list[dict]:
        results = []
        for inv in self.invariants:
            base_value = inv.metric(self.baseline_traces_data)
            cand_value = inv.metric(candidate_traces)
            passed, delta = self._compare(inv, base_value, cand_value)
            results.append(dict(name=inv.name, passed=passed, delta=delta,
                                tolerance=inv.tolerance, rationale=inv.rationale))
        return results

    def passed(self, candidate_traces: list[dict]) -> bool:
        return all(r["passed"] for r in self.evaluate(candidate_traces))

    def _compare(self, inv: Invariant, base: Any, cand: Any) -> tuple[bool, float]:
        if inv.compare == "delta_percent":
            delta = abs(cand - base) / base * 100.0 if base else float("inf")
            return delta <= inv.tolerance, delta
        if inv.compare == "delta_absolute":
            delta = abs(cand - base)
            return delta <= inv.tolerance, delta
        if inv.compare == "kl_divergence":
            delta = kl_divergence(base, cand)
            return delta <= inv.tolerance, delta
        raise ValueError(f"unknown compare rule: {inv.compare}")


# --------------------------------------------------------------------------
# metric functions used by the customer_support contract
# --------------------------------------------------------------------------
def tool_call_distribution(traces: list[dict]) -> dict[str, float]:
    counts: Counter[str] = Counter()
    for t in traces:
        for call in t.get("tool_calls", []):
            counts[call["tool"]] += 1
    total = sum(counts.values()) or 1
    return {tool: n / total for tool, n in counts.items()}


def avg_quality(traces: list[dict]) -> float:
    scores = [t["quality"] for t in traces if "quality" in t]
    return sum(scores) / len(scores) if scores else 0.0


def refusal_rate(traces: list[dict]) -> float:
    return sum(t.get("refused", False) for t in traces) / len(traces) if traces else 0.0


def customer_support_contract(baseline: list[dict]) -> EvalContract:
    return EvalContract(
        name="customer_support",
        baseline_traces_data=baseline,
        invariants=[
            Invariant("avg-quality-delta", avg_quality, "delta_percent", 2.0,
                      "2% loss is below the per-incident threshold from PM-2026-01-04."),
            Invariant("tool-call-dist-kl", tool_call_distribution, "kl_divergence", 0.05,
                      "0.05 KL is the tolerance that would have caught the March cohort drop."),
            Invariant("refusal-rate-delta", refusal_rate, "delta_absolute", 0.01,
                      "1pp absolute refusal-rate change has paged on-call three times."),
        ],
    )

"""EU AI Act Article 14 runtime: decision traces, risk classification, and
human-oversight routing.

Companion code for the AmtocSoft post
"EU AI Act Article 14: An Engineering Checklist (August 2026)".

Every decision gets a `DecisionTrace`. A pluggable classifier assigns a risk
class, and the router enforces the oversight each class requires: HIGH blocks
on human review, ELEVATED queues async review and delivers, STANDARD delivers
and samples for review. The post's code is async with a real review queue;
this uses an in-memory queue and a deterministic RNG so it runs standalone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

REFUSAL = "I can't complete that automatically; it has been escalated."


@dataclass
class DecisionTrace:
    decision_id: str
    user_id: str = ""
    model_id: str = ""
    model_version: str = ""
    resolved_prompt: str = ""
    tool_calls: list = field(default_factory=list)
    final_output: str = ""
    confidence_score: Optional[float] = None
    risk_class: str = "standard"  # standard | elevated | high


class RiskClass(Enum):
    STANDARD = "standard"
    ELEVATED = "elevated"
    HIGH = "high"


def classify_risk(decision: DecisionTrace) -> RiskClass:
    """Pluggable risk classifier; thresholds tune per system."""
    if decision.risk_class == "high":
        return RiskClass.HIGH
    if decision.confidence_score is not None and decision.confidence_score < 0.6:
        return RiskClass.HIGH
    if decision.confidence_score is not None and decision.confidence_score < 0.8:
        return RiskClass.ELEVATED
    return RiskClass.STANDARD


@dataclass
class Verdict:
    approved: bool
    alternate_output: Optional[str] = None


class ReviewQueue:
    def __init__(self):
        self.blocking: list[DecisionTrace] = []
        self.async_queue: list[tuple[DecisionTrace, int]] = []
        self._verdicts: dict[str, Verdict] = {}

    def set_verdict(self, decision_id: str, verdict: Verdict) -> None:
        self._verdicts[decision_id] = verdict

    def enqueue_blocking(self, d: DecisionTrace) -> Verdict:
        self.blocking.append(d)
        # In production this awaits a human; here we read a pre-set verdict,
        # defaulting to "not approved" (fail closed) if none was provided.
        return self._verdicts.get(d.decision_id, Verdict(approved=False))

    def enqueue_async(self, d: DecisionTrace, sla_hours: int) -> None:
        self.async_queue.append((d, sla_hours))


def route_decision(decision: DecisionTrace, output: str, queue: ReviewQueue,
                   sample) -> str:
    """Returns what is actually delivered to the user. `sample` is a callable
    returning a float in [0,1) (injected RNG) for STANDARD sampling."""
    risk = classify_risk(decision)
    if risk == RiskClass.HIGH:
        verdict = queue.enqueue_blocking(decision)
        if verdict.approved:
            return output
        return verdict.alternate_output or REFUSAL
    if risk == RiskClass.ELEVATED:
        queue.enqueue_async(decision, sla_hours=24)
        return output
    # STANDARD: deliver, sample 5% for retrospective review.
    if sample() < 0.05:
        queue.enqueue_async(decision, sla_hours=72)
    return output

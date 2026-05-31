"""EU AI Act Article 14 traceability: an oversight adapter that records every
auto and human-reviewed decision into a tamper-evident audit log.

Companion code for the AmtocSoft post
"EU AI Act Article 14: Traceability for AI Engineers".

Subjects are referenced by pseudonym (never raw PII). Each decision is
emitted as an audit event; the log is hash-chained so a removed or altered
record is detectable. The post is async with a real sink; this uses an
in-memory hash-chained log so it runs standalone. Pure standard library.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelOutput:
    decision: str
    score: float
    confidence_calibrated: float
    contributing_factors: list[str] = field(default_factory=list)


@dataclass
class HumanReview:
    reviewer_id_pseudonym: str
    reviewer_role: str
    decision: str
    rationale_id: str
    rationale_text: str
    automation_bias_acknowledgment: bool


class AuditLog:
    """Hash-chained append-only audit log."""

    def __init__(self):
        self.records: list[dict] = []

    def emit(self, event_type: str, data: dict) -> dict:
        prev = self.records[-1]["hash"] if self.records else "genesis"
        payload = {"type": event_type, "data": data, "prev": prev}
        h = hashlib.sha256(
            (prev + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
        record = {**payload, "hash": h}
        self.records.append(record)
        return record

    def verify(self) -> bool:
        """Return True if the chain is intact."""
        prev = "genesis"
        for r in self.records:
            payload = {"type": r["type"], "data": r["data"], "prev": r["prev"]}
            expect = hashlib.sha256(
                (prev + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
            if r["prev"] != prev or r["hash"] != expect:
                return False
            prev = r["hash"]
        return True


class OversightAdapter:
    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    def submit_decision(self, subject_pseudonym: str, model_output: ModelOutput,
                        review: Optional[HumanReview]) -> dict:
        if review is None:
            return self.audit_log.emit("auto_decision_applied", {
                "subject_pseudonym": subject_pseudonym,
                "decision": model_output.decision,
                "score": model_output.score,
                "confidence_calibrated": model_output.confidence_calibrated,
                "contributing_factors": model_output.contributing_factors,
            })
        return self.audit_log.emit("human_reviewed_decision", {
            "subject_pseudonym": subject_pseudonym,
            "model_decision": model_output.decision,
            "final_decision": review.decision,
            "reviewer": review.reviewer_id_pseudonym,
            "reviewer_role": review.reviewer_role,
            "rationale_id": review.rationale_id,
            "automation_bias_acknowledged": review.automation_bias_acknowledgment,
        })

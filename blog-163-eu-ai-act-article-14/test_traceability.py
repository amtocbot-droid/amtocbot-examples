"""Tests. Run: python3 test_traceability.py"""

from __future__ import annotations

from traceability import AuditLog, OversightAdapter, ModelOutput, HumanReview


def _adapter():
    log = AuditLog()
    return log, OversightAdapter(log)


def test_auto_decision_recorded():
    log, a = _adapter()
    a.submit_decision("s1", ModelOutput("approve", 0.9, 0.85), review=None)
    assert log.records[0]["type"] == "auto_decision_applied"


def test_human_review_recorded():
    log, a = _adapter()
    a.submit_decision("s1", ModelOutput("deny", 0.5, 0.4),
                      HumanReview("r1", "officer", "approve", "RAT-1", "why", True))
    rec = log.records[0]
    assert rec["type"] == "human_reviewed_decision"
    assert rec["data"]["final_decision"] == "approve"


def test_no_raw_pii_only_pseudonym():
    log, a = _adapter()
    a.submit_decision("subj-abc", ModelOutput("approve", 0.9, 0.8), review=None)
    assert log.records[0]["data"]["subject_pseudonym"] == "subj-abc"


def test_chain_verifies_when_intact():
    log, a = _adapter()
    a.submit_decision("s1", ModelOutput("approve", 0.9, 0.8), review=None)
    a.submit_decision("s2", ModelOutput("deny", 0.5, 0.4), review=None)
    assert log.verify() is True


def test_chain_detects_tampering():
    log, a = _adapter()
    a.submit_decision("s1", ModelOutput("approve", 0.9, 0.8), review=None)
    log.records[0]["data"]["decision"] = "deny"
    assert log.verify() is False


def test_chain_detects_deletion():
    log, a = _adapter()
    a.submit_decision("s1", ModelOutput("approve", 0.9, 0.8), review=None)
    a.submit_decision("s2", ModelOutput("deny", 0.5, 0.4), review=None)
    del log.records[0]
    assert log.verify() is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

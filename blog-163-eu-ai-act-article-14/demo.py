"""Record an auto decision and a human-reviewed decision, then show the audit
chain verifies and detects tampering.

    $ python3 demo.py
"""

from __future__ import annotations

from traceability import AuditLog, OversightAdapter, ModelOutput, HumanReview


def main() -> None:
    log = AuditLog()
    adapter = OversightAdapter(log)

    adapter.submit_decision(
        "subj-7f3a",
        ModelOutput("approve", score=0.88, confidence_calibrated=0.82,
                    contributing_factors=["tenure", "history"]),
        review=None)

    adapter.submit_decision(
        "subj-9c1b",
        ModelOutput("deny", score=0.55, confidence_calibrated=0.51),
        review=HumanReview("rev-22", "credit_officer", "approve", "RAT-9",
                           "Model under-weighted recent repayment.", True))

    print(f"audit records: {len(log.records)}")
    for r in log.records:
        print(f"  {r['type']}  hash={r['hash'][:8]}")

    assert log.verify() is True
    print("chain verifies:", log.verify())

    # Tamper with a record -> verification must fail.
    log.records[0]["data"]["decision"] = "deny"
    assert log.verify() is False
    print("after tampering, chain verifies:", log.verify())
    print("\nOK: pseudonymous, hash-chained traceability detects tampering.")


if __name__ == "__main__":
    main()

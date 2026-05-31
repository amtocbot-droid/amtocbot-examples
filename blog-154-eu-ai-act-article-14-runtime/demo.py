"""Route three decisions of different risk classes through oversight.

    $ python3 demo.py
"""

from __future__ import annotations

from oversight import (
    DecisionTrace, RiskClass, classify_risk, route_decision, ReviewQueue, Verdict,
    REFUSAL,
)


def main() -> None:
    queue = ReviewQueue()

    high = DecisionTrace("d-high", confidence_score=0.4)
    elevated = DecisionTrace("d-elev", confidence_score=0.72)
    standard = DecisionTrace("d-std", confidence_score=0.95)

    print("risk classes:")
    for d in (high, elevated, standard):
        print(f"  {d.decision_id}: {classify_risk(d).value}")

    # HIGH blocks; with no human approval it fails closed to a refusal.
    out_high = route_decision(high, "auto-approve $9000 refund", queue, sample=lambda: 1.0)
    print("\nhigh-risk delivered:", out_high)
    assert out_high == REFUSAL
    assert queue.blocking and queue.blocking[0].decision_id == "d-high"

    # HIGH with a human approval delivers the original output.
    queue.set_verdict("d-high", Verdict(approved=True))
    assert route_decision(high, "auto-approve $9000 refund", queue,
                          sample=lambda: 1.0) == "auto-approve $9000 refund"

    # ELEVATED delivers but queues async review.
    out_elev = route_decision(elevated, "answer", queue, sample=lambda: 1.0)
    assert out_elev == "answer" and queue.async_queue
    print("elevated delivered + queued for async review")

    # STANDARD delivers; sampled 5% for retrospective review.
    out_std = route_decision(standard, "answer", queue, sample=lambda: 0.01)
    assert out_std == "answer"
    print("standard delivered (sampled for review)")
    print("\nOK: Article 14 oversight enforced per risk class.")


if __name__ == "__main__":
    main()

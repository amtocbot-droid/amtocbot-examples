"""Simulate a daily drift job: no-drift day stays quiet, a shifted day fires;
then grade two canaries.

    $ python3 simulate_drift.py
"""

from __future__ import annotations

import random

from drift import detect_embedding_drift, grade_canary, Criterion


def cluster(center, n, spread, rng, dim=8):
    return [[center + rng.gauss(0, spread) for _ in range(dim)] for _ in range(n)]


def main() -> None:
    rng = random.Random(0)
    baseline = cluster(0.0, 200, 0.3, rng)

    same = cluster(0.0, 80, 0.3, rng)
    drifted = cluster(1.2, 80, 0.3, rng)

    r_same = detect_embedding_drift(baseline, same, threshold=0.05)
    r_drift = detect_embedding_drift(baseline, drifted, threshold=0.05)
    print(f"no-drift day:  mmd={r_same.score:.4f}  fired={r_same.fired}")
    print(f"shifted day:   mmd={r_drift.score:.4f}  fired={r_drift.fired} "
          f"({r_drift.direction})")
    assert r_same.fired is False
    assert r_drift.fired is True

    criteria = [
        Criterion("must cite the refund policy", "required", "refund policy"),
        Criterion("should mention 30-day window", "preferred", "30 day"),
    ]
    good = grade_canary("refund_q", "Per our refund policy you have a 30 day window.",
                        criteria)
    bad = grade_canary("refund_q", "Sure, you can get your money back.", criteria)
    print(f"\ncanary good: fired={good.fired}  passed={good.passed}")
    print(f"canary bad:  fired={bad.fired}  failed={bad.failed}")
    assert good.fired is False and bad.fired is True
    print("\nOK: drift job quiet on stable traffic, fires on a shift; canaries grade.")


if __name__ == "__main__":
    main()

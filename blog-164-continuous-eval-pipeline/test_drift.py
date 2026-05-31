"""Tests. Run: python3 test_drift.py"""

from __future__ import annotations

import random

from drift import (
    mmd_squared, detect_embedding_drift, grade_canary, Criterion,
)


def _cluster(center, n, spread, rng, dim=8):
    return [[center + rng.gauss(0, spread) for _ in range(dim)] for _ in range(n)]


def test_mmd_near_zero_for_same_distribution():
    rng = random.Random(1)
    a = _cluster(0.0, 100, 0.3, rng)
    b = _cluster(0.0, 100, 0.3, rng)
    assert mmd_squared(a, b) < 0.05


def test_mmd_large_for_shifted_distribution():
    rng = random.Random(1)
    a = _cluster(0.0, 100, 0.3, rng)
    b = _cluster(1.5, 100, 0.3, rng)
    assert mmd_squared(a, b) > 0.05


def test_insufficient_sample_does_not_fire():
    rng = random.Random(1)
    base = _cluster(0.0, 200, 0.3, rng)
    r = detect_embedding_drift(base, _cluster(0.0, 10, 0.3, rng))
    assert r.direction == "insufficient" and r.fired is False


def test_drift_fires_on_shift():
    rng = random.Random(2)
    base = _cluster(0.0, 200, 0.3, rng)
    r = detect_embedding_drift(base, _cluster(1.2, 80, 0.3, rng), threshold=0.05)
    assert r.fired is True


def test_canary_required_failure_fires():
    crit = [Criterion("cite policy", "required", "policy")]
    assert grade_canary("c", "no mention here", crit).fired is True


def test_canary_preferred_failure_does_not_fire():
    crit = [Criterion("nice to have", "preferred", "bonus")]
    assert grade_canary("c", "no mention here", crit).fired is False


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

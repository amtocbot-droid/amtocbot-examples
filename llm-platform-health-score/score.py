"""Platform Health Score: roll four SLO categories up into one 0-100 number.

Companion code for the AmtocSoft posts
"Platform Health Score for LLM Systems: Rolling Up Four SLOs Into a
Board-Ready Number" and "Per-Tenant Platform Health Score at Scale".

The composite is a weighted average of per-category SLO compliance, where
each category's compliance is how much of its error budget remains. The
Prometheus wiring in the post is omitted; the scoring core is verbatim and
pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_WEIGHTS = {
    "availability": 0.30,
    "quality": 0.30,
    "latency": 0.25,
    "cost": 0.15,
}


@dataclass(frozen=True)
class CategoryReading:
    target: float        # SLO target as a fraction, e.g. 0.999 availability
    actual: float        # observed value over the rolling window
    higher_is_better: bool


def compliance(reading: CategoryReading) -> float:
    """SLO compliance in [0, 100] = fraction of error budget remaining."""
    if reading.higher_is_better:
        deficit = max(0.0, reading.target - reading.actual)
        budget = 1.0 - reading.target
    else:
        deficit = max(0.0, reading.actual - reading.target)
        budget = reading.target
    if budget == 0:
        return 100.0 if deficit == 0 else 0.0
    return max(0.0, 100.0 * (1.0 - deficit / budget))


def platform_health_score(readings: dict[str, CategoryReading],
                          weights: dict[str, float] = DEFAULT_WEIGHTS) -> float:
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1.0")
    return sum(weights[c] * compliance(r) for c, r in readings.items())


def per_tenant_scores(tenant_readings: dict[str, dict[str, CategoryReading]],
                      min_traffic: dict[str, int],
                      traffic_floor: int = 1000) -> dict[str, float | None]:
    """Per-tenant rollup. Low-traffic tenants are suppressed (return None)
    to keep noise out of the board number — the post's noise-suppression rule."""
    out: dict[str, float | None] = {}
    for tenant, readings in tenant_readings.items():
        if min_traffic.get(tenant, 0) < traffic_floor:
            out[tenant] = None
        else:
            out[tenant] = platform_health_score(readings)
    return out


def _sample() -> dict[str, CategoryReading]:
    return {
        "availability": CategoryReading(0.999, 0.9994, True),
        "quality": CategoryReading(0.95, 0.96, True),
        "latency": CategoryReading(0.95, 0.92, True),
        "cost": CategoryReading(0.95, 0.88, False),  # under budget -> full marks
    }


if __name__ == "__main__":
    readings = _sample()
    print("per-category compliance:")
    for cat, r in readings.items():
        print(f"  {cat:<14}{compliance(r):6.1f}")
    print(f"\nplatform health score: {platform_health_score(readings):.1f} / 100")

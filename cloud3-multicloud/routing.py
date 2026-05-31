"""Active-active / failover traffic routing for a hybrid multicloud
("Cloud 3") architecture: weighted DNS-style routing with health checks.

Companion code for the AmtocSoft post
"Cloud 3: Hybrid Multicloud Sovereign Architecture".

The post drives Route53 weighted records via boto3. The portable logic is
the *routing decision*: split traffic across providers by weight, drop an
unhealthy provider out of rotation, and fail over deterministically. This
models that with no AWS dependency. Pure standard library.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Endpoint:
    name: str            # e.g. "aws-primary"
    target: str          # CNAME target
    weight: int          # relative routing weight
    healthy: bool = True


class WeightedRouter:
    def __init__(self, endpoints: list[Endpoint]):
        self.endpoints = endpoints

    def healthy_endpoints(self) -> list[Endpoint]:
        return [e for e in self.endpoints if e.healthy and e.weight > 0]

    def route(self, key: int) -> Endpoint | None:
        """Deterministically map an integer key (e.g. hash of client ip) to an
        endpoint, proportional to weight, over healthy endpoints only."""
        live = self.healthy_endpoints()
        total = sum(e.weight for e in live)
        if total == 0:
            return None
        slot = key % total
        cursor = 0
        for e in live:
            cursor += e.weight
            if slot < cursor:
                return e
        return live[-1]

    def distribution(self, n: int = 10_000) -> dict[str, float]:
        """Empirical traffic share over n synthetic keys."""
        counts: dict[str, int] = {}
        for k in range(n):
            e = self.route(k)
            if e:
                counts[e.name] = counts.get(e.name, 0) + 1
        return {name: c / n for name, c in counts.items()}

    def set_health(self, name: str, healthy: bool) -> None:
        for e in self.endpoints:
            if e.name == name:
                e.healthy = healthy

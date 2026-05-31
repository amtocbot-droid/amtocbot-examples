"""Split traffic 80/20 across AWS/Azure, then fail AWS and watch all traffic
move to Azure.

    $ python3 demo.py
"""

from __future__ import annotations

from routing import Endpoint, WeightedRouter


def main() -> None:
    router = WeightedRouter([
        Endpoint("aws-primary", "api-aws.internal", weight=80),
        Endpoint("azure-secondary", "api-azure.internal", weight=20),
    ])

    print("active-active 80/20 distribution:")
    for name, share in sorted(router.distribution().items()):
        print(f"  {name}: {share:.1%}")
    dist = router.distribution()
    assert 0.77 <= dist["aws-primary"] <= 0.83

    # AWS health check fails -> failover.
    router.set_health("aws-primary", False)
    failover = router.distribution()
    print("\nafter AWS health check fails:")
    for name, share in sorted(failover.items()):
        print(f"  {name}: {share:.1%}")
    assert failover.get("aws-primary", 0) == 0
    assert abs(failover["azure-secondary"] - 1.0) < 1e-9

    # Both down -> no route (caller surfaces 503).
    router.set_health("azure-secondary", False)
    assert router.route(0) is None
    print("\nboth unhealthy -> no endpoint (503 to caller)")
    print("\nOK: weighted active-active with deterministic health failover.")


if __name__ == "__main__":
    main()

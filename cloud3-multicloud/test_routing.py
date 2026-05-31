"""Tests. Run: python3 test_routing.py"""

from __future__ import annotations

from routing import Endpoint, WeightedRouter


def _router():
    return WeightedRouter([
        Endpoint("aws", "a", weight=80),
        Endpoint("azure", "b", weight=20),
    ])


def test_distribution_matches_weights():
    d = _router().distribution()
    assert 0.77 <= d["aws"] <= 0.83
    assert 0.17 <= d["azure"] <= 0.23


def test_routing_is_deterministic():
    r = _router()
    assert r.route(12345).name == r.route(12345).name


def test_failover_removes_unhealthy():
    r = _router()
    r.set_health("aws", False)
    d = r.distribution()
    assert d.get("aws", 0) == 0 and abs(d["azure"] - 1.0) < 1e-9


def test_all_down_returns_none():
    r = _router()
    r.set_health("aws", False)
    r.set_health("azure", False)
    assert r.route(0) is None


def test_zero_weight_excluded():
    r = WeightedRouter([Endpoint("a", "a", 0), Endpoint("b", "b", 10)])
    assert r.route(5).name == "b"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

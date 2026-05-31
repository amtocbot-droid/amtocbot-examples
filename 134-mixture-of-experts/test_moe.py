"""Tests. Run: python3 test_moe.py"""

from __future__ import annotations

import random

from moe import softmax, top_k_indices, MoERouter, load_balancing_loss


def test_softmax_sums_to_one():
    s = softmax([1.0, 2.0, 3.0])
    assert abs(sum(s) - 1.0) < 1e-9


def test_top_k_picks_largest():
    assert top_k_indices([0.1, 0.9, 0.5, 0.2], 2) == [1, 2]


def test_router_assigns_top_k_per_token():
    r = MoERouter(num_experts=4, top_k=2)
    routes = r.route([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.5]])
    assert all(len(x) == 2 for x in routes)
    assert r.total_assignments == 4


def test_uniform_loss_near_one():
    # perfectly uniform logits -> loss ~ 1.0
    n, e = 80, 8
    logits = [[0.0] * e for _ in range(n)]
    # break ties deterministically so dispatch spreads
    for i, row in enumerate(logits):
        row[i % e] = 0.01
    loss = load_balancing_loss(logits, e)
    assert 0.9 <= loss <= 1.2


def test_collapsed_loss_higher_than_balanced():
    rng = random.Random(1)
    bal = [[rng.gauss(0, 1) for _ in range(8)] for _ in range(200)]
    col = [[5.0 if j == 0 else 0.0 for j in range(8)] for _ in range(200)]
    assert load_balancing_loss(col, 8) > load_balancing_loss(bal, 8)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

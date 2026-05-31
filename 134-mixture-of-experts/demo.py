"""Route tokens through a balanced vs a collapsed router and compare the
load-balancing loss. Reproduces the "expert collapse" the post warns about.

    $ python3 demo.py
"""

from __future__ import annotations

import random

from moe import MoERouter, load_balancing_loss


def balanced_logits(n, num_experts, rng):
    return [[rng.gauss(0, 1) for _ in range(num_experts)] for _ in range(n)]


def collapsed_logits(n, num_experts, rng):
    # Expert 0 nearly always wins -> utilization collapses onto it.
    return [[5.0 if e == 0 else rng.gauss(0, 0.3) for e in range(num_experts)]
            for _ in range(n)]


def main() -> None:
    rng = random.Random(0)
    num_experts, k = 8, 2

    bal = balanced_logits(300, num_experts, rng)
    col = collapsed_logits(300, num_experts, rng)

    r = MoERouter(num_experts, k)
    r.route(bal)
    print("balanced usage distribution:")
    for e, pct in sorted(r.usage_distribution().items()):
        print(f"  expert {e}: {pct:.1%}")

    bal_loss = load_balancing_loss(bal, num_experts)
    col_loss = load_balancing_loss(col, num_experts)
    print(f"\nload-balancing loss (uniform≈1.0): balanced={bal_loss:.3f}  "
          f"collapsed={col_loss:.3f}")
    assert col_loss > bal_loss, "collapsed routing should incur higher aux loss"
    print("\nOK: the aux loss is low when experts share load, high on collapse.")


if __name__ == "__main__":
    main()

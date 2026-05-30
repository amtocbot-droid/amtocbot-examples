"""Tests for the cost model and recall benchmark.
Run: python3 test_showdown.py
"""

from __future__ import annotations

from cost_model import Workload, showdown, index_bytes
from recall_benchmark import run as recall_run, brute_force_topk, make_corpus
import random


def test_index_bytes_scales_with_dim():
    assert index_bytes(1, 1536) == 1536 * 4
    assert index_bytes(1000, 768) == 1000 * 768 * 4


def test_ram_includes_graph_overhead():
    w = Workload(n_vectors=1_000_000, dim=1536, graph_overhead=1.5)
    raw_gb = index_bytes(1_000_000, 1536) / (1024 ** 3)
    assert abs(w.ram_gb() - raw_gb * 1.5) < 1e-6


def test_showdown_is_sorted_cheapest_first():
    rows = showdown(Workload())
    costs = [c for _, c, _ in rows]
    assert costs == sorted(costs)
    assert len(rows) == 4


def test_every_engine_fits_default_workload():
    rows = showdown(Workload())
    assert all(fits for _, _, fits in rows)


def test_recall_is_high():
    assert recall_run() > 0.9


def test_brute_force_returns_k():
    rng = random.Random(1)
    corpus = make_corpus(50, 16, rng)
    q = make_corpus(1, 16, rng)[0]
    assert len(brute_force_topk(q, corpus, 10)) == 10


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

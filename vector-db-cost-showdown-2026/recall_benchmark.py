"""Recall@k benchmark: brute-force ground truth vs a tiny HNSW-style
greedy graph index. Reproduces the methodology behind the post's
"Recall@20: 97.1%" spot-check, in pure Python (no numpy, no engine).

    $ python3 recall_benchmark.py

The point is the *method*, not the absolute numbers: build ground truth by
exact cosine, then measure how often an approximate index returns the same
neighbors. This is exactly how the post validated each engine's recall.
"""

from __future__ import annotations

import math
import random


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    na = math.sqrt(dot(a, a)) or 1e-9
    nb = math.sqrt(dot(b, b)) or 1e-9
    return dot(a, b) / (na * nb)


def make_corpus(n, dim, rng):
    return [[rng.gauss(0, 1) for _ in range(dim)] for _ in range(n)]


def brute_force_topk(query, corpus, k):
    scored = sorted(range(len(corpus)),
                    key=lambda i: cosine(query, corpus[i]), reverse=True)
    return scored[:k]


class GreedyGraphIndex:
    """A deliberately small approximate index: each node links to its M
    nearest neighbors; search is greedy beam descent. Mirrors HNSW's
    recall/latency tradeoff without the multi-layer machinery."""

    def __init__(self, corpus, M=12, ef=32):
        self.corpus = corpus
        self.M = M
        self.ef = ef
        self.neighbors = self._build()

    def _build(self):
        n = len(self.corpus)
        nb = []
        for i in range(n):
            order = sorted((j for j in range(n) if j != i),
                           key=lambda j: cosine(self.corpus[i], self.corpus[j]),
                           reverse=True)
            nb.append(order[:self.M])
        return nb

    def search(self, query, k):
        """Greedy beam search: keep an `ef`-wide candidate set, expand the
        best unexpanded node's neighbors, stop when the beam stops improving."""
        n = len(self.corpus)
        seeds = random.Random(0).sample(range(n), min(self.ef, n))
        visited = set(seeds)
        beam = sorted(seeds, key=lambda x: cosine(query, self.corpus[x]),
                      reverse=True)[:self.ef]
        changed = True
        while changed:
            changed = False
            for node in list(beam):
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        beam.append(nb)
                        changed = True
            beam = sorted(beam, key=lambda x: cosine(query, self.corpus[x]),
                          reverse=True)[:self.ef]
        return beam[:k]


def recall_at_k(index, corpus, queries, k):
    hits = total = 0
    for q in queries:
        truth = set(brute_force_topk(q, corpus, k))
        got = set(index.search(q, k))
        hits += len(truth & got)
        total += k
    return hits / total


def run(n=400, dim=32, n_queries=40, k=20, seed=7):
    rng = random.Random(seed)
    corpus = make_corpus(n, dim, rng)
    queries = make_corpus(n_queries, dim, rng)
    index = GreedyGraphIndex(corpus)
    r = recall_at_k(index, corpus, queries, k)
    return r


if __name__ == "__main__":
    r = run()
    print(f"Recall@20 (approx vs brute-force): {r:.1%}")
    print("Method matches the post: build exact ground truth, then measure")
    print("how many true neighbors the approximate index recovers.")
    assert r > 0.5, "approximate index should recover a majority of neighbors"
    print("\nOK")

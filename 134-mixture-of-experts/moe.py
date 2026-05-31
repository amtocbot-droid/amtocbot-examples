"""A tiny Mixture-of-Experts router in pure Python: top-k gating, expert-usage
tracking, and the Switch-Transformer load-balancing auxiliary loss.

Companion code for the AmtocSoft post
"Mixture of Experts Architecture for LLMs".

The post inspects Mixtral with torch hooks. The portable ideas — how tokens
are routed to the top-k experts, why utilization skews, and how the
load-balancing loss pushes it back toward uniform — are reproduced here with
no torch. Pure standard library.
"""

from __future__ import annotations

import math
from collections import defaultdict


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps)
    return [e / s for e in exps]


def top_k_indices(weights: list[float], k: int) -> list[int]:
    return sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)[:k]


class MoERouter:
    """Routes each token (a router-logit vector) to its top-k experts."""

    def __init__(self, num_experts: int, top_k: int = 2):
        self.num_experts = num_experts
        self.top_k = top_k
        self.expert_usage: dict[int, int] = defaultdict(int)
        self.total_assignments = 0

    def route(self, router_logits: list[list[float]]) -> list[list[int]]:
        """router_logits: one logit vector per token. Returns the chosen
        expert indices per token, and records usage."""
        routes = []
        for logits in router_logits:
            chosen = top_k_indices(softmax(logits), self.top_k)
            routes.append(chosen)
            for idx in chosen:
                self.expert_usage[idx] += 1
                self.total_assignments += 1
        return routes

    def usage_distribution(self) -> dict[int, float]:
        return {e: self.expert_usage[e] / self.total_assignments
                for e in range(self.num_experts)
                if self.expert_usage[e]} if self.total_assignments else {}


def load_balancing_loss(router_logits: list[list[float]], num_experts: int) -> float:
    """Switch-Transformer auxiliary loss: num_experts * sum(f_i * P_i), where
    f_i is the fraction of tokens dispatched to expert i and P_i is the mean
    router probability for expert i. Minimized (=1.0) when load is uniform."""
    n = len(router_logits)
    probs = [softmax(l) for l in router_logits]
    # mean router probability per expert
    P = [sum(probs[t][e] for t in range(n)) / n for e in range(num_experts)]
    # fraction of tokens whose argmax is expert e (the dispatched fraction)
    dispatch = [0] * num_experts
    for p in probs:
        dispatch[p.index(max(p))] += 1
    f = [d / n for d in dispatch]
    return num_experts * sum(f[e] * P[e] for e in range(num_experts))

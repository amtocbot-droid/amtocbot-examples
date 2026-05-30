"""An agent memory store you can actually run: in-memory vectors, the post's
recency/frequency/similarity scoring, and contradiction detection.

Companion code for the AmtocSoft post
"AI Memory Systems: Building Agents That Remember".

The post wires this to pgvector + an embedding API. To keep the example
dependency-free, embeddings here are a deterministic hashing embedding and
storage is a list. The *ranking logic* — `compute_memory_score` — is exactly
the formula from the post.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field


def embed(text: str, dim: int = 64) -> list[float]:
    """Deterministic bag-of-hashed-tokens embedding. Stand-in for a real
    embedding API; good enough to demonstrate similarity ranking."""
    vec = [0.0] * dim
    for tok in text.lower().split():
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_memory_score(similarity: float, days_old: int, access_count: int) -> float:
    """The post's blended score: relevance, recency, frequency."""
    recency = 1.0 / (1.0 + 0.1 * days_old)
    frequency = min(1.0, access_count / 10)
    return 0.6 * similarity + 0.25 * recency + 0.15 * frequency


@dataclass
class Memory:
    user_id: str
    text: str
    memory_type: str
    days_old: int = 0
    access_count: int = 0
    embedding: list[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.embedding:
            self.embedding = embed(self.text)


class AgentMemorySystem:
    def __init__(self):
        self._memories: list[Memory] = []

    def store(self, user_id: str, text: str, memory_type: str = "semantic",
              days_old: int = 0, access_count: int = 0) -> Memory:
        m = Memory(user_id, text, memory_type, days_old, access_count)
        self._memories.append(m)
        return m

    def retrieve(self, user_id: str, query: str, top_k: int = 5,
                 memory_type: str | None = None) -> list[tuple[Memory, float]]:
        q = embed(query)
        scored = []
        for m in self._memories:
            if m.user_id != user_id:
                continue
            if memory_type and m.memory_type != memory_type:
                continue
            sim = cosine(q, m.embedding)
            score = compute_memory_score(sim, m.days_old, m.access_count)
            scored.append((m, score))
        scored.sort(key=lambda t: t[1], reverse=True)
        for m, _ in scored[:top_k]:
            m.access_count += 1
        return scored[:top_k]

    def find_contradictions(self, user_id: str, threshold: float = 0.85
                            ) -> list[tuple[Memory, Memory, float]]:
        """High embedding similarity between two memories of the same user is
        a candidate contradiction to reconcile (the post's dedup query)."""
        mem = [m for m in self._memories if m.user_id == user_id]
        out = []
        for i in range(len(mem)):
            for j in range(i + 1, len(mem)):
                sim = cosine(mem[i].embedding, mem[j].embedding)
                if sim > threshold:
                    out.append((mem[i], mem[j], sim))
        return out

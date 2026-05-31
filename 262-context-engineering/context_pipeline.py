"""Context assembly pipeline: curate, rank, budget, and log provenance.

Companion code for the AmtocSoft post "Context Engineering as Infrastructure:
The 2026 Field Guide". Pure standard library.

Stages:
    blended_score  - score chunks on similarity + recency + authority
    dedupe         - drop near-identical chunks (shingled Jaccard)
    assemble       - greedily fill a token budget, position best near the question,
                     and record what was dropped (provenance)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Chunk:
    source: str
    text: str
    score: float          # relevance, 0..1
    tokens: int


@dataclass
class AssemblyResult:
    blocks: list[Chunk]
    used_tokens: int
    dropped: list[str] = field(default_factory=list)


def estimate_tokens(text: str) -> int:
    """Rough heuristic: ~4 chars per token. Swap for a real tokenizer in prod."""
    return max(1, len(text) // 4)


# --------------------------------------------------------------------------
# Scoring: more than cosine similarity
# --------------------------------------------------------------------------
def blended_score(similarity: float, age_days: float,
                  authority: float, tokens: int) -> float:
    recency = math.exp(-age_days / 180.0)          # half-life ~6 months
    length_penalty = 1.0 / (1.0 + tokens / 500)    # gently disfavor bloat
    return 0.6 * similarity + 0.25 * recency + 0.15 * authority * length_penalty


# --------------------------------------------------------------------------
# Curation: drop near-duplicates
# --------------------------------------------------------------------------
def shingles(text: str, n: int = 5) -> set[str]:
    words = text.lower().split()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def dedupe(chunks: list[Chunk], threshold: float = 0.8) -> list[Chunk]:
    kept: list[Chunk] = []
    for c in sorted(chunks, key=lambda x: x.score, reverse=True):
        c_sh = shingles(c.text)
        dup = False
        for k in kept:
            k_sh = shingles(k.text)
            if c_sh and k_sh:
                jac = len(c_sh & k_sh) / len(c_sh | k_sh)
                if jac >= threshold:
                    dup = True
                    break
        if not dup:
            kept.append(c)
    return kept


# --------------------------------------------------------------------------
# Assembly: budget + position + provenance
# --------------------------------------------------------------------------
def assemble(chunks: list[Chunk], budget_tokens: int,
             relevance_floor: float = 0.0) -> AssemblyResult:
    candidates = [c for c in chunks if c.score >= relevance_floor]
    deduped = dedupe(candidates)
    ranked = sorted(deduped, key=lambda c: c.score, reverse=True)

    blocks: list[Chunk] = []
    used = 0
    dropped: list[str] = []
    for c in ranked:
        if used + c.tokens <= budget_tokens:
            blocks.append(c)
            used += c.tokens
        else:
            dropped.append(f"{c.source} (score={c.score:.2f}, {c.tokens} tok)")

    for c in chunks:
        if c.score < relevance_floor:
            dropped.append(f"{c.source} (below floor {relevance_floor:.2f})")

    # Position the highest-scoring block LAST, nearest the question.
    blocks.sort(key=lambda c: c.score)
    return AssemblyResult(blocks=blocks, used_tokens=used, dropped=dropped)

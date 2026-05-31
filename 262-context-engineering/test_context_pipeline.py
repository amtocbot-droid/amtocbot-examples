"""Tests for the context assembly pipeline. Run: python test_context_pipeline.py"""

from __future__ import annotations

from context_pipeline import (
    Chunk,
    assemble,
    blended_score,
    dedupe,
    estimate_tokens,
    shingles,
)


def _c(source, text, score, tokens=None):
    return Chunk(source, text, score, tokens or estimate_tokens(text))


def test_blended_score_penalizes_age():
    fresh = blended_score(0.9, age_days=1, authority=1.0, tokens=100)
    stale = blended_score(0.9, age_days=240, authority=1.0, tokens=100)
    assert fresh > stale


def test_blended_score_rewards_authority():
    high = blended_score(0.8, age_days=10, authority=1.0, tokens=100)
    low = blended_score(0.8, age_days=10, authority=0.2, tokens=100)
    assert high > low


def test_dedupe_keeps_higher_scored_of_duplicates():
    a = _c("a", "the quick brown fox jumps over the lazy dog again", 0.6)
    b = _c("b", "the quick brown fox jumps over the lazy dog again", 0.9)
    kept = dedupe([a, b])
    assert len(kept) == 1
    assert kept[0].source == "b"


def test_dedupe_keeps_distinct_chunks():
    a = _c("a", "refund policy for physical goods and returns process detail", 0.6)
    b = _c("b", "shipping timelines vary by region and carrier selection options", 0.5)
    assert len(dedupe([a, b])) == 2


def test_assemble_respects_budget():
    chunks = [_c(f"s{i}", "word " * 40, 0.9 - i * 0.1) for i in range(5)]
    result = assemble(chunks, budget_tokens=20)
    assert result.used_tokens <= 20
    assert len(result.dropped) >= 1


def test_assemble_positions_best_last():
    a = _c("low", "alpha beta gamma delta epsilon zeta eta theta", 0.3)
    b = _c("high", "one two three four five six seven eight nine", 0.9)
    result = assemble([a, b], budget_tokens=100)
    assert result.blocks[-1].source == "high"


def test_relevance_floor_drops_weak_chunks():
    a = _c("strong", "this chunk is clearly relevant to the user question", 0.8)
    b = _c("weak", "this chunk is only tangentially related at best honestly", 0.2)
    result = assemble([a, b], budget_tokens=1000, relevance_floor=0.5)
    sources = {blk.source for blk in result.blocks}
    assert "strong" in sources and "weak" not in sources
    assert any("below floor" in d for d in result.dropped)


def test_shingles_empty_on_short_text():
    assert shingles("too short", n=5) == set()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

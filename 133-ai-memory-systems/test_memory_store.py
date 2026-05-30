"""Tests. Run: python3 test_memory_store.py"""

from __future__ import annotations

from memory_store import (
    AgentMemorySystem, compute_memory_score, embed, cosine,
)


def test_score_weights_sum_behaviour():
    # perfect similarity, fresh, frequently accessed -> near 1.0
    s = compute_memory_score(1.0, 0, 10)
    assert abs(s - 1.0) < 1e-9


def test_recency_decays():
    fresh = compute_memory_score(0.5, 0, 0)
    stale = compute_memory_score(0.5, 100, 0)
    assert fresh > stale


def test_embedding_is_normalized():
    v = embed("hello world")
    assert abs(cosine(v, v) - 1.0) < 1e-6


def test_retrieve_respects_user_isolation():
    m = AgentMemorySystem()
    m.store("a", "alpha topic")
    m.store("b", "beta topic")
    res = m.retrieve("a", "alpha topic")
    assert all(mem.user_id == "a" for mem, _ in res)


def test_retrieve_increments_access_count():
    m = AgentMemorySystem()
    stored = m.store("a", "vector search service")
    m.retrieve("a", "vector search service")
    assert stored.access_count == 1


def test_contradiction_detected():
    m = AgentMemorySystem()
    m.store("a", "user prefers python over java")
    m.store("a", "user prefers python over java strongly")
    assert m.find_contradictions("a", threshold=0.8)


def test_type_filter():
    m = AgentMemorySystem()
    m.store("a", "fact one", "semantic")
    m.store("a", "event one", "episodic")
    res = m.retrieve("a", "one", memory_type="episodic")
    assert all(mem.memory_type == "episodic" for mem, _ in res)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

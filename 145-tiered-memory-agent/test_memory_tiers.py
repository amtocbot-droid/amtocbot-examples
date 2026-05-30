"""Tests. Run: python3 test_memory_tiers.py"""

from __future__ import annotations

from memory_tiers import (
    WorkingMemory, EpisodicMemory, SemanticMemory, route_query, retrieve_for_query,
)


def test_working_memory_context_string():
    w = WorkingMemory(active_task={"goal": "x"},
                      retrieved_context=[{"content": "abc"}])
    s = w.to_context_string()
    assert "Current task" in s and "abc" in s


def test_episodic_retrieval_ranks_relevant_first():
    e = EpisodicMemory()
    e.write("pgvector corpus migration notes", {})
    e.write("unrelated billing question", {})
    top = e.retrieve("pgvector corpus", n_results=1)[0]
    assert "pgvector" in top["content"]


def test_router_picks_episodic_on_history_keyword():
    assert "episodic" in route_query("what did we do last time", WorkingMemory())["tiers"]


def test_router_picks_semantic_on_profile_keyword():
    assert "semantic" in route_query("what is my account tier", WorkingMemory())["tiers"]


def test_router_always_includes_working():
    assert "working" in route_query("anything", WorkingMemory())["tiers"]


def test_retrieve_for_query_pulls_semantic_profile():
    sem = SemanticMemory()
    sem.put("user_profile", {"tier": "pro"})
    docs = retrieve_for_query("what is my account tier", WorkingMemory(),
                              EpisodicMemory(), sem)
    assert any(d["source"] == "semantic" for d in docs)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

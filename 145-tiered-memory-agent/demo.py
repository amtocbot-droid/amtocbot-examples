"""Wire the three tiers together and route a few queries.

    $ python3 demo.py
"""

from __future__ import annotations

from memory_tiers import (
    WorkingMemory, EpisodicMemory, SemanticMemory, route_query, retrieve_for_query,
)


def main() -> None:
    working = WorkingMemory(active_task={"goal": "ship vector search"})
    episodic = EpisodicMemory()
    semantic = SemanticMemory()

    episodic.write("We migrated the corpus to pgvector last week", {"thread": "t1"})
    episodic.write("User asked about HNSW index tuning earlier", {"thread": "t2"})
    semantic.put("user_profile", {"tier": "pro", "lang": "python"})

    for q in ["what did we do last time with the corpus",
              "what is my account tier",
              "summarize the current task"]:
        routing = route_query(q, working)
        docs = retrieve_for_query(q, working, episodic, semantic)
        print(f"\nQ: {q}")
        print(f"  tiers: {routing['tiers']}")
        for d in docs:
            print(f"  [{d['source']}] {d['content'][:60]}")

    # Episodic query routes to episodic; profile query routes to semantic.
    assert "episodic" in route_query("what did we do last time", working)["tiers"]
    assert "semantic" in route_query("what is my account tier", working)["tiers"]
    print("\nOK: router sends each query to the right tier(s).")


if __name__ == "__main__":
    main()

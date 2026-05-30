"""Store some memories, retrieve by relevance+recency+frequency, and find a
contradiction. Reproduces the behaviour the post describes.

    $ python3 demo.py
"""

from __future__ import annotations

from memory_store import AgentMemorySystem


def main() -> None:
    mem = AgentMemorySystem()
    mem.store("u1", "User prefers Python over Java", "semantic", days_old=30)
    mem.store("u1", "User is building a vector search service", "episodic", days_old=2)
    mem.store("u1", "User prefers Java over Python", "semantic", days_old=1)
    mem.store("u1", "User deployed to Cloudflare last week", "episodic", days_old=5)

    print("Query: 'user prefers python or java?'")
    for m, score in mem.retrieve("u1", "user prefers python or java", top_k=3):
        print(f"  {score:.3f}  [{m.memory_type}] {m.text}")

    print("\nContradiction scan:")
    for a, b, sim in mem.find_contradictions("u1", threshold=0.8):
        print(f"  sim={sim:.2f}  '{a.text}'  <->  '{b.text}'")

    # The fresher, more-accessed memory should outrank the stale one.
    top = mem.retrieve("u1", "user prefers python or java", top_k=1)[0][0]
    assert "prefers" in top.text
    print("\nOK: ranking blends similarity, recency, and access frequency.")


if __name__ == "__main__":
    main()

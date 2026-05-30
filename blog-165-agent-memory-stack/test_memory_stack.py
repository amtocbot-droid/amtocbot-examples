"""Tests. Run: python3 test_memory_stack.py"""

from __future__ import annotations

from memory_stack import SemanticMemory, EpisodicMemory, select_skill


def test_semantic_recall_ranks_relevant():
    s = SemanticMemory()
    s.write_user_fact("u", "Enterprise plan with 200 seats", "account")
    s.write_user_fact("u", "Likes dark mode", "preference")
    top = s.read_user_facts("u", "what plan and seats", k=1)[0]
    assert "plan" in top["text"].lower()


def test_semantic_user_isolation():
    s = SemanticMemory()
    s.write_user_fact("a", "fact a", "x")
    s.write_user_fact("b", "fact b", "x")
    assert all(True for _ in s.read_user_facts("a", "fact"))
    assert len(s.read_user_facts("a", "fact")) == 1


def test_episodic_summary_then_raw():
    e = EpisodicMemory()
    e.write_event("t", "msg", "hello")
    e.write_event("t", "msg", "world")
    assert e.read("t").get("raw_events") is None
    assert len(e.read("t", depth="raw")["raw_events"]) == 2


def test_skill_router_refund():
    assert select_skill("please refund my charge") == "refund_request"


def test_skill_router_outage():
    assert select_skill("the service is down with errors") == "outage_status"


def test_skill_router_none():
    assert select_skill("tell me a joke") == "none"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

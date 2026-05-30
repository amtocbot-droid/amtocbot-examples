"""Exercise all three memory patterns.

    $ python3 demo.py
"""

from __future__ import annotations

from memory_stack import SemanticMemory, EpisodicMemory, select_skill


def main() -> None:
    sem = SemanticMemory()
    sem.write_user_fact("u1", "Prefers email over phone", "preference")
    sem.write_user_fact("u1", "Enterprise plan, 200 seats", "account")
    print("semantic read:")
    for f in sem.read_user_facts("u1", "what plan is the account on", k=2):
        print(f"  {f['similarity']}  [{f['type']}] {f['text']}")

    epi = EpisodicMemory()
    epi.write_event("t1", "user_msg", "my dashboard is returning 500s")
    epi.write_event("t1", "tool_call", "status.check -> incident INC-42 open")
    epi.write_event("t1", "agent_msg", "known incident, ETA 20m")
    print("\nepisodic summary:", epi.read("t1")["summary"])
    print("episodic raw event count:", len(epi.read("t1", depth="raw")["raw_events"]))

    print("\nskill routing:")
    for q in ["I want a refund for last month's charge",
              "the service is down and returning errors",
              "how's the weather"]:
        print(f"  {select_skill(q):<16} <- {q}")

    assert select_skill("I want a refund for the charge") == "refund_request"
    assert select_skill("service is down with errors") == "outage_status"
    assert select_skill("how's the weather") == "none"
    print("\nOK: semantic recall, episodic depth control, procedural routing.")


if __name__ == "__main__":
    main()

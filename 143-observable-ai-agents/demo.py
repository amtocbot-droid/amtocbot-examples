"""Build the agent_run span tree from the post and roll up cost + tokens.

    $ python3 demo.py
"""

from __future__ import annotations

from tracing import Span, traced_llm_call, render


def main() -> None:
    root = Span("agent_run")

    supervisor = root.child("node:supervisor")
    traced_llm_call(supervisor, "gpt-4o", "supervisor", 1240, 87, 980)

    researcher = root.child("node:researcher")
    researcher.child("tool_call:web_search", **{"query": "Q1 2026 NVDA earnings"})
    traced_llm_call(researcher, "gpt-4o", "researcher", 2100, 320, 1450)

    writer = root.child("node:writer")
    traced_llm_call(writer, "gpt-4o-mini", "writer", 1800, 540, 600)

    print(render(root))
    print(f"\ntotal tokens: {root.total_tokens()}")
    print(f"total cost:   ${root.total_cost():.5f}")

    assert root.total_tokens() == 1240 + 87 + 2100 + 320 + 1800 + 540
    assert root.total_cost() > 0
    print("\nOK: nested spans roll cost and tokens up to the agent_run root.")


if __name__ == "__main__":
    main()

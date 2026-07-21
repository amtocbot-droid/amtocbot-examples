"""Two-user before/after repro of the Langflow IDOR (CVE-2026-55255).

Mirrors the curl walkthrough in the blog post: user-b requests
user-a's flow by UUID alone. Vulnerable handler serves it using
user-a's embedded credentials; patched handler rejects it.

    $ python3 demo.py
"""

from __future__ import annotations

from langflow_idor import (
    Flow, FlowStore, NotAuthorized,
    handle_responses_vulnerable, handle_responses_patched,
)

FLOW_ID = "8f2c1e40-flow-owned-by-user-a"


def main() -> None:
    store = FlowStore()
    store.add(Flow(flow_id=FLOW_ID, owner="user-a", embedded_secret="sk-mock-a1b2***"))

    print("=== Pre-1.9.1: vulnerable handler ===")
    print("user-a requests their own flow:")
    own = handle_responses_vulnerable(store, requester="user-a", flow_id=FLOW_ID,
                                       input_value="summarize the last ticket")
    print(" ", own)

    print("\nuser-b requests user-a's flow by UUID alone:")
    hijacked = handle_responses_vulnerable(store, requester="user-b", flow_id=FLOW_ID,
                                            input_value="summarize the last ticket")
    print(" ", hijacked)
    assert hijacked["flow_owner"] == "user-a"
    assert "sk-mock-a1b2" in hijacked["outputs"]["results"]["message"]
    print("  -> user-b got a response executed with user-a's embedded credentials.")

    print("\n=== 1.9.1+: patched handler ===")
    print("user-a requests their own flow:")
    own_patched = handle_responses_patched(store, requester="user-a", flow_id=FLOW_ID,
                                            input_value="summarize the last ticket")
    print(" ", own_patched)

    print("\nuser-b requests user-a's flow by UUID alone:")
    try:
        handle_responses_patched(store, requester="user-b", flow_id=FLOW_ID,
                                  input_value="summarize the last ticket")
        raise SystemExit("expected NotAuthorized, but the patched handler let it through")
    except NotAuthorized as exc:
        print(f"  -> rejected: {exc}")

    print("\nOK: vulnerable handler leaks user-a's credentials to user-b; "
          "patched handler blocks it with one ownership check.")


if __name__ == "__main__":
    main()

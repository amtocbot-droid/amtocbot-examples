"""Run a few tool calls through the policy-enforced server: an allowed call,
a denied table, an unknown tool, and a rate-limit trip. Show the audit log.

    $ python3 demo.py
"""

from __future__ import annotations

import io

from sandbox import PolicyEnforcedServer, AuditLogger, PolicyViolation


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def main() -> None:
    sink = io.StringIO()
    clock = FakeClock()
    audit = AuditLogger(sink)

    def run_query(args):
        return f"rows from {args.get('table')}"

    policy = {"tools": {"query": {
        "rate_limit_per_minute": 3,
        "allowed_schemas": ["public"],
        "denied_tables": ["secrets"],
    }}}
    server = PolicyEnforcedServer({"query": run_query}, policy, audit, clock=clock)

    print("allowed:", server.call("query", {"schema": "public", "table": "orders"}))

    for label, fn in [
        ("denied table", lambda: server.call("query", {"table": "secrets"})),
        ("unknown tool", lambda: server.call("nuke", {})),
    ]:
        try:
            fn()
        except (PolicyViolation, KeyError) as e:
            print(f"{label} blocked: {type(e).__name__}")

    # Trip the rate limit (3/min). We've used 1 successful + need 3 more.
    tripped = False
    for _ in range(5):
        try:
            server.call("query", {"schema": "public", "table": "orders"})
        except PolicyViolation:
            tripped = True
            break
    assert tripped, "rate limit should trip"
    print("rate limit tripped after burst")

    print("\naudit records written:", sink.getvalue().count("\n"))
    assert 'call_denied' in sink.getvalue()
    print("OK: policy enforced, every attempt audited.")


if __name__ == "__main__":
    main()

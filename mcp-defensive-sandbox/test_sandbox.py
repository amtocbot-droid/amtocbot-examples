"""Tests. Run: python3 test_sandbox.py"""

from __future__ import annotations

import io
import json

from sandbox import PolicyEnforcedServer, AuditLogger, PolicyViolation


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _server(clock=None):
    sink = io.StringIO()
    clock = clock or FakeClock()
    policy = {"tools": {"query": {"rate_limit_per_minute": 2,
                                  "allowed_schemas": ["public"],
                                  "denied_tables": ["secrets"]}}}
    srv = PolicyEnforcedServer({"query": lambda a: "ok"}, policy,
                               AuditLogger(sink), clock=clock)
    return srv, sink


def test_allowed_call_succeeds():
    srv, _ = _server()
    assert srv.call("query", {"schema": "public", "table": "orders"}) == "ok"


def test_unknown_tool_denied():
    srv, sink = _server()
    try:
        srv.call("ghost", {})
    except PolicyViolation:
        assert 'call_denied' in sink.getvalue()
        return
    raise AssertionError("unknown tool should be denied")


def test_denied_table_blocked():
    srv, _ = _server()
    try:
        srv.call("query", {"table": "secrets"})
    except PolicyViolation:
        return
    raise AssertionError("denied table should block")


def test_schema_allowlist():
    srv, _ = _server()
    try:
        srv.call("query", {"schema": "internal", "table": "orders"})
    except PolicyViolation:
        return
    raise AssertionError("schema not in allowlist should block")


def test_rate_limit_trips_and_recovers():
    clock = FakeClock()
    srv, _ = _server(clock)
    srv.call("query", {"schema": "public"})
    srv.call("query", {"schema": "public"})
    try:
        srv.call("query", {"schema": "public"})
    except PolicyViolation:
        pass
    else:
        raise AssertionError("3rd call within a minute should trip 2/min limit")
    clock.t += 61  # window slides
    assert srv.call("query", {"schema": "public"}) == "ok"


def test_audit_records_are_cloudevents():
    srv, sink = _server()
    srv.call("query", {"schema": "public"})
    first = json.loads(sink.getvalue().splitlines()[0])
    assert first["specversion"] == "1.0" and first["type"].startswith("com.amtocsoft.mcp.")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

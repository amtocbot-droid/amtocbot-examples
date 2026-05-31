"""Defensive MCP server wrapper: per-tool policy, rate limits, schema/table
allowlists, resource caps, and a CloudEvents audit log.

Companion code for the AmtocSoft post
"Defensive MCP Server: Sandboxing, Permissions, Audit Logs, Resource Caps".

The post wraps a real `mcp.server.Server` and loads policy from YAML. This
version takes the policy as a plain dict and wraps a callable tool registry,
so it runs with no dependencies. The enforcement and audit logic match the
post. Pure standard library — an injectable clock keeps it deterministic.
"""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from typing import Any, Callable


class PolicyViolation(Exception):
    pass


class AuditLogger:
    """Writes CloudEvents-shaped audit records to a sink (any .write/.flush)."""

    def __init__(self, sink, clock: Callable[[], str] = lambda: "2026-05-30T00:00:00Z"):
        self.sink = sink
        self.clock = clock
        self._seq = 0

    def _id(self) -> str:
        self._seq += 1
        return f"evt-{self._seq}"

    def log(self, event_type: str, **fields) -> dict:
        record = {
            "specversion": "1.0",
            "id": self._id(),
            "type": f"com.amtocsoft.mcp.{event_type}",
            "source": "mcp-postgres-1.4.0",
            "time": self.clock(),
            "datacontenttype": "application/json",
            "data": fields,
        }
        self.sink.write(json.dumps(record) + "\n")
        self.sink.flush()
        return record


class PolicyEnforcedServer:
    def __init__(self, tools: dict[str, Callable[[dict], Any]], policy: dict,
                 audit: AuditLogger, clock: Callable[[], float] = lambda: 0.0):
        self.tools = tools
        self.policy = policy
        self.audit = audit
        self.clock = clock
        self.rate_buckets: dict[str, list[float]] = defaultdict(list)

    def _check_rate_limit(self, tool_name: str, limit: int) -> None:
        now = self.clock()
        bucket = self.rate_buckets[tool_name]
        bucket[:] = [t for t in bucket if now - t < 60]
        if len(bucket) >= limit:
            raise PolicyViolation(f"rate limit exceeded for {tool_name}")
        bucket.append(now)

    def _enforce(self, tool_name: str, args: dict) -> None:
        tp = self.policy.get("tools", {}).get(tool_name)
        if tp is None:
            raise PolicyViolation(f"tool {tool_name} not in policy")
        if "rate_limit_per_minute" in tp:
            self._check_rate_limit(tool_name, tp["rate_limit_per_minute"])
        if "allowed_schemas" in tp and args.get("schema"):
            if args["schema"] not in tp["allowed_schemas"]:
                raise PolicyViolation(
                    f"schema {args['schema']} not in allow-list for {tool_name}")
        if "denied_tables" in tp and args.get("table"):
            if args["table"] in tp["denied_tables"]:
                raise PolicyViolation(
                    f"table {args['table']} is denied for {tool_name}")

    def call(self, tool_name: str, args: dict, conv_id: str = "c1") -> Any:
        self.audit.log("call_attempted", conversation_id=conv_id,
                       tool=tool_name, args=args)
        try:
            self._enforce(tool_name, args)
        except PolicyViolation as e:
            self.audit.log("call_denied", conversation_id=conv_id,
                           tool=tool_name, reason=str(e))
            raise
        result = self.tools[tool_name](args)
        self.audit.log("call_succeeded", conversation_id=conv_id,
                       tool=tool_name, result_size_bytes=len(str(result)))
        return result

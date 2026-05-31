# Defensive MCP Server: Sandboxing, Permissions, Audit Logs, Resource Caps

Companion code for the AmtocSoft post
[Defensive MCP Server: Sandboxing, Permissions, Audit Logs, Resource Caps](https://amtocsoft.blogspot.com/).

A thin policy wrapper around a tool registry that enforces, per tool:
a rate limit, a schema allowlist, a denied-table list, and writes a
CloudEvents audit record for every attempt (attempted / denied / succeeded).

The post wraps a real `mcp.server.Server` and loads YAML policy; this version
takes a plain dict policy and a callable registry so it runs with no
dependencies. The enforcement and audit logic match the post.

## Files

- `sandbox.py` — `PolicyEnforcedServer` + `AuditLogger`. Pure stdlib.
- `demo.py` — allowed call, denied table, unknown tool, rate-limit trip.
- `test_sandbox.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_sandbox.py
```

## License

MIT

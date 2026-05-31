# Agentic AI in Production: Lessons From Early Adopters

Companion code for the AmtocSoft post
[Agentic AI in Production: Lessons From Early Adopters](https://amtocsoft.blogspot.com/).

Two lessons made runnable:

1. **Typed tool results.** A naive tool explodes on the first non-200. A
   production tool returns a `ToolResult` the agent loop can reason about
   (retry the transient/rate-limited, give up on the permanent).
2. **Token budget.** A `TokenBudget` halts a runaway loop before it burns
   the month's spend.

The post uses pydantic + requests; this uses a stdlib dataclass and an
injected fake HTTP client. No dependencies.

## Files

- `tools.py` — `ToolResult`, `classify_http`, `TokenBudget`.
- `demo.py` — tool outcomes + a budget gating a loop.
- `test_tools.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_tools.py
```

## License

MIT

# Observable AI Agents with OpenTelemetry

Companion code for the AmtocSoft post
[Observable AI Agents with OpenTelemetry](https://amtocsoft.blogspot.com/).

The reusable part of agent observability is the *shape* of the trace —
`agent_run > node > llm_call / tool_call` — and rolling token/cost up to the
root. This builds that span tree in memory, with the pricing table from the
post, so you can see and assert on it without the OTel SDK.

## Files

- `tracing.py` — span tree, `MODEL_COST`, `traced_llm_call`, cost rollups.
- `demo.py` — the post's agent_run tree, total tokens and cost.
- `test_tracing.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_tracing.py
```

## License

MIT

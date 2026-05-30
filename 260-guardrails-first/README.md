# Guardrails-First: Making AI Agents Reliable at 3am

Companion code for the AmtocSoft post
[Guardrails-First: Making AI Agents Reliable at 3am](https://amtocsoft.blogspot.com/).

Four cheap layers wrap a fallible model and turn every failure mode from
unbounded into bounded:

| Layer | What it does |
|-------|--------------|
| **Budget** | Hard ceiling on steps, tokens, wall-clock, and dollars per run |
| **Validation** | Tool allowlist + typed argument checks before any tool runs |
| **Circuit breaker** | Trips on repeated identical failure (normalized error signature) |
| **Recovery** | Typed policy: retry transient, re-propose correctable, escalate repeated |

## Files

- `guardrails.py` — the four layers and the agent loop. Pure standard library.
- `simulate_3am_migration.py` — reproduces the runaway migration from the post.
- `test_guardrails.py` — failure-path tests (the trajectories that page you at 3am).

## Run it

```bash
python3 simulate_3am_migration.py     # watch the spiral halt in 3 steps
python3 test_guardrails.py            # run the failure-path tests
```

Expected simulation output:

```
status:            escalated
reason:            repeated failure: lock timeout on ALTER TABLE orders
steps taken:       3
destructive acts:  0
```

Same model, same prompt: 3 steps and zero destructive actions instead of an
11-step, 40-minute runaway. The reliability is in the harness, not the model.

## License

MIT

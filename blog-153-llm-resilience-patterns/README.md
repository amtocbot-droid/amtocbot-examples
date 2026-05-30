# Production AI Agent Patterns: Retry, Idempotency, Circuit Breakers

Companion code for the AmtocSoft post
[Production AI Agent Patterns: Retry, Idempotency, Circuit Breakers](https://amtocsoft.blogspot.com/).

Three layers that keep a fallible provider from taking down your agent:

| Layer | What it does |
|-------|--------------|
| **Retry budget** | Token-bucket in dollars — bounds how much you'll spend retrying |
| **Idempotency + negative cache** | Identical calls collide; known-bad keys aren't re-fired |
| **Circuit breaker** | Opens on failure-rate over a rolling window, recovers via half-open |

The post uses Redis; this example uses an in-process `DictStore` with the
same interface so it runs with zero dependencies.

## Files

- `resilience.py` — the three layers. Pure stdlib.
- `simulate_outage.py` — drives a provider outage through all three.
- `test_resilience.py` — unit tests.

## Run it

```bash
python3 simulate_outage.py
python3 test_resilience.py
```

## License

MIT

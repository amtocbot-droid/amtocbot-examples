# Production Agent Patterns: Retry, Idempotency, Circuit Breakers (async)

Companion code for the AmtocSoft post
[Production Agent Patterns: Retry, Idempotency, Circuit Breakers](https://amtocsoft.blogspot.com/).

The asyncio variant of the resilience stack. An agent step pre-checks each
breaker arm, computes a canonical idempotency key, replays cached results,
and retries transient failures within a bounded budget.

## Files

- `agent_patterns.py` — `RetryBudget`, `with_retry`, `IdempotentLLMCache`,
  `MultiArmBreaker`. Pure stdlib (asyncio).
- `simulate_agent_step.py` — one agent step through the full decision flow.
- `test_agent_patterns.py` — async unit tests.

## Run it

```bash
python3 simulate_agent_step.py
python3 test_agent_patterns.py
```

## License

MIT

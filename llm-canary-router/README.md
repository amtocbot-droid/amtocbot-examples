# Production LLM Canary Deployments

Companion code for the AmtocSoft post
[Production LLM Canary Deployments: Shadow Mode, Traffic Splits, Safe Model Rollouts](https://amtocsoft.blogspot.com/).

Two primitives for rolling out a new model without breaking users:

- **Sticky traffic splits** — `route_decision` hashes the user id into a
  bucket, so the same user always lands in the same bucket for a given
  rollout percentage (and stays on new as the percentage climbs).
- **Shadow mode** — `shadow_route` serves the OLD model to the user while
  running the NEW model in the background and logging a diff; the new model
  never blocks or breaks the user.

The post is async over real models; this uses injected model callables.

## Files

- `canary.py` — `route_decision`, `shadow_route`. Pure stdlib (asyncio).
- `demo.py` — bucketing convergence + a shadow route diff.
- `test_canary.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_canary.py
```

## License

MIT

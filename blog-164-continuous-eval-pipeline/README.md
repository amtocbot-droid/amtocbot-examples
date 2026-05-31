# Continuous Evaluation: Drift Detection & Replay

Companion code for the AmtocSoft post
[Continuous Evaluation for AI Agents: Drift Detection and Replay](https://amtocsoft.blogspot.com/).

Two pieces of a continuous-eval pipeline:

1. **Embedding drift** via Maximum Mean Discrepancy (RBF kernel) — compares a
   rolling baseline against the recent window and fires when they diverge.
2. **Canary replay** — grade a fixed answer against required/preferred
   criteria; a canary fires only when a *required* criterion fails.

The post computes MMD with numpy; this reimplements it in pure Python (fine
for the small daily samples a drift job compares). No dependencies.

## Files

- `drift.py` — MMD drift detection + canary grading. Pure stdlib.
- `simulate_drift.py` — quiet on stable traffic, fires on a shift.
- `test_drift.py` — tests.

## Run it

```bash
python3 simulate_drift.py
python3 test_drift.py
```

## License

MIT

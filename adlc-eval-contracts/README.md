# ADLC Eval Contracts

Companion code for the AmtocSoft ADLC eval-contract series:

- [Eval Contracts: From Ad-Hoc Cohort Evals to Codified Regression Bases](https://amtocsoft.blogspot.com/) (post 189)
- and the follow-on posts on contract-drift detection, attestation-aware
  retrospectives, and manifest-ledger tooling (posts 190–201), which all
  build on this contract foundation.

An **eval contract** turns a regression class into a versioned invariant
with a pinned tolerance and a written rationale. A candidate model is
promoted only if every invariant holds against the baseline traces.

## Files

- `eval_contracts.py` — `EvalContract`, `Invariant`, `kl_divergence`, and the
  `customer_support` contract. Pure stdlib.
- `run.py` — runs the contract against a regressing candidate (tool-call
  distribution drifts -> KL invariant fails -> promotion blocked).
- `test_eval_contracts.py` — tests.

## Run it

```bash
python3 run.py                     # the PASS/FAIL promotion table
python3 test_eval_contracts.py
```

## License

MIT

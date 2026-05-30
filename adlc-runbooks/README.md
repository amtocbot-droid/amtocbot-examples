# ADLC On-Call Runbook Structure

Companion code for the AmtocSoft post
[ADLC On-Call Runbook Structure: Sixty-Second Triage, Entry, Three-Stage Map](https://amtocsoft.blogspot.com/).

A runbook the on-call can act on in sixty seconds has a fixed shape:
five sections in order, a short human headline, and a *deterministic*
rollback gate. This linter enforces that shape in CI.

## Files

- `lint_runbooks.py` — the structure linter. Pure stdlib.
- `runbooks/` — two example runbooks that pass.
- `test_lint_runbooks.py` — tests, including rejection cases.

## Run it

```bash
python3 lint_runbooks.py        # lints runbooks/
python3 test_lint_runbooks.py
```

## License

MIT

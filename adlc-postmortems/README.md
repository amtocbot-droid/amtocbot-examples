# ADLC Postmortem Template

Companion code for the AmtocSoft post
[ADLC Postmortem Template: From Runbook Miss to Runbook Fix](https://amtocsoft.blogspot.com/).

A postmortem template is only useful if CI enforces it. This linter checks
three rules: all six sections present and in order, every follow-up carries
a PR/ticket artefact, and every follow-up is due within the 14-day SLA.

## Files

- `lint.py` — the compliance linter (stdlib frontmatter parser, no deps).
- `postmortems/` — a compliant example postmortem.
- `test_lint.py` — tests, including the three rejection cases.

## Run it

```bash
python3 lint.py
python3 test_lint.py
```

## License

MIT

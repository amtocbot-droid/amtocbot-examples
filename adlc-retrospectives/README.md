# ADLC Postmortem Retrospective Cadence

Companion code for the AmtocSoft post
[Postmortem Retrospective Cadence: Quarterly Cross-Incident Review, Recurring Contributing Factors](https://amtocsoft.blogspot.com/).

The single most valuable retrospective artefact is a count of which
contributing factors keep recurring. This rollup scans the quarter's
postmortems, validates every tag against a closed vocabulary, and lists the
factors that appear in three or more incidents.

## Files

- `rollup.py` — the quarterly tag rollup. Pure stdlib.
- `postmortems/tags.md` — the closed tag vocabulary.
- `postmortems/incidents/` — five example postmortems for Q2 2026.
- `test_rollup.py` — tests.

## Run it

```bash
python3 rollup.py          # recurring factors for Q2 2026
python3 test_rollup.py
```

## License

MIT

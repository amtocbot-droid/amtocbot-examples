# AI Coding Tools in 2026: Head-to-Head Harness

Companion code for the AmtocSoft post
[AI Coding Tools in 2026](https://amtocsoft.blogspot.com/).

The harness behind the head-to-head comparison: each tool's run is recorded as
a small JSON result, and `summarize_runs.py` produces the ranked table from the
post (fewest manual corrections first, then fastest time-to-green).

## Files

- `summarize_runs.py` — load result JSONs and print the ranked comparison table.
- `results/*.json` — one record per tool (Claude Code, Cursor, Copilot, Windsurf) for the shared rate-limiting task.
- `test_summarize.py` — tests for duration parsing and ranking.

## Run it

```bash
python3 summarize_runs.py results/*.json     # the comparison table from the post
python3 test_summarize.py                    # run the tests
```

To benchmark your own tools, drop a JSON record per tool into `results/` with
`tool`, `time_to_green` (e.g. `"9m48s"`), `manual_corrections`, and `notes`.

## License

MIT

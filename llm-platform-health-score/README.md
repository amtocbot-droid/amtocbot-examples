# Platform Health Score for LLM Systems

Companion code for the AmtocSoft posts
[Platform Health Score for LLM Systems: Rolling Up Four SLOs Into a Board-Ready Number](https://amtocsoft.blogspot.com/)
and [Per-Tenant Platform Health Score at Scale](https://amtocsoft.blogspot.com/).

One number for the board: a weighted average of per-category SLO compliance
(availability, quality, latency, cost), where each category's compliance is
how much of its error budget remains. Plus the per-tenant rollup with
low-traffic noise suppression.

## Files

- `score.py` — `compliance`, `platform_health_score`, `per_tenant_scores`.
  Pure stdlib (Prometheus wiring from the post omitted).
- `test_score.py` — tests.

## Run it

```bash
python3 score.py
python3 test_score.py
```

## License

MIT

# AI Coding Tool Stack Consolidation: From Five Tools to Two

Companion code for the AmtocSoft post
[AI Coding Tool Stack Consolidation: From Five Tools to Two](https://amtocsoft.blogspot.com/).

The post argues a sprawling 5-tool stack costs more than its license fees
suggest, because every tool boundary is a context switch. This makes that
quantitative: total monthly cost = seat licenses + the context-switch tax
(switches/day × minutes/switch × working days × loaded hourly rate).

## Files

- `stack_cost.py` — `Stack` cost model + a 5-tool vs 2-tool comparison.
- `demo.py` — the comparison for a 20-dev team, license vs switch tax.
- `test_stack_cost.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_stack_cost.py
```

## License

MIT

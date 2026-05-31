# EU AI Act Article 14: Runtime Oversight

Companion code for the AmtocSoft post
[EU AI Act Article 14: An Engineering Checklist (August 2026)](https://amtocsoft.blogspot.com/).

Article 14 requires effective human oversight. This makes the runtime
enforcement concrete: every decision carries a `DecisionTrace`, a pluggable
classifier assigns a risk class, and the router enforces the oversight each
class demands — HIGH blocks on human review (fail closed), ELEVATED queues
async review and delivers, STANDARD delivers and samples for retrospective
review.

The post's version is async with a real review queue; this uses an in-memory
queue and injected RNG so it runs standalone.

## Files

- `oversight.py` — `DecisionTrace`, `classify_risk`, `route_decision`.
- `demo.py` — routes high/elevated/standard decisions.
- `test_oversight.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_oversight.py
```

## License

MIT

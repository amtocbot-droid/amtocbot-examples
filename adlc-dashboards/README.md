# ADLC Dashboards & Alert Fatigue

Companion code for the AmtocSoft post
[ADLC Dashboards: Panel Queries, Layouts, PromQL, Grafana, Alert Fatigue](https://amtocsoft.blogspot.com/).

The dashboards and PromQL panels in the post live in Grafana; the part you
can run here is the alert-hygiene logic that keeps them from becoming noise:

1. Every alert rule must carry a `runbook` annotation.
2. An alert whose *actionable ratio* falls below the floor is a fatigue
   offender — tune it, route it to a dashboard, or delete it.

## Files

- `alert_fatigue.py` — runbook-coverage + actionable-ratio analyzer over a
  firing log. Pure stdlib.
- `test_alert_fatigue.py` — tests.

## Run it

```bash
python3 alert_fatigue.py        # the per-alert hygiene table
python3 test_alert_fatigue.py
```

## License

MIT

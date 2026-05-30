# The ADLC Metric Map

Companion code for the AmtocSoft post
[The Agent Development Lifecycle (ADLC): Pre-Deploy, Post-Deploy, Steady-State Metrics](https://amtocsoft.blogspot.com/).

One decision function per lifecycle stage:

| Stage | Function | Rule |
|-------|----------|------|
| Pre-deploy | `decide_deploy` | four-check gate, all must pass |
| Post-deploy | `score_trajectory_diff` | asymmetric — tolerate "same", flag "worse" |
| Steady-state | `steady_state_drift` | z-scored drop vs a rolling baseline |

## Run it

```bash
python3 metric_map.py        # one decision per stage
python3 test_metric_map.py   # tests
```

## License

MIT

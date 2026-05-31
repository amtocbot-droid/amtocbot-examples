# Cloud 3: Hybrid Multicloud Sovereign Architecture

Companion code for the AmtocSoft post
[Cloud 3: Hybrid Multicloud Sovereign Architecture](https://amtocsoft.blogspot.com/).

The routing layer that makes active-active multicloud work: split traffic
across providers by weight, drop an unhealthy provider out of rotation, and
fail over deterministically.

The post drives Route53 weighted records via boto3; this models the routing
decision with no AWS dependency so the failover logic is testable in
isolation.

## Files

- `routing.py` — `WeightedRouter` with health-aware weighted routing.
- `demo.py` — 80/20 split, then AWS failover to Azure.
- `test_routing.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_routing.py
```

## License

MIT

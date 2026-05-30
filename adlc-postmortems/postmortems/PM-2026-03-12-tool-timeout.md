---
incident_date: 2026-03-12
severity: sev2
---

# PM-2026-03-12: Tool timeout storm during the migration window

## Timeline
- 02:14 first tool timeouts on `lookup_order`
- 02:19 error rate crosses 5%, post-deploy alert fires
- 02:41 rolled back to previous release tag

## Detection
Post-deploy tool-error alert fired 5 minutes after the spike began.

## Response
On-call rolled back per the PostDeployToolErrorSpike runbook. Error rate
returned to baseline within 8 minutes of the rollback.

## Contributing Factors
- New release shipped a 2s tool timeout, down from 10s — too aggressive for the migration window. src/tools/config.py
- No canary on tool-latency distribution before full ramp. evals/contracts/customer_support.py

## Follow-ups
- [x] Restore 10s tool timeout during migration windows | owner: @alice | due: 2026-03-14 | PR: #4821
- [ ] Add tool-latency canary invariant to the contract | owner: @bob | due: 2026-03-20 | ticket: TICKET-3390

## Prevention Measures Shipped
- Tool-latency canary now blocks ramp if p99 regresses >50%.

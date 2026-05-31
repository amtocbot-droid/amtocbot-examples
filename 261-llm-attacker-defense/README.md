# When the Attacker Has an LLM: Defending Against AI-Developed Exploits

Companion code for the AmtocSoft post
[When the Attacker Has an LLM](https://amtocsoft.blogspot.com/).

**Defensive only.** This directory audits posture and detects an attacker
agent's behavior. It contains no exploit code.

Three controls that blunt agent-driven intrusions:

| Control | What it does |
|---------|--------------|
| **Scope the pivot** | `audit_role_policy` + `check_imds_hardening` shrink what a stolen credential is worth |
| **Detect enumeration** | `EnumerationDetector` flags action *diversity* (not raw rate), so backups stay quiet and agents get caught |
| **Auto-respond** | `respond` forks on identity: revoke workloads fast, step-up-MFA humans |

## Files

- `defense.py` — the three controls. Pure standard library.
- `replay_agent_trace.py` — replays a simulated post-compromise trace; backup stays quiet, agent enumeration trips the alert.
- `test_defense.py` — unit tests for each control.

## Run it

```bash
python3 replay_agent_trace.py     # backup quiet, agent caught before exfil
python3 test_defense.py           # run the tests
```

## License

MIT

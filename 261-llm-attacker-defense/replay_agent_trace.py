"""Replay a simulated attacker-agent trace through the detector and show the
identity-aware response fire before exfiltration. DEFENSIVE simulation only.

    $ python replay_agent_trace.py
"""

from __future__ import annotations

from defense import EnumerationDetector, respond

# A simulated post-compromise enumeration trace (the Marimo-style pivot):
# one workload identity touching many distinct sensitive actions fast.
AGENT_TRACE = [
    (0.4, "i-09fa", "ListBuckets"),
    (0.9, "i-09fa", "DescribeInstances"),
    (1.1, "i-09fa", "ListSecrets"),
    (1.4, "i-09fa", "GetSecretValue"),
    (1.6, "i-09fa", "ListAccessKeys"),
]

# A legitimate nightly backup: hammers the SAME small action set repeatedly.
BACKUP_TRACE = [(float(i) * 0.1, "backup-role", "ListBuckets") for i in range(40)]


def main() -> None:
    detector = EnumerationDetector(
        baselines={"backup-role": {"ListBuckets", "DescribeInstances"}}
    )

    print("=== legitimate backup job ===")
    fired = False
    for t, ident, action in BACKUP_TRACE:
        alert = detector.observe(ident, action, t)
        if alert:
            fired = True
            print("ALERT", alert)
    print("no alert" if not fired else "(unexpected)")
    assert not fired, "backup baseline should not trip the detector"

    print("\n=== attacker agent enumeration ===")
    alerted_on = None
    for t, ident, action in AGENT_TRACE:
        print(f"t+{t:.1f}s  {ident} {action}")
        alert = detector.observe(ident, action, t)
        if alert and alerted_on is None:
            alerted_on = ident
            print("ALERT", alert)
            action_plan = respond(ident, identity_type="workload")
            print("RESPONSE", action_plan["actions"])

    assert alerted_on == "i-09fa", "agent enumeration must trip the detector"
    print("\nOK: backup stayed quiet, agent enumeration caught before GetSecretValue chain completed.")


if __name__ == "__main__":
    main()

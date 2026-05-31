"""Defensive controls against AI-developed exploits and agent-driven intrusions.

Companion code for the AmtocSoft post "When the Attacker Has an LLM:
Defending Against AI-Developed Exploits". DEFENSIVE ONLY: this module
audits posture and detects an attacker agent's behavior. It contains no
exploit code.

Three controls:
    1. audit_role_policy / check_imds_hardening - shrink the credential pivot
    2. EnumerationDetector                       - catch action-diversity recon
    3. respond                                   - identity-aware auto-response

Pure standard library.
"""

from __future__ import annotations

from collections import defaultdict


# --------------------------------------------------------------------------
# Control 1: scope + bind credentials, harden the metadata pivot
# --------------------------------------------------------------------------
DANGEROUS_ACTIONS = {"*", "s3:*", "iam:*", "secretsmanager:*", "sts:AssumeRole"}


def audit_role_policy(policy: dict) -> list[str]:
    """Flag overly-broad grants that turn a stolen token into a skeleton key."""
    findings = []
    for stmt in policy.get("Statement", []):
        if stmt.get("Effect") != "Allow":
            continue
        actions = stmt.get("Action", [])
        actions = [actions] if isinstance(actions, str) else actions
        resources = stmt.get("Resource", [])
        resources = [resources] if isinstance(resources, str) else resources

        for a in actions:
            if a in DANGEROUS_ACTIONS:
                findings.append(f"broad action '{a}' grants too much on compromise")
        if "*" in resources and any("*" not in a for a in actions):
            findings.append("Resource '*' widens blast radius; scope to ARNs")
        if not stmt.get("Condition"):
            findings.append("no Condition block; bind to VPC/source IP/MFA")
    return findings


def check_imds_hardening(instance_md: dict) -> list[str]:
    findings = []
    if instance_md.get("HttpTokens") != "required":
        findings.append("IMDSv2 not enforced; v1 lets any process pull creds")
    if instance_md.get("HttpPutResponseHopLimit", 2) > 1:
        findings.append("hop limit > 1; containers can reach host metadata")
    if instance_md.get("HttpEndpoint") == "enabled" and not instance_md.get("needs_metadata"):
        findings.append("metadata endpoint enabled on a workload that never uses it")
    return findings


# --------------------------------------------------------------------------
# Control 2: detect enumeration by ACTION DIVERSITY, not raw rate
# --------------------------------------------------------------------------
SENSITIVE = {
    "ListBuckets", "GetSecretValue", "ListSecrets", "DescribeInstances",
    "ListAccessKeys", "GetParameter", "AssumeRole", "ListRoles",
}


class EnumerationDetector:
    def __init__(self, window_s: float = 60.0, distinct_threshold: int = 5,
                 baselines: dict[str, set[str]] | None = None):
        self.window_s = window_s
        self.distinct_threshold = distinct_threshold
        # known-broad workload identities with their expected action sets
        self.baselines = baselines or {}
        self.seen: dict[str, list[tuple[float, str]]] = defaultdict(list)

    def observe(self, identity: str, action: str, now: float) -> str | None:
        if action not in SENSITIVE:
            return None
        events = self.seen[identity]
        events.append((now, action))
        cutoff = now - self.window_s
        self.seen[identity] = [(t, a) for (t, a) in events if t >= cutoff]
        distinct = {a for _, a in self.seen[identity]}

        # exempt identities whose behavior matches their known baseline
        baseline = self.baselines.get(identity)
        if baseline is not None and distinct <= baseline:
            return None

        if len(distinct) >= self.distinct_threshold:
            return (f"enumeration: {identity} touched {len(distinct)} distinct "
                    f"sensitive actions in {self.window_s:.0f}s")
        return None


# --------------------------------------------------------------------------
# Control 3: identity-aware auto-response
# --------------------------------------------------------------------------
def respond(identity: str, identity_type: str) -> dict:
    """Workload identities: revoke first, ask later. Humans: step-up MFA."""
    if identity_type == "workload":
        return {
            "identity": identity,
            "actions": ["revoke_session", "rotate_role_credentials",
                        "snapshot_and_isolate_host", "open_incident"],
            "automatic": True,
        }
    return {
        "identity": identity,
        "actions": ["step_up_mfa_challenge"],
        "automatic": True,
        "on_fail": ["revoke_session", "snapshot_and_isolate_host"],
    }

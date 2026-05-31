"""Tests for the defensive controls. Run: python test_defense.py"""

from __future__ import annotations

from defense import (
    EnumerationDetector,
    audit_role_policy,
    check_imds_hardening,
    respond,
)


def test_audit_flags_broad_action():
    policy = {"Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}]}
    findings = audit_role_policy(policy)
    assert any("s3:*" in f for f in findings)
    assert any("Condition" in f for f in findings)


def test_audit_flags_wildcard_resource_on_scoped_action():
    # A scoped action but Resource '*' still widens blast radius.
    policy = {"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}]}
    findings = audit_role_policy(policy)
    assert any("Resource '*'" in f for f in findings)


def test_audit_clean_policy_passes():
    policy = {"Statement": [{
        "Effect": "Allow",
        "Action": ["s3:GetObject"],
        "Resource": ["arn:aws:s3:::my-bucket/*"],
        "Condition": {"StringEquals": {"aws:SourceVpc": "vpc-123"}},
    }]}
    assert audit_role_policy(policy) == []


def test_imds_flags_v1():
    md = {"HttpTokens": "optional", "HttpPutResponseHopLimit": 2, "HttpEndpoint": "enabled"}
    findings = check_imds_hardening(md)
    assert any("IMDSv2 not enforced" in f for f in findings)
    assert any("hop limit" in f for f in findings)


def test_imds_hardened_passes():
    md = {"HttpTokens": "required", "HttpPutResponseHopLimit": 1,
          "HttpEndpoint": "enabled", "needs_metadata": True}
    assert check_imds_hardening(md) == []


def test_detector_catches_diversity():
    d = EnumerationDetector(distinct_threshold=5)
    actions = ["ListBuckets", "DescribeInstances", "ListSecrets",
               "GetSecretValue", "ListAccessKeys"]
    alert = None
    for i, a in enumerate(actions):
        alert = d.observe("i-09fa", a, now=float(i) * 0.1)
    assert alert is not None and "enumeration" in alert


def test_detector_ignores_repeated_same_action():
    d = EnumerationDetector(distinct_threshold=5)
    alert = None
    for i in range(40):
        alert = d.observe("backup-role", "ListBuckets", now=float(i) * 0.1)
    assert alert is None  # 40 calls, but only one distinct action


def test_detector_respects_baseline():
    d = EnumerationDetector(distinct_threshold=2,
                            baselines={"backup-role": {"ListBuckets", "DescribeInstances"}})
    a1 = d.observe("backup-role", "ListBuckets", now=0.1)
    a2 = d.observe("backup-role", "DescribeInstances", now=0.2)
    assert a1 is None and a2 is None  # within baseline


def test_response_forks_on_identity_type():
    workload = respond("i-09fa", "workload")
    human = respond("alice", "human")
    assert "revoke_session" in workload["actions"]
    assert workload["actions"][0] == "revoke_session"
    assert human["actions"] == ["step_up_mfa_challenge"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

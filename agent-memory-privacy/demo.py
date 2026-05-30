"""Redact PII before storage, then reveal at the trusted boundary.

    $ python3 demo.py
"""

from __future__ import annotations

from pii_redaction import TokenVault, redact, reveal

MESSAGE = ("Hi, I'm Dana. Email dana@example.com, phone 415-555-0142, "
           "SSN 123-45-6789. Please update my account.")


def main() -> None:
    vault = TokenVault(tenant_id="acme")
    redacted = redact(MESSAGE, vault)
    print("stored / sent to model:")
    print(" ", redacted)

    restored = reveal(redacted, vault)
    print("\nrevealed at trusted boundary:")
    print(" ", restored)

    assert "dana@example.com" not in redacted
    assert "123-45-6789" not in redacted
    assert restored == MESSAGE

    # Cross-tenant isolation: same email -> different token in another tenant.
    other = TokenVault(tenant_id="globex")
    t1 = redact("ping dana@example.com", vault)
    t2 = redact("ping dana@example.com", other)
    assert t1 != t2
    print("\ncross-tenant tokens differ:", t1.split()[-1], "vs", t2.split()[-1])
    print("\nOK: PII never reaches the model; reversal works; tenants isolated.")


if __name__ == "__main__":
    main()

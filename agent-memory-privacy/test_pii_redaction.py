"""Tests. Run: python3 test_pii_redaction.py"""

from __future__ import annotations

from pii_redaction import TokenVault, TokenSpan, redact, reveal


def test_roundtrip():
    v = TokenVault("t1")
    msg = "email a@b.com and ssn 123-45-6789"
    r = redact(msg, v)
    assert "a@b.com" not in r and "123-45-6789" not in r
    assert reveal(r, v) == msg


def test_same_plaintext_stable_token_within_tenant():
    v = TokenVault("t1")
    a = redact("x@y.com", v)
    b = redact("x@y.com", v)
    assert a == b


def test_cross_tenant_tokens_differ():
    a = redact("x@y.com", TokenVault("t1"))
    b = redact("x@y.com", TokenVault("t2"))
    assert a != b


def test_detokenize_unknown_token_is_passthrough():
    v = TokenVault("t1")
    assert v.detokenize("<EMAIL_0000>") == "<EMAIL_0000>"


def test_entity_types_detected():
    v = TokenVault("t1")
    r = redact("call 415-555-0142 about card 4111 1111 1111 1111", v)
    assert "PHONE" in r and "CARD" in r


def test_vault_stores_ciphertext_not_plaintext():
    v = TokenVault("t1")
    redact("secret@x.com", v)
    for ct in v._store.values():
        assert b"secret@x.com" not in ct


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

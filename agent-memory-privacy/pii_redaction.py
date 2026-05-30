"""Preemptive PII redaction for agent memory.

Companion code for the AmtocSoft post
"AI Agent Memory Privacy: Preemptive PII Redaction Patterns".

PII is tokenized *before* it ever reaches the model or long-term memory:
the agent sees `<EMAIL_a8c2>`, the vault holds the reversible mapping, and
detokenization happens only at the trusted boundary. Same plaintext in two
tenants produces two different tokens (per-tenant salted key).

The post uses AWS KMS + DynamoDB for the vault. To keep this runnable with
no dependencies, the vault here encrypts with an XOR keystream derived from
a per-tenant secret via PBKDF2 (stdlib `hashlib`). The interface mirrors the
post; swap in KMS/DynamoDB for production.
"""

from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass

# Detection patterns for common PII entity types.
PATTERNS = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "PHONE": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}
# Order matters: redact more specific patterns (SSN) before greedier ones (CARD).
ORDER = ["EMAIL", "SSN", "PHONE", "CARD"]


@dataclass
class TokenSpan:
    entity_type: str
    plaintext: str
    token: str


def _keystream(secret: bytes, salt: bytes, n: int) -> bytes:
    out = b""
    counter = 0
    while len(out) < n:
        out += hashlib.pbkdf2_hmac("sha256", secret, salt + counter.to_bytes(4, "big"),
                                   1000, dklen=32)
        counter += 1
    return out[:n]


class TokenVault:
    """Per-tenant reversible PII vault. Encrypts at rest; same plaintext maps
    to a stable token within a tenant and a different token across tenants."""

    def __init__(self, tenant_id: str, secret: str = "demo-master-secret"):
        self.tenant_id = tenant_id
        self._secret = f"{secret}:{tenant_id}".encode()
        self._store: dict[str, bytes] = {}  # token -> ciphertext

    def _token_id(self, plaintext: str, entity_type: str) -> str:
        h = hashlib.sha256(
            f"{self.tenant_id}:{entity_type}:{plaintext}".encode()).hexdigest()
        return h[:4]

    def _encrypt(self, plaintext: str, salt: bytes) -> bytes:
        data = plaintext.encode()
        ks = _keystream(self._secret, salt, len(data))
        return bytes(a ^ b for a, b in zip(data, ks))

    def _decrypt(self, ct: bytes, salt: bytes) -> str:
        ks = _keystream(self._secret, salt, len(ct))
        return bytes(a ^ b for a, b in zip(ct, ks)).decode()

    def tokenize(self, span: TokenSpan) -> str:
        tid = self._token_id(span.plaintext, span.entity_type)
        token = f"<{span.entity_type}_{tid}>"
        salt = tid.encode()
        self._store.setdefault(token, self._encrypt(span.plaintext, salt))
        return token

    def detokenize(self, token: str) -> str:
        ct = self._store.get(token)
        if ct is None:
            return token
        tid = token.rsplit("_", 1)[1].rstrip(">")
        return self._decrypt(ct, tid.encode())


def redact(text: str, vault: TokenVault) -> str:
    """Replace every PII span with a vault token before the text is stored
    or sent to the model."""
    redacted = text
    for entity_type in ORDER:
        pat = PATTERNS[entity_type]

        def _sub(m):
            return vault.tokenize(TokenSpan(entity_type, m.group(0), ""))

        redacted = pat.sub(_sub, redacted)
    return redacted


def reveal(text: str, vault: TokenVault) -> str:
    """Reverse redaction at the trusted boundary."""
    return re.sub(r"<[A-Z]+_[0-9a-f]{4}>", lambda m: vault.detokenize(m.group(0)), text)

# AI Agent Memory Privacy: Preemptive PII Redaction

Companion code for the AmtocSoft post
[AI Agent Memory Privacy: Preemptive PII Redaction Patterns](https://amtocsoft.blogspot.com/).

PII is tokenized *before* it reaches the model or long-term memory. The
agent only ever sees `<EMAIL_a8c2>`; a per-tenant vault holds the reversible
mapping; detokenization happens only at the trusted boundary. The same email
in two tenants maps to two different tokens.

The post uses AWS KMS + DynamoDB. This version encrypts with a PBKDF2-derived
keystream (stdlib `hashlib`) and an in-memory store, so it runs with no
dependencies — swap in KMS/DynamoDB for production.

## Files

- `pii_redaction.py` — detection patterns, `TokenVault`, `redact`/`reveal`.
- `demo.py` — redact → store → reveal, plus cross-tenant isolation.
- `test_pii_redaction.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_pii_redaction.py
```

## License

MIT

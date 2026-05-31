# EU AI Act Article 14: Traceability for AI Engineers

Companion code for the AmtocSoft post
[EU AI Act Article 14: Traceability for AI Engineers](https://amtocsoft.blogspot.com/).

Traceability means you can reconstruct, after the fact, what the system
decided and what a human did about it. This adapter records every auto and
human-reviewed decision into a hash-chained audit log. Subjects are
referenced by pseudonym (never raw PII), and any altered or removed record
breaks the chain.

## Files

- `traceability.py` — `OversightAdapter` + hash-chained `AuditLog`. Pure stdlib.
- `demo.py` — record decisions, verify the chain, detect tampering.
- `test_traceability.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_traceability.py
```

## License

MIT

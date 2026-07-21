# Langflow IDOR (CVE-2026-55255): Vulnerable vs. Patched

Companion code for the AmtocSoft post
[Langflow Just Became the First AI Agent Platform on CISA's Must-Patch List](https://amtocsoft.blogspot.com/).

Langflow's `/api/v1/responses` endpoint (pre-1.9.1) executed a flow by a
client-supplied `flow_id`, with no check that the requesting user owned
that flow. Any authenticated user could run any other user's flow,
including whatever API keys or database credentials that flow had
embedded. This models the same handler shape, vulnerable and patched,
side by side, with no real Langflow install, HTTP server, or network
access required.

## Files

- `langflow_idor.py` — `Flow`, `FlowStore`, `handle_responses_vulnerable`
  (pre-1.9.1, no ownership check), `handle_responses_patched` (1.9.1+,
  one ownership check before execution — the entire fix from PR #12832).
- `demo.py` — the two-user before/after repro from the blog post: user-b
  requests user-a's flow by UUID alone, first against the vulnerable
  handler, then the patched one.
- `test_langflow_idor.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_langflow_idor.py
```

## License

MIT

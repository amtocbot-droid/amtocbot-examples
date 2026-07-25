# MCP fURI SSRF Audit Checker

Companion code for the AmtocSoft post
[36.7% of MCP Servers Are Exposed to SSRF. Here's How to Check If Yours Is One.](https://amtocsoft.blogspot.com/).

Microsoft's MarkItDown MCP server's `convert_to_markdown` tool fetches
whatever URI a caller supplies, with no validation. Point it at
`169.254.169.254` (the AWS instance metadata address) on an EC2 instance
still running IMDSv1, and it returns live IAM credentials. Point it at a
`file://` path instead, and it reads local secrets. A scan of 7,000+ live
MCP servers found 36.7% share this exposure class.

This directory has three pieces: a repro of the bug (vulnerable, patched,
and a "looks patched but isn't" version), a static AST scanner that finds
candidate tools to review, and a safe dynamic prober that actually
confirms whether a flagged tool leaks. No real Langflow/MarkItDown
install, HTTP server outside `127.0.0.1`, or network access to a real
cloud metadata service is required or attempted anywhere in this code.

## Files

- `mcp_furi.py` — `convert_to_markdown_vulnerable` (no validation, the
  bug), `convert_to_markdown_patched` (resolves the hostname, blocks
  loopback/private/link-local ranges), `naive_patched_scheme_check_only`
  (rejects `file://` and non-http(s) schemes by string prefix only, never
  resolves the hostname, and still leaks against a literal private/
  link-local IP given as the host — this is the blog post's debugging
  story, reproduced).
- `ssrf_audit_scanner.py` — static AST scanner: finds function parameters
  named like a URI (`uri`, `url`, `endpoint`, etc.) and flags any without
  a validation-looking call in the function body. Run standalone:
  `python3 ssrf_audit_scanner.py mcp_furi.py`. Known limitation, on
  purpose: it marks `naive_patched_scheme_check_only` as "guarded" because
  the function textually raises `BlockedDestination`, even though it
  never actually resolves the hostname. That's why the dynamic probe
  below exists.
- `ssrf_dynamic_probe.py` — safe dynamic prober: spins up a local HTTP
  server on `127.0.0.1` standing in for a metadata endpoint, and a local
  temp file standing in for an LFI target, then actually calls a given
  tool against both and reports whether it leaked. This is the step that
  catches what the static scanner misses. Run standalone:
  `python3 ssrf_dynamic_probe.py`.
- `demo.py` — the full six-step repro from the blog post: the attack
  chain against the vulnerable tool, the same chain blocked by the
  patched tool, the naive "fix" still leaking, the static scanner being
  fooled by that same naive fix, and the dynamic probe correctly catching
  all three.
- `test_mcp_ssrf_audit.py` — tests covering all three tool variants, both
  audit tools, and the scanner's documented limitation.

## Run it

```bash
python3 demo.py
python3 test_mcp_ssrf_audit.py
python3 ssrf_audit_scanner.py mcp_furi.py
python3 ssrf_dynamic_probe.py
```

## Using this against your own MCP tools

1. Run `ssrf_audit_scanner.py` against your own MCP server source to find
   candidate functions with a URI/URL-shaped parameter.
2. For each candidate, import the function and pass it to
   `ssrf_dynamic_probe.probe_tool()` to confirm whether it actually blocks
   a local metadata stand-in and a `file://` path.
3. Treat a scanner "OK" as a hint, not a verdict — only the dynamic probe
   result is proof.

## License

MIT

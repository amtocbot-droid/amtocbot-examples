"""Full repro from the blog post: the SSRF/LFI attack chain against a
vulnerable MCP tool, the same chain blocked by the patched version, the
gotcha where a naive "fix" still leaks, and the static-scan-vs-dynamic-
probe audit workflow catching what the naive fix's guard-shaped code
fools the static scanner into missing.

    $ python3 demo.py
"""

from __future__ import annotations

import tempfile

from mcp_furi import (
    BlockedDestination,
    convert_to_markdown_vulnerable,
    convert_to_markdown_patched,
    naive_patched_scheme_check_only,
)
from ssrf_audit_scanner import scan_source
from ssrf_dynamic_probe import start_fake_metadata_server, probe_tool


def main() -> None:
    server, port = start_fake_metadata_server()
    fake_imds_url = f"http://127.0.0.1:{port}/latest/meta-data/iam/security-credentials/demo-role"

    print("=== Step 1: vulnerable tool against a local stand-in for IMDS ===")
    result = convert_to_markdown_vulnerable(fake_imds_url)
    print(f"convert_to_markdown_vulnerable({fake_imds_url!r})")
    print(f"  -> {result}")

    print("\n=== Step 2: LFI via file:// against the vulnerable tool ===")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("DB_PASSWORD=hunter2-not-a-real-secret\nAPI_KEY=fake-demo-key\n")
        tmp_path = f.name
    lfi_uri = f"file://{tmp_path}"
    result = convert_to_markdown_vulnerable(lfi_uri)
    print(f"convert_to_markdown_vulnerable({lfi_uri!r})")
    print(f"  -> {result!r}")

    print("\n=== Step 3: patched tool against the same two targets ===")
    for uri in (fake_imds_url, lfi_uri):
        try:
            convert_to_markdown_patched(uri)
            print(f"convert_to_markdown_patched({uri!r}) -> UNEXPECTEDLY SUCCEEDED")
        except BlockedDestination as exc:
            print(f"convert_to_markdown_patched({uri!r})")
            print(f"  -> BLOCKED: {exc}")

    print("\n=== Step 4: the gotcha - scheme-only check still falls to a literal-IP SSRF ===")
    try:
        result = naive_patched_scheme_check_only(fake_imds_url)
        print(f"naive_patched_scheme_check_only({fake_imds_url!r})")
        print(f"  -> STILL LEAKED: {result}")
    except BlockedDestination as exc:
        print(f"  -> blocked: {exc}")

    server.shutdown()

    print("\n=== Step 5: static scanner over this file's own three functions ===")
    source = open("mcp_furi.py", encoding="utf-8").read()
    findings = scan_source("mcp_furi.py", source)
    for finding in findings:
        status = "OK (validation call present)" if finding.guarded else "FLAG (no validation call found)"
        print(f"  {finding.function}({finding.param}) -> {status}")
    naive_finding = next(f for f in findings if f.function == "naive_patched_scheme_check_only")
    print(f"\n  Note: the scanner marks naive_patched_scheme_check_only as "
          f"{'guarded' if naive_finding.guarded else 'unguarded'}, but step 4 above "
          f"just proved it leaks. Static analysis alone would have missed this.")

    print("\n=== Step 6: dynamic probe against all three, confirming the real behavior ===")
    for name, fn in (
        ("convert_to_markdown_vulnerable", convert_to_markdown_vulnerable),
        ("convert_to_markdown_patched", convert_to_markdown_patched),
        ("naive_patched_scheme_check_only", naive_patched_scheme_check_only),
    ):
        result = probe_tool(fn)
        leaked = not (result["metadata_blocked"] and result["file_blocked"])
        print(f"  {name}: {'LEAKS' if leaked else 'safe'} "
              f"(metadata_blocked={result['metadata_blocked']}, file_blocked={result['file_blocked']})")

    print("\nOK: the dynamic probe is the only step that correctly flags all "
          "three functions, matching the blog post's audit guide.")


if __name__ == "__main__":
    main()

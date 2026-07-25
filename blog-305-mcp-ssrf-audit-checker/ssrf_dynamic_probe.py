"""Safe dynamic prober: actually call a flagged MCP tool against targets
you fully control, to confirm whether it's exploitable.

Companion code for the AmtocSoft post "36.7% of MCP Servers Are Exposed
to SSRF. Here's How to Check If Yours Is One."

Spins up a local HTTP server on 127.0.0.1 standing in for a "leaked
secret" endpoint (NOT the real 169.254.169.254 - that address isn't safe
or legal to probe outside an EC2 instance you control, but the same
unauthenticated GET-and-return-body mechanics apply here) and a local
temp file standing in for a `/proc/self/environ`-style LFI target.

This is the step that catches what `ssrf_audit_scanner.py`'s static pass
can't: a tool can contain guard-shaped code and still be exploitable.

Pure standard library.
"""

from __future__ import annotations

import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable

FAKE_CREDENTIALS_BODY = (
    b'{"AccessKeyId": "ASIADEMOFAKEKEY123", '
    b'"SecretAccessKey": "fake-secret-not-real", '
    b'"Token": "fake-session-token"}'
)


class _FakeMetadataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(FAKE_CREDENTIALS_BODY)

    def log_message(self, format, *args):
        pass  # keep probe output clean


def start_fake_metadata_server() -> tuple[HTTPServer, int]:
    """A local stand-in for a cloud metadata endpoint. Never binds to a
    real link-local or cloud address - just 127.0.0.1 on an OS-assigned
    port, so this is safe to run anywhere, including a laptop."""
    server = HTTPServer(("127.0.0.1", 0), _FakeMetadataHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def probe_tool(fetch_fn: Callable[[str], str]) -> dict:
    """Call `fetch_fn` against a local metadata stand-in and a local
    file:// path. Returns a dict with two keys, "metadata" and "file",
    each True if the tool was BLOCKED (safe) or False if it leaked."""
    results = {}

    server, port = start_fake_metadata_server()
    metadata_url = f"http://127.0.0.1:{port}/latest/meta-data/iam/security-credentials/demo-role"
    try:
        fetch_fn(metadata_url)
        results["metadata_blocked"] = False
    except Exception:
        results["metadata_blocked"] = True
    finally:
        server.shutdown()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("DB_PASSWORD=hunter2-not-a-real-secret\nAPI_KEY=fake-demo-key\n")
        tmp_path = f.name
    lfi_uri = f"file://{tmp_path}"
    try:
        fetch_fn(lfi_uri)
        results["file_blocked"] = False
    except Exception:
        results["file_blocked"] = True

    return results


def main() -> int:
    from mcp_furi import (
        convert_to_markdown_vulnerable,
        convert_to_markdown_patched,
        naive_patched_scheme_check_only,
    )

    tools = {
        "convert_to_markdown_vulnerable": convert_to_markdown_vulnerable,
        "convert_to_markdown_patched": convert_to_markdown_patched,
        "naive_patched_scheme_check_only": naive_patched_scheme_check_only,
    }

    any_leaked = False
    for name, fn in tools.items():
        result = probe_tool(fn)
        leaked = not (result["metadata_blocked"] and result["file_blocked"])
        any_leaked = any_leaked or leaked
        status = "LEAKS" if leaked else "safe"
        print(f"{name}: metadata_blocked={result['metadata_blocked']} "
              f"file_blocked={result['file_blocked']} -> {status}")

    return 1 if any_leaked else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

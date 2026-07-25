"""Model of the MarkItDown-style MCP fURI SSRF, vulnerable and patched.

Companion code for the AmtocSoft post "36.7% of MCP Servers Are Exposed
to SSRF. Here's How to Check If Yours Is One."

The real bug: Microsoft's MarkItDown MCP server's `convert_to_markdown`
tool fetches whatever URI a caller supplies, with no validation at all.
Point it at `169.254.169.254` (the AWS instance metadata address) on an
EC2 instance still running IMDSv1, and it returns live IAM credentials.
Point it at a `file://` path, and it reads local secrets instead.

This module models the same tool shape at three stages: `vulnerable`
(pre-fix, no validation), `patched` (resolves the hostname and blocks
loopback/private/link-local ranges before fetching), and `naive_patched`
(a "looks safe but isn't" version that only string-checks the scheme and
still falls to SSRF, kept here specifically because it's the version that
fools a naive code reviewer, and even fools the static scanner in
`ssrf_audit_scanner.py`, on its own).

No real MarkItDown install or network access to a real cloud metadata
service is required or attempted here. Pure standard library.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local, incl. cloud IMDS
]


class BlockedDestination(Exception):
    """Raised by the patched tool when a destination is not allowed."""


def convert_to_markdown_vulnerable(uri: str) -> str:
    """Pre-fix `convert_to_markdown(uri)`: fetch whatever URI the caller
    supplies, no validation at all. This is the entire vulnerability."""
    with urllib.request.urlopen(uri, timeout=3) as resp:
        return resp.read().decode("utf-8", errors="replace")


def convert_to_markdown_patched(uri: str) -> str:
    """Fixed version: scheme allowlist, then resolve the hostname and
    check the RESOLVED IP against a blocklist, not the literal string in
    the URL. Resolving before checking is what stops a hostname that
    resolves to a blocked range from sailing past a naive check."""
    parsed = urlparse(uri)
    if parsed.scheme not in ("http", "https"):
        raise BlockedDestination(f"scheme {parsed.scheme!r} not allowed")
    host = parsed.hostname
    if host is None:
        raise BlockedDestination("no hostname in URI")
    try:
        resolved_ip = ipaddress.ip_address(socket.gethostbyname(host))
    except (socket.gaierror, ValueError) as exc:
        raise BlockedDestination(f"could not resolve {host!r}: {exc}") from None
    for net in BLOCKED_NETWORKS:
        if resolved_ip in net:
            raise BlockedDestination(
                f"{host} resolves to {resolved_ip}, inside blocked range {net}"
            )
    with urllib.request.urlopen(uri, timeout=3) as resp:
        return resp.read().decode("utf-8", errors="replace")


def naive_patched_scheme_check_only(uri: str) -> str:
    """The 'looks safe but isn't' version from the blog's debugging
    story: rejects file:// and non-http(s) schemes by string prefix, but
    never resolves the hostname, so it still falls to SSRF against
    link-local/private IPs given directly as the host (127.0.0.1,
    169.254.169.254, etc. are all valid http:// URLs)."""
    if uri.startswith("file://"):
        raise BlockedDestination("file:// blocked")
    if not (uri.startswith("http://") or uri.startswith("https://")):
        raise BlockedDestination("non-http(s) scheme blocked")
    with urllib.request.urlopen(uri, timeout=3) as resp:
        return resp.read().decode("utf-8", errors="replace")

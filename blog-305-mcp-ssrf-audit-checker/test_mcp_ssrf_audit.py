"""Tests. Run: python3 test_mcp_ssrf_audit.py"""

from __future__ import annotations

import os
import tempfile

from mcp_furi import (
    BlockedDestination,
    convert_to_markdown_vulnerable,
    convert_to_markdown_patched,
    naive_patched_scheme_check_only,
)
from ssrf_audit_scanner import scan_source
from ssrf_dynamic_probe import probe_tool, start_fake_metadata_server


def _fake_target():
    server, port = start_fake_metadata_server()
    url = f"http://127.0.0.1:{port}/latest/meta-data/iam/security-credentials/demo-role"
    return server, url


def test_vulnerable_fetches_local_metadata_stand_in():
    server, url = _fake_target()
    try:
        result = convert_to_markdown_vulnerable(url)
        assert "AccessKeyId" in result
    finally:
        server.shutdown()


def test_vulnerable_reads_local_file_via_lfi():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SECRET=leaked-value\n")
        path = f.name
    try:
        result = convert_to_markdown_vulnerable(f"file://{path}")
        assert "leaked-value" in result
    finally:
        os.unlink(path)


def test_patched_blocks_local_metadata_stand_in():
    server, url = _fake_target()
    try:
        try:
            convert_to_markdown_patched(url)
            assert False, "expected BlockedDestination"
        except BlockedDestination:
            pass
    finally:
        server.shutdown()


def test_patched_blocks_file_scheme():
    try:
        convert_to_markdown_patched("file:///etc/hostname")
        assert False, "expected BlockedDestination"
    except BlockedDestination:
        pass


def test_naive_patched_still_leaks_literal_ip_target():
    """The gotcha from the blog post: a scheme-only check still falls to
    SSRF against a literal private/link-local IP given as the host."""
    server, url = _fake_target()
    try:
        result = naive_patched_scheme_check_only(url)
        assert "AccessKeyId" in result, "expected the naive check to still leak"
    finally:
        server.shutdown()


def test_naive_patched_blocks_file_scheme():
    try:
        naive_patched_scheme_check_only("file:///etc/hostname")
        assert False, "expected BlockedDestination"
    except BlockedDestination:
        pass


def test_static_scanner_flags_vulnerable_function():
    source = open("mcp_furi.py", encoding="utf-8").read()
    findings = scan_source("mcp_furi.py", source)
    by_name = {f.function: f for f in findings}
    assert by_name["convert_to_markdown_vulnerable"].guarded is False
    assert by_name["convert_to_markdown_patched"].guarded is True


def test_static_scanner_is_fooled_by_naive_check():
    """Documents the scanner's known limitation: it marks the naive,
    exploitable version as guarded because it textually raises
    BlockedDestination, even though it never resolves the hostname."""
    source = open("mcp_furi.py", encoding="utf-8").read()
    findings = scan_source("mcp_furi.py", source)
    by_name = {f.function: f for f in findings}
    assert by_name["naive_patched_scheme_check_only"].guarded is True


def test_dynamic_probe_confirms_vulnerable_leaks():
    result = probe_tool(convert_to_markdown_vulnerable)
    assert result["metadata_blocked"] is False
    assert result["file_blocked"] is False


def test_dynamic_probe_confirms_patched_is_safe():
    result = probe_tool(convert_to_markdown_patched)
    assert result["metadata_blocked"] is True
    assert result["file_blocked"] is True


def test_dynamic_probe_catches_what_static_scan_misses():
    """The core point of the blog post's audit guide: the dynamic probe
    catches the naive check's leak even though the static scanner didn't."""
    result = probe_tool(naive_patched_scheme_check_only)
    assert result["metadata_blocked"] is False  # still leaks


def _run_all() -> None:
    tests = [obj for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    _run_all()

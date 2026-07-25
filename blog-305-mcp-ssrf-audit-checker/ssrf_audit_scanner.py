"""Static AST scanner: find MCP tool functions with URI/URL-shaped
parameters that have no adjacent validation call in the same function
body.

Companion code for the AmtocSoft post "36.7% of MCP Servers Are Exposed
to SSRF. Here's How to Check If Yours Is One."

Heuristic, not proof. As the blog post's debugging story shows, this
scanner will mark `naive_patched_scheme_check_only` in `mcp_furi.py` as
"guarded" even though it's exploitable, because the function textually
raises a class called `BlockedDestination` and that string is one of the
scanner's guard markers. Static analysis narrows down what to look at by
hand; it does not replace looking. Use `ssrf_dynamic_probe.py` to actually
confirm a flagged (or unflagged) tool's behavior.

Pure standard library (ast module only).
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass

URI_PARAM_NAMES = {"uri", "url", "target_url", "endpoint", "href", "fetch_url", "source_url"}
GUARD_MARKERS = (
    "ipaddress", "is_private", "gethostbyname", "urlparse", "allowlist",
    "ALLOWED_HOSTS", "blocked", "BlockedDestination", "validate_url",
    "check_url", "resolve", "hostname",
)


@dataclass
class Finding:
    file: str
    function: str
    line: int
    param: str
    guarded: bool


def function_is_guarded(node) -> bool:
    body_src = ast.dump(node)
    return any(marker in body_src for marker in GUARD_MARKERS)


def scan_source(path: str, source: str) -> list[Finding]:
    tree = ast.parse(source, filename=path)
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for arg in node.args.args:
            if arg.arg.lower() in URI_PARAM_NAMES:
                findings.append(Finding(
                    file=path,
                    function=node.name,
                    line=node.lineno,
                    param=arg.arg,
                    guarded=function_is_guarded(node),
                ))
    return findings


def scan_file(path: str) -> list[Finding]:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    return scan_source(path, source)


def main(paths: list[str]) -> int:
    all_findings: list[Finding] = []
    for path in paths:
        all_findings.extend(scan_file(path))

    unguarded = [f for f in all_findings if not f.guarded]
    for f in all_findings:
        status = "OK (validation call present)" if f.guarded else "FLAG (no validation call found)"
        print(f"{f.file}:{f.line} {f.function}({f.param}) -> {status}")

    print()
    print(f"{len(all_findings)} URI-shaped parameter(s) found, {len(unguarded)} unguarded.")
    return 1 if unguarded else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["mcp_furi.py"]))

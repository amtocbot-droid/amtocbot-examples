"""Tests. Run: python3 test_tools.py"""

from __future__ import annotations

from tools import classify_http, get_order_status, TokenBudget, ToolResult


def test_success():
    assert classify_http(200, {"x": 1}).status == "success"


def test_rate_limit_retry_safe():
    r = classify_http(429, None)
    assert r.error_type == "rate_limit" and r.retry_safe


def test_server_error_transient():
    assert classify_http(503, None).error_type == "transient"


def test_not_found_permanent():
    assert classify_http(404, None).retry_safe is False


def test_timeout_is_transient():
    def boom(_):
        raise TimeoutError

    r = get_order_status("x", http=boom)
    assert r.error_type == "transient" and r.retry_safe


def test_budget_ok_warning_exceeded():
    b = TokenBudget(1000, warning_threshold=0.75)
    assert b.check(100) == "OK"
    b.consume(800)
    assert b.check(50) == "WARNING"
    assert b.check(300) == "EXCEEDED"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

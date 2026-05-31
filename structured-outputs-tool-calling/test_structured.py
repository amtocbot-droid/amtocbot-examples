"""Tests. Run: python3 test_structured.py"""

from __future__ import annotations

from structured import EXTRACT_ORDER_SCHEMA, validate, is_valid, execute_tool


def test_valid_passes():
    assert is_valid({"product_id": "x", "quantity": 1, "shipping_tier": "standard"},
                    EXTRACT_ORDER_SCHEMA)


def test_missing_required():
    errs = validate({"quantity": 1, "shipping_tier": "standard"}, EXTRACT_ORDER_SCHEMA)
    assert any("product_id" in e for e in errs)


def test_enum_violation():
    errs = validate({"product_id": "x", "quantity": 1, "shipping_tier": "warp"},
                    EXTRACT_ORDER_SCHEMA)
    assert any("enum" in e for e in errs)


def test_minimum_violation():
    errs = validate({"product_id": "x", "quantity": 0, "shipping_tier": "standard"},
                    EXTRACT_ORDER_SCHEMA)
    assert any("minimum" in e for e in errs)


def test_nullable_field_accepts_null():
    assert is_valid({"product_id": "x", "quantity": 1, "shipping_tier": "standard",
                     "special_instructions": None}, EXTRACT_ORDER_SCHEMA)


def test_bool_is_not_integer():
    errs = validate({"product_id": "x", "quantity": True, "shipping_tier": "standard"},
                    EXTRACT_ORDER_SCHEMA)
    assert any("quantity" in e for e in errs)


def test_dispatch_unknown_tool_raises():
    try:
        execute_tool("rm_rf", {})
    except ValueError:
        return
    raise AssertionError("should raise on unknown tool")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("\nall tests passed")

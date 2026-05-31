"""Validate good and bad tool inputs, then dispatch a tool call.

    $ python3 demo.py
"""

from __future__ import annotations

from structured import EXTRACT_ORDER_SCHEMA, validate, is_valid, execute_tool


def main() -> None:
    good = {"product_id": "SKU-4821", "quantity": 3, "shipping_tier": "express",
            "special_instructions": "leave at door"}
    print("valid order:", is_valid(good, EXTRACT_ORDER_SCHEMA))
    assert is_valid(good, EXTRACT_ORDER_SCHEMA)

    bad = {"product_id": "SKU-1", "quantity": 0, "shipping_tier": "teleport"}
    errs = validate(bad, EXTRACT_ORDER_SCHEMA)
    print("invalid order errors:")
    for e in errs:
        print("  -", e)
    assert any("enum" in e for e in errs)
    assert any("minimum" in e for e in errs)

    print("\ntool dispatch:", execute_tool("get_order_status", {"order_id": "ORD-1"}))
    print("\nOK: schema validation catches drift the provider guarantee can't.")


if __name__ == "__main__":
    main()

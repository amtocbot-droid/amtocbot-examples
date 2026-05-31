"""Structured outputs via tool calling: validate a model's tool input against
its JSON schema before you trust it.

Companion code for the AmtocSoft post
"Structured Outputs and Tool Calling".

The provider guarantees the tool input *shape*, but in production you still
validate (schema versions drift, you proxy multiple providers). This module
is a small JSON-Schema validator covering the subset the post's schemas use:
type, enum, minimum, required, and nullable unions. Plus a tool dispatch
table. Pure standard library.
"""

from __future__ import annotations

from typing import Any

# The order-extraction schema from the post.
EXTRACT_ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "product_id": {"type": "string"},
        "quantity": {"type": "integer", "minimum": 1},
        "shipping_tier": {"type": "string",
                          "enum": ["standard", "express", "overnight"]},
        "special_instructions": {"type": ["string", "null"]},
    },
    "required": ["product_id", "quantity", "shipping_tier"],
}

_PY_TYPES = {
    "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "object": dict, "array": list, "null": type(None),
}


def _type_ok(value: Any, type_spec: Any) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    # bool is a subclass of int — keep them distinct.
    for t in types:
        py = _PY_TYPES[t]
        if t == "integer" and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    return False


def validate(instance: dict, schema: dict) -> list[str]:
    """Return a list of validation errors ([] means valid)."""
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in instance:
            errors.append(f"missing required field: {field}")
    for key, spec in schema.get("properties", {}).items():
        if key not in instance:
            continue
        val = instance[key]
        if not _type_ok(val, spec["type"]):
            errors.append(f"{key}: expected {spec['type']}, got {type(val).__name__}")
            continue
        if "enum" in spec and val not in spec["enum"]:
            errors.append(f"{key}: {val!r} not in enum {spec['enum']}")
        if "minimum" in spec and isinstance(val, (int, float)) and val < spec["minimum"]:
            errors.append(f"{key}: {val} below minimum {spec['minimum']}")
    return errors


def is_valid(instance: dict, schema: dict) -> bool:
    return not validate(instance, schema)


# --------------------------------------------------------------------------
# Tool dispatch (the `match` table from the post).
# --------------------------------------------------------------------------
def get_order_status(order_id: str) -> str:
    return f"order {order_id}: shipped, tracking 1Z999, ETA 2 days"


def get_product_info(product_id: str) -> str:
    return f"product {product_id}: in stock"


def execute_tool(tool_name: str, tool_input: dict) -> str:
    match tool_name:
        case "get_order_status":
            return get_order_status(tool_input["order_id"])
        case "get_product_info":
            return get_product_info(tool_input["product_id"])
        case _:
            raise ValueError(f"Unknown tool: {tool_name}")

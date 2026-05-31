"""Run input validation (PII fix, length, gibberish) and an output grounding
check end to end.

    $ python3 demo.py
"""

from __future__ import annotations

from guardrails import validate_input, check_grounding, ValidationError

CONTEXT = ("The subscription renews on the 15th of each month. Customers on "
           "the Pro plan get priority support and 200 seats.")


def main() -> None:
    clean = validate_input("My email is dana@example.com, when do I renew?")
    print("input after PII fix:", clean)
    assert "dana@example.com" not in clean

    for bad in ["hi", "asdkfj qwlkfj zxcvbn wqerty"]:
        try:
            validate_input(bad)
        except ValidationError as e:
            print(f"rejected {bad!r}: {e}")

    grounded = check_grounding(CONTEXT, "Your subscription renews on the 15th.")
    hallucinated = check_grounding(CONTEXT, "Your plan includes a free yacht.")
    print("\ngrounded response:   ", grounded["verdict"])
    print("hallucinated response:", hallucinated["verdict"],
          hallucinated["unsupported_claims"])

    assert grounded["verdict"] == "SUPPORTED"
    assert hallucinated["verdict"] == "UNSUPPORTED"
    print("\nOK: PII fixed, junk rejected, ungrounded claims caught.")


if __name__ == "__main__":
    main()

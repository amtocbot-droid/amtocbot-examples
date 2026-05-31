# Structured Outputs and Tool Calling

Companion code for the AmtocSoft post
[Structured Outputs and Tool Calling](https://amtocsoft.blogspot.com/).

Tool calling gives you schema-shaped output, but in production you still
validate it (schema versions drift, you proxy multiple providers). This is a
small JSON-Schema validator covering the subset the post's schemas use —
type, enum, minimum, required, nullable unions — plus a tool dispatch table.

## Files

- `structured.py` — the validator + `execute_tool` dispatch. Pure stdlib.
- `demo.py` — validates good/bad order extractions, dispatches a tool.
- `test_structured.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_structured.py
```

## License

MIT

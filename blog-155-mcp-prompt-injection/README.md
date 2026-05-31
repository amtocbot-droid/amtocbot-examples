# MCP Prompt Injection: Tool Descriptions as Attack Surface

Companion code for the AmtocSoft post
[MCP Prompt Injection: Tool Descriptions as Attack Surface](https://amtocsoft.blogspot.com/).

A malicious MCP server can smuggle instructions into a tool *description*.
Three defenses:

1. **Scan descriptions** for instructional / credential-seeking language.
2. **Gate capabilities** — a tool can't exceed what its policy grants.
3. **Spotlight** tool descriptions and outputs in a per-session random tag
   so the model treats them as data, never instruction.

The post's scanner is a Haiku classifier; this is a transparent rule-based
scorer with the same JSON shape. Pure stdlib.

## Files

- `mcp_defense.py` — scanner, `ToolGate`, spotlighting.
- `demo.py` — benign vs malicious description, gate, spotlight.
- `test_mcp_defense.py` — tests.

## Run it

```bash
python3 demo.py
python3 test_mcp_defense.py
```

## License

MIT

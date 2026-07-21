# amtocbot-examples

Working code companions for [AmtocSoft](https://amtocsoft.blogspot.com) blog
posts. Each directory is a self-contained, runnable example matching a published
deep-dive. No orphan snippets: if it appears in a post, it runs here.

Every example is pure Python standard library (no install step) unless a
directory notes otherwise. External services from the posts (databases, model
APIs, AWS/OTel SDKs) are swapped for in-process stand-ins so the *logic* runs
and tests pass offline. Run any example with `python3 <demo_or_sim>.py` and its
tests with `python3 test_*.py`.

## Index

| Dir | Post |
|-----|------|
| [`llm-evals`](llm-evals) | LLM Evaluation in Production |
| [`structured-outputs-tool-calling`](structured-outputs-tool-calling) | Structured Outputs and Tool Calling |
| [`prompt-caching-2026`](prompt-caching-2026) | Prompt Caching for LLM Cost Optimization |
| [`cloud3-multicloud`](cloud3-multicloud) | Cloud 3: Hybrid Multicloud Sovereign Architecture |
| [`agentic-ai-production`](agentic-ai-production) | Agentic AI in Production: Lessons From Early Adopters |
| [`133-ai-memory-systems`](133-ai-memory-systems) | AI Memory Systems: Building Agents That Remember |
| [`134-mixture-of-experts`](134-mixture-of-experts) | Mixture of Experts Architecture for LLMs |
| [`137-ai-guardrails`](137-ai-guardrails) | AI Guardrails in Production |
| [`143-observable-ai-agents`](143-observable-ai-agents) | Observable AI Agents with OpenTelemetry |
| [`145-tiered-memory-agent`](145-tiered-memory-agent) | Context Window Limits and the Memory Myth |
| [`blog-153-llm-resilience-patterns`](blog-153-llm-resilience-patterns) | Production AI Agent Patterns: Retry, Idempotency, Circuit Breakers |
| [`blog-154-eu-ai-act-article-14-runtime`](blog-154-eu-ai-act-article-14-runtime) | EU AI Act Article 14: An Engineering Checklist |
| [`blog-155-mcp-prompt-injection`](blog-155-mcp-prompt-injection) | MCP Prompt Injection: Tool Descriptions as Attack Surface |
| [`blog-160-mcp-marketplace-lessons`](blog-160-mcp-marketplace-lessons) | MCP Marketplace: Lessons From the 2014 API Gold Rush |
| [`blog-161-ai-coding-consolidation`](blog-161-ai-coding-consolidation) | AI Coding Tool Stack Consolidation: From Five Tools to Two |
| [`blog-162-production-agent-patterns`](blog-162-production-agent-patterns) | Production Agent Patterns: Retry, Idempotency, Circuit Breakers (async) |
| [`blog-163-eu-ai-act-article-14`](blog-163-eu-ai-act-article-14) | EU AI Act Article 14: Traceability for AI Engineers |
| [`blog-164-continuous-eval-pipeline`](blog-164-continuous-eval-pipeline) | Continuous Evaluation for AI Agents: Drift Detection and Replay |
| [`blog-165-agent-memory-stack`](blog-165-agent-memory-stack) | AI Agent Memory Patterns: Semantic, Episodic, Procedural |
| [`blog-166-ai-observability-stack`](blog-166-ai-observability-stack) | The AI Observability Stack 2026: Langfuse, Arize, Portkey, Splunk |
| [`otel-genai-agent`](otel-genai-agent) | OpenTelemetry GenAI Conventions: LLM Span Attributes |
| [`mcp-defensive-sandbox`](mcp-defensive-sandbox) | Defensive MCP Server: Sandboxing, Permissions, Audit Logs, Resource Caps |
| [`agent-memory-privacy`](agent-memory-privacy) | AI Agent Memory Privacy: Preemptive PII Redaction Patterns |
| [`prompt-cache-strategies`](prompt-cache-strategies) | LLM Prompt Cache Strategies: Hit-Rate Optimisation |
| [`streaming-llm-production`](streaming-llm-production) | Streaming LLM Responses in Production |
| [`embedding-migration`](embedding-migration) | Embedding Model Migration: Zero-Downtime Reindex |
| [`llm-judge-calibration`](llm-judge-calibration) | LLM-as-a-Judge in Production: Bias Correction & Calibration |
| [`llm-canary-router`](llm-canary-router) | Production LLM Canary Deployments: Shadow Mode, Traffic Splits |
| [`llm-platform-health-score`](llm-platform-health-score) | Platform Health Score for LLM Systems (+ per-tenant at scale) |
| [`llm-rate-limit-engineering`](llm-rate-limit-engineering) | LLM Rate Limit Engineering: Batch Jobs vs User Traffic |
| [`adlc-metric-map`](adlc-metric-map) | The ADLC Metric Map: Pre-Deploy, Post-Deploy, Steady-State |
| [`adlc-dashboards`](adlc-dashboards) | ADLC Dashboards: PromQL, Grafana, Alert Fatigue |
| [`adlc-runbooks`](adlc-runbooks) | ADLC On-Call Runbook Structure: Sixty-Second Triage |
| [`adlc-postmortems`](adlc-postmortems) | ADLC Postmortem Template: From Runbook Miss to Runbook Fix |
| [`adlc-retrospectives`](adlc-retrospectives) | Postmortem Retrospective Cadence: Recurring Contributing Factors |
| [`adlc-eval-contracts`](adlc-eval-contracts) | Eval Contracts & the ADLC manifest-ledger series (posts 189–201) |
| [`vector-db-cost-showdown`](vector-db-cost-showdown) | Vector Database Cost Showdown 2026 |
| [`vector-db-cost-showdown-2026`](vector-db-cost-showdown-2026) | Vector DB Cost Showdown 2026 |
| [`260-guardrails-first`](260-guardrails-first) | Guardrails-First: Making AI Agents Reliable at 3am |
| [`261-llm-attacker-defense`](261-llm-attacker-defense) | When the Attacker Has an LLM: Defending Against AI-Developed Exploits |
| [`262-context-engineering`](262-context-engineering) | Context Engineering as Infrastructure: The 2026 Field Guide |
| [`263-slm-on-device`](263-slm-on-device) | SLMs On-Device: Pick, Quantize, and Ship a Small Language Model |
| [`259-ai-coding-tools`](259-ai-coding-tools) | AI Coding Tools in 2026: Cursor, Claude Code, Copilot, Windsurf Compared |
| [`blog-301-langflow-idor-repro`](blog-301-langflow-idor-repro) | Langflow Just Became the First AI Agent Platform on CISA's Must-Patch List (CVE-2026-55255) |

## License

MIT unless noted otherwise inside a directory.

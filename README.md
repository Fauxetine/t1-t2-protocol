[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/t1-t2-protocol.svg)](https://pypi.org/project/t1-t2-protocol/)
[![CI](https://github.com/Fauxetine/t1-t2-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/Fauxetine/t1-t2-protocol/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--03--26-purple.svg)](https://modelcontextprotocol.io/)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.Fauxetine%2Ft1--t2--protocol-blue)](https://registry.modelcontextprotocol.io/)

# T1/T2 Protocol — Heterogeneous Validation for MCP

[中文文档](README.zh.md) · [MCP Registry entry](https://registry.modelcontextprotocol.io/) (`io.github.Fauxetine/t1-t2-protocol`)

<!-- mcp-name: io.github.Fauxetine/t1-t2-protocol -->

> **Reference implementation.** This is a **stdlib-only MCP reference server** for structured reasoning discipline — not a production security product. Evaluate your own threat model before deploying in sensitive environments. Unlike official Python MCP servers, it does **not** use the `mcp` SDK; it speaks JSON-RPC over stdio directly.

**T1/T2 is an MCP server that makes AI reasoning verifiable, auditable, and trustworthy** — by decomposing ambiguous questions into structured tiers (T1), then validating answers through cross-model evaluation (T2), with a deterministic checksum layer that doesn't depend on any LLM.

## Why?

When an LLM checks its own answer, it uses the same training data, the same reasoning preferences, and the same systematic biases. **Self-reflection cannot catch its own blind spots.**

T1/T2 introduces **heterogeneous validation**: the model that produces the answer and the model that evaluates it should be different. Their different training distributions cover each other's blind spots.

## Tools

| Tool | Function | Why it matters |
|------|----------|---------------|
| **t1_protocol** | Decomposes ambiguous questions into L1 (facts) / L2 (assumptions) / L3 (hypotheses) / L4 (unknowns) | Forces structured reasoning before answering |
| **t2_protocol** | Evaluates answer quality from another model's perspective (qualitative five-level confidence) | Catches blind spots self-reflection misses |
| **checksum** | Deterministic structural validation — pure regex, zero LLM dependency | Safety that doesn't scale with intelligence |

> **How tools return data:** `t1_protocol` and `t2_protocol` return **structured prompt templates** for your MCP host's LLM to execute. Only `checksum` returns deterministic JSON (`checksum_passed`, `errors`).

### Tool inputs (MCP schema)

#### t1_protocol

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | yes | The ambiguous question to decompose |
| `locale` | string | no | `en` (default) or `zh` |
| `weight_hint` | string | no | `fact-first`, `efficiency-first`, `cost-first`, `robustness-first`, `general-first` (or Chinese equivalents) |

#### t2_protocol

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `answer` | string | yes | Text to evaluate (often the host LLM's draft answer) |
| `locale` | string | no | `en` (default) or `zh` |
| `weight_hint` | string | no | Same values as `t1_protocol` |

#### checksum

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | Structured answer text to validate |

Returns JSON: `{"checksum_passed": bool, "errors": [...]}`.

## Quick Start

### Requirements

- Python 3.10+
- An MCP client: [Cursor](https://cursor.sh/), [Claude Desktop](https://claude.ai/download), [Windsurf](https://codeium.com/windsurf), or any MCP-compatible host

### Install

From PyPI (recommended):

```bash
pip install "t1-t2-protocol>=0.1.0"
```

From source (development):

```bash
git clone https://github.com/Fauxetine/t1-t2-protocol.git
cd t1-t2-protocol
pip install -e ".[dev]"
T1T2_DISABLE_COUNTERS=1 python -m pytest tests/ -v
```

Or run directly without installing:

```bash
python src/t1_t2_mcp_server.py   # Windows
python3 src/t1_t2_mcp_server.py  # macOS / Linux
```

### Configure

After `pip install`, use the console script in MCP config (recommended):

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "type": "stdio",
      "command": "t1-t2-protocol"
    }
  }
}
```

**Cursor** — `.cursor/mcp.json` (same as above).

**Claude Desktop** — `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "command": "t1-t2-protocol"
    }
  }
}
```

**From source (no pip install)** — point at the script:

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "type": "stdio",
      "command": "python",
      "args": ["C:/path/to/t1-t2-protocol/src/t1_t2_mcp_server.py"]
    }
  }
}
```

On macOS/Linux use `"command": "python3"` instead of `"python"`.

### Verify it works

1. Restart or reload your MCP host after editing config.
2. Confirm three tools appear: `t1_protocol`, `t2_protocol`, `checksum`.
3. Call `t1_protocol` with `{"question": "Should we adopt microservices?", "locale": "en"}` — you should receive a structured T1 prompt template.
4. Call `checksum` with sample `[L1 Facts]` … `---` text — you should receive JSON with `checksum_passed`.

## Usage

### T1: Structure a vague question

Call `t1_protocol` with your question. The host LLM receives a structured prompt template with four tiers:

```
Input:  {"question": "Should we migrate our monolith to microservices?"}

Output: Prompt template instructing the host to produce:
  [L1 Facts]      Team size, codebase size, current stack
  [L2 Assumptions] Expected benefits that need verification
  [L3 Hypotheses] Testable claims about migration risk
  [L4 Unknown]    Future growth trajectory
  [Core Question] The precise feasibility question
```

### T2: Cross-validate a decision

Call `t2_protocol` with a decision or answer text. Returns an evaluation prompt for the host LLM:

```
Input:  {"answer": "Decision text for approach A..."}

Output: Prompt template requesting:
  Confidence: high | medium-high | medium | medium-low | low
  Adoption table with:
    ✅ Adopt     — verified conclusions (L1)
    ⚠️ Reserved — needs more evidence (L2)
    ❌ N/A      — blind spots to address
```

### checksum: Validate output structure

Call `checksum` with structured text. It returns pass/fail based on deterministic rules:

```
Input: "[L1 Facts]\n1. ...\n[L2 Assumptions]\n1. ...\n---"
Output: {"checksum_passed": true, "errors": []}
```

### Full pipeline

```
Vague question → T1 structured decomposition → Decision based on structure → checksum (optional) → T2 validation → Refined decision
```

For time-sensitive factual claims, **search on the caller side before T2** — see [Caller-side web verification (v2.6)](docs/caller-protocol.md).

## Configuration

### Locale

Both `t1_protocol` and `t2_protocol` accept an optional `locale` parameter:

| Value | Output |
|-------|--------|
| `en` (default) | English templates |
| `zh` | Chinese templates |

Example: `{"question": "...", "locale": "zh"}`

### Weight hints

Both `t1_protocol` and `t2_protocol` accept an optional `weight_hint` parameter to bias evaluation criteria:

| Weight | Effect |
|--------|--------|
| `事实优先` / `fact-first` | Prioritizes factual accuracy |
| `效率优先` / `efficiency-first` | Prioritizes efficiency |
| `成本优先` / `cost-first` | Prioritizes cost |
| `鲁棒性优先` / `robustness-first` | Prioritizes robustness |
| `通用优先` / `general-first` | No specific bias |

### Recursion protection

T2 automatically detects recursion depth and terminates at depth >= 3, where marginal information gain drops below 5%.

## Design Philosophy

See [docs/philosophy.md](docs/philosophy.md) for the full design rationale.

Core tenets:

1. **Separate intelligence from trust** — AI capability and AI safety should be guaranteed by different systems
2. **Heterogeneous over self-referential** — Cross-model validation is more reliable than self-reflection
3. **Deterministic over probabilistic** — What can be checked by code should not be left to model judgment

## Examples

See [examples/](examples/) for step-by-step walkthroughs:

- [T1: Structure a vague question](examples/t1-basic.md)
- [T2: Cross-validate a decision](examples/t2-basic.md)
- [Full pipeline: T1 → decision → T2](examples/full-pipeline.md)

## Positioning

| Project | Layer | What it does | T1/T2 relationship |
|---------|-------|--------------|-------------------|
| [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) (official MCP) | Caller-side chain-of-thought | One model logs iterative steps | Complementary — T1 adds L1–L4 tiers + T2 cross-model review |
| [ThoughtProof](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2574) / verdict APIs | Server-side verification | `APPROVE`/`DENY`/`UNCERTAIN` with confidence | Complementary — T1/T2 structures reasoning *before* verdict APIs act |
| Self-reflection / prompt chains | Same model | Re-reads or re-prompts its own output | Replaced — heterogeneous validation catches shared blind spots |
| Tool integrity (e.g. Phionyx) | Transport / tool schema | Detects tool poisoning, schema drift | Orthogonal — T1/T2 does not secure tool definitions |

T1/T2 is a **stdlib reference implementation** for [MCP Discussion #2574](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2574)-style reasoning discipline: structure first (T1), cross-validate second (T2), checksum what code can verify. It is not a signed verdict API and not a security scanner.

## Versioning

Two version numbers — do not conflate them:

| | Example | Meaning |
|---|---------|---------|
| **Package** (PyPI) | `0.1.0` | Distribution lifecycle. `0.x` = experimental ([SemVer](https://semver.org/), [FastAPI policy](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/deployment/versions.md)). |
| **Protocol** (spec) | `v2.5` | T1/T2 tool semantics in server output footer. Caller-side web verify docs use `v2.6`. |

Recommended install: `pip install "t1-t2-protocol>=0.1.0"`. Erroneous PyPI releases `2.5.2`–`2.5.4` are yanked.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

*Built for the MCP ecosystem. Part of a broader exploration into AI safety through deterministic architecture.*

---

## Links

- [Contributing](CONTRIBUTING.md)
- [MCP Registry](https://registry.modelcontextprotocol.io/) — `io.github.Fauxetine/t1-t2-protocol`
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Design philosophy](docs/philosophy.md)
- [Caller-side web verification v2.6](docs/caller-protocol.md)
- [Agent / MCP host instructions](AGENTS.md)

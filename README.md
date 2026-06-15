[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--03--26-purple.svg)](https://modelcontextprotocol.io/)

# T1/T2 Protocol — Heterogeneous Validation for MCP

**T1/T2 is an MCP server that makes AI reasoning verifiable, auditable, and trustworthy** — by decomposing ambiguous questions into structured tiers (T1), then validating answers through cross-model evaluation (T2), with a deterministic checksum layer that doesn't depend on any LLM.

## Why?

When an LLM checks its own answer, it uses the same training data, the same reasoning preferences, and the same systematic biases. **Self-reflection cannot catch its own blind spots.**

T1/T2 introduces **heterogeneous validation**: the model that produces the answer and the model that evaluates it should be different. Their different training distributions cover each other's blind spots.

## Tools

| Tool | Function | Why it matters |
|------|----------|---------------|
| **t1_protocol** | Decomposes ambiguous questions into L1 (facts) / L2 (assumptions) / L3 (hypotheses) / L4 (unknowns) | Forces structured reasoning before answering |
| **t2_protocol** | Evaluates answer quality from another model's perspective | Catches blind spots self-reflection misses |
| **checksum** | Deterministic structural validation — pure regex, zero LLM dependency | Safety that doesn't scale with intelligence |

## Quick Start

### Requirements

- Python 3.10+
- An MCP client: [Cursor](https://cursor.sh/), [Claude Desktop](https://claude.ai/download), [Windsurf](https://codeium.com/windsurf), or any MCP-compatible host

### Install

From PyPI (when published):

```bash
pip install t1-t2-protocol
```

From source (development):

```bash
git clone https://github.com/neo-reid/t1-t2-protocol.git
cd t1-t2-protocol
pip install -e ".[dev]"
python -m pytest tests/ -v
```

Or run directly without installing:

```bash
python3 src/t1_t2_mcp_server.py
```

After `pip install`, register the console script in MCP config:

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

### Configure

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/src/t1_t2_mcp_server.py"]
    }
  }
}
```

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "command": "python3",
      "args": ["/path/to/src/t1_t2_mcp_server.py"]
    }
  }
}
```

## Usage

### T1: Structure a vague question

Call `t1_protocol` with your question. It returns a structured prompt with four tiers:

```
Input: "Should we migrate our monolith to microservices?"

Output: Structured prompt with:
  [L1 Facts]     Team size, codebase size, current stack
  [L2 Assumptions] Expected benefits that need verification
  [L3 Hypotheses] Testable claims about migration risk
  [L4 Unknown]   Future growth trajectory
  [Core Question] The precise feasibility question
```

### T2: Cross-validate a decision

Call `t2_protocol` with a decision or answer text. It returns confidence assessment + adoption recommendations:

```
Input: "Decision text for approach A..."

Output:
  Confidence: Medium-High
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

## Why not existing tools?

| Tool | Approach | Limitation |
|------|----------|------------|
| Sequential Thinking (MCP) | One model thinks step by step | No cross-validation, no structural tiers |
| Self-reflection / Self-critique | Same model reviews own output | Cannot catch own blind spots |
| Prompt chains | Multiple prompts in sequence | No standardized protocol, no checksum |

T1/T2 is the only MCP server that provides **heterogeneous validation** — explicitly designed for different models to check each other.

## License

MIT — see [LICENSE](LICENSE).

---

*Built for the MCP ecosystem. Part of a broader exploration into AI safety through deterministic architecture.*

---

## Links

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Design philosophy](docs/philosophy.md)
- [Caller-side web verification v2.6](docs/caller-protocol.md)
- [Agent / MCP host instructions](AGENTS.md)

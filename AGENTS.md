# Agent instructions (MCP hosts)

This repository ships an **stdio MCP server** with three tools: `t1_protocol`, `t2_protocol`, and `checksum`.

## Recommended call order

1. **`t1_protocol`** — when the user question is ambiguous; decompose into L1–L4 tiers first.
2. **`checksum`** — before T2 when the answer must follow structural format (`[L1…]` sections + trailing `---`).
3. **`t2_protocol`** — evaluate confidence and adoption recommendations from a **different model** than the producer when possible.

## Caller-side web verification (v2.6)

The server has **no network access**. If the topic involves time-sensitive facts (library status, prices, recent events), **search on the caller side first**, then call `t2_protocol`. See [docs/caller-protocol.md](docs/caller-protocol.md).

## Parameters

| Tool | Key args | Notes |
|------|----------|-------|
| `t1_protocol` | `question`, optional `weight_hint`, `locale` | `locale`: `en` (default) or `zh` |
| `t2_protocol` | `answer`, optional `weight_hint`, `locale` | Same weights as T1 |
| `checksum` | `text` | Returns JSON; deterministic, stdlib-only |

**Weight hints (English or Chinese):** `fact-first` / `事实优先`, `efficiency-first` / `效率优先`, `cost-first` / `成本优先`, `robustness-first` / `鲁棒性优先`, `general-first` / `通用优先`.

## Constraints for contributors and agents

- Keep `src/t1_t2_mcp_server.py` **stdlib-only** (Layer 0).
- Do not add web search, pip dependencies, or network I/O to the MCP server.
- Prefer extending caller-side rules/docs over bloating the server.

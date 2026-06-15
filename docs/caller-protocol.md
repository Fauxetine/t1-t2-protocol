# Caller-Side Web Verification (v2.6)

## Rationale

T2 protocol evaluates answer confidence. But if the answer contains factual claims that may be time-sensitive, **the model's internal knowledge may be outdated** — even a high-confidence evaluation based on stale data is unreliable.

The solution is **caller-side web verification**: before sending text to `t2_protocol`, check factual claims against live web sources.

## Architecture

```
┌─ Caller (Cursor, Claude Desktop, your script)
│  ← Agent-Reach / Jina / Brave Search → Live web
│  ← t2_protocol → MCP server (no internet access)
```

- **Web search stays in Layer 2** (caller side, Agent-Reach, Jina, etc.)
- **T2 evaluation stays in Layer 0** (MCP server, stdlib, no network)
- This separation is intentional — see [philosophy.md](philosophy.md#deterministic-safety)

## When to verify

| Check before T2 | Skip |
|-----------------|------|
| Tool/library current status | Pure logical reasoning |
| Recent research/events | Architecture design evaluation |
| Price/market data | Local probe / structured tool output |
| Any timestamped factual claim | Foundational mathematics |
| An earlier conclusion that may be stale | — |

## Implementation

This protocol is a **caller convention**, not MCP code. The T1/T2 server itself never makes network calls.

**Cursor** — the `.cursor/rules/t2-web-verify-v2.6.mdc` rule handles this automatically:

```
AlwaysApply: true
Step: before calling t2_protocol, if topic involves time-sensitive facts,
      search via Agent-Reach / web search first
```

**Claude Desktop** — in your prompt convention, add:

```
Before calling t2_protocol, if the answer contains factual claims that
may be time-sensitive, search the web for current information first.
```

## Why not built into the MCP server?

1. **Layer separation**: MCP belongs in Layer 0 (stdlib, deterministic). Web search belongs in Layer 2 (network, third-party APIs).

2. **Choice of search tool**: Different users prefer different search backends (Agent-Reach, Brave, Tavily, Jina). The server should not mandate one.

3. **Offline compatibility**: The server should work without internet. Caller-side verification is optional — the server doesn't depend on it.

## See also

- [Design philosophy](philosophy.md#the-safety-intelligence-paradox)
- [T1 protocol specification](../README.md#t1-structure-a-vague-question)
- [T2 protocol specification](../README.md#t2-cross-validate-a-decision)
- [Chinese version](caller-protocol.zh.md)

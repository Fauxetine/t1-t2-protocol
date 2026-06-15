# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.5.4] - 2026-06-15

- Relicense future releases to Apache-2.0 to align with MCP official protocol/infrastructure direction
- Update PyPI metadata to PEP 639 SPDX license fields
- Remove PyPI API-token fallback from publish workflow; use Trusted Publishing only
- Add repository and website metadata to `server.json`

## [2.5.3] - 2026-06-15

- Fix MCP Registry namespace case (`io.github.Fauxetine/t1-t2-protocol`)
- Sync `mcp-name` marker in README for PyPI ownership verification

## [2.5.2] - 2026-06-15

- PyPI publish + MCP Registry metadata (`server.json`, `publish.yml`)
- README positioning vs Sequential Thinking / ThoughtProof / MCP #2574
- `mcp-name` ownership marker for registry verification

## [2.5.1] - 2026-06-15

- Open-source release polish: packaging (`package-dir`, `setuptools.build_meta`, `main()` entry point)
- Default `locale` is now `en`; `zh` remains fully supported
- English `weight_hint` aliases (`fact-first`, `efficiency-first`, etc.) match README
- Checksum error messages in English; optional counter via `~/.t1-t2-protocol` (disable in tests with `T1T2_DISABLE_COUNTERS=1`)
- Docs: caller-side web verification v2.6, `AGENTS.md`, bilingual caller-protocol
- CI: `pip install -e ".[dev]"` + pytest across Python 3.10–3.12

## [2.5.0] - 2026-06-12

- Enhanced L3 template with explicit evidence status tracking
- New tool: `checksum` — deterministic structural pre-validation (zero LLM dependency)
- Added core link exemption clarification to T1 output requirements
- Refined tool descriptions for protocol lifecycle (0→1 stage)

## [2.0.0] - 2026-06-12

- Added evaluation criteria weight assumption preamble to all outputs
- Added recursion depth detection and automatic termination (depth ≥ 3)
- Changed confidence from precise percentage to qualitative descriptors (high/medium/low)
- Added recursion depth label to all T2 outputs
- Clarified pure T2 vs T2+RAG scope
- Added version tag in output footer

## [1.0.0] - 2026-06-10

- Initial release
- T1: structured prompt translation (L1/L2/L3/L4)
- T2: confidence evaluation with adoption recommendations
- stdio MCP transport, stdlib-only

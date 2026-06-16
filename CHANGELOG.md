# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.1] - 2026-06-16

### Changed

- README / docs polish: tool input schemas, Windows config, verification steps, reference disclaimer
- `t2_protocol` MCP tool description: five-level qualitative confidence (was high/medium/low)

## [0.1.0] - 2026-06-16

First public PyPI release under honest pre-1.0 semver (FastAPI/requests pattern).

- Reset **package** version to `0.1.0`; **protocol specification** remains v2.5 (tool output semantics unchanged)
- Apache-2.0 license, PEP 639 metadata, MCP Registry + PyPI Trusted Publishing
- Yanked erroneous PyPI releases `2.5.2`–`2.5.4` (incorrect semver for day-one public release)

### Included capabilities (protocol v2.5)

- T1: structured prompt translation (L1/L2/L3/L4)
- T2: cross-model confidence evaluation with recursion depth guard
- `checksum`: deterministic structural pre-validation (stdlib-only)
- Bilingual templates (`en` / `zh`), weight hints, caller-side web verification docs (v2.6)

## Superseded PyPI releases (yanked)

| Version | Reason |
|---------|--------|
| 2.5.2–2.5.4 | Erroneous semver; superseded by `0.1.0`. Git tags `v2.5.x` remain as historical tombstones. |

## Protocol history (not package semver)

These entries document **protocol specification** evolution, not PyPI package versions.

### Protocol v2.5.0 — 2026-06-12

- Enhanced L3 template with explicit evidence status tracking
- New tool: `checksum` — deterministic structural pre-validation
- Added core link exemption clarification to T1 output requirements

### Protocol v2.0.0 — 2026-06-12

- Evaluation criteria weight assumption preamble
- Recursion depth detection and termination (depth ≥ 3)
- Qualitative confidence descriptors; version tag in output footer

### Protocol v1.0.0 — 2026-06-10

- Initial T1/T2 tools, stdio MCP transport, stdlib-only

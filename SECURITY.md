# Security

## Reporting a vulnerability

If you discover a security issue in T1/T2 Protocol, please **do not** open a public GitHub issue.

Instead, send a description of the issue to the project maintainer via [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability).

Please include:

- A description of the issue
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You should receive a response within 5 business days. If the issue is confirmed, a fix will be released and a security advisory will be published after the fix is deployed.

## Scope

This security policy covers the `t1_t2_mcp_server.py` source code and its official distribution on PyPI. It does not cover third-party MCP clients that connect to the server.

## Deterministic safety

The `checksum` tool is designed as a deterministic safety layer — it uses pure regex and string operations with zero LLM dependency. This means its behavior is fully predictable and testable. If you find a case where `checksum` produces incorrect results, please report it as a security issue.

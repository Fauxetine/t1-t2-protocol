# Contributing

Thanks for your interest in T1/T2 Protocol.

## How to contribute

- **Report bugs**: Open a GitHub issue with the `bug` label. Include the MCP client you're using, the exact tool call, and the unexpected output.
- **Suggest improvements**: Open a GitHub issue with the `enhancement` label. Explain what you'd like to see and why.
- **Submit code**: Fork the repo, create a feature branch, and open a pull request.

## Before submitting a PR

1. Install dev dependencies and run the full test suite:

   ```bash
   pip install -e ".[dev]"
   T1T2_DISABLE_COUNTERS=1 python -m pytest tests/ -v
   ```

2. Keep the server `stdlib-only`. This is a core design constraint — no pip dependencies in `src/t1_t2_mcp_server.py`.
3. If you're adding a new feature, include a brief rationale in the PR description. T1/T2 is intentionally minimal; every addition should justify itself.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to maintain a harassment-free environment for everyone.

## Questions?

Open a GitHub issue with the `question` label (or comment on an existing issue). Use `bug` / `enhancement` labels for actionable reports.

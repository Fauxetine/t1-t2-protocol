"""Shared pytest fixtures for MCP stdio integration tests."""

import json
import os
import subprocess
import sys

try:
    import pytest
except ImportError:
    pytest = None

# Prevent checksum counter writes during tests
os.environ.setdefault("T1T2_DISABLE_COUNTERS", "1")

SERVER_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "t1_t2_mcp_server.py")


class MCPClientSession:
    """Spawns one server process and sends multiple JSON-RPC messages."""

    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._id = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params:
            req["params"] = params
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        resp = self.proc.stdout.readline()
        return json.loads(resp.strip())

    def notify(self, method: str, params: dict | None = None):
        req = {"jsonrpc": "2.0", "method": method}
        if params:
            req["params"] = params
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

    def close(self):
        if self.proc.returncode is None:
            self.proc.kill()
        self.proc.wait()


if pytest:
    @pytest.fixture
    def mcp_session():
        session = MCPClientSession()
        session.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}})
        session.notify("notifications/initialized")
        yield session
        session.close()

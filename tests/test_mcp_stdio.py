"""MCP stdio smoke test — initialize + tools/list + checksum round-trip."""

import json

from conftest import MCPClientSession


def test_initialize():
    session = MCPClientSession()
    resp = session.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}})
    info = resp["result"]["serverInfo"]
    assert info["name"] == "t1-t2-protocol"
    assert info["version"] == "2.5.1"
    caps = resp["result"]["capabilities"]
    assert "tools" in caps
    assert "sampling" not in caps
    session.close()


def test_tools_list(mcp_session):
    resp = mcp_session.call("tools/list")
    tools = resp["result"]["tools"]
    names = [t["name"] for t in tools]
    assert names == ["t1_protocol", "t2_protocol", "checksum"]


def test_checksum_round_trip(mcp_session):
    resp = mcp_session.call("tools/call", {
        "name": "checksum",
        "arguments": {"text": "[L1 Facts]\n1. Test\n[L2 Assumptions]\n1. Test\n---"},
    })
    result_text = resp["result"]["content"][0]["text"]
    result = json.loads(result_text)
    assert result["checksum_passed"] is True


def test_missing_required_fails(mcp_session):
    resp = mcp_session.call("tools/call", {
        "name": "t1_protocol",
        "arguments": {},
    })
    assert resp["error"]["code"] == -32602

"""Locale tests — verify en/zh templates and default locale."""

from conftest import MCPClientSession


def _init(session: MCPClientSession):
    session.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}})
    session.notify("notifications/initialized")


def test_t1_default_is_en():
    session = MCPClientSession()
    _init(session)
    resp = session.call("tools/call", {
        "name": "t1_protocol",
        "arguments": {"question": "test"},
    })
    text = resp["result"]["content"][0]["text"]
    assert "According to T1 Protocol" in text
    session.close()


def test_t1_zh():
    session = MCPClientSession()
    _init(session)
    resp = session.call("tools/call", {
        "name": "t1_protocol",
        "arguments": {"question": "test", "locale": "zh"},
    })
    text = resp["result"]["content"][0]["text"]
    assert "根据T1协议" in text
    assert "L1事实" in text
    session.close()


def test_t1_en():
    session = MCPClientSession()
    _init(session)
    resp = session.call("tools/call", {
        "name": "t1_protocol",
        "arguments": {"question": "test", "locale": "en"},
    })
    text = resp["result"]["content"][0]["text"]
    assert "According to T1 Protocol" in text
    assert "[L1 Facts]" in text
    session.close()


def test_t2_zh():
    session = MCPClientSession()
    _init(session)
    resp = session.call("tools/call", {
        "name": "t2_protocol",
        "arguments": {"answer": "test answer", "locale": "zh"},
    })
    text = resp["result"]["content"][0]["text"]
    assert "根据T2协议" in text
    session.close()


def test_t2_en():
    session = MCPClientSession()
    _init(session)
    resp = session.call("tools/call", {
        "name": "t2_protocol",
        "arguments": {"answer": "test answer", "locale": "en"},
    })
    text = resp["result"]["content"][0]["text"]
    assert "According to T2 Protocol" in text
    assert "**Confidence**" in text
    session.close()

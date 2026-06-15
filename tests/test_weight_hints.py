"""Unit tests for weight_hint normalization and English aliases."""

from t1_t2_mcp_server import T1T2Server, validate_weight_hint


def test_english_aliases_normalize():
    for alias, canonical in [
        ("fact-first", "事实优先"),
        ("efficiency-first", "效率优先"),
        ("cost-first", "成本优先"),
        ("robustness-first", "鲁棒性优先"),
        ("general-first", "通用优先"),
    ]:
        valid, result = validate_weight_hint(alias)
        assert valid, alias
        assert result == canonical


def test_chinese_weights_still_valid():
    valid, result = validate_weight_hint("事实优先")
    assert valid
    assert result == "事实优先"


def test_unknown_weight_rejected():
    valid, err = validate_weight_hint("speed-first")
    assert not valid
    assert "Unknown weight" in err


def test_t1_en_weight_hint_in_output():
    server = T1T2Server()
    text = server._handle_t1("test?", weight_hint="fact-first", locale="en")
    assert "fact-first" in text
    assert "[Weight Declaration]" in text

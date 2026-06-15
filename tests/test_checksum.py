"""Tests for the deterministic checksum layer — zero LLM dependency, pure logic."""

import os
import sys

os.environ.setdefault("T1T2_DISABLE_COUNTERS", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from t1_t2_mcp_server import structural_checksum


def test_well_formed_output_passes():
    text = """[L1 Facts]
1. This is a verifiable fact.

[L2 Assumptions]
1. This is a reasonable assumption.

[Core Question]
Should this pass checksum?

---"""
    result = structural_checksum(text)
    assert result["checksum_passed"] is True
    assert result["errors"] == []


def test_missing_level_tags_fails():
    text = """Some unstructured text without level tags.

---"""
    result = structural_checksum(text)
    assert result["checksum_passed"] is False
    assert any("level tags" in err.lower() for err in result["errors"])


def test_missing_closing_delimiter_fails():
    text = """[L1 Facts]
1. A fact.

[L2 Assumptions]
1. An assumption."""
    result = structural_checksum(text)
    assert result["checksum_passed"] is False


def test_single_section_fails():
    text = """[L1 Facts]
1. Only one section here.

---"""
    result = structural_checksum(text)
    assert result["checksum_passed"] is False


def test_dangerous_patterns_detected():
    text = """[L1 Facts]
1. Run rm -rf / as a test.

[L2 Assumptions]
1. This is dangerous.

---"""
    result = structural_checksum(text)
    assert result["has_dangerous_patterns"] is True
    assert result["checksum_passed"] is False


def test_empty_input_fails():
    result = structural_checksum("")
    assert result["checksum_passed"] is False


def test_all_four_levels_pass():
    text = """[L1 Facts]
1. Verified fact.

[L2 Assumptions]
1. Reasonable assumption.

[L3 Hypotheses]
1. Falsifiable claim.

[L4 Unknown]
1. Known boundary.

[Core Question]
Test question?

---"""
    result = structural_checksum(text)
    assert result["checksum_passed"] is True
    assert result["section_count"] >= 4

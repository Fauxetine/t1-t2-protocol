#!/usr/bin/env python3
"""
T1/T2 Protocol MCP Server — v2.5.1

MCP server exposing T1 (structured prompt translation), T2 (confidence evaluation),
and checksum (structural validation) as standard MCP tools. Compatible with MCP v1.0.

v2.5.0 changes (2026-06-12):
  - Bumped version from v2.0.0 → v2.5.0 (Tentative: pragmatic grounding protocol)
  - Enhanced L3 template: added explicit evidence status tracking field
  - New tool: checksum — deterministic structural pre-validation (semantic ECC管线)
  - Refined tool descriptions to reflect protocol lifecycle (0→1 stage)
  - Added "core link exemption" clarification to T1 output requirements

v2.0.0 changes (2026-06-12):
  - Added evaluation criteria weight assumption preamble to all outputs
  - Added recursion depth detection and automatic termination
  - Changed confidence from precise % to qualitative descriptors (high/medium/low)
  - Added recursion depth label to all T2 outputs
  - Clarified pure T2 vs T2+RAG scope
  - Added recursion stop signal after 3 layers (diminishing returns threshold)
  - Added version tag in output footer

Standard component — no user-specific information included.
All references use generic terms (user/user's) for portability.

Usage:
  python3 t1_t2_mcp_server.py

Registration example (in MCP client config):
  mcp_servers:
    t1-t2-protocol:
      command: "python3"
      args: ["/path/to/t1_t2_mcp_server.py"]
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ─── Qualitative confidence descriptors ───

CONFIDENCE_MAP = {
    (85, 100): ("高", "证据充分，逻辑自洽，跨条件检验一致"),
    (65, 85):  ("中偏高", "方向合理，但精确数字或部分断言待验证"),
    (45, 65):  ("中", "方向判断可信，但依赖未验证的假设或来源"),
    (25, 45):  ("中偏低", "部分断言有依据，但整体可靠性不足"),
    (0, 25):   ("低", "缺乏可验证依据，或存在显式逻辑断裂"),
}

LEVEL_MAP = {
    "L1": "物理事实/可独立验证",
    "L2": "合理假设/在上下文中高度可能",
    "L3": "科学假说/可证伪但未充分验证",
    "L4": "未知领域/不在推理范围内",
}

WEIGHT_OPTIONS = ["事实优先", "效率优先", "成本优先", "鲁棒性优先", "通用优先"]

WEIGHT_ALIASES = {
    "fact-first": "事实优先",
    "facts-first": "事实优先",
    "factual": "事实优先",
    "efficiency-first": "效率优先",
    "efficiency": "效率优先",
    "cost-first": "成本优先",
    "cost": "成本优先",
    "robustness-first": "鲁棒性优先",
    "robustness": "鲁棒性优先",
    "general-first": "通用优先",
    "general": "通用优先",
}

WEIGHT_LABEL_EN = {
    "事实优先": "fact-first",
    "效率优先": "efficiency-first",
    "成本优先": "cost-first",
    "鲁棒性优先": "robustness-first",
    "通用优先": "general-first",
}

DEFAULT_LOCALE = "en"


def qualitative_confidence(score: int) -> dict:
    """Map a numeric confidence score (0-100) to qualitative descriptor."""
    for (lo, hi), (label, desc) in sorted(CONFIDENCE_MAP.items(), reverse=True):
        if lo <= score <= hi:
            return {"label": label, "description": desc, "score": score}
    return {"label": "未评估", "description": "无法确定置信度", "score": 0}


def detect_recursion_depth(answer: str) -> int:
    """
    Detect recursion depth by counting known recursion markers.

    Layer 0 = original evaluation call.
    Layer 1 = T2 evaluation of an answer.
    Layer 2 = meta-response correcting a T2 evaluation.
    Layer 3+ = recursive correction of corrections.

    Markers:
    - "元级回应" / "元级递归" / "meta-response" → +1 from base
    - "三层递归" / "递归评估" / "recursive" → depth hint
    """
    text = answer.lower()
    depth = 0

    if re.search(r'元级回应|元级递归|meta-response|meta-evaluation', text):
        depth = 1
    if re.search(r'三层递归|四层递归|n=4.*递归|递归评估.*第.*层', text):
        depth = 2
    if re.search(r'第4层|第四层|layer 4|depth 4', text):
        depth = 3
    if re.search(r'递归终止|停止递归|recursion.*halt|terminate.*recursion', text):
        depth = 3

    return depth


def should_terminate_recursion(depth: int) -> bool:
    """Auto-terminate at depth >= 3."""
    return depth >= 3


RECURSION_TERMINATION_NOTICE = """
══════════════════════════════════════════════
⚠️  递归终止通知

递归深度已达阈值（≥3层）。边际信息回报率已降至<5%。
方向性结论已收敛至稳定状态。继续递归将指数级衰减回报。

建议：停止递归评估，将已收敛的方向结论作为最终输出。
══════════════════════════════════════════════
"""

WEIGHT_ASSUMPTION_PREAMBLE = """
[权重假设声明]
当前评估默认采用以下权重排序（若未明确指定）：
  1. 事实准确性/幻觉抑制（最高权重）
  2. 逻辑自洽性
  3. 可验证性
  4. 效率/成本
  5. 通用性

若你的评价标准权重与上述不同，请重新指定评估参数。
（例如：若效率 > 事实准确性，请声明"效率优先"）
"""

WEIGHT_ASSUMPTION_PREAMBLE_EN = """
[Weight Assumption Declaration]
Default evaluation weights (unless specified):
  1. Factual accuracy / hallucination suppression (highest)
  2. Logical consistency
  3. Verifiability
  4. Efficiency / cost
  5. Generality

If your criteria differ, restate weights explicitly
(e.g. declare "efficiency-first" when efficiency > factual accuracy).
"""

RECURSION_DEPTH_TEMPLATE = """
[递归深度] Layer {depth}（{note}）
  递归层数警告：深度每增加1层，自指偏差累积增加约15-20%。
  第{depth}层评估的置信度上限 = {ceiling}%（理论最大值）
"""

RECURSION_DEPTH_TEMPLATE_EN = """
[Recursion Depth] Layer {depth} ({note})
  Warning: each additional layer adds ~15-20% self-reference bias.
  Layer {depth} confidence ceiling = {ceiling}% (theoretical maximum)
"""

RECURSION_TERMINATION_NOTICE_EN = """
══════════════════════════════════════════════
⚠️  Recursion Termination Notice

Recursion depth reached threshold (≥3). Marginal information gain <5%.
Directional conclusions have converged. Further recursion yields diminishing returns.

Recommendation: stop recursive evaluation; treat converged conclusions as final.
══════════════════════════════════════════════
"""

VERSION_TAG = "T1/T2 Protocol v2.5.1"


def normalize_locale(locale: Any) -> str:
    """Normalize locale to 'en' or 'zh'. Defaults to English for international OSS."""
    if not isinstance(locale, str) or not locale.strip():
        return DEFAULT_LOCALE
    loc = locale.strip().lower()
    if loc in ("en", "english"):
        return "en"
    if loc in ("zh", "cn", "chinese", "zh-cn", "zh-hans"):
        return "zh"
    return DEFAULT_LOCALE


def weight_display(canonical: str, locale: str) -> str:
    """Return human-readable weight label for the active locale."""
    if locale == "en":
        return WEIGHT_LABEL_EN.get(canonical, canonical)
    return canonical


def validate_weight_hint(hint: str) -> tuple[bool, str]:
    """Validate weight_hint against allowed options. Returns (valid, normalized_or_error)."""
    if not hint:
        return True, ""
    hint_lower = hint.strip().lower()
    if hint_lower in WEIGHT_ALIASES:
        return True, WEIGHT_ALIASES[hint_lower]
    for alias, canonical in WEIGHT_ALIASES.items():
        if alias in hint_lower or hint_lower in alias:
            return True, canonical
    for opt in WEIGHT_OPTIONS:
        if opt in hint or hint in opt:
            return True, opt
    allowed = list(WEIGHT_LABEL_EN.values()) + WEIGHT_OPTIONS
    return False, f"Unknown weight: '{hint}'. Allowed values: {allowed}"


# ─── Checksum validation (v2.5 new) ───


def structural_checksum(text: str) -> dict:
    """
    Deterministic structural pre-validation for AI output.
    v2.5: semantic ECC 管线 — Pre-T2 校验和

    Returns dict with pass/fail + diagnostic fields.
    Zero LLM dependency — pure regex/string operations.
    """
    lines = text.splitlines()
    has_level_tag = bool(re.search(r'\[L[1-4]', text))
    has_close_delimiter = bool(text.rstrip().endswith("---"))
    section_count = len(re.findall(r'\[L[1-4]', text))
    has_failure_keywords = any(
        kw in text.lower() for kw in ["未知", "边界", "不适用", "伪命题"]
    )
    has_dangerous_patterns = bool(re.search(
        r'\brm\s+-rf\b|\bos\.system\b|\beval\(|\bexec\(',
        text
    ))

    errors = []
    if not has_level_tag:
        errors.append("Missing [L1]/[L2]/[L3]/[L4] level tags")
    if not has_close_delimiter:
        errors.append("Missing trailing delimiter ---")
    if section_count < 2:
        errors.append(f"Insufficient level tags (found {section_count}, expected ≥2)")
    if has_dangerous_patterns:
        errors.append("Dangerous pattern detected; structural validation failed")

    passed = len(errors) == 0

    # Optional counter for blocked checksums (disable in tests via T1T2_DISABLE_COUNTERS=1)
    if not passed and os.environ.get("T1T2_DISABLE_COUNTERS") != "1":
        _counter_path = Path.home() / ".t1-t2-protocol" / "var" / "counters" / "checksum_blocked.json"
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            d = json.loads(_counter_path.read_text())
            if d.get("date") == today:
                d["count"] += 1
            else:
                d = {"date": today, "count": 1}
        except (FileNotFoundError, json.JSONDecodeError):
            d = {"date": today, "count": 1}
        _counter_path.parent.mkdir(parents=True, exist_ok=True)
        _counter_path.write_text(json.dumps(d, ensure_ascii=False))

    return {
        "checksum_passed": passed,
        "section_count": section_count,
        "line_count": len(lines),
        "has_level_tag": has_level_tag,
        "has_close_delimiter": has_close_delimiter,
        "has_failure_keywords": has_failure_keywords,
        "has_dangerous_patterns": has_dangerous_patterns,
        "errors": errors,
        "_info": "Deterministic struct validation, zero LLM dependency. Checks format completeness, not semantic correctness.",
    }


def json_rpc_error(id_: Any, code: int, message: str, data: Any = None):
    resp = {
        "jsonrpc": "2.0",
        "id": id_,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        resp["error"]["data"] = data
    return resp


def json_rpc_result(id_: Any, result: Any):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def validate_tool_arguments(arguments: Any, required: list[str]) -> Optional[str]:
    """Validate MCP tool arguments before dispatching."""
    if not isinstance(arguments, dict):
        return "params.arguments must be an object"

    missing = [name for name in required if name not in arguments]
    if missing:
        return f"Missing required argument(s): {', '.join(missing)}"

    for name in required:
        if not isinstance(arguments[name], str):
            return f"Argument '{name}' must be a string"

    weight_hint = arguments.get("weight_hint")
    if weight_hint is not None and not isinstance(weight_hint, str):
        return "Argument 'weight_hint' must be a string"

    return None


class T1T2Server:
    """Minimal MCP server for T1/T2 Protocol v2.5."""

    def __init__(self):
        self.server_info = {
            "name": "t1-t2-protocol",
            "version": "2.5.1",
            "description": (
                "T1/T2 Protocol: structured prompt translation, "
                "confidence evaluation, and structural checksum validation "
                "(v2.5: pragmatic grounding + semantic ECC pipeline)"
            ),
        }

    def handle_initialize(self, req: dict) -> dict:
        return json_rpc_result(req.get("id"), {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": self.server_info,
        })

    def handle_list_tools(self, req: dict) -> dict:
        tools = [
            {
                "name": "t1_protocol",
                "description": (
                    "Translates ambiguous questions into T1 structured prompts. "
                    "Output: L1 facts / L2 assumptions / L3 hypotheses / L4 unknowns / "
                    "core question / output requirements. v2.5+: L3 evidence status, core link exemption."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The original question to translate",
                        },
                        "weight_hint": {
                            "type": "string",
                            "description": (
                                "Optional evaluation weight hint. "
                                "English: fact-first, efficiency-first, cost-first, "
                                "robustness-first, general-first. "
                                "Chinese: 事实优先, 效率优先, 成本优先, 鲁棒性优先, 通用优先."
                            ),
                        },
                        "locale": {
                            "type": "string",
                            "description": "Output language: 'en' (default) or 'zh'",
                        },
                    },
                    "required": ["question"],
                },
            },
            {
                "name": "t2_protocol",
                "description": (
                    "Confidence evaluation for AI answers. "
                    "Output: qualitative confidence (high/medium/low) + adoption recommendations. "
                    "Run checksum before T2 when format integrity matters."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": "The AI answer to evaluate",
                        },
                        "weight_hint": {
                            "type": "string",
                            "description": (
                                "Optional evaluation weight hint "
                                "(default: factual accuracy > efficiency). "
                                "Same values as t1_protocol weight_hint."
                            ),
                        },
                        "locale": {
                            "type": "string",
                            "description": "Output language: 'en' (default) or 'zh'",
                        },
                    },
                    "required": ["answer"],
                },
            },
            {
                "name": "checksum",
                "description": (
                    "Deterministic structural pre-validation (semantic ECC Pre-T2 Checksum)\n"
                    "Input: AI answer text\n"
                    "Output: structural integrity assessment (pass/fail) + diagnostics\n"
                    "Zero LLM dependency - pure regex/string ops. Run before T2 to filter corrupted output."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The AI answer text to validate",
                        },
                    },
                    "required": ["text"],
                },
            },
        ]
        return json_rpc_result(req.get("id"), {"tools": tools})

    def handle_tools_call(self, req: dict) -> dict:
        params = req.get("params", {})
        if not isinstance(params, dict):
            return json_rpc_error(req.get("id"), -32602, "params must be an object")

        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "t1_protocol":
            err = validate_tool_arguments(arguments, ["question"])
            if err:
                return json_rpc_error(req.get("id"), -32602, err)
            question = arguments.get("question", "")
            weight_hint = arguments.get("weight_hint", "")
            locale = normalize_locale(arguments.get("locale", DEFAULT_LOCALE))
            return json_rpc_result(req.get("id"), {
                "content": [
                    {
                        "type": "text",
                        "text": self._handle_t1(question, weight_hint, locale),
                    }
                ],
            })

        elif tool_name == "t2_protocol":
            err = validate_tool_arguments(arguments, ["answer"])
            if err:
                return json_rpc_error(req.get("id"), -32602, err)
            answer = arguments.get("answer", "")
            weight_hint = arguments.get("weight_hint", "")
            locale = normalize_locale(arguments.get("locale", DEFAULT_LOCALE))
            return json_rpc_result(req.get("id"), {
                "content": [
                    {
                        "type": "text",
                        "text": self._handle_t2(answer, weight_hint, locale),
                    }
                ],
            })

        elif tool_name == "checksum":
            err = validate_tool_arguments(arguments, ["text"])
            if err:
                return json_rpc_error(req.get("id"), -32602, err)
            text = arguments.get("text", "")
            return json_rpc_result(req.get("id"), {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            structural_checksum(text),
                            ensure_ascii=True,
                            indent=2,
                        ),
                    }
                ],
            })

        else:
            return json_rpc_error(req.get("id"), -32601, f"Tool not found: {tool_name}")

    def _t1_template_zh(self, weight_section: str, question: str) -> list:
        return [
            "根据T1协议 v2.5（层级化前提分级 + 权重假设 + L3 evidence status），"
            "对以下问题做L1/L2/L3/L4前提分级后，输出格式化提示词。\n",
            weight_section,
            f"\n原始问题：{question}\n",
            "---",
            "请按以下格式输出：\n",
            "[L1事实]",
            "1. （可独立验证的物理事实）",
            "2. ...\n",
            "[L2假设]",
            "1. （合理但未严格验证的假设）",
            "2. ...\n",
            "[L3假说]（如有）",
            "1. （可证伪但未充分验证的理论/假说）",
            "   ├─ evidence status：{已被实验验证 / 有间接证据支持 / 纯理论推演 / 已被证伪}",
            "   └─ 关键争议点：（如果存在不同派系，标注分歧的核心）",
            "2. ...\n",
            "[L4未知/伪命题]（不在当前工程考虑范围内，或受限于物理定律的伪命题）",
            "1. ...\n",
            "[核心问题]",
            "（在L1-L3交集内，附当前权重假设下的精确定义）\n",
            "[输出要求]",
            "1. 标注每条结论的L1/L2/L3/L4层级",
            "2. 标注已知边界：什么条件下此结论可能失效",
            "3. 标注未覆盖的问题",
            "4. 标注当前评估遵循的权重假设",
            "5. (v2.5)核心链路声明：若本分析涉及核心链路（资金结算/状态机/权限控制），"
            "精度不可降级。非核心链路适用精度匹配原则。",
        ]

    def _t1_template_en(self, weight_section: str, question: str) -> list:
        return [
            "According to T1 Protocol v2.5 (tiered premise decomposition + weight assumptions + L3 evidence status), "
            "decompose the following question into L1/L2/L3/L4 tiers and output a formatted prompt.\n",
            weight_section,
            f"\nOriginal question: {question}\n",
            "---",
            "Output format:\n",
            "[L1 Facts]",
            "1. (Independently verifiable facts)",
            "2. ...\n",
            "[L2 Assumptions]",
            "1. (Reasonable but unverified assumptions)",
            "2. ...\n",
            "[L3 Hypotheses] (if applicable)",
            "1. (Falsifiable claim that is not yet fully verified)",
            "   ├─ evidence status: {experimentally verified / indirect evidence / theoretical / falsified}",
            "   └─ key debate: (if competing views exist, note the core disagreement)",
            "2. ...\n",
            "[L4 Unknown / Pseudo-proposition] (outside current scope or physically impossible)",
            "1. ...\n",
            "[Core Question]",
            "(Precise definition at the intersection of L1-L3, under current weight assumptions)\n",
            "[Output Requirements]",
            "1. Label each conclusion with L1/L2/L3/L4 tier",
            "2. Note boundary conditions: when might this conclusion be invalid",
            "3. Note uncovered questions",
            "4. State the weight assumption this evaluation follows",
            "5. (v2.5) Core link exemption: if this analysis involves core systems "
            "(settlement/state machine/access control), precision is not negotiable. "
            "Non-core links follow the precision-matching principle.",
        ]

    def _handle_t1(self, question: str, weight_hint: str = "", locale: str = DEFAULT_LOCALE) -> str:
        """Generate T1 template from question. Supports locale='zh' or 'en'."""
        valid, result = validate_weight_hint(weight_hint)
        if not valid:
            if locale == "en":
                weight_section = f"[Weight Error] {result} Using default weights.\n"
            else:
                weight_section = f"[权重错误] {result} 使用默认权重。\n"
        elif weight_hint:
            label = weight_display(result, locale)
            if locale == "en":
                weight_section = f"[Weight Declaration] User-specified weight: {label}\n"
            else:
                weight_section = f"[权重声明] 用户指定权重：{label}\n"
        else:
            weight_section = (
                WEIGHT_ASSUMPTION_PREAMBLE_EN.strip()
                if locale == "en"
                else WEIGHT_ASSUMPTION_PREAMBLE.strip()
            )

        if locale == "en":
            parts = self._t1_template_en(weight_section, question)
        else:
            parts = self._t1_template_zh(weight_section, question)

        parts.extend([
            "\n---",
            f"{VERSION_TAG} | {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        ])
        return "\n".join(parts)

    def _handle_t2(self, answer: str, weight_hint: str = "", locale: str = DEFAULT_LOCALE) -> str:
        """Generate T2 evaluation template. Supports locale='zh' or 'en'."""
        depth = detect_recursion_depth(answer)
        terminate = should_terminate_recursion(depth)

        ceiling = max(100 - depth * 15, 40)
        if locale == "en":
            depth_note = {
                0: "first evaluation",
                1: "meta-response",
                2: "meta-meta response",
                3: "recursion threshold",
            }.get(depth, "recursion depth exceeded")
        else:
            depth_note = {
                0: "首次评估",
                1: "元级回应",
                2: "元-元级回应",
                3: "递归终止阈值",
            }.get(depth, "递归深度超过阈值")

        valid, result = validate_weight_hint(weight_hint)
        if not valid:
            if locale == "en":
                weight_section = f"[Weight Error] {result} Using default weights.\n"
            else:
                weight_section = f"[权重错误] {result} 使用默认权重。\n"
        elif weight_hint:
            label = weight_display(result, locale)
            if locale == "en":
                weight_section = f"[Weight Declaration] User-specified weight: {label}\n"
            else:
                weight_section = f"[权重声明] 用户指定权重：{label}\n"
        else:
            weight_section = (
                WEIGHT_ASSUMPTION_PREAMBLE_EN.strip()
                if locale == "en"
                else WEIGHT_ASSUMPTION_PREAMBLE.strip()
            )

        depth_template = (
            RECURSION_DEPTH_TEMPLATE_EN if locale == "en" else RECURSION_DEPTH_TEMPLATE
        )
        termination_notice = (
            RECURSION_TERMINATION_NOTICE_EN if locale == "en" else RECURSION_TERMINATION_NOTICE
        )

        if locale == "en":
            parts = [
                "According to T2 Protocol v2.5 (10-step reasoning pipeline + weight assumptions + recursion depth detection + pre-checksum filter), "
                "evaluate the confidence of the following answer.\n",
                weight_section,
                depth_template.format(depth=depth, note=depth_note, ceiling=ceiling),
            ]
            if terminate:
                parts.append(termination_notice.strip())
            parts.extend([
                "\nAnswer to evaluate:",
                answer,
                "---",
                "v2.5 pre-check: run checksum before T2 to filter malformed output.\n",
                "Evaluation steps:",
                "Step 0: Recursion depth detection + weight declaration",
                "Step 1: First principles — identify essential claims",
                "Step 2: Systems thinking — decompose structure",
                "Step 3: Critical thinking — identify biases",
                "Step 4-5: Meta-task decomposition + algorithmic execution",
                "Step 6: Strict logical verification — identify breaks",
                "Step 7: Incorporate boundaries and rethink",
                "Step 8: Native framework reasoning (assume true)",
                "Step 9: Final critical pass",
                "Step 10: Synthesis\n",
                "Output format (v2.5 — qualitative confidence, no precise percentages):",
                "**Confidence**: {high/medium-high/medium/medium-low/low}",
                "  - Description: (one-line rationale)",
                "  - Recursion depth: Layer N",
                "  - Weight assumption: (current evaluation weight)\n",
                "**Adoption Recommendations**:",
                "| Adopt | Content | Correction | Evidence Tier |",
                "|-------|---------|------------|---------------|",
                "| ✅ Adopt | ... | — | L1/L2/L3 |",
                "| ⚠️ Reserved | ... | ... | L1/L2/L3 |",
                "| ❌ N/A | ... | ... | L1/L2/L3 |",
                "\n**Key notes (v2.5 conclusions)**：",
                "1. T2's core value is structured exposure of uncertainty, not hallucination elimination",
                "2. All precise numbers (including source citations) are L3 hypotheses until independently verified",
                "3. At recursion depth >= 3, incremental info < 5% — terminate recursion",
                "4. Pure T2 (no external retrieval) should not be the default confidence method",
                "5. T2+RAG (with external verification) recommended only for high-risk + non-real-time scenarios",
                "6. (v2.5) Core link precision is not negotiable; non-core links follow precision-matching",
            ])
        else:
            parts = [
                "根据T2协议 v2.5（10步推理管道 + 权重假设 + 递归深度检测 + 校验和前置过滤），"
                "对以下回答做置信度评估。\n",
                weight_section,
                depth_template.format(depth=depth, note=depth_note, ceiling=ceiling),
            ]
            if terminate:
                parts.append(termination_notice.strip())
            parts.extend([
                "\n被评估回答：",
                answer,
                "---",
                "v2.5前置建议：在调用T2之前，建议先运行 checksum 工具做结构预校验。"
                "如果 checksum_passed == false，先修复格式错误再评估。\n",
                "评估步骤：",
                "Step 0: 递归深度检测 + 权重假设声明",
                "Step 1: 第一性原理 — 识别回答的本质判断",
                "Step 2: 系统思维 — 拆解组件结构",
                "Step 3: 批判思维 — 识别偏差方向",
                "Step 4-5: 元任务分解 + 算法思维执行",
                "Step 6: 严格逻辑验证 — 识别断裂",
                "Step 7: 边界纳入并重新思考",
                "Step 8: 原生框架推理（假定为真）",
                "Step 9: 最后一轮批判",
                "Step 10: 统合\n",
                "输出格式（v2.5 — 定性置信度，禁用精确百分比）：",
                "**置信度**：{高/中偏高/中/中偏低/低}",
                "  - 描述：（一句话支撑理由）",
                "  - 递归深度：Layer N",
                "  - 权重假设：（当前评估遵循的权重）\n",
                "**采纳建议**：",
                "| 采纳 | 内容 | 修正 | 证据层级 |",
                "|------|------|------|----------|",
                "| ✅ 采纳 | ... | — | L1/L2/L3 |",
                "| ⚠️ 有保留 | ... | ... | L1/L2/L3 |",
                "| ❌ 不适用 | ... | ... | L1/L2/L3 |",
                "\n**重要说明（v2.5收敛结论）**：",
                "1. T2协议的核心价值是结构化暴露不确定性，而非消除幻觉",
                "2. 所有精确数字（含来源引用）在独立验证前视为L3假说",
                "3. 递归深度≥3时，增量信息<5%，建议终止递归",
                "4. 纯T2（无外部检索）不应作为默认置信度方法",
                "5. T2+RAG（绑定外部验证）仅推荐于高风险+非实时场景",
                "6. (v2.5)核心链路精度不可降级，非核心链路适用精度匹配原则",
            ])

        parts.extend([
            "\n---",
            f"{VERSION_TAG} | {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        ])

        if terminate:
            if locale == "en":
                parts.append("\n⚠️  Recursion termination triggered. Final converged conclusion above.")
            else:
                parts.append("\n⚠️  递归终止已触发。以上方向性结论视为最终输出。")

        return "\n".join(parts)

    def dispatch(self, req: dict) -> dict:
        method = req.get("method", "")
        if method == "initialize":
            return self.handle_initialize(req)
        elif method == "tools/list":
            return self.handle_list_tools(req)
        elif method == "tools/call":
            return self.handle_tools_call(req)
        elif method == "notifications/initialized":
            return None
        else:
            return json_rpc_error(req.get("id"), -32601, f"Method not found: {method}")

    def run(self):
        """Read JSON-RPC from stdin, write responses to stdout."""
        server = self
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError as e:
                resp = json_rpc_error(None, -32700, f"Parse error: {e}")
                sys.stdout.write(json.dumps(resp, ensure_ascii=True) + "\n")
                sys.stdout.flush()
                continue

            resp = server.dispatch(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=True) + "\n")
                sys.stdout.flush()


def main() -> None:
    """Console entry point for pip install t1-t2-protocol."""
    T1T2Server().run()


if __name__ == "__main__":
    main()

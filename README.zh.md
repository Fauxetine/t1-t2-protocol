[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/t1-t2-protocol.svg)](https://pypi.org/project/t1-t2-protocol/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2025--03--26-purple.svg)](https://modelcontextprotocol.io/)

# T1/T2 协议 — MCP 异构验证协议

<!-- mcp-name: io.github.Fauxetine/t1-t2-protocol -->

**T1/T2 是一个 MCP 服务器，让 AI 的推理可验证、可审计、可信任** — 通过将模糊问题分解为结构化层级（T1），再通过跨模型评估验证答案（T2），以及一个不依赖任何 LLM 的确定性校验层（checksum）。

## 为什么需要这个协议？

当 LLM 检查自己的回答时，它使用同一套训练数据、同一套推理偏好、同一套系统性偏差。**自我反思无法发现自己看不到的东西。**

T1/T2 引入**异构验证**：负责产出的模型和负责评估的模型应该是不同的。它们的训练分布差异覆盖彼此的盲区。

## 工具

| 工具 | 功能 | 为什么重要 |
|------|------|-----------|
| **t1_protocol** | 将模糊问题分解为 L1（事实）/ L2（假设）/ L3（假说）/ L4（未知） | 强制在回答之前进行结构化推理 |
| **t2_protocol** | 从另一个模型的视角评估回答质量 | 发现自我反思无法覆盖的盲区 |
| **checksum** | 确定性结构校验 — 纯正则，零 LLM 依赖 | 不随智能增长而减弱的安全性 |

## 快速开始

### 要求

- Python 3.10+
- 一个 MCP 客户端：[Cursor](https://cursor.sh/)、[Claude Desktop](https://claude.ai/download)、[Windsurf](https://codeium.com/windsurf) 或任何兼容 MCP 的主机

### 安装

PyPI（推荐）：

```bash
pip install t1-t2-protocol
```

源码（开发）：

```bash
git clone https://github.com/Fauxetine/t1-t2-protocol.git
cd t1-t2-protocol
pip install -e ".[dev]"
python -m pytest tests/ -v
```

或直接运行：

```bash
python3 src/t1_t2_mcp_server.py
```

安装后可在 MCP 配置中使用 `t1-t2-protocol` 命令作为 `command`。

### 配置

**Cursor** — 添加到 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/src/t1_t2_mcp_server.py"]
    }
  }
}
```

**Claude Desktop** — 添加到 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "t1-t2-protocol": {
      "command": "python3",
      "args": ["/path/to/src/t1_t2_mcp_server.py"]
    }
  }
}
```

## 使用

### T1：结构化一个模糊问题

调用 `t1_protocol`，传入你的问题。它返回一个四层级的结构化提示词：

```
输入："我们是否应该把单体应用迁移到微服务？"

输出：结构化提示词包含：
  [L1 事实]     团队规模、代码量、当前技术栈
  [L2 假设]     需要验证的预期收益
  [L3 假说]     关于迁移风险的假设
  [L4 未知]     未来业务增长路径
  [核心问题]    精确的可行性问题
```

### T2：交叉验证一个决策

调用 `t2_protocol`，传入决策或答案文本。返回置信度评估 + 采纳建议：

```
输入："关于方案A的决策文本..."

输出：
  置信度：中偏高
  采纳建议表：
    ✅ 采纳    — 已验证的结论（L1）
    ⚠️ 保留   — 需要更多证据（L2）
    ❌ 不适用 — 需要处理的盲区
```

### checksum：校验输出结构

调用 `checksum`，传入结构化文本。基于确定性规则返回通过/失败：

```
输入："[L1事实]\n1. ...\n[L2假设]\n1. ...\n---"
输出：{"checksum_passed": true, "errors": []}
```

### 全链路

```
模糊问题 → T1 结构化分解 → 基于结构做决策 → checksum（可选）→ T2 验证 → 改进的决策
```

涉及时效性事实时，**在 T2 前由调用方先 Web 搜索** — 见 [调用方 Web 验证 v2.6](docs/caller-protocol.zh.md)。

## 配置

### 语言（locale）

`t1_protocol` 与 `t2_protocol` 支持可选参数 `locale`：

| 值 | 输出 |
|----|------|
| `en`（默认） | 英文模板 |
| `zh` | 中文模板 |

### 权重提示

`t1_protocol` 和 `t2_protocol` 都接受可选的 `weight_hint` 参数来调整评估标准：

| 权重 | 效果 |
|------|------|
| `事实优先` / `fact-first` | 优先考虑事实准确性 |
| `效率优先` / `efficiency-first` | 优先考虑效率 |
| `成本优先` / `cost-first` | 优先考虑成本 |
| `鲁棒性优先` / `robustness-first` | 优先考虑鲁棒性 |
| `通用优先` / `general-first` | 无特定偏好 |

### 递归保护

T2 自动检测递归深度，当深度 ≥ 3 时自动终止，此时边际信息增益低于 5%。

## 设计理念

详见 [docs/philosophy.zh.md](docs/philosophy.zh.md)。

核心原则：

1. **智能与信任分离** — AI 的能力和 AI 的安全性应由不同系统保证
2. **异构优于自指** — 跨模型的交叉验证比自我反思更可靠
3. **确定性优于概率性** — 能由代码检查的，不应交给模型判断

## 示例

见 [examples/](examples/) 目录的分步指南：

- [T1：结构化一个模糊问题](examples/t1-basic.zh.md)
- [T2：交叉验证一个决策](examples/t2-basic.zh.md)
- [全链路：T1 → 决策 → T2](examples/full-pipeline.zh.md)

## 生态定位

| 项目 | 层级 | 作用 | 与 T1/T2 的关系 |
|------|------|------|----------------|
| [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)（官方 MCP） | 调用方思维链 | 单模型逐步记录思考 | 互补 — T1 增加 L1–L4 分级 + T2 跨模型复核 |
| [ThoughtProof](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2574) / 裁决 API | 服务端验证 | `APPROVE`/`DENY`/`UNCERTAIN` + 置信度 | 互补 — T1/T2 在裁决 API 之前结构化推理 |
| 自我反思 / Prompt chains | 同模型 | 重读或重 prompt 自身输出 | 替代 — 异构验证覆盖共同盲区 |
| 工具完整性（如 Phionyx） | 传输 / schema | 检测 tool poisoning、schema 漂移 | 正交 — T1/T2 不保护工具定义 |

T1/T2 是面向 [MCP Discussion #2574](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2574) 推理纪律的 **stdlib 参考实现**：先结构化（T1），再交叉验证（T2），代码能校验的走 checksum。它不是签名裁决 API，也不是安全扫描器。

## 版本号

两套编号，请勿混用：

| | 示例 | 含义 |
|---|------|------|
| **包版本**（PyPI） | `0.1.0` | 分发生命周期。`0.x` = 实验期（[SemVer](https://semver.org/lang/zh-CN/)，[FastAPI 策略](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/deployment/versions.md)）。 |
| **协议版本**（规格） | `v2.5` | T1/T2 工具语义（server 输出 footer）。调用方 Web 验证文档为 `v2.6`。 |

推荐安装：`pip install "t1-t2-protocol>=0.1.0"`。错误的 PyPI 版本 `2.5.2`–`2.5.4` 已 yank。

## 许可证

Apache License 2.0 — 详见 [LICENSE](LICENSE)。

---

*为 MCP 生态而建。是对通过确定性架构实现 AI 安全这一更广泛探索的一部分。*

---

## 链接

- [参与贡献](CONTRIBUTING.md)
- [安全策略](SECURITY.md)
- [更新日志](CHANGELOG.md)
- [设计哲学](docs/philosophy.zh.md)
- [调用方 Web 验证 v2.6](docs/caller-protocol.zh.md)
- [Agent / MCP 主机说明](AGENTS.md)

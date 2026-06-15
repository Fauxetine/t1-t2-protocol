# 调用方 Web 验证（v2.6）

## 动机

T2 协议评估答案置信度。但若答案含有时效性事实，**模型内部知识可能已过时** — 基于陈旧数据的高置信评估同样不可靠。

解决方案是 **调用方 Web 验证**：在调用 `t2_protocol` 之前，用实时 Web 来源核对事实性断言。

## 架构

```
┌─ 调用方（Cursor、Claude Desktop、你的脚本）
│  ← Agent-Reach / Jina / Brave Search → 实时 Web
│  ← t2_protocol → MCP 服务器（无网络访问）
```

- **Web 搜索留在 Layer 2**（调用方、Agent-Reach、Jina 等）
- **T2 评估留在 Layer 0**（MCP 服务器，stdlib，无网络）
- 此分离是刻意的 — 见 [philosophy.zh.md](philosophy.zh.md)

## 何时验证

| T2 前需验证 | 可跳过 |
|------------|--------|
| 工具/库当前状态 | 纯逻辑推理 |
| 近期研究/事件 | 架构设计评估 |
| 价格/市场数据 | 本地探针 / 结构化工具输出 |
| 任何带时间戳的事实断言 | 基础数学 |
| 可能已过时的先前结论 | — |

## 实现

这是 **调用方约定**，不是 MCP 代码。T1/T2 服务器本身从不发起网络请求。

**Cursor** — 在 `.cursor/rules/` 中添加规则，例如：

```
AlwaysApply: true
在调用 t2_protocol 前，若话题涉及时效性事实，先通过 Web 搜索核实
```

**Claude Desktop** — 在 prompt 约定中加入：

```
Before calling t2_protocol, if the answer contains factual claims that
may be time-sensitive, search the web for current information first.
```

## 为何不内置到 MCP 服务器？

1. **层级分离**：MCP 属于 Layer 0（stdlib、确定性）。Web 搜索属于 Layer 2（网络、第三方 API）。
2. **搜索工具选择**：不同用户偏好不同后端（Agent-Reach、Brave、Tavily、Jina），服务器不应强制一种。
3. **离线兼容**：服务器应无网可用。调用方验证是可选的 — 服务器不依赖它。

## 参见

- [设计哲学](philosophy.zh.md)
- [T1 规范](../README.zh.md)
- [T2 规范](../README.zh.md)
- [English version](caller-protocol.md)

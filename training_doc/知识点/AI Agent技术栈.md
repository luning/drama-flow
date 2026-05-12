# AI Agent 技术栈：从 LLM 到 Agent 的分层架构

## 目录

1. [我们感知到的 Agent](#我们感知到的-agent)
2. [为什么需要分层？](#为什么需要分层)
3. [一张图看清全貌](#一张图看清全貌)
4. [重要前提：同一架构，两种实现形态](#重要前提同一架构两种实现形态)
5. [Context OS（上下文操作系统）](#context-os上下文操作系统)
   - [Agent 怎么调用 Context OS？](#agent-怎么调用-context-os)
   - [三类 context，三个最合适的主体来管](#三类-context三个最合适的主体来管)
   - [三层分工总结](#三层分工总结)
6. [Execution Runtime（执行运行时）](#execution-runtime执行运行时)
   - [个人场景：确实不需要独立 Runtime](#个人场景确实不需要独立-runtime)
   - [组织场景：核心基础设施](#组织场景核心基础设施)
   - [Agent 怎么调用 Execution Runtime？](#agent-怎么调用-execution-runtime)
7. [Model Router（模型路由）](#model-router模型路由)
8. [LLM Provider（推理引擎）](#llm-provider推理引擎)
9. [关键结论](#关键结论)

---

## 我们感知到的 Agent

Claude Code、Cursor、Cline——这些是大多数人第一次真正"使用" Agent 的方式。它不只是一个聊天窗口，而是能够多步骤规划、自主调用工具、反思纠错、持续执行，直到任务完成。

| 普通 LLM 调用 | Agent |
|-------------|-------|
| 一次 prompt → 一次 response | 多步推理 → 多次行动 |
| 无法主动获取信息 | 调用 shell / git / browser / API |
| 无状态 | 有记忆、有上下文 |
| 人在循环中 | 可以自主决策 |

**核心能力**：Planning（任务分解）· Tool Calling（工具调用）· Reflection（自我修正）· Multi-step Execution（多轮执行）

但 Agent 能做到这些，背后依赖一套分层的基础设施。接下来要回答的问题就是：**这些能力从何而来，各层之间如何协作？**

---

## 为什么需要分层？

很多人以为"接入 GPT/Claude API"就等于有了 AI 产品。但真正能在生产环境中工作的 AI 系统，远比一次 API 调用复杂。

理解 AI Agent 的技术栈，本质上是回答一个问题：

> **一个 AI 要完成真实任务，需要哪些"基础设施"？**

---

## 一张图看清全貌

```
┌──────────────────────────────────┐
│            Agent 层              │  ← AI 员工：思考、规划、行动
├──────────────────────────────────┤
│          Context OS 层           │  ← AI 记忆：知道什么、该知道什么
├──────────────────────────────────┤
│       Execution Runtime 层       │  ← AI 执行环境：安全、可控、可治理
├──────────────────────────────────┤
│         Model Router 层          │  ← 调度层：用对模型、控制成本
├──────────────────────────────────┤
│         LLM Provider 层          │  ← 推理引擎：真正产生智能
└──────────────────────────────────┘
```

每一层解决完全不同的问题。下面自上而下逐层介绍。

---

## 重要前提：同一架构，两种实现形态

这个分层是**概念架构**，不是物理部署图。同样的五层，在不同规模下对应截然不同的实现：

```
     个人助手（增强 IDE）              企业数字员工
  ┌──────────────────────┐
  │       Agent 产品      │         Agent · Agent · Agent
  │  Context OS（内置）   │               ↓
  │  Execution Runtime   │    ┌─────────────────────────┐
  │  （本地 OS）          │    │  Context OS 服务（共享）  │
  │  Model Router（无）   │    │  Execution Runtime 平台  │
  └──────────────────────┘    │  Model Router 网关       │
            ↓                 └─────────────────────────┘
      LLM Provider API                  ↓
                                  LLM Provider
```

| 维度 | 个人助手 | 企业数字员工 |
|------|---------|------------|
| Agent 的本质 | 用户工具，风险由用户自己承担 | 组织劳动力，风险由组织承担 |
| 其余各层的实现 | 内嵌在 Agent 产品内部 | 独立服务，可跨多个 Agent 共享 |
| 关注重点 | 使用体验、能力 | 治理、安全、可审计、成本控制 |

**为什么大家容易混淆？** 目前大多数人用的还是个人 Agent，却在讨论组织级基础设施——对个人场景说"你需要 Execution Runtime"，确实是在过度工程化。

---

## Context OS（上下文操作系统）

**解决什么问题**：Agent 怎么得到它需要知道的东西？

LLM 的上下文窗口是有限的，Agent 不可能每次把所有信息塞进 prompt。Context OS 负责管理 AI 的"记忆"——按需检索、注入相关上下文、跨 session 保持状态。

### Agent 怎么调用 Context OS？

```
Agent 收到任务："帮我 review 这段认证代码"
         ↓
Agent 向 Context OS 查询：
  ├─ 检索相关文档：我们的认证系统架构是什么？（RAG）
  ├─ 读取项目约定：这个项目有什么规范和约束？（CLAUDE.md / 规范文档）
  └─ 调取历史记忆：上次类似 review 发现了什么？（Memory）
         ↓
Context OS 返回相关片段（不是全部，只取相关的）
         ↓
Agent 将这些 context 加入推理窗口，开始工作
```

每次 Agent 开始新任务，或者需要特定知识时，都会主动向 Context OS 查询。任务结束后，Agent 也可以向 Context OS 写入新的记忆，供下次使用。

### 三类 context，三个最合适的主体来管

Context OS 不是单一的层，而是三类问题各有最合适的负责方。判断原则：

> **只有"共享收益 > 协调成本"时，独立的中间层才有存在价值。**

**第一类：Agent 自己管——当前任务 context**

当前任务的状态、当前 repo 的理解、当前 session 的规划历史——这些高度动态、高度私有，Agent 自己管最合适。Claude Code 的 CLAUDE.md 和 memory 文件、Cursor 的 `.cursorrules` 和代码索引，都属于这一类。

**第二类：企业内部平台——组织私有 context**

有一类 context 不属于某个 Agent，而属于整个组织：私有代码库 graph、内部文档、Jira/飞书/Slack 数据、内部 API schema……

特点：**在企业内跨 Agent 共享价值极大，但不能流出企业边界**。

企业内部统一建设 Context OS，所有 Agent 共享访问——同时在这一层实现**访问控制边界**：销售 Agent 可以查客户合同，但不该看薪酬数据；客服 Agent 能读产品手册，但不该接触财务报表。

**第三类：跨企业共享 infra——世界级 context**

全球每个 Agent 每天都在重复"理解" React、Kubernetes、LangChain、AWS CDK……这些是全世界共享的开源知识，却被每个 Agent 从零重新学习，浪费大量 token 和计算成本。

适合在这一层共享的内容：开源框架语义图谱、Package 依赖关系图、GitHub 开源项目索引、API schema 地图——高重复、高计算成本、与私有数据弱相关。

这一层的类比是**搜索引擎**：未来最贵的不是模型推理，而是"找到真正相关的上下文"——可以理解为面向 AI 的 **Context CDN**。

### 三层分工总结

```
主体           负责的 context        核心问题
──────────────────────────────────────────────
Agent 自身     当前任务              效率（当前 session）
企业内部平台   组织私有知识          效率 + 权限（跨 Agent 共享）
跨企业 infra   世界级公共知识        成本（消除全球重复学习）
```

---

## Execution Runtime（执行运行时）

**解决什么问题**：Agent 安全、可控地执行操作。

### 个人场景：确实不需要独立 Runtime

在本机用 Claude Code 或 Cursor，`shell.exec()` 直接执行，Docker 本来就有隔离，浏览器就是你自己的。独立搭一套 Runtime 平台是过度工程化——因为**你是风险承担者**，`rm -rf` 删的是你自己的文件。

### 组织场景：核心基础设施

一旦 Agent 成为"数字员工"，操作的是企业共享资源（生产数据库、内网 API、CI/CD、GitHub org……），问题就变了：**最怕的不是技术执行失败，而是权限与行为失控。**

五类真实风险：

| 风险 | 场景 |
|------|------|
| 并发冲突 | 10 个 Agent 同时 `git push` 同一仓库 |
| 误调生产 | Agent 判断"清理测试数据"，结果调了 `delete_all_orders()` |
| 数据泄露 | 浏览器 Agent 把内部合同作为上下文发给外部 LLM |
| 资源失控 | Agent 陷入循环，不断 `docker run` 耗尽服务器 |
| 无法审计 | "谁改了生产配置？" 是 Agent 改的，但没有任何日志 |

### Agent 怎么调用 Execution Runtime？

Agent 不直接调用系统资源，而是通过 Runtime 提供的接口发起操作请求。Runtime 在中间充当"执行代理"：

```
Agent 决定执行一个操作
  "我需要运行：DELETE FROM orders WHERE status='test'"
         ↓
提交给 Execution Runtime
         ↓
Runtime 执行检查：
  ├─ 身份检查：这个 Agent 有数据库写权限吗？
  ├─ 策略检查：这类操作需要人工二次确认吗？
  └─ 范围检查：这是生产库还是测试库？
         ↓
通过 → 执行操作 + 写入审计日志 → 返回结果给 Agent
拒绝 → 返回错误信息 + 通知管理员
```

这就是 Execution Runtime 的核心价值：Agent 的每一个操作都经过它，任何"不该发生的行为"在这一层被拦截，任何"已发生的行为"都有日志可查。

**个人 Agent 里同样有这个角色**——Claude Code 在执行 shell 命令前弹出确认框，就是最简单的 Runtime：它在 Agent 和操作系统之间加了一层"你确定吗？"。只不过个人场景里这一层非常轻量，无需独立建设。

> 核心认知：不是"AI 能不能执行"，而是**"组织是否允许 AI 执行，以及如何对执行负责"**。

---

## Model Router（模型路由）

**解决什么问题**：调用哪个模型最合适？

不同任务用不同模型，可以大幅降低成本、提升效果。

| 任务类型 | 推荐模型 |
|---------|---------|
| 简单问答、分类 | Gemini Flash（快且便宜） |
| 代码生成 | Claude / GPT-4 |
| 深度推理 | Claude Opus |
| 超长上下文 | Gemini 1.5 Pro |

个人 Agent 通常直接硬编码调某个模型，不需要独立 Router。企业场景变成统一 AI Gateway（如 LiteLLM、Azure AI Gateway），集中管控成本和访问策略，所有 Agent 都通过它访问模型。

---

## LLM Provider（推理引擎）

**解决什么问题**：谁来产生智能？

LLM Provider 是整个系统的认知底座，负责文本理解、推理、代码生成。这些能力的技术实现（Transformer、KV Cache、GPU 调度）完全由 Provider 控制，外部无法插手。

**代表厂商**：OpenAI · Anthropic · Google Gemini · Meta Llama

---

## 关键结论

> **真正难的越来越不是"让 AI 说一句聪明的话"，而是"让 AI 在真实世界中长期、低成本、可治理地工作"。**

这正是 Context OS 和 Execution Runtime 的核心价值：它们解决的是 AI 从"演示"走向"生产"的工程挑战，而这些挑战只有在 Agent 从个人工具变成组织级数字劳动力之后，才会真正浮现。

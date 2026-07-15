# Agentic Harness Engineering - 让 Harness 自主进化

## 目录

1. [核心概念：Harness 的七个组件](#核心概念harness-的七个组件)
2. [为什么 Harness Engineering 是瓶颈](#为什么-harness-engineering-是瓶颈)
   - [手工工程化的极限](#手工工程化的极限)
   - [自动演化面临的三重障碍](#自动演化面临的三重障碍)
3. [AHE 原理：三支柱可观测性驱动的自动演化](#ahe-原理三支柱可观测性驱动的自动演化)
   - [支柱 1：组件可观测性（Component Observability）](#支柱-1组件可观测性component-observability)
   - [支柱 2：经验可观测性（Experience Observability）](#支柱-2经验可观测性experience-observability)
   - [支柱 3：决策可观测性（Decision Observability）](#支柱-3决策可观测性decision-observability)
4. [演化循环：从失败轨迹到可验证改进](#演化循环从失败轨迹到可验证改进)
   - [外层循环（Algorithm 1）](#外层循环algorithm-1)
   - [案例分析：db-wal-recovery 任务](#案例分析dbwalrecovery-任务)
   - [组件层级选择](#组件层级选择)
5. [关键实验发现](#关键实验发现)
   - [主实验：AHE 超越人工设计和自动化基线](#主实验ahe-超越人工设计和自动化基线)
   - [跨基准转移：Harness 具备通用性](#跨基准转移harness-具备通用性)
   - [跨模型转移：+5.1 到 +10.1 pp](#跨模型转移51-到-101-pp)
   - [组件消融：增益在哪？](#组件消融增益在哪)
   - [自归因的可靠性](#自归因的可靠性)
6. [在 Claude Code 中走向 Harness 自动演化](#在-claude-code-中走向-harness-自动演化)
   - [可观测性基础：Session JSONL](#可观测性基础session-jsonl)
   - [演化闭环](#演化闭环)
   - [举个例子](#举个例子)
   - [成熟度](#成熟度)
   - [实操建议](#实操建议)

---

## 核心概念：Harness 的七个组件

AHE 论文在 NexAU 框架上将 Harness 解耦为七个正交的组件类型，每个都以独立文件的形式存在：

| 组件 | 文件 | 作用 | 约束层级 |
|------|------|------|----------|
| **System Prompt**（系统提示词） | `systemprompt.md` | 行为规则、工作流指导，适用于所有任务 | 最弱（建议性） |
| **Tool Description**（工具描述） | `tool_descriptions/*.tool.yaml` | 解释工具用法、参数含义、注意事项 | 弱（文档性） |
| **Tool Implementation**（工具实现） | `tools/` | 控制工具的实际执行行为 | 强（执行级） |
| **Middleware**（中间件） | `middleware/` | 挂入 agent 循环管线，拦截/转换输入输出 | 强（管线级） |
| **Skill**（技能） | `skills/` | 按需加载的可复用工作流模式 | 中（注入式） |
| **Sub-Agent**（子代理） | `sub_agents/` | 隔离上下文的委派执行单元 | 强（隔离级） |
| **Long-Term Memory**（长期记忆） | `LongTermMEMORY.md` | 跨会话持久化的经验教训 | 中（参考性） |

**关键设计原则**：组件之间是**松耦合**的——添加一个 middleware 不需要修改 system prompt，添加一个 skill 不影响任何 tool。这种解耦使得每个失败模式可以清晰地映射到单一组件，演化 agent 可以精确地在正确的层级上做修改。

[论文：Section 3.1, Appendix B.1-B.2]

研究表明，**即使在基础模型不变的情况下，Harness 设计的差异可以在长时间任务基准测试上产生显著的得分差异**。而且，最优的 Harness 是**模型特定的（model-specific）**：为一个基础模型调优的 Harness，换一个模型往往表现下降，需要重新适配。

---

## 为什么 Harness Engineering 是瓶颈

### 手工工程化的极限

当前实践中，Harness 的调优几乎全靠**人工**：
1. 开发者检查运行轨迹（trajectory）
2. 识别重复出现的失败模式
3. 手工修改 prompt、工具或中间件
4. 重新运行验证

但随着基础模型快速迭代（每个月都有新模型发布），手工循环根本跟不上节奏，形成"模型能力提升 → Harness 跟不上 → 新模型的实际效果被 Harness 拖累"的困境。

### 自动演化面临的三重障碍

如果用另一个 Agent 来自动优化 Harness，会遇到三个结构性难题：

| 难题 | 说明 | AHE 的解法 |
|------|------|-----------|
| **异质动作空间** | 可编辑的组件类型不同（prompt 是文本，tool 是代码，middleware 是 Python 类），动作空间的表示不统一 | **组件可观测性**：每个组件都变成文件，git diff 就是动作记录 |
| **轨迹信息淹没** | 一次运行产生数百万 token 的原始轨迹，其中只有极少数是有用信号 | **经验可观测性**：分层蒸馏，从原始轨迹 → 单任务分析 → 基准概览 |
| **效果难以归因** | 修改了 prompt 后得分涨了，到底是因为这条修改还是因为随机波动？ | **决策可观测性**：每次修改附带自声明的预测，下一轮验证 |

这三个障碍的本质，正如论文的核心洞察所言：

> **"瓶颈在于可观测性（observability），而非 agent 能力。"**
>
> 一旦演化 agent 获得了结构化上下文和清晰的动作空间，它就能可靠地收敛到更好的 Harness 设计。

---

## AHE 原理：三支柱可观测性驱动的自动演化

![AHE 三支柱可观测性](../images/AHE_pipeline.png)

AHE（Agentic Harness Engineering）的核心设计理念是：**演化循环的每个阶段都必须是可观测的**。这通过三个可观测性支柱实现。

### 支柱 1：组件可观测性（Component Observability）

**做法**：将 Harness 的七个组件类型全部暴露为文件系统中的显式文件，每个逻辑修改对应一次 git commit。

**效果**：
- 失败模式 → 单一组件类的映射路径清晰
- 每次得分变动归因到具体文件，而非散落在数百行非结构化的 prompt 文本中
- Git 历史提供了文件级 diff 和回滚粒度

**种子 Harness（H₀）的设计哲学**：刻意极简——只有一个 shell 执行工具，没有 middleware，没有 skills，没有 sub-agents。这是为了**避免种子本身污染归因**：如果种子已经很适配目标基准，就无法分辨增益来自演化循环还是来自种子本身。

### 支柱 2：经验可观测性（Experience Observability）

**做法**：用 Agent Debugger 将百万 token 的原始轨迹蒸馏为分层、可下钻的证据语料。

蒸馏管线：

```
原始轨迹 (~10M tokens)
    ↓ 清洗：去掉 base64、去重工具输出
清洗后轨迹 (~1M tokens)
    ↓ Agent Debugger：用 agent 分析轨迹，寻找根因
单任务分析报告 (per-task analysis)
    ↓ 聚合
基准级概览 (benchmark-level overview)
```

**Agent Debugger 的工作方式**：把每条轨迹消息放进独立文件，形成可导航的文件系统环境。Debugger agent 通过通用的 shell 和脚本工具访问轨迹，分析失败根因或成功模式，生成结构化的分析报告。

**渐进式信息披露（Progressive Disclosure）**：概览 → 详细分析 → 原始轨迹，按需下钻，节省 token 消耗。

### 支柱 3：决策可观测性（Decision Observability）

**做法**：Evolve Agent 的每次修改都附带一个 **change manifest**（变更清单），包含：

```json
{
  "id": "chg-1",
  "description": "修改了什么，为什么",
  "failure_pattern": "要解决的失败模式",
  "predicted_fixes": ["应该修复的任务A", "任务B"],
  "risk_tasks": ["可能被破坏的任务C"],
  "constraint_level": "middleware|tool_impl|tool_desc|skill|prompt"
}
```

**下一轮验证**：将预测的修复/回归集合与实际观测到的任务级 delta 做交集，生成每条修改的裁决：
- ✅ 预测的修复实际出现了 → 保留
- ❌ 预测的修复没出现 / 预测的回归出现了 → **回滚**

**关键约束**：
- **Controllability（可控性）**：Evolve Agent 只能写 `workspace/` 目录；runs/、LLM 配置、验证器都是只读的
- **Evidence-driven（证据驱动）**：每条修改必须追溯到具体的失败证据，禁止基于直觉的"最佳实践"式修改

> **这为什么重要？** 在没有决策可观测性的情况下，自动演化容易退化为 trial-and-error —— agent 不断随机尝试修改，偶尔运气好得分涨了就保留。AHE 让每次修改都变成**可证伪的合约**（falsifiable contract），无效修改会被自动发现和回滚。

[论文：Section 3, Algorithm 1, Appendix B.2]

---

## 演化循环：从失败轨迹到可验证改进

### 外层循环（Algorithm 1）

```
迭代 t = 1, 2, ..., N:
  Phase 1: 用当前 Harness H_{t-1} 跑 k 次 rollout（k≥2，per task）
  Phase 2: 清洗轨迹（去 base64、去重）
  Phase 3: 归因上一轮的 change manifest，回滚无效修改
  Phase 4: Agent Debugger 蒸馏轨迹 → 分层证据语料
  Phase 5: Evolve Agent 读证据 → 编辑 workspace → 输出新 manifest
  Phase 6: Git commit，记录迭代快照
  保留 best-so-far
```

### 案例分析：db-wal-recovery 任务

**任务**：从损坏的 SQLite WAL 文件中重建数据库表。

**演化前的失败轨迹**（种子 Harness，得分 0）：
1. 从过时的 shell 缓冲区读取 WAL 字节
2. 只看到 5 行数据，猜测缺失的 6 行遵循 `value = id × 100` 的模式
3. 提交了凭空编造的数据
4. 自我检查只数了行数（"json length == 11"），而非对照真实验证器

**演化后的修改 (chg-1)**：在 system prompt 中追加 8 条通用规则，包括：
- "Contract first"：测试和验证器脚本是真相的来源，不是 shell 历史
- "Generalize, do not overfit"：不要从可见样本推断
- "Mirror the evaluator"：用验证器断言做最终检查

**演化后的成功轨迹**（同一随机种子，得分 1.0）：
1. 重新逐字阅读任务规格，"WAL changes"被理解为对现有行的**修改**
2. 从原始磁盘恢复 WAL 文件
3. 正确解析所有 11 行，包括被修改的行（value=150 而非 100）
4. 最终验收步骤完全镜像了验证器的断言

**关键点**：修改的 prompt 中没有提"SQLite"、"WAL"、"db-wal-recovery"这些具体词——AHE 提取的是**通用工程经验**，而非任务特定的 hack。

### 组件层级选择

分析失败模式后，选择正确的组件层级来修复：

| 失败模式 | 错误层级 | 正确层级 | 原因 |
|----------|---------|---------|------|
| agent 在验收后删除交付物 | prompt 规则 | **tool 实现** | prompt 建议挡不住执行；需要在 shell 工具中做硬拦截 |
| agent 忽略 risk 警告 | middleware（after_tool） | **middleware（before_model）** | 警告跟在 tool output 后面，模型在下一轮看不到；需要注入到 reasoning context |
| agent 使用简陋的自检替代验证器 | prompt | **middleware** | 需要跨步骤状态追踪来检测"你用行数检查替代了字段断言" |

**约束层级**（从强到弱）：

> Tool Implementation > Middleware > Skill > Tool Description > System Prompt

[论文：Section 3, Appendix C]

---

## 关键实验发现

### 主实验：AHE 超越人工设计和自动化基线

在 Terminal-Bench 2（89 个任务）上，10 轮 AHE 迭代（约 32 小时）：

| 方法 | 总得分 | Easy | Medium | Hard |
|------|--------|------|--------|------|
| Codex CLI（人工设计） | 71.9% | 75.0% | 80.0% | 56.7% |
| NexAU 0（种子） | 69.7% | 87.5% | 78.2% | 51.7% |
| ACE（自动演化，仅 prompt） | 68.9% | 91.7% | 78.2% | 48.9% |
| TF-GRPO（自动演化） | 72.3% | 100.0% | 79.4% | 55.6% |
| **AHE** | **77.0%** | **100.0%** | **88.2%** | 53.3% |

> ACE 和 TF-GRPO 只能编辑 prompt / skill，无法触及 tools、middleware、memory——而这些正是增益所在的组件层。

### 跨基准转移：Harness 具备通用性

在 SWE-bench-verified（500 个真实 GitHub issue）上，**无需重新演化**：

| 指标 | ACE | TF-GRPO | NexAU 0 | **AHE** |
|------|-----|---------|---------|---------|
| 成功率 | 74.6% | 74.2% | 75.2% | **75.6%** |
| Token 消耗 | 679k | 582k | 526k | **461k**（-12%） |

AHE 不仅在成功率上领先，而且**平均节省 12% token**——因为它在 tools/middleware/memory 中编码行为，避免每次调用都重新推导。

### 跨模型转移：+5.1 到 +10.1 pp

AHE Harness 在不同的基础模型上（不做任何调整）都能带来正向提升：

| 基础模型 | NexAU 0 种子 | 使用 AHE Harness | 增益 |
|----------|-------------|-----------------|------|
| deepseek-v4-flash | 51.7% | 61.8% | **+10.1 pp** |
| qwen-3.6-plus | 56.2% | 62.5% | **+6.3 pp** |
| gemini-3.1-flash-lite | 36.5% | 41.6% | **+5.1 pp** |
| GPT-5.4 high | 69.7% | 77.0% | **+7.3 pp** |

**规律**：能力离饱和越远的基础模型，从 AHE Harness 中获益越大——因为弱模型更需要 Harness 中编码的协调模式。

### 组件消融：增益在哪？

逐组件拆解 AHE 的贡献：

| 变体 | 总得分 | 相对种子 |
|------|--------|---------|
| NexAU 0 种子 | 69.7% | — |
| + memory only | 75.3% | **+5.6 pp** |
| + tool only | 73.0% | **+3.3 pp** |
| + middleware only | 71.9% | **+2.2 pp** |
| + system_prompt only | 67.4% | **-2.3 pp** ❌ |
| AHE 全量 | 77.0% | +7.3 pp |

**核心发现**：
1. **增益在 tools、middleware、long-term memory**，不在 system prompt
2. System prompt 单独使用反而退步（-2.3 pp）：prose 层的策略不具备可转移性
3. 组件之间**非加性交互**：三个正组件单独增益之和为 +11.1 pp，但全量只有 +7.3 pp（部分效果重叠，甚至互相干扰）

> **结论**：**事实性的 Harness 结构（工具做什么、中间件怎么拦截）可以跨任务和跨模型转移，而散文式的策略指导（prompt 写什么）不能。**

### 自归因的可靠性

Evolve Agent 的自声明预测准确度：

| 维度 | 精确率 | 召回率 | 随机基线 |
|------|--------|--------|---------|
| 修复预测（fix） | **33.7%** | **51.4%** | 6.5% / 10.6% |
| 回归预测（regression） | 11.8% | 11.1% | 5.6% / 5.4% |

- 修复预测约 5 倍于随机基线：agent 确实能基于证据定位问题，而非瞎猜
- **回归预测近乎瞎蒙**：agent 能解释为什么修改应该有效，但无法预测哪些任务会被意外破坏

这指出未来方向：**回归预见能力（regression foresight）是自动演化循环最明确的前沿**。

[论文：Section 4, Table 1-3, Figure 3-4]

---

## 在 Claude Code 中走向 Harness 自动演化

AHE 的核心主张是 Harness 可以成为一个可观测、可自动演化的适应层。Claude Code 已经具备跑通这个闭环的基础设施，本章给出大致思路和关键细节。

### 可观测性基础：Session JSONL

Claude Code 每次会话都会在 `~/.claude/projects/<项目名>/` 下保存结构化日志 `<session-id>.jsonl`，每行一条 JSON，记录该轮的 message、tool call 及 tool result。这是自动化演化的数据起点。

从 JSONL 中可直接提取的信号：

- `tool_result` 中 `is_error: true` → 工具调用失败
- 同一 tool call 连续出现 ≥3 次 → agent 陷入无效重试循环
- `Stop` / `PreToolUse` hook 的触发记录 → 拦截事件
- session 有 task 描述但无完成标记 → 任务提前终止

这些信号几行 `jq` 或 Python 就能批量扫描，不需要人工翻日志。

### 演化闭环

```
近 N 天 JSONL → 脚本提取失败信号 → 聚合为失败模式（频次、类型）
    → LLM 批量分析根因 + 推荐修复层级
    → 生成 harness 变更（修改 settings.json / CLAUDE.md / skill）
    → 人工确认后应用
    → 继续采集新 session 日志，对比修改前后同一失败模式的频次变化
```

关键细节：

- **失败提取**：Python 脚本遍历 JSONL 目录，按 `is_error`、连续重复 tool call、hook 类型打标签，输出按频次排序的失败模式列表。
- **根因分析**：把聚合后的失败模式 + 典型 JSONL 片段喂给 LLM，让它判断每个失败适合在 prompt / skill / hook / tool 哪一层修复。
- **效果验证**：对比变更前后各 7 天的 session 日志，目标失败模式频次下降 → 保留；不变或上升 → 回滚换层级。

### 举个例子

agent 频繁在 `npm install` 失败后仍继续 `npm run build`，最终 build 也失败，浪费 token。

- 脚本发现该模式在过去 10 个 session 中出现 7 次。
- LLM 分析判断：最适合用 PreToolUse hook 拦截 — 在 agent 执行 `npm run build` 前检查上一步 `npm install` 的 exit code。
- 生成 hook 配置，确认后应用。一周后对比：频次从 7/10 降到 1/10。

### 成熟度

| 能力 | 做法 |
|------|------|
| JSONL 解析 + 失败统计 | Python 脚本遍历，`jq` 预处理也行 |
| 变更前后频次对比 | 按时间段拉两个 batch 做 diff |
| LLM 批量根因分析 | 聚合失败片段喂给 LLM，输出修复建议 |
| 自动生成 harness 变更 | 脚本生成 diff，人工确认 |
| 全自动闭环 | 需要回归预见能力（前沿方向），避免修 A 坏 B |

### 实操建议

- **先攒数据**。确保 session 日志积累到几十个再分析，数据太少偏差大。
- **先跑只读闭环**。第一步只做分析脚本，输出"Top 3 高频失败模式 + 推荐层级"。跑通了再考虑自动应用。
- **每次变更记录预测**。commit message 里写一句"预计减少 X 类失败"，验证时对号入座。
- **一个失败模式只在一个层级修**。多层冗余不加增益只加 token。同一层级连修两次没效果，果断换层级。

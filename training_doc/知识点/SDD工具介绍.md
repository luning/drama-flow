# SDD 工具全景

## 目录

1. [为什么需要 SDD 工具？](#为什么需要-sdd-工具)
   - [从 Vibe Coding 到 SDD](#从-vibe-coding-到-sdd)
   - [为什么需要工具？](#为什么需要工具)
2. [SDD 工具的核心能力框架](#sdd-工具的核心能力框架)
   - [上下文策略](#上下文策略)
   - [执行深度](#执行深度)
   - [平台集成](#平台集成)
3. [主流 SDD 工具详解](#主流-sdd-工具详解)
   - [GSD（Get Shit Done）](#gsdget-shit-done)
   - [OpenSpec（Fission AI）](#openspecfission-ai)
   - [Spec Kit（GitHub）](#spec-kitgithub)
   - [Kiro（AWS）](#kiroaws)
   - [Taskmaster AI](#taskmaster-ai)
   - [SDD 生态中的其他代表性工具](#sdd-生态中的其他代表性工具)
   - [快速上手指南对比](#快速上手指南对比)
4. [核心维度对比](#核心维度对比)
   - [执行哲学对比](#执行哲学对比)
5. [各工具适用场景](#各工具适用场景)
6. [总结](#总结)
7. [参考资料](#参考资料)

---

## 为什么需要 SDD 工具？

### 从 Vibe Coding 到 SDD

2025 年 AI 辅助编码已成为主流，但"聊天式编程"（Vibe Coding）在小型 Demo 或一次性脚本中效率惊人，在以下场景中迅速失效：

- **跨模块改造**：改一个 API 涉及前端、后端、数据模型，AI 容易遗漏依赖
- **存量系统维护**："不要破坏已有功能"的约束比"实现新功能"更难传达
- **团队协作**：不同开发者用不同的 Prompt 风格，产出质量方差极大
- **长上下文衰减**：多轮对话后 AI 忘记早期决策，产生不一致代码

**Spec-Driven Development（SDD）** 的核心思想是：**在编码之前，先把"怎么做才算完成"写清楚**。这一思想并不新——BDD、TDD、ATDD 都是它的前身。SDD 的不同之处在于，规格不再仅仅是供人阅读的文档，而是**直接驱动 AI Agent 行为的可执行工件**。

### 为什么需要工具？

早期团队的"Prompt SDD"做法是：在 CLAUDE.md 中写一段约束，要求 Agent 每次任务前阅读 SPEC.md。这种做法有效，但有三个局限：

| 局限 | 表现 | 后果 |
|------|------|------|
| **约束易遗漏** | 只靠 Prompt 提醒，Agent 可能在复杂任务中跳过自检 | AC 覆盖率下降 |
| **AC 无法自动化验证** | 人工逐条对照，耗时且容易疲劳 | 验收流于形式 |
| **Traceability 缺失** | 做了哪些变更、对应哪个 AC、是谁批准的，没有记录 | 审计困难 |

SDD 工具正是为解决这些问题而生——它们将规格从**文本**升级为**可执行的流程单元**，提供结构化的变更管理、自动化验证和上下文隔离。

在引入工具之前，最简单的起点是在 CLAUDE.md 中写入 SDD 约束：

```markdown
## SDD 最小约束
1. 接受任务前，先阅读对应模块的 SPEC.md 中的验收标准
2. 生成代码后，逐条自检 AC，确保所有验收标准被覆盖
3. 修改已有 AC 时标注变更记录，保留历史意图
```

这种"Prompt SDD"零成本、立即生效，但依赖 Agent 自觉性。当遇到以下信号时，是引入工具的时机：

- Agent 跳过了 AC 自检，改完才发现遗漏
- 改了一处影响了另一处，没有任何记录
- 多人并行修改互相干扰，没有隔离机制
- 长任务中 Agent 忘记了早期决策

工具本身也不必全量使用——遇到具体痛点，用对应命令解决即可。在 DramaFlow 课程中：迭代 1 使用 Prompt SDD，迭代 2 引入 OpenSpec（从 `/opsx:new` 开始），迭代 3 引入 GSD（从 `/gsd:discuss-phase` 开始）。

---

## SDD 工具的核心能力框架

所有 SDD 工具都围绕一个基本循环构建：

```
讨论/探索 → 规划 → 执行 → 验证 → 归档
```

在这个循环基础上，不同工具在以下维度上产生分化：

### 上下文策略

这是 SDD 工具最核心的技术差异，也是区分工具能力的关键指标：

- **新鲜上下文隔离**（GSD 代表）：每次执行从项目工件重新构建上下文，而非累积聊天历史。解决"上下文腐烂"问题——执行到第 10 个任务时，Agent 对前 9 个的记忆仍然清晰一致，不会出现"忘记早期决策"的情况。
- **工件结构管理**（Spec Kit / OpenSpec 代表）：通过级联文件（spec → plan → task → research）创建隐式上下文边界。Agent 在规格阶段加载宪法和功能规格，计划阶段只看到计划相关文件，执行阶段聚焦实现。每个阶段的上下文被精准控制在当前所需的范围内。
- **变更隔离**（OpenSpec 特有）：每个变更拥有独立目录，防止跨变更污染。存量系统上同时进行两个功能开发时，各自的 spec、task、design 互不干扰。
- **持久化上下文**（Taskmaster AI 代表）：维持长期持久化上下文，通过结构化提示词和多模型路由管理，无显式隔离机制。

### 执行深度

- **编排型**（GSD）：工具管理任务的并行执行、代理调度、依赖追踪。GSD 的波级并行是代表——4 个研究器可同时工作，独立任务并行执行，依赖任务自动等待。
- **委托型**（Taskmaster AI）：工具负责规划和分解，实际编码交给 Cursor / Claude Code 等外部代理执行。
- **中间态**（OpenSpec / Spec Kit）：工具管理"构建什么"（spec + task），不管理"如何构建"（执行交给底层 AI 代理）。

### 平台集成

- **广度型**：OpenSpec 支持 20+ 工具、Spec Kit 支持 18+ 代理——使用跨平台斜杠命令，不绑定特定 IDE
- **深度型**：Taskmaster AI 通过 MCP 与 Cursor 深度集成、Kiro 自建 IDE——提供第一类体验但锁定平台
- **中间态**：GSD 支持 Claude Code / OpenCode / Gemini CLI 三个运行时，有深度适配层但数量有限

---

## 主流 SDD 工具详解

多数工具的命令可以单独使用，不必走完整工作流。用 `/opsx:explore` 思考一个问题，无需提交完整变更提案；用 `/gsd:discuss-phase` 规划一个任务，无需建立完整里程碑体系。了解每款工具解决的核心问题，然后用最简单的命令开始探索——这比研究完整流程更有价值。

### GSD（Get Shit Done）

| 属性 | 详情 |
|------|------|
| **GitHub** | 16.7k stars, MIT |
| **平台** | Claude Code, OpenCode, Gemini CLI |
| **定位** | 执行优先的上下文工程系统 |

GSD 不追求流程仪式感，核心解决两个问题：**上下文腐烂**和**执行效率**。其哲学是交付结果，而不是流程文档。

**工作流**：`Discuss → Plan (wave split) → Execute (parallel) → Verify`

**Project / Milestone / Phase 三级组织**：用户初始化项目（`/gsd:new-project`）时自动生成 ROADMAP.md，以里程碑和阶段组织任务。日常使用无需记忆四个命令的流程，而是通过 `/gsd:progress` 查看当前进度和下一步建议，或通过 `/gsd:ns-workflow` 路由到当前阶段所需的操作。内部每个 phase 的完整生命周期确实包含讨论 → 计划 → 执行 → 验证四个环节，但这是工具内部编排的，用户感受到的是"沿 roadmap 推进"，而非手动执行一套仪式流程。执行阶段会将 phase 内的多个 plan 拆分为波（Wave），依赖分析后决定哪些可以并行、哪些需要串行。

**新鲜上下文隔离**（Execution-First Context Engineering）：上下文不是事先搜集的，而是在执行中产生的。每个子 Agent 启动时只带最小上下文，执行完毕后将结果沉淀为工件，工件成为下一阶段的上下文来源，而非累积聊天历史：

```
Phase N 执行（orchestrator 拆分为 3 个 plan）
├── Agent A（plan-01）：读 CONTEXT.md + PLAN.md → 实现 → 提交 → 写 SUMMARY.md
├── Agent B（plan-02）：读 CONTEXT.md + PLAN.md → 实现 → 提交 → 写 SUMMARY.md
└── Agent C（plan-03）：读 CONTEXT.md + PLAN.md → 实现 → 提交 → 写 SUMMARY.md
         ↓ 各自独立，无上下文干扰
验证 Agent：读全部 SUMMARY.md + 代码 → 产出 VERIFICATION.md
```

**适用场景**：长任务（跨半天或数天）、跨模块改造（涉及 3+ 模块）、复杂重构。在 DramaFlow 课程的迭代 3（需求演进）中引入——存量改造最大的挑战不是"改哪里"，而是"让 Agent 理解上下文不丢失"。

---

### OpenSpec（Fission AI）

| 属性 | 详情 |
|------|------|
| **GitHub** | 24.9k stars, MIT |
| **平台** | 20+ AI 工具（Claude Code, Cursor, Windsurf 等）|
| **定位** | 棕地优先的变更隔离框架 |

OpenSpec 自称**"棕地优先"**——专为已有代码库的团队设计。其切入点是**变更隔离**：在存量系统上，最怕的不是改不动，而是改 A 的时候破坏了 B。

**工作流**：`Explore → Propose → Spec → Apply → Verify → Archive`

**变更隔离结构**：每个变更拥有独立目录 `openspec/changes/<name>/`，内含 `proposal.md`（为什么改）、`design.md`（怎么改）、`tasks.md`（拆解步骤）、`specs/`（验收标准）。这种结构让更改不串扰、提供完整审计追踪、支持渐进式采用。

**核心命令**：`/opsx:new` 创建提案、`/opsx:ff` 快速前进（一步生成所有规划工件）、`/opsx:explore` 探索模式、`/opsx:apply` 执行、`/opsx:verify` 验证、`/opsx:archive` 归档。支持双模式：完整模式适合复杂变更，快速前进模式适合中等复杂度变更。

**适用场景**：存量系统迭代、需要审计追踪的合规场景、多人并行变更。在 DramaFlow 课程的迭代 2 中替代纯 Prompt SDD，解决约束遗漏率高、AC 自动化验证困难、跨变更追溯缺失三个问题。

---

### Spec Kit（GitHub）

| 属性 | 详情 |
|------|------|
| **GitHub** | 70.8k stars, MIT |
| **平台** | 18+ AI 编码代理（Claude Code, Cursor, Copilot 等）|
| **定位** | 企业级规格治理工具 |

Spec Kit 来自 GitHub 官方，强调**"规格不服务于代码；代码服务于规格"**。通过"项目宪法"机制确保团队规范。

**工作流**：`Constitution → Specify → Plan → Implement → Analyze`

**项目宪法**：`.specify/constitution.md` 定义团队规则（如"所有 API 必须包含 OpenAPI 文档"），每次任务执行时被加载，确保 AI 生成代码遵循团队标准。

**8 步结构化闭环**：初始化 → 定义宪法 → 编写功能规格 → 返回澄清（循环）→ 生成实现计划 → 分解任务 → AI 执行实现 → 验证分析。生成丰富的工件集：`spec.md`、`plan.md`、`research.md`、`data-model.md`、`contracts/` 等。

**适用场景**：大型企业项目、跨团队协作、需要向上汇报和审计的团队。弱点在于**流程较重**——8 步闭环在大型项目中提供必要治理，但在快速原型迭代中显得笨重。

---

### Kiro（AWS）

| 属性 | 详情 |
|------|------|
| **平台** | 独立 IDE（桌面应用）|
| **定位** | 代理式 IDE，个人/小团队加速器 |
| **集成** | MCP 插件生态 |

Kiro 是一个**代理式 IDE**，将 AI 代理内置为 IDE 的一等公民。口号是"意图即代码"。

**工作流**：`Intent → Plan → Generate → Hook (test/lint) → Review → Deploy`

通过 `steering.md` 控制 AI 行为，支持三种模式：Kiro Design（设计优先）、Kiro Build（构建优先）、Kiro Bugfix（修复优先）。

**适用场景**：个人独立开发者（最快"想法→产品"路径）、小团队早期原型验证。局限在于限定在桌面 IDE 内，无法作为 CLI 集成到 CI/CD 流程，规格追踪能力较弱。

---

### Taskmaster AI

| 属性 | 详情 |
|------|------|
| **GitHub** | 25.5k stars, MIT + Commons Clause |
| **平台** | Cursor（第一类）、Windsurf、VS Code、Claude Code |
| **定位** | 将 AI 视为项目经理，专注任务分解 |

Taskmaster AI 的独特切入点是：**AI 不是开发者，而是项目经理**。将 PRD 解析为分层的、感知依赖关系的任务列表，再交给编码代理执行。

**工作流**：`PRD → Parse → Task graph (dependency sort) → Delegate to coding agent`

**多模型架构**：主模型（核心操作）+ 研究模型（获取最新信息）+ 后备模型（降级兜底）。PRD 被解析为依赖感知任务图，阻塞任务先执行，独立任务并行。与 Cursor IDE 深度 MCP 集成，在 Cursor 内部直接操控编辑器。

**适用场景**：以 Cursor 为主要 IDE 的团队、从 PRD 出发的完整项目管理。需注意许可证为 MIT + Commons Clause，限制将软件作为服务销售。

---

### SDD 生态中的其他代表性工具

除了上述 5 款主流 SDD 框架，社区中还涌现了一批专注特定环节的工具，以下两款值得关注：

#### Trellis

| 属性 | 详情 |
|------|------|
| **定位** | 跨平台工作流与项目记忆组织 |
| **核心理念** | 用 Specs / Tasks / Workspace 三层结构组织跨平台工作流 |

Trellis 的切入点是：当你同时在 Claude Code、Cursor、GitHub Copilot 等多个 AI 工具间切换时，如何保持上下文和工作流的连续性？它通过三层抽象来解耦：**Workspace** 定义项目全景，**Specs** 定义功能规格，**Tasks** 定义执行单元。Trellis 的设计哲学是"工具无关"——你的 Spec 和 Task 可以在任何 AI 工具中加载执行，不绑定特定平台。

**工作流**：`Workspace → Specs → Tasks → Cross-tool sync`

#### Superpowers（GSD 作者）

| 属性 | 详情 |
|------|------|
| **定位** | 方法论与技能增强层 |
| **关联** | 与 GSD 同作者，可配合使用 |

Superpowers 不做完整的 SDD 流程编排，而是专注于一件事：**把 TDD、Code Review、调试等传统工程习惯编码为 Agent 的默认动作**。它是一组可复用的 Agent Skills，安装后 Claude Code 会在日常开发中自动执行测试驱动、审查代码质量、定位 Bug 根因。适合已经有一套成熟 SDD 工具、希望补充工程纪律的团队。

---

### 快速上手指南对比

各工具的安装与首次使用路径对比：

| 工具 | 安装方式 | 初始化步骤 | 第一个命令 |
|------|----------|-----------|-----------|
| **GSD** | `npx get-shit-done-cc@latest` | 重启 VS Code 后生效 | `/gsd:discuss-phase` |
| **OpenSpec** | `npm install -g @fission-ai/openspec` | `openspec init` | `/opsx:explore` 或 `/opsx:new my-change` |
| **Spec Kit** | `pip install specify-cli` | `specify init my-app --ai claude` | `/speckit.specify` |
| **Kiro** | 官网下载安装包 | 安装即用 | `/kiro:init` 生成 steering.md |
| **Taskmaster AI** | npm 安装 + Cursor 配置 | 在 Cursor 中启用扩展 | 输入 PRD 文本 |
| **Trellis** | `npm install -g @trellis/cli` | `trellis init` | `trellis spec create` |
| **Superpowers** | `/plugin install superpowers@claude-plugins-official` | 重启 VS Code 后生效 | 无需显式触发，自动生效 |

---

## 核心维度对比

### 执行哲学对比

| 工具 | 哲学 | 名句 |
|------|------|------|
| **GSD** | 编排执行 | "上下文管理比提示词工程更重要" |
| **OpenSpec** | 变更隔离 | "不改坏现有功能比实现新功能更重要" |
| **Spec Kit** | 规格即契约 | "代码服务于规格，而非反过来" |
| **Kiro** | 意图即代码 | "不要让开发者离开 IDE" |
| **Taskmaster AI** | AI 是 PM | "好的架构来自好的任务分解" |
| **Trellis** | 工具无关 | "Spec 和 Task 应在任何 Agent 中可执行" |
| **Superpowers** | 习惯编码化 | "把 TDD 和 CR 变成 Agent 的肌肉记忆" |

---

## 各工具适用场景

下表用"适合/不适合"双向约束帮助决策——不适合列往往比适合列更有筛选价值。

| 场景 | 首选工具 | 不适合 |
|------|----------|--------|
| 存量系统迭代，怕改 A 坏 B | **OpenSpec** | Kiro（无 CLI/CI 集成，规格追踪弱） |
| 从零绿地 MVP，速度优先 | **Kiro** | Spec Kit（8 步流程在原型期过重） |
| 长任务跨模块重构（3+ 模块） | **GSD** | Taskmaster AI（委托型，不编排执行） |
| 大型企业，需要向上汇报和审计 | **Spec Kit** | GSD（审计追踪能力相对弱） |
| 以 Cursor 为主、从 PRD 驱动 | **Taskmaster AI** | GSD（不深度集成 Cursor） |
| 多 AI 工具切换，需统一工作流 | **Trellis** | Kiro（锁定 IDE，工具无关性差） |
| 已有 SDD 工具，强化工程纪律 | **Superpowers** | 单独使用（需配合其他 SDD 工具）|

---

## 总结

SDD 工具的涌现是 AI 辅助编程走向成熟化的必然结果。当"让 AI 写出代码"不再是问题时，行业的下一个核心挑战变成了**"如何确保 AI 写出的代码是正确、一致、可维护的"**。

从 Prompt SDD 到工具化 SDD，本质上是**把规范和约束从人脑/文字中提取出来，编码为可执行的系统**。这个过程与软件工程过去几十年走过的路如出一辙：从个人手艺→口头约定→文档规范→代码化/自动化。

值得注意的是，所有主流 SDD 工具在 **Spec → Plan → Execute → Verify** 的核心循环上已经趋同——这个基本模式已被验证，工具之间的真正差异在于上下文策略、执行深度和平台集成方式。

SDD 工具没有普适的最优解。了解每款工具核心解决的问题，从一个命令开始试，遇到实际痛点再深入——工具适不适合，用过才知道。

---

## 参考资料

- [GSD - Get Shit Done](https://github.com/gsd-build/get-shit-done)
- [OpenSpec - Fission AI](https://github.com/fission-ai/openspec)
- [Spec Kit - GitHub](https://github.com/github/spec-kit)
- [Kiro - AWS](https://aws.amazon.com/cn/campaigns/kiro/)
- [Taskmaster AI](https://github.com/bmadcode/taskmaster-ai)
- Martin Fowler: [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- Thoughtworks: [Spec-Driven Development Technology Radar](https://www.thoughtworks.com/en-sg/radar/techniques/spec-driven-development)

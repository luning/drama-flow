# SDD 工具全景

## 为什么需要 SDD 工具？

**Spec-Driven Development** 的核心思想是：在编码之前把"怎么做才算完成"写清楚。BDD / TDD / ATDD 都是它的前身，SDD 的不同在于规格不是供人阅读的文档，而是**直接驱动 AI Agent 行为的可执行工件**。

最简单的起点是在 CLAUDE.md 中写入约束（"Prompt SDD"）：

```markdown
## SDD 最小约束
1. 接受任务前，先阅读对应模块的 SPEC.md 中的验收标准
2. 生成代码后，逐条自检 AC，确保所有验收标准被覆盖
3. 修改已有 AC 时标注变更记录，保留历史意图
```

这种做法零成本、立即生效，但远不如 SDD 工具可靠：

- Prompt 约束依赖 Agent 自觉性，复杂任务中容易被跳过
- 没有变更隔离，改 A 坏 B 没有任何记录
- 多轮对话后 Agent 会忘记早期决策

**建议从项目一开始就引入工具，而不是等到出了问题再补救。**

---

## SDD 工具的核心能力框架

所有工具围绕同一个基本循环：`讨论/探索 → 规划 → 执行 → 验证 → 归档`

工具之间的差异体现在三个维度：

### 上下文策略

- **新鲜上下文隔离**（GSD）：每个子 Agent 启动时只带最小上下文，执行结果沉淀为工件，工件作为下一阶段输入——不累积聊天历史，解决上下文腐烂。
- **工件结构管理**（Spec Kit / OpenSpec）：级联文件（spec → plan → task → research）创建隐式上下文边界，每阶段只加载当前所需范围。
- **变更隔离**（OpenSpec 特有）：每个变更独立目录，防止跨变更上下文污染。
- **持久化上下文**（Taskmaster AI）：维持长期上下文，通过结构化提示词和多模型路由管理，无显式隔离机制。

### 执行深度

- **编排型**（GSD）：工具直接管理并行执行、Agent 调度、依赖追踪。
- **委托型**（Taskmaster AI）：工具负责规划分解，实际编码交给外部 Agent 执行。
- **中间态**（OpenSpec / Spec Kit）：工具管理"构建什么"，不管理"如何构建"。

### 平台集成

- **广度型**：OpenSpec（20+ 工具）、Spec Kit（18+ 代理）——跨平台斜杠命令，不绑定 IDE
- **深度型**：Taskmaster AI（与 Cursor 深度 MCP 集成）、Kiro（自建 IDE）——第一类体验但锁定平台
- **中间态**：GSD 支持 Claude Code / OpenCode / Gemini CLI 三个运行时

---

## 主流 SDD 工具详解

工具的命令可以单独使用，不必走完整工作流。了解每款工具解决的核心问题，然后从最简单的命令开始——比研究完整流程更有价值。

### OpenSpec（Fission AI）

| 属性 | 详情 |
|------|------|
| **GitHub** | 24.9k stars, MIT |
| **平台** | 20+ AI 工具 |
| **定位** | 棕地优先的变更隔离框架 |

专为已有代码库设计，核心是**变更隔离**：每个变更独立目录 `openspec/changes/<name>/`，内含 `proposal.md`（为什么改）、`design.md`（怎么改）、`tasks.md`（拆解步骤）、`specs/`（验收标准）。

**工作流**：`Explore → Propose → Spec → Apply → Verify → Archive`

核心命令：`/opsx:explore` 探索、`/opsx:new` 创建提案、`/opsx:ff` 快速前进（一步生成所有规划工件）、`/opsx:apply` 执行、`/opsx:archive` 归档。

**适用场景**：存量系统迭代、需要审计追踪的合规场景、多人并行变更。在 DramaFlow 迭代 2 引入，替代纯 Prompt SDD。

---

### Superpowers（GSD 作者）

专注把 TDD、Code Review、调试等传统工程习惯编码为 Agent 的默认动作——一组可复用的 Agent Skills，安装后自动在日常开发中生效。不做完整 SDD 流程编排，适合配合其他 SDD 工具补充工程纪律。

---

### GSD（Get Shit Done）

| 属性 | 详情 |
|------|------|
| **GitHub** | 16.7k stars, MIT |
| **平台** | Claude Code, OpenCode, Gemini CLI |
| **定位** | 执行优先的上下文工程系统 |

核心解决两个问题：**上下文腐烂**和**执行效率**。哲学是交付结果，不追求流程仪式感。

**工作流**：`Discuss → Plan (wave split) → Execute (parallel) → Verify`

**新鲜上下文隔离**：

```
Phase N（orchestrator 拆分为 3 个 plan）
├── Agent A：读 CONTEXT.md + PLAN.md → 实现 → 写 SUMMARY.md
├── Agent B：读 CONTEXT.md + PLAN.md → 实现 → 写 SUMMARY.md
└── Agent C：读 CONTEXT.md + PLAN.md → 实现 → 写 SUMMARY.md
         ↓ 各自独立，无上下文干扰
验证 Agent：读全部 SUMMARY.md + 代码 → 产出 VERIFICATION.md
```

执行阶段将 phase 内的多个 plan 拆分为波（Wave），依赖分析后决定并行或串行。

**适用场景**：长任务（跨半天或数天）、跨模块改造（3+ 模块）、复杂重构。在 DramaFlow 迭代 3 引入。

---

### Spec Kit（GitHub）

| 属性 | 详情 |
|------|------|
| **GitHub** | 70.8k stars, MIT |
| **平台** | 18+ AI 编码代理 |
| **定位** | 企业级规格治理工具 |

核心是**项目宪法**：`.specify/constitution.md` 定义团队规则（如"所有 API 必须包含 OpenAPI 文档"），每次任务执行时被加载，确保 AI 生成代码遵循团队标准。

**工作流**：`Constitution → Specify → Plan → Implement → Analyze`（8 步闭环）

产出丰富工件集：`spec.md`、`plan.md`、`research.md`、`data-model.md`、`contracts/` 等。

**适用场景**：大型企业项目、跨团队协作、需要审计的场景。流程较重，快速迭代场景不适合。

---

### Kiro（AWS）

| 属性 | 详情 |
|------|------|
| **平台** | 独立 IDE（桌面应用）|
| **定位** | 代理式 IDE，绿地项目加速器 |

将 AI 代理内置为 IDE 一等公民。通过 `steering.md` 控制 AI 行为，支持 Design / Build / Bugfix 三种模式。

**工作流**：`Intent → Plan → Generate → Hook (test/lint) → Review → Deploy`

**适用场景**：个人独立开发者、小团队早期原型验证。局限：限定桌面 IDE，无法集成 CI/CD，规格追踪能力较弱。

---

### Taskmaster AI

| 属性 | 详情 |
|------|------|
| **GitHub** | 25.5k stars, MIT + Commons Clause |
| **平台** | Cursor（第一类）、Windsurf、VS Code、Claude Code |
| **定位** | AI 作为项目经理，专注任务分解 |

将 PRD 解析为依赖感知任务图，再委托给编码 Agent 执行。多模型架构：主模型（核心操作）+ 研究模型 + 后备模型。与 Cursor 深度 MCP 集成。

**工作流**：`PRD → Parse → Task graph → Delegate to coding agent`

**适用场景**：以 Cursor 为主要 IDE 的团队、从 PRD 出发的完整项目管理。注意许可证含 Commons Clause，限制作为服务销售。

---

### 选型速查

| 工具 | 最适合 | 不适合 |
|------|--------|--------|
| **OpenSpec** | 存量系统迭代，怕改 A 坏 B | — |
| **Superpowers** | 配合其他 SDD 工具，强化工程纪律 | 单独使用 |
| **GSD** | 长任务跨模块重构（3+ 模块） | 深度审计追踪 |
| **Spec Kit** | 大型企业，需向上汇报和审计 | 快速原型迭代 |
| **Kiro** | 从零绿地 MVP，速度优先 | CLI / CI 集成场景 |
| **Taskmaster AI** | Cursor 为主、PRD 驱动开发 | 编排执行场景 |

---

## SDD 的定制与扩展

各工具的扩展点设计不同。OpenSpec 和 Superpowers 是定制能力最强、也最值得深入了解的两个。

### OpenSpec：自定义 Schema

OpenSpec 通过 **Schema** 定制整个变更工作流——Schema 声明 artifact 列表、每个 artifact 的模板和 AI 执行指令、依赖链，以及 apply 阶段行为。`template` 控制文档结构，`instruction` 控制 AI 行为，两者分工明确，均可按团队规范定制。

---

### Superpowers：修改现有 Skill 或新增 Skill

Superpowers 的扩展单元是 **Skill**（Markdown 文件），扩展方式有两种：

**修改内置 Skill**：TDD、Code Review、系统调试等内置 Skill 都是可以直接编辑的 `SKILL.md` 文件。在现有步骤中加入团队特有约束，Agent 下次执行该 Skill 时行为随之改变。修改后用 `writing-skills` 的 TDD 方法验证：写压力场景确认 Agent 确实按新步骤执行。

**新增自定义 Skill**：创建新的 Skill 文件，`description` 字段**只写触发条件**（"Use when..."），不描述执行过程——若 description 里概括了流程，Agent 会走捷径跳过 Skill 正文，导致步骤被省略。

Skill 可以通过 Hook 挂在任何 SDD 命令前后，作为"门禁"附加在工作流外侧，不改动被挂载工具本身：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash(openspec apply*)",
      "hooks": [{ "type": "command", "command": "claude /my-ac-check" }]
    }]
  }
}
```

---

### 其他工具

**GSD**：每个命令背后是一个 Skill 文件（Markdown），可以直接编辑插入团队逻辑，或通过 Hook 触发附加检查。`.planning/CONTEXT.md` 是项目级约束注入点。

**Spec Kit**：`.specify/constitution.md` 是每次任务执行时都加载的团队规则，加入命名规范、禁止依赖即可影响 AI 行为。spec / plan / research 等文档的模板文件也可以覆盖。

**Kiro**：`steering.md` 控制 Agent 在 Design / Build / Bugfix 三种模式下的行为，是唯一的扩展入口。

**Taskmaster AI**：`.taskmaster/config.json` 配置模型选择和任务分解策略，PRD 模板可定制以适配团队的需求文档格式。

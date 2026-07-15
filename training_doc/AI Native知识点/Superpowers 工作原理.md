# Superpowers 工作原理

Superpowers 是一组**将工程纪律编码为 Agent 默认行为**的可复用 Skill。安装后，Agent 在开发全程自动触发 TDD、设计评审、代码审查等流程，无需手动提醒。

---

## 运行机制

Skill 列表注入 system-reminder

Claude Code 扫描插件目录下所有 SKILL.md 的 YAML frontmatter，提取 `name` 和 `description`，每轮对话以 `system-reminder` 形式注入：

```
Available skills for use with the Skill tool:
- brainstorming: You MUST use this before any creative work...
- subagent-driven-development: Use when executing implementation plans...
```

Agent 对照 description 判断是否触发，匹配到则通过 `Skill` 工具加载完整 SKILL.md 内容执行。

**关键约束**：description 只写触发条件，不写执行流程。description 一旦概括流程，Agent 会把它当作完整指令直接执行，跳过 SKILL.md 正文。

---

## 开发工作流

四个步骤形成完整链路。前两步自动衔接，执行阶段用户三选一，收尾自动触发。

### 1. brainstorming（设计）

**触发**：自动，Agent 检测到"构建功能"意图即触发。

**产出**：`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`

SKILL.md 通过两个机制控制执行：Checklist 定义必序步骤，HARD-GATE 阻断违规操作。格式规范内嵌在 SKILL.md 说明文字中，无独立模板文件。

```markdown
# skills/brainstorming/SKILL.md

## Checklist     ← using-superpowers/SKILL.md 的 flowchart 规定：
                 #   "Has checklist?" → "Create a todo per item"
                 #   Agent 为每项创建 todo，靠 todo 状态机追踪进度

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Offer the visual companion just-in-time** — NOT upfront. Only when a question would be clearer shown than described.
3. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections, get user approval after each section
6. **Write design doc** — save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
7. **Spec self-review** — check for placeholders, contradictions, ambiguity, scope
8. **User reviews written spec** — ask user to review before proceeding
9. **Transition to implementation** — invoke writing-plans skill

<HARD-GATE>      ← Agent 看到此标记不得跳过
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any
implementation action until you have presented a design and the user has approved it.
</HARD-GATE>
```

### 2. writing-plans（实现计划）

**触发**：brainstorming 尾部自动调用。

**产出**：`docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

SKILL.md 内嵌 PLAN.md 头部模板（Goal、Architecture、Tech Stack、Global Constraints），并规定 task 粒度（2-5 分钟/步）、TDD 要求、commit 节奏。PLAN.md 头部包含一行提示说明执行方式，但不自动触发下一步。

### 3. 执行（三选一）

| 方式 | Skill | 场景 |
|------|-------|------|
| **Subagent-Driven Development** | `subagent-driven-development` | 推荐。当前会话，每个 task 派独立 subagent，完成后双重审查（spec 合规 + 代码质量） |
| **Executing Plans** | `executing-plans` | 多会话并行，有人工 checkpoint |
| **手动执行** | 无 | 当前对话逐 task 推进 |

选 SDD 时，工件写入 `.superpowers/sdd/`（git-ignored）：

```
.superpowers/sdd/
  task-N-brief.md     ← 从 PLAN.md 提取的单 task 文本
  task-N-report.md    ← implementer subagent 执行报告
  review-<sha>.diff   ← reviewer 阅读的 diff 包
  progress.md         ← 进度账本，防会话恢复后重复执行
```

工件通过脚本生成，不粘贴进 prompt，避免 Controller 上下文膨胀。

### 4. finishing-a-development-branch（收尾）

**触发**：所有 task 完成后自动触发。呈现三个选项：合并 / 开 PR / 保留分支，并清理 worktree。

---

## 定制扩展

Superpowers **没有扩展点**。内置工作流无法被外部插入步骤；内置 Skill 文件在插件更新时会被重置，直接修改无效。官方 PR 贡献通常也不接受新 Skill，只接受对已有 Skill 的跨平台改进。

项目特有的流程约束应通过 **Claude Code Hook** 或**独立项目 Skill**（放在 `.claude/skills/`）实现，与 Superpowers 并列共存。

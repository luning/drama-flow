# Claude Code 使用技巧

## 目录

1. [工作原理](#工作原理)
2. [CLAUDE.md 配置原则](#claudemd-配置原则)
3. [高效工作流](#高效工作流)
   - [复杂任务用 Plan Mode](#复杂任务用-plan-mode)
   - [让 Claude 先采访你](#让-claude-先采访你)
   - [分阶段工作流](#分阶段工作流)
   - [小任务别用复杂工作流](#小任务别用复杂工作流)
4. [调试与纠错](#调试与纠错)
5. [上下文管理](#上下文管理)
   - [50% 时考虑手动压缩](#50-时考虑手动压缩)
   - [指定压缩策略](#指定压缩策略)
   - [Checkpoints（检查点）](#checkpoints检查点)
6. [Subagents（子智能体）](#subagents子智能体)
7. [Skills 与 Commands](#skills-与-commands)
   - [Skills（技能）](#skills技能)
   - [常用内置 Commands](#常用内置-commands)
   - [自定义 Skill 与 Command 的区别](#自定义-skill-与-command-的区别)
8. [权限与安全](#权限与安全)
   - [Hooks vs CLAUDE.md 选型](#hooks-vs-claudemd-选型)
   - [Allowlist 减少审批疲劳](#allowlist-减少审批疲劳)
   - [deny 比 Hooks 更安全](#deny-比-hooks-更安全)
9. [常见陷阱（Gotchas）](#常见陷阱gotchas)
10. [核心原则](#核心原则)
11. [拓展阅读：更多进阶内容](#拓展阅读更多进阶内容)
   - [Claude Code + OpenSpec（规格驱动开发）](#claude-code-openspec规格驱动开发)
   - [Superpowers（工程纪律框架）](#superpowers工程纪律框架)
12. [参考资料](#参考资料)

---

## 工作原理

```
┌─────────────────────────────────────────────────────┐
│              Claude Code 执行循环                    │
│                                                     │
│  你的输入 + CLAUDE.md + 打开的文件                   │
│                  ↓                                  │
│         LLM 思考：下一步做什么？                     │
│                  ↓                                  │
│         调用工具（Tool Use）                         │
│         ├── Read   → 读文件内容                     │
│         ├── Edit   → 修改文件                       │
│         ├── Write  → 创建新文件                     │
│         ├── Bash   → 运行命令（测试 / 编译）         │
│         └── Search → 在代码库中搜索                  │
│                  ↓                                  │
│         观察结果 → 再思考 → 再调用工具               │
│                  ↓                                  │
│         完成 or 等待人工确认                         │
└─────────────────────────────────────────────────────┘
```

**几个关键点**

- CLAUDE.md 在每次对话开始时**自动注入到 system prompt**，这是约束持久化的底层机制
- 工具调用是**可观测的**：你能看到它读了哪些文件、改了什么、运行了什么命令
- 每次工具调用结果都会返回给模型，模型基于结果决定下一步——这就是为什么测试失败信息要清晰
- 模型没有"记忆"，依赖的是**当前上下文窗口里的全部内容**

---

## CLAUDE.md 配置原则

- **保持简短**：控制在 60 行以内，硬上限 300 行
- **只放 Claude 可能忽略的信息**：构建命令、测试命令、分支规范、架构决策
- **能从代码推断的内容不要写**：语言语法、框架 API 等不需要
- **规则太多？拆分到 `.claude/rules/`**，按需加载，不污染主文件
- **关键规则用 XML 标签包裹**，防止被忽略

好的 CLAUDE.md 结构示例：
```
## 工作流
- 每次代码变更后运行 `npm test`
- 使用 Conventional Commits（feat:, fix:, refactor:, docs:）
- 每次提交前运行 `eslint . --fix`
## 技术栈
- Node.js 18+, Express 4.x, PostgreSQL 16
- 测试：Jest + React Testing Library
```

---

## 高效工作流

### 复杂任务用 Plan Mode
- 按 Shift+Tab 两次进入计划模式 → Claude 只研究不写代码
- 确认计划后再切换回正常模式执行
- 推荐流程：探索 → 规划 → 实现 → 提交

### 让 Claude 先采访你
- 给出简单需求，让 Claude 用 AskUserQuestion 采访你
- 它能发现你忽略的边缘情况
- 采访后建议开新会话执行（采访对话会污染上下文）

### 分阶段工作流
- 理解代码库 → 修改；先规划 → 再实现；生成 → 验证
- 不要把所有步骤压缩到一个大提示词里

### 小任务别用复杂工作流
- 3-5 分钟能完成的事，直接说
- 重命名变量这种小事，一句话就行

---

## 调试与纠错

1. **粘贴 bug，说 "fix"**
   - 把错误信息粘贴给 Claude，说一个字："fix"
   - 不要指导怎么修、不要猜测原因、不要指定解决方案
   - 直接让 Claude 修的成功率 80%+

2. **两次失败 = /clear**
   - 同一个问题修正超过两次，`/clear` 重新开始
   - 上下文污染会降低性能

3. **走偏了？Esc Esc 回滚**
   - 按两次 Esc（或 `/rewind`）直接回滚到上一个检查点
   - 同一问题偏差两次？`/clear` 重启

4. **要求重写平庸方案**
   - 当 Claude 给出能工作但不优雅的解决方案时，说：
   - "知道你现在知道的一切，抛弃这个，实现优雅的解决方案"
   - 重写版本通常比修补版本好得多

---

## 上下文管理

### 50% 时考虑手动压缩
- 上下文使用超过 60-70% 时，性能明显下降
- **在 50% 时考虑手动执行 `/compact`**，不要等自动压缩
- 用 `/statusline` 实时监控使用情况

### 指定压缩策略
```
/compact focusing on API changes     # 聚焦 API 变更
/compact keep test-related history   # 保留测试相关
/compact keep error resolution       # 保留错误解决
```

### Checkpoints（检查点）
- 每次 Claude 操作自动创建，可独立回滚对话或代码
- 跨会话持久化，但不是 git 的替代品

---

## Subagents（子智能体）

- **提示词中加 "use subagents"** —— Claude 自动拆分任务并行处理
- **专用子智能体 > 通用 mega-agent**：功能越具体，上下文越精准
- **子智能体有独立上下文窗口**：研究、验证、审查隔离在独立上下文中，不污染主上下文

应用场景：代码审查、跨文件重命名、大规模重构

---

## Skills 与 Commands

### Skills（技能）

Skills 是 Claude Code 的功能扩展，将特定领域的规则和工具打包成可复用的模块。本课程中的 `rebuild-deploy`、`spec-validate`、`cr-refactor` 等就是 Skill。调用方式：对话中输入 `/skill-name`。

**目录结构**：
```
.claude/commands/skill-name/
  SKILL.md       # 主文件（Claude 优先读取）
  references/    # 参考资料（渐进式披露，按需读取）
  scripts/       # 辅助脚本（固定逻辑，无需 AI 推理的部分）
  examples/      # 示例代码
```

**核心设计原则**（详见 [Skills设计.md](Skills设计.md)）：
- **参数最小化**：让 Skill 自己从上下文推断，减少调用者出错
- **幂等性**：可重复调用，不产生副作用
- **结构化反馈**：stdout 输出让 Agent 可自修复
- **固定逻辑剥离**：无需推理的流程用脚本实现，Skill 聚焦推理判断

### 常用内置 Commands

| 命令 | 作用 | 使用时机 |
|------|------|---------|
| `/compact` | 压缩上下文 | 上下文使用超过 50% 时 |
| `/clear` | 清空会话重启 | 同一问题失败两次 |
| `/rewind` 或 `Esc Esc` | 回滚到上一检查点 | 发现走偏时立即回滚 |
| `/status` | 查看当前状态 | 随时检查上下文和文件状态 |
| `/plan` (Shift+Tab x2) | 进入计划模式 | 复杂任务先规划后执行 |

### 自定义 Skill 与 Command 的区别

- **Skill**：领域知识包（目录结构），适用于需要专业知识和上下文的场景，如代码审查、部署；CLI Skill vs MCP Server 的选型见 [Skills设计.md](Skills设计.md)
- **Command**：内置快捷操作，适用于通用控制操作，如压缩、回滚

---

## 权限与安全

### Hooks vs CLAUDE.md 选型

| 需求 | 推荐 | 原因 |
|------|------|------|
| 文件保存后自动 lint | Hook | 每次必须执行 |
| 阻止写入敏感文件 | Hook | 安全不能妥协 |
| 代码规范遵循 | CLAUDE.md | 需要情境判断 |
| API 命名规则 | CLAUDE.md | 存在例外模式 |

### Allowlist 减少审批疲劳
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint:*)",
      "Bash(npm run test:*)",
      "Bash(git status)",
      "Read",
      "Glob",
      "Grep"
    ]
  }
}
```

### deny 比 Hooks 更安全
```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(curl:*)"
    ]
  }
}
```
权限评估顺序：deny → ask → allow。设为 deny 后文件对 Claude "不可见"。

---

## 常见陷阱（Gotchas）

| # | 陷阱 | 表现 | 缓解方法 |
|---|------|------|---------|
| 1 | 过早放弃 | 说"已实现大部分功能，但 XX 不工作" | 拆分任务为更小单元，每个 10 分钟可完成 |
| 2 | 上下文压缩后变笨 | 忘记之前纠正的错误 | 50% 时手动 `/compact`，必要时 `/clear` |
| 3 | 测试质量差 | 测试看起来对但实际失败 | TDD 模式，仔细审查测试 |
| 4 | 修改测试而非代码 | 降低测试标准匹配错误代码 | 严格审查测试变更 |
| 5 | 忘记编译 | 测试失败因为未编译 | 在 CLAUDE.md 中明确编译步骤 |
| 6 | 工作目录混乱 | 留下测试脚本、构建产物 | `git status` 检查，手动清理 |
| 7 | Git 操作危险 | 错误的变更合并到 PR | 人工执行 Git 操作 |
| 8 | 重写但不删除旧代码 | 新旧代码共存 | 审查 diff，确认删除 |

---

## 核心原则

- **上下文是宝贵资源**：保持简洁、及时压缩、污染就重置
- **系统约束 > 提示词约束**：用 Hooks 和权限配置代替"希望 Claude 记住"
- **分而治之**：子智能体、分阶段工作流、规格与实现分离
- **不要过度工程**：3-5 分钟能完成的事，直接用
- **持续改进**：每次犯错记录 Gotchas，定期回顾，高频问题转化为规则

---

## 拓展阅读：更多进阶内容

以下内容在培训课程中另有详细讲解，此处列出供查阅参考。

### Claude Code + OpenSpec（规格驱动开发）

详见课程 **6.1 规格驱动：从 Prompt SDD 到工具化 SDD** 及 **9.3 SDD 生态全景**。

核心流程：`/opsx:propose` 提出变更 → 生成 Spec/Design/Tasks → `/opsx:apply` 实现 → `/opsx:archive` 归档。

### Superpowers（工程纪律框架）

第三方插件，强制 TDD、审查、验证等工程纪律。本课程未使用但值得了解。详见 [Superpowers GitHub](https://github.com/obra/superpowers)。

---

## 参考资料

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [10 个 Claude Code 最佳实践](https://discuss.huggingface.co/t/10-essential-claude-code-best-practices-you-need-to-know/174731)
- [Claude Code Gotchas（DoltHub）](https://www.dolthub.com/blog/2025-06-30-claude-code-gotchas/)
- [Superpowers 插件](https://github.com/obra/superpowers)
- [OpenSpec 框架](https://openspec.dev/)

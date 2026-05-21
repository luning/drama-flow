# Harness 工程之项目空间

## 目录

1. [什么是 Harness？](#什么是-harness)
2. [一个典型的 Harness 目录树](#一个典型的-harness-目录树)
3. [Harness 的五个层级](#harness-的五个层级)
   - [1. 架构层 — 让 Agent "看到"边界](#1-架构层-让-agent-看到边界)
   - [2. 文档层 — 渐进披露，按需下钻](#2-文档层-渐进披露按需下钻)
   - [3. 经验层 — 让 Agent 不踩同样的坑](#3-经验层-让-agent-不踩同样的坑)
   - [4. 约束层 — 可执行规则，而不是口头约定](#4-约束层-可执行规则而不是口头约定)
   - [5. 执行层 — Agent 的"手"和"工具箱"](#5-执行层-agent-的手和工具箱)
4. [Harness 的团队治理与 Git 管理](#harness-的团队治理与-git-管理)
   - [Git 提交边界](#git-提交边界)
   - [Code Review 策略](#code-review-策略)
   - [个人偏好管理："分层覆盖"模型](#个人偏好管理分层覆盖模型)
   - [经验文件的质量管控](#经验文件的质量管控)
5. [Memory：Agent 自管理的跨会话持久化](#memoryagent-自管理的跨会话持久化)

---

## 什么是 Harness？

在 AI Coding Agent（如 Claude Code、Codex CLI）中，**模型本身只是拼图的一块**。模型周围的工程组件同样决定了任务完成的质量。这些模型外部的、可编辑的组件集合，统称为 Agent 的 **Harness**（挽具/工装）。

> **直觉类比**：把 Coding Agent 比作一支施工队，模型就是工人的技能水平，Harness 则是工地的工程管理体系——施工图纸、安全规范、质量巡检、进度管控。没有这套体系，几个工人也能搭个简易棚子；但要盖摩天大楼，缺了它寸步难行。

Harness 包含系统提示词（system prompt）、工具（tools）、中间件（middleware）、技能库（skills）、子代理（sub-agents）、长期记忆（long-term memory）等。它决定了：

- 模型如何感知环境（能看到什么文件和上下文）
- 模型如何执行操作（能调哪些工具，工具的行为是什么）
- 模型如何从错误中恢复（中间件的拦截与重试逻辑）
- 模型的"工作风格"（提示词注入的行为准则）

---

## 一个典型的 Harness 目录树

下面用一个虚拟项目的完整目录树直观展示：**从项目源码到 .claude 配置，哪些内容在充当 Agent 的 Harness**。

```
my-project/
│
├── CLAUDE.md                          # ① System Prompt — 全局行为规则与架构约束
├── README.md                          #    项目总览
├── SPEC.md                            #    可执行规格（AC 验收标准，Agent 自检依据）
├── .mcp.json                          # ⑦ MCP 注册 — Agent 启动时自动发现 MCP 工具
│
├── api/
│   └── openapi.yaml                   #    接口契约（强类型 Schema，Agent 不猜参数）
│
├── src/
│   ├── modules/
│   │   ├── auth/                      #    DDD 限界上下文：认证
│   │   │   ├── README.md              #       模块级 Purpose / Interfaces / Constraints
│   │   │   ├── EXPERIENCE.md          #       本模块的经验陷阱（可从 Git History 提炼）
│   │   │   ├── auth_service.py        #       Type Hints = 代码级文档
│   │   │   └── auth_schema.py         #       Pydantic → Agent 的"强类型提示"
│   │   ├── profile/                   #    限界上下文：用户画像
│   │   │   ├── README.md
│   │   │   ├── EXPERIENCE.md
│   │   │   └── ...
│   │   └── notification/              #    限界上下文：通知
│   │       ├── README.md
│   │       └── ...
│   ├── mcp/                            # ⑦ MCP 工具实现 — Agent 通过 .mcp.json 自动发现
│   │   └── server.py
│   │
│   └── shared/
│       └── types.py                   # 跨模块共享类型的集中定义点
│
├── docs/
│   └── adr/                           #    架构决策记录
│       ├── 001-sqlite-not-pg.md       #       为什么选 SQLite — 防止 Agent 走回头路
│       └── 002-jwt-session.md         #       认证方案选型
│
├── design-system/                     #    设计约束（被 Skills 和 System Prompt 引用）
│   ├── tokens.css                    #       CSS 变量 — 颜色/间距/阴影/动画/字体（单一真相源）
│   ├── tokens.ts                     #       TypeScript 版本 — Vue/React 组件引用
│   ├── constraints.md                #       业务约束与尺寸规范（UX 规则，Agent 生成 UI 必读）
│   ├── design-rules.md               #       AI 生成规则（Prototype Skill 自动注入此文件）
│   ├── components/
│   │   └── index.html                #       组件 Gallery — 可视化验证所有组件在 Token 下的渲染效果
│   └── README.md                     #       设计系统总览与变更流程
│
├── .importlinter                       # Architecture as Code — 模块依赖规则
├── pyproject.toml                      # Lint / Type Check（mypy, ruff）
├── .github/workflows/ci.yml           # CI — 提交即验证
│
├── .claude/
│   ├── settings.json                  # ② Tool 权限 — allowlist / deny list
│   ├── settings.local.json
│   │
│   ├── hooks/                         # ③ Middleware — 管线拦截（PreToolUse / PostToolUse）
│   │   ├── validate-commit.sh         #    提交前自动跑 lint + test
│   │   ├── secret-scanner.js          #    阻止密钥泄露
│   │   └── dangerous-cmd-guard.js     #    拦截危险命令
│   │
│   │── skills/                        # ④ Skills — 按需注入的工作流
│   │   ├── code-review/
│   │   ├── debug/
│   │   ├── test-run/
│   │   └── deploy/
│   │
│   ├── agents/                        # ⑤ Sub-Agents — 隔离执行的委派单元，隔离上下文膨胀
│   │   ├── code-reviewer.md
│   │   ├── debugger.md
│   │   └── planner.md
│   │
│   ├── experience/                    # ⑥ 跨模块经验的索引（具体经验文件在代码目录中）
│   │   └── INDEX.md                   #    "新增路由 → src/modules/EXPERIENCE.md"
│   │
│   └── memory/                        # Ⓜ Agent 自管理的跨会话记忆
│       ├── user.md
│       ├── project.md
│       └── feedback.md
│
└── scripts/                           # 工具支撑脚本
    ├── reset_db.sh
    └── seed_data.py
```

---

## Harness 的五个层级

这棵目录树的每一部分都可以归入以下五个层级，从松到紧排列：

| 层 | 涵盖内容 | 约束强度 | 存在形式 |
|---|---------|---------|---------|
| **架构层** | 模块目录结构、OpenAPI、Type Hints、DDD 限界上下文 | ★★☆☆☆ | 源码目录 + 类型系统 + 接口契约 |
| **文档层** | CLAUDE.md、模块 README、ADR、SPEC、PRD、design-system | ★★☆☆☆ | Markdown，渐进披露，按需下钻 |
| **经验层** | 模块 EXPERIENCE.md、.claude/experience/INDEX.md | ★★☆☆☆ | 结构化经验文件，随代码 colocate |
| **约束层** | import-linter、pyproject.toml、CI、Hooks | ★★★★☆ | 可执行规则 + 管线拦截 |
| **执行层** | Skills、Sub-Agents、settings.json 权限、MCP（.mcp.json + src/mcp/）、scripts | ★★★★☆ | 注入 Prompt + 隔离执行 + allowlist |

### 1. 架构层 — 让 Agent "看到"边界

架构层与其他四层有本质区别：**文档、经验、约束、执行都是可以"外挂"到项目上的 Harness 组件，而架构层就是项目源码本身**——目录怎么切、模块怎么拆、类型怎么定义。

正因如此，项目架构的设计质量直接决定了 Agent 的工作效果。一套对人类工程师友好的架构，往往也对 Agent 友好——两者的核心诉求一致：**快速定位"改哪里"、清晰识别"边界在哪"**。

推荐基于 **DDD（领域驱动设计）** 来组织代码架构，它和 LLM 的运作方式天然契合：

- **限界上下文 → 模块边界**：DDD 按业务领域拆分限界上下文，每个上下文映射为一个模块目录（`auth/`、`profile/`、`notification/`），Agent 修改某一个时不会误入其他上下文的实现细节
- **通用语言（Ubiquitous Language）→ 命名体系**：DDD 要求每个限界上下文内建立统一的术语，目录名、类名、字段名共享同一套词汇——这与 LLM 基于语义匹配的推理模式高度一致，Agent 的"理解"和"生成"都更精准
- **聚合根 → 类型约束**：DDD 的聚合根通过类型系统（OpenAPI Schema、Pydantic 模型、Type Hints）固化为代码级约束，Agent 无需跳转即可理解数据结构的边界和校验规则

具体落地到目录树：

- 模块目录结构（DDD 限界上下文）：目录即边界
- `api/openapi.yaml` → 接口契约，强类型 Schema，Agent 不猜参数
- Type Hints（`src/modules/*/auth_service.py`）+ Pydantic（`src/modules/*/auth_schema.py`）→ 代码级文档 + 强类型校验
- `src/shared/types.py` → 跨模块共享类型

### 2. 文档层 — 渐进披露，按需下钻

文档层回答"为什么要这么做"。Agent 不会一次性吞下所有文档，而是按任务范围按需查阅。

- `CLAUDE.md` / `SPEC.md` → 全局行为规则与可执行规格，Agent 启动即加载，完成后以此为自检清单
- `src/modules/*/README.md` → 模块级 Purpose / Interfaces / Constraints，Agent 只需读当前模块
- `docs/adr/` → 架构决策记录（如"为什么选 SQLite"），防止 Agent 走回头路
- `design-system/` → 设计 Token 与约束，被 Skills 和 System Prompt 引用

### 3. 经验层 — 让 Agent 不踩同样的坑

经验层是团队与 Agent 之间的"错题本"。某段代码出过什么 Bug、踩过什么坑，沉淀为结构化经验文件。

- `src/modules/*/EXPERIENCE.md` → 与模块代码 colocate，记录该模块的历史陷阱和反模式
- `.claude/experience/INDEX.md` → 跨模块经验的索引入口，让 Agent 按关键词快速定位

### 4. 约束层 — 可执行规则，而不是口头约定

约束层与文档层的区别在于：文档层靠 Agent 自觉遵守，约束层**编译时或运行时强制拦截**。

- `.importlinter` → 模块依赖规则，Architecture as Code，违规即 CI 红灯
- `pyproject.toml` / `.github/workflows/ci.yml` → Lint + Type Check + 测试，提交即验证，不规范的代码无法合入
- `.claude/hooks/` → PreToolUse / PostToolUse 管线拦截（扫描密钥、阻止 `rm -rf` 等危险命令）

### 5. 执行层 — Agent 的"手"和"工具箱"

执行层定义 Agent 能做什么、怎么委派任务、如何调用外部系统。

- `.mcp.json` + `src/mcp/` → MCP 工具声明与实现，启动时自动发现。`.mcp.json` 声明 Server（命令、环境变量），`src/mcp/` 存放实现代码
- `.claude/settings.json` → Tool 权限 allowlist / deny list，控制 Agent 能调用哪些系统命令
- `.claude/skills/` → 按需注入的工作流（CR、debug、deploy），Agent 识别意图后自动加载
- `.claude/agents/` → 隔离执行的委派单元（子代理），独立上下文，并行执行，保护主会话不受污染
- `scripts/` → 工具支撑脚本（数据库重置、种子数据导入），Agent 直接调用而非手写

这五个层级的核心规律是：**越往上层，约束越"软"（靠 Agent 自觉）；越往下层，约束越"硬"（靠工具和规则强制执行）。** 一个成熟的 Harness 不会只依赖某一层，而是在五层之间形成纵深防御。

---

## Harness 的团队治理与 Git 管理

### Git 提交边界

核心原则：**代表团队共识的 → 提交；Agent 自动生成或纯个人偏好的 → .gitignore。**

绝大多数 Harness 文件都是团队共识的产物，应当提交。真正不该提交的只有两类：

| 文件 | 不提交的原因 |
|------|-------------|
| `.claude/settings.local.json` | 个人对工具权限的微调，`.claude/settings.json` 已提供团队默认值 |
| `.claude/memory/` | Agent 自动生成的个人记忆，每个开发者有自己的一份 |

其余目录树中出现的所有 Harness 文件——`CLAUDE.md`、`SPEC.md`、`.mcp.json`、`hooks/`、`skills/`、`agents/`、`experience/INDEX.md`、`design-system/`、`docs/adr/`、`scripts/`、模块级 `README.md` 和 `EXPERIENCE.md`——全部提交。

### Code Review 策略

**一个错误的 CLAUDE.md 比一行错误的代码破坏力更大**——代码出错是单点 Bug，提示词出错会让 Agent 系统性地产出有问题的代码。

| 级别 | 文件类型 | Review 要求 | 理由 |
|------|---------|------------|------|
| **严格 Review** | `CLAUDE.md`、`.claude/hooks/`、`.claude/skills/`、`.claude/agents/`、`.claude/settings.json` | 必须 PR + 至少一人 Approve | 直接影响 Agent 行为模式和安全边界 |
| **正常 Review** | `SPEC.md`、`EXPERIENCE.md`、`docs/adr/`、`design-system/` | 建议 PR Review | 影响团队知识对齐，但不直接改变 Agent 执行路径 |
| **低门槛** | `scripts/`、`.claude/experience/INDEX.md` | 变更通知即可 | 影响面可控 |

关键判断标准：**这个改动会让 Agent 在不知情的情况下做出不同的决策吗？** 如果是，就必须 Review。

### 个人偏好管理："分层覆盖"模型

团队成员风格差异是现实——有人爱用 SDD，有人嫌繁琐；有人加自约束，有人嫌别人的经验文件"污染"自己的 Agent。硬性统一引发抵触，完全放任导致 Harness 失效。

解决思路：**分层覆盖**——每一层有明确的权威范围和冲突解决规则。

```
个人层（.claude/settings.local.json, memory/）
  ↓ 覆盖
项目层（.claude/settings.json, CLAUDE.md, hooks/, skills/）
  ↓ 引用
模块层（src/modules/*/EXPERIENCE.md, README.md）
  ↓ 被约束
执行层（CI, import-linter, pyproject.toml）
```

| 层 | 修改方式 | 补充说明 |
|----|---------|---------|
| **执行层** | 不可绕过 | CI、import-linter、pyproject.toml 是硬约束，代码合入的必要条件 |
| **项目层** | PR 博弈 | `CLAUDE.md`、`hooks/` 等团队级 Harness，增删改都要走 PR 并有理由 |
| **模块层** | PR 博弈 | `EXPERIENCE.md` 属于文档层（约束强度 ★★），本质是建议。觉得某条过时或误导 → 提 PR 删除并附理由（如"该 Bug 已在 v2.3 修复"）。经验条目建议**标注日期**，超过 6 个月标记待审查 |
| **个人层** | 自由调整 | `.claude/settings.local.json` 覆盖团队默认权限；不喜欢的 Skill 可以不调用。但**不能移除项目层的强制性约束**（hooks、CI） |

### 经验文件的质量管控

`EXPERIENCE.md` 最容易引发"洁癖 vs 实用"的争议。几条质量原则：

- **写"陷阱条件"，不写"个人偏好"**：`"当 token 为 None 时 refresh_token() 会抛未捕获异常"` ✅；`"不要用 async/await"` ❌
- **标日期**：过时经验不如没有经验
- **少而精**：5 条验证过的陷阱 > 50 条未经检验的"注意事项"
- **实验性经验走 Memory 先验证**：不确定是否普适 → 写入 `.claude/memory/`（个人、不提交），验证有效后再提炼到 `EXPERIENCE.md`（团队共享）

---

**总结**：Harness 治理的核心不是统一所有人的风格，而是建立清晰的**分层架构**——硬约束强制执行，软建议 PR 讨论，个人偏好有逃生舱。

---

## Memory：Agent 自管理的跨会话持久化

Memory 与上面五个层级有本质区别：

> **五个层是人写的、注入给 Agent 的；Memory 是 Agent 自己写的、自己维护的。**

- 架构、文档、经验、约束、执行 —— 都是**人主动编写的工程制品**，回答"我们希望 Agent 遵守什么"
- `.claude/memory/`（`user.md` / `project.md` / `feedback.md` / `reference.md`）→ Agent 在对话中自动提取并持久化的跨会话记忆，回答"Agent 从这次会话中学到了什么"

Memory 不是第六层，而是**横切所有层的持久化机制**。Agent 可以在任何一层学到东西并写入 memory：

| 当 Agent 在… | 学到的东西 | 写入 memory 类型 |
|-------------|-----------|-----------------|
| 文档层 | 用户偏好的技术栈、项目约定 | `user.md`、`project.md` |
| 经验层 | 某个模块的陷阱被验证了 | `project.md` |
| 约束层 | 用户纠正了某种行为风格 | `feedback.md` |
| 执行层 | 某个外部系统的连接方式 | `reference.md` |

**关键类比**：五个层是 Agent 的"规章制度手册"（人写的）；Memory 是 Agent 的"工作笔记"（自己写的）。规章制度可以引用笔记中的经验，但笔记本身是 Agent 在遵守制度的过程中不断积累的。

这也解释了为什么经验层和记忆容易混淆——**EXPERIENCE.md 是人写的陷阱预判，Memory 是 Agent 踩过坑之后自己记下的教训。** 前者是预防，后者是复盘。

# Harness 工程基础概念

## 目录

1. [什么是 Harness？](#什么是-harness)
2. [一个典型的 Harness 目录树](#一个典型的-harness-目录树)
3. [Harness 的五个层级](#harness-的五个层级)
   - [1. 架构层 — 让 Agent "看到"边界](#1-架构层-让-agent-看到边界)
   - [2. 文档层 — 渐进披露，按需下钻](#2-文档层-渐进披露按需下钻)
   - [3. 经验层 — 让 Agent 不踩同样的坑](#3-经验层-让-agent-不踩同样的坑)
   - [4. 约束层 — 可执行规则，而不是口头约定](#4-约束层-可执行规则而不是口头约定)
   - [5. 执行层 — Agent 的"手"和"工具箱"](#5-执行层-agent-的手和工具箱)
4. [Memory：Agent 自管理的跨会话持久化](#memoryagent-自管理的跨会话持久化)

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
│   │   │   ├── EXPERIENCE.md          #       本模块的经验陷阱（从 Git History 提炼）
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
│       └── types.py
│
├── docs/
│   └── adr/                           #    架构决策记录
│       ├── 001-sqlite-not-pg.md       #       为什么选 SQLite — 防止 Agent 走回头路
│       └── 002-jwt-session.md         #       认证方案选型
│
├── design-system/                     #    设计约束（被 Skills 和 System Prompt 引用）
│   ├── tokens.css
│   └── constraints.md
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
│   ├── agents/                        # ⑤ Sub-Agents — 隔离执行的委派单元
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

架构层不靠文档说教，而是靠目录和类型系统让 Agent **客观上无法越界**。

- **模块目录结构**：DDD 限界上下文通过目录隔离，Agent 在修改 `auth/` 时不会误入 `profile/` 的实现细节
- **OpenAPI / 接口契约**：强类型 Schema 消除了 Agent 对参数格式的猜测，API 边界一目了然
- **Type Hints**：Python 类型标注 = 代码级的微型文档，Agent 无需跳转即可理解数据结构

### 2. 文档层 — 渐进披露，按需下钻

文档层回答"为什么要这么做"。Agent 不会一次性吞下所有文档，而是按任务范围按需查阅。

- **CLAUDE.md**：全局行为准则与架构约束，Agent 启动即加载
- **SPEC.md**：可执行规格，定义验收标准。Agent 完成任务后以此为自检清单
- **ADR**：记录历史决策（如"为什么选 SQLite 而不是 PostgreSQL"），防止 Agent 在未来的 PR 中走回头路
- **模块 README**：每个模块维护自己的 Purpose / Interfaces / Constraints，Agent 只需读当前模块

### 3. 经验层 — 让 Agent 不踩同样的坑

经验层是团队与 Agent 之间的"错题本"。某段代码出过什么 Bug、踩过什么坑，沉淀为结构化经验文件。

- **EXPERIENCE.md**：与模块代码 colocate，记录该模块的历史陷阱和反模式
- **INDEX.md**：经验索引入口，让 Agent 按关键词快速定位相关经验

### 4. 约束层 — 可执行规则，而不是口头约定

约束层与文档层的区别在于：文档层靠 Agent 自觉遵守，约束层**编译时或运行时强制拦截**。

- **import-linter**：架构即代码，模块间依赖关系由工具检查，违规即 CI 红灯
- **pyproject.toml / ruff / mypy**：Lint 和类型检查在提交前运行，不规范的代码无法合入
- **CI Pipeline**：提交即验证，Agent 的每一次改动都必须通过全量测试
- **Hooks**：PreToolUse / PostToolUse 管线，在 Agent 调工具之前拦截危险操作（如扫描密钥、阻止 `rm -rf`）

### 5. 执行层 — Agent 的"手"和"工具箱"

执行层定义 Agent 能做什么、怎么委派任务、如何调用外部系统。

- **Skills**：按需注入的工作流（如 code-review、debug、deploy），Agent 识别意图后自动加载对应 Skill
- **Sub-Agents**：隔离执行的委派单元——子代理拥有独立上下文，用于并行执行或保护主会话不受污染
- **settings.json 权限**：Tool 的白名单/黑名单，控制 Agent 能调用哪些系统命令
- **MCP**（`.mcp.json` + `src/mcp/`）：`.mcp.json` 在项目根目录声明 MCP Server（命令、参数、环境变量），Claude Code 启动时自动发现并注册；`src/mcp/` 存放 Server 的实现代码。两者分离：声明让 Agent 知道"有什么能力可用"，实现则是普通源码
- **Scripts**：支撑脚本（数据库重置、种子数据导入），Agent 通过 Tool 调用而非自己手写

这五个层级的核心规律是：**越往上层，约束越"软"（靠 Agent 自觉）；越往下层，约束越"硬"（靠工具和规则强制执行）。** 一个成熟的 Harness 不会只依赖某一层，而是在五层之间形成纵深防御。

---

## Memory：Agent 自管理的跨会话持久化

Memory 与上面五个层级有本质区别：

> **五个层是人写的、注入给 Agent 的；Memory 是 Agent 自己写的、自己维护的。**

- 架构、文档、经验、约束、执行 —— 都是**人主动编写的工程制品**，回答"我们希望 Agent 遵守什么"
- Memory（`.claude/memory/`）—— 是 **Agent 在对话中自动提取并持久化的**，回答"Agent 从这次会话中学到了什么"

Memory 不是第六层，而是**横切所有层的持久化机制**。Agent 可以在任何一层学到东西并写入 memory：

| 当 Agent 在… | 学到的东西 | 写入 memory 类型 |
|-------------|-----------|-----------------|
| 文档层 | 用户偏好的技术栈、项目约定 | `user.md`、`project.md` |
| 经验层 | 某个模块的陷阱被验证了 | `project.md` |
| 约束层 | 用户纠正了某种行为风格 | `feedback.md` |
| 执行层 | 某个外部系统的连接方式 | `reference.md` |

**关键类比**：五个层是 Agent 的"规章制度手册"（人写的）；Memory 是 Agent 的"工作笔记"（自己写的）。规章制度可以引用笔记中的经验，但笔记本身是 Agent 在遵守制度的过程中不断积累的。

这也解释了为什么经验层和记忆容易混淆——**EXPERIENCE.md 是人写的陷阱预判，Memory 是 Agent 踩过坑之后自己记下的教训。** 前者是预防，后者是复盘。

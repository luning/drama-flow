# Harness 工程之项目空间 - 打造 Agent 友好型工程基座

## 目录

1. [什么是项目空间](#什么是项目空间)
2. [一个典型的 Harness 目录树](#一个典型的-harness-目录树)
3. [代码库基础结构 — Harness 的地基](#代码库基础结构--harness-的地基)
4. [Harness 的四个层级](#harness-的四个层级)
   - [1. 文档层 — 渐进披露，按需下钻](#1-文档层--渐进披露按需下钻)
   - [2. 经验层 — 让 Agent 不踩同样的坑](#2-经验层--让-agent-不踩同样的坑)
   - [3. 约束层 — 可执行规则，而不是口头约定](#3-约束层--可执行规则而不是口头约定)
   - [4. 执行层 — Agent 的行动与反馈回路](#4-执行层--agent-的行动与反馈回路)
5. [改造优先级](#改造优先级)
6. [Harness 的团队治理与 Git 管理](#harness-的团队治理与-git-管理)
   - [Git 提交边界](#git-提交边界)
   - [Code Review 策略](#code-review-策略)
   - [个人偏好管理："分层覆盖"模型](#个人偏好管理分层覆盖模型)
   - [经验文件的质量管控](#经验文件的质量管控)
7. [Memory：Agent 自管理的跨会话持久化](#memoryagent-自管理的跨会话持久化)

---

> **核心思想**：让你的代码仓库成为 Agent 的"操作系统"——不是训练 Agent 适应混乱的项目，而是主动将项目改造成 Agent 能精准识别、高效协作的数字基座。

---

## 什么是项目空间

Harness 由两部分构成：**Agent 内核**（模型本身、推理机制、上下文压缩等）和**项目空间**。内核是 AI 工具厂商提供的，工程师无法直接干预；而项目空间是工程师和团队完全自主管理的部分——代码库结构、文档、规则文件、工具配置、经验沉淀，每一项都是团队可以主动建设和持续演化的工程制品。

**Harness Engineering 的实质，就是把项目空间建设好。** 模型在运行时能看到什么、能调用什么、被什么规则约束——这些全由项目空间决定。一个粗糙的项目空间，再强的模型也只能低效试探；一个精心建设的项目空间，普通模型也能稳定完成复杂任务。

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
├── design-system/                     #    可执行设计系统（唯一视觉真相源）
│   ├── tokens/                        #       Layer 1: Design Token
│   │   ├── tokens.css                 #          CSS 变量（:root 定义 60+ 变量，Agent 生成 UI 必须引用）
│   │   └── tokens.ts                  #          TypeScript 等价版（组件动态样式引用）
│   ├── specs/                         #       Layer 2: 约束 + 屏幕规格
│   │   ├── constraints.md             #          业务约束（单 btn-primary、loading 态等，可自动检查）
│   │   ├── design-rules.md            #          AI 生成规则（Skill 触发时自动注入 Prompt）
│   │   └── screens/                   #          屏幕规格（平台无关，驱动多平台代码生成）
│   │       ├── home.yaml
│   │       └── detail.yaml
│   ├── components/                    #       Layer 3: 组件规格
│   │   ├── components.yaml            #          平台无关组件定义（唯一源，生成 CSS/Android XML）
│   │   ├── components.css             #          生成产物：H5 直接引用的 class 库
│   │   └── index.html                 #          组件 Gallery（可视化验证所有组件渲染效果）
│   └── exports/                       #       Layer 4: 平台导出（从 yaml 生成，禁止手改）
│       ├── h5/designsystem.css        #          一键导入：tokens + components 合并包
│       └── android/
│           ├── colors.xml             #          从 tokens.css 生成的 Android 颜色资源
│           └── styles.xml             #          从 components.yaml 生成的 Android 样式
│
├── prototype/                         #    可交互 HTML 原型（引用 design-system，PM 验收用）
│   ├── generated/                     #       从 screen spec 自动生成，改 yaml 即更新
│   │   ├── home.html
│   │   └── detail.html
│   └── README.md
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
│   │   └── INDEX.md
│   │
│   └── memory/                        # Ⓜ Agent 自管理的跨会话记忆
│       ├── user.md
│       ├── project.md
│       └── feedback.md
│
├── tests/                             # 可测试性 — Agent 可直接运行验证改动
│   ├── test_api.py                    #    行为级测试（pytest）
│   └── conftest.py
│
├── scripts/                           # 执行层工具脚本 — Agent 直接调用，输出结构化结果
│   ├── start.sh                       #    启动应用（dev 模式）
│   ├── reset_db.sh                    #    重置数据库（输出：已重置，导入 N 条）
│   └── seed_data.py                   #    导入测试数据
│
└── logs/                              # 可观测性 — 结构化运行日志，Agent 可读取诊断问题
    └── app.log                        #    JSON 格式，含请求/错误/耗时
```

---

## 代码库基础结构 — Harness 的地基

Harness 的四个层级（文档、经验、约束、执行）都是"外挂"到项目上的工程制品，可以独立建设和演化。但它们共同依赖一个前提：**代码库本身的结构质量**。

目录怎么切、模块怎么拆、接口怎么描述、类型怎么定义——这些不是 Harness 层级，而是 Harness 能否发挥作用的地基。一套混乱的单体代码库上，再精心的文档和约束都只能事倍功半；而一套边界清晰的代码库，Agent 能自然地定位任务范围、理解调用关系，甚至无需额外文档。

### 利用 DDD 划分模块边界

推荐基于 **DDD（领域驱动设计）** 来组织代码架构，它和 LLM 的运作方式天然契合：

- **限界上下文 → 模块边界**：每个上下文映射为一个模块目录（`auth/`、`profile/`、`notification/`），Agent 修改某一个时不会误入其他上下文的实现细节
- **通用语言（Ubiquitous Language）→ 命名体系**：目录名、类名、字段名共享同一套词汇，这与 LLM 基于语义匹配的推理模式高度一致，Agent 的"理解"和"生成"都更精准
- **聚合根 → 类型约束**：通过类型系统（OpenAPI Schema、Pydantic 模型、Type Hints）固化为代码级约束，Agent 无需跳转即可理解数据结构的边界和校验规则

**示例**：将一个巨大的 `UserService` 拆分为 `ProfileService`、`AuthService` 和 `NotificationService`。当 Agent 处理"修改头像"任务时，其关注点仅局限在 `ProfileService`，不需要理解整个用户体系。

### 接口契约标准化（OpenAPI / Protobuf）

**强类型协议**比弱类型描述更能防止 Agent 产生通讯幻觉。

| 模糊描述 | 标准化描述 |
|---------|-----------|
| "传一个 id 给用户中心" | OpenAPI JSON：明确 `id` 为 UUID 格式，包含 404 错误响应示例、字段类型与校验规则 |

强制使用 OpenAPI 或 Protobuf 描述所有内部和外部接口，给模型提供清晰的 Schema，可以大幅提升 API 调用代码生成的成功率。

---

## Harness 的四个层级

代码库结构是地基，四个层级是地基之上可独立建设的工程制品，从软到硬排列：

| 层 | 涵盖内容 | 约束强度 | 存在形式 |
|---|---------|---------|---------|
| **文档层** | CLAUDE.md、模块 README、ADR、SPEC、PRD、design-system | ★★☆☆☆ | Markdown，渐进披露，按需下钻 |
| **经验层** | 模块 EXPERIENCE.md、.claude/experience/INDEX.md | ★★☆☆☆ | 结构化经验文件，随代码 colocate |
| **约束层** | import-linter、pyproject.toml、CI、Hooks | ★★★★☆ | 可执行规则 + 管线拦截 |
| **执行层** | Skills、Sub-Agents、MCP、scripts、测试套件、可观测性接口 | ★★★★☆ | 注入 Prompt + 隔离执行 + 反馈回路 |

核心规律：**约束越往下越硬（靠工具强制而非 Agent 自觉）。** 成熟的 Harness 在四层之间形成纵深防御，不会只依赖某一层。

---

### 1. 文档层 — 渐进披露，按需下钻

> **原则**：将知识从工程师脑中同步到 Agent 的"磁盘"——Agent 在运行时无法访问的任何东西都等同于不存在。

文档层回答"为什么要这么做"。Agent 不会一次性吞下所有文档，而是按任务范围按需查阅。底层逻辑是**渐进披露（Progressive Disclosure）**：任何时刻只加载当前任务所需的那一层信息，无关内容不占推理窗口，每层各司其职，不会牵一发动全身。

#### 三层文档体系

```
系统级 MD（CLAUDE.md / README.md）
  └── 顶层架构、核心技术栈选型理由（Decision Log）、全局约束

模块级 MD（每个子目录的 README.md）
  └── 职责定位、对外接口、依赖关系、特殊约束

代码级辅助（Type Hints / JSDoc）
  └── 函数签名、参数含义、"为什么"而非"是什么"
```

- `CLAUDE.md` / `SPEC.md` → 全局行为规则与可执行规格，Agent 启动即加载，完成后以此为自检清单
- `src/modules/*/README.md` → 模块级 Purpose / Interfaces / Constraints，Agent 只需读当前模块
- `docs/adr/` → 架构决策记录（如"为什么选 SQLite"），防止 Agent 走回头路
- `design-system/` → 设计 Token 与约束，被 Skills 和 System Prompt 引用

#### 模块级 README 标准模板

```markdown
## Purpose
本模块负责 [具体职责描述]

## Interfaces
- `GET /api/xxx` — 返回 [描述]
- `POST /api/xxx` — 接受 [参数描述]

## Dependencies
- 依赖 `AuthService` 进行 JWT 校验
- 依赖 `Database` 模块读写用户数据

## Constraints
- 禁止直接操作数据库，必须通过 Repository 层
- 所有错误响应统一使用 `ErrorResponse` Schema
```

`Purpose` 字段是 Agent 语义定位的锚点——处理新任务时，Agent 先基于各模块 Purpose 描述锁定目标目录，再按需读取文件，不必扫描整个 Repo。描述越精准，定位越准，进入上下文的噪音越少。

#### 代码级类型提示的价值

类型定义是给 Agent 最直接的"强力暗示"：

```python
# 没有类型提示 — Agent 需要猜
def get_drama(id, include_episodes=False):
    ...

# 有类型提示 — Agent 直接知道
def get_drama(
    drama_id: UUID,
    include_episodes: bool = False,
    db: Session = Depends(get_db)
) -> DramaDetailResponse:
    """
    获取剧集详情。include_episodes=True 时附带集数列表。
    注意：已下架剧集返回 404，不返回空对象。
    """
    ...
```

#### 架构决策记录（ADR）

**结构化的 ADR** 是 Agent 进行长远演进的"营养来源"。将架构选型、弃用的方案和踩过的坑记录在 ADR 中，当 Agent 重构代码时，通过阅读 ADR 可以自动规避团队已经尝试并证伪的技术方案——避免"3 年后重蹈覆辙"。

```markdown
# ADR-001: 选择 SQLite 而非 PostgreSQL 作为开发环境数据库

## 状态：已采纳

## 背景
...

## 决策
...

## 后果（包括已知的权衡）
...

## 被否决的方案
- 方案 A（原因：...）
- 方案 B（原因：...）
```

---

### 2. 经验层 — 让 Agent 不踩同样的坑

经验层是团队与 Agent 之间的"错题本"。某段代码出过什么 Bug、踩过什么坑，沉淀为结构化经验文件，colocate 在对应模块目录下。

- `src/modules/*/EXPERIENCE.md` → 与模块代码 colocate，记录该模块的历史陷阱和反模式
- `.claude/experience/INDEX.md` → 跨模块经验的索引入口，让 Agent 按关键词快速定位

> **重要前提**：经验层是"遇到问题后才引入"的应对手段，而非前置工程。模型能力在持续演进，Agent 未必像你想象的那么笨——不要把它能自己推理出来的东西写成知识文件，否则只是在制造维护负担。**先让 Agent 直接尝试，真的反复犯同一类错误时，再提炼经验注入。**

#### 什么情况值得沉淀经验

以下信号说明某个任务适合提炼为经验文件：
- Agent 在同类任务上**反复遗漏同一个步骤**（如忘记注册路由、忘记更新 OpenAPI）
- 任务涉及**项目特有的隐性约定**，无法从代码结构本身推断
- 高复杂度长链路任务中，Agent 出现**顾此失彼**的情况

这时将经验显性化，本质是提供搜索空间的修剪（Pruning）——让 Agent 跳过探索阶段，直接进入执行。

**示例**：`NEW_API_ROUTE.md`（在发现 Agent 多次遗漏注册步骤后才创建）

```markdown
# 新增 API 路由 — 执行检查清单

每次新增 API 路由时，必须修改以下位置：
1. `backend/app/api/` — 添加路由处理函数
2. `backend/app/services/` — 添加对应 Service 方法
3. `backend/app/schemas/` — 定义请求/响应 Pydantic 模型
4. `backend/app/api/__init__.py` — 注册新路由（常见遗漏点：不报错但接口 404）
5. `tests/` — 添加对应的行为级测试
```

#### 从 Git History 提炼实现模式

经验文件不必手写，**Git 提交历史本身就是最真实的经验库**——它记录了团队在真实约束下，每类任务实际动了哪些文件。

**提炼流程**：

1. 取出最近一段时间的提交记录（commit messages + diff stat）
2. 按**任务**而非提交聚合：一个功能往往横跨多个提交（数据模型、API、前端各一个提交），要把同一个任务的多个提交当作一个整体来分析
3. 让 LLM 按任务类型归类（"新增功能模块"、"修改数据模型"、"重构模块"…），并识别每类任务的完整变更集
4. 整理成结构化的"执行笔记"存入经验库

```bash
# 按 PR/分支提取完整任务历史（比逐提交更准确）
git log --oneline --stat origin/main..HEAD > task_history.txt
# 或提取近期合并的 PR 记录
git log --merges --oneline --stat --since="3 months ago" > merged_prs.txt
# 然后让 Claude 分析：
# "每个合并记录代表一个完整任务，识别出 5 类最常见的任务类型，
#  并列出每类任务通常涉及的文件集合和执行顺序"
```

**注意：提炼出的是候选项，不是定论。** 以下几类经验应当直接丢弃：

- **偶然经验**：两个文件碰巧同时被改，但并无因果关系
- **Agent 能力范围内的经验**：凭代码结构和类型系统就能推断出的步骤，写出来只是噪音
- **可以用设计声明替代的经验**：能从设计上消除的遗漏，不应靠经验文件打补丁
- **极少触发的经验**：一年用不到一次的场景，等真正遇到时再写

错误的经验比没有经验更危险——Agent 照着错误的检查清单执行，问题更难排查。

#### 将经验文件与任务关键词挂钩

经验提炼出来不够，还要让 Agent **在正确的时机自动加载**。核心原则是**保持 CLAUDE.md 精简**，推荐用渐进披露的方式组织：

```
CLAUDE.md（一级指针，始终精简）
  └── "如果任务触发以下场景，查阅对应经验文件，见 .claude/experience/INDEX.md"

.claude/experience/INDEX.md（二级索引，按需维护）
  ├── 新增 API 路由       → NEW_API_ROUTE.md
  ├── 修改数据模型        → DATA_MODEL_CHANGE.md
  └── 新增 Android 页面   → ANDROID_PAGE.md

.claude/experience/*.md（具体经验文件）
```

CLAUDE.md 只放一句话："遇到以下场景先查 INDEX.md"。新增经验只需更新 INDEX.md，不触碰 CLAUDE.md。Agent 在任务开始时读 INDEX，按需加载相关文件，不相关的经验文件完全不进入上下文。

对于高频且复杂的任务类型，把"加载经验 + 执行任务"整体封装成 Skill，比依赖 Agent 自觉查 INDEX 更可靠——Skill 开头直接 `Read` 对应的经验文件，不依赖 Agent 的主动性。

---

### 3. 约束层 — 可执行规则，而不是口头约定

约束层与文档层的区别在于：文档层靠 Agent 自觉遵守，约束层**编译时或运行时强制拦截**。

- `.importlinter` → 模块依赖规则，Architecture as Code，违规即 CI 红灯
- `pyproject.toml` / `.github/workflows/ci.yml` → Lint + Type Check + 测试，提交即验证
- `.claude/hooks/` → PreToolUse / PostToolUse 管线拦截（扫描密钥、阻止危险命令）

#### Architecture as Code：让机器守护架构边界

**Architecture as Code** 的核心思想是：把架构规则写成**可执行的代码**，而不是藏在 Wiki 或口头约定里靠人工 Review 把关。

以 `import-linter`（Python）为例，"API 路由层禁止直接操作数据库"这条规则可以写成：

```ini
[importrule]
name = No direct DB access from routes
source_modules = app.api
forbidden_modules = app.models
```

这段规则本身就是代码，可以被 Git 管理和版本化。将它放入 CI 流水线后，每次提交都会自动执行——违规时 CI 报错，Agent 读取错误信息并自主修正代码结构，**约束本身就成了 Agent 的纠错信号**。

同类工具：`ArchUnit`（Java/Kotlin）可以用代码断言表达模块依赖规则，原理一致。

#### SOP 即规格（Steps as Constraints）

将团队的 SOP（标准作业程序）编写为 SDD（Spec-Driven Development）约束，强行规范 Agent 的行为轨迹。强调"**过程正义**"：代码写得对不够，过程必须符合规范。最小可行的 SDD 约束写在 `CLAUDE.md` 中即可生效：

```markdown
## SDD 最小约束
1. 接受任务前，先阅读对应模块的 SPEC.md 中的验收标准（AC）
2. 生成代码后，逐条自检 AC，确保所有验收标准被覆盖
3. 修改 API 后运行测试，失败则禁止提交
4. 修改已有 AC 时标注 [Changed]，保留历史意图
```

这种"Prompt SDD"成本为零，适合早期项目和小团队快速切入。随着项目复杂度提升，可逐步引入工具化 SDD 框架，提供完整的规格→计划→执行→验证闭环。

---

### 4. 执行层 — Agent 的行动与反馈回路

执行层定义 Agent 能做什么、怎么委派任务，以及每次行动后能得到什么反馈。工具和反馈是一体的：**Agent 能调用程序，也必须能看到程序的结果**，否则执行就是盲目的。

**工具与委派**

- `.mcp.json` + `src/mcp/` → MCP 工具声明与实现，启动时自动发现
- `.claude/settings.json` → Tool 权限 allowlist / deny list，控制 Agent 能调用哪些系统命令
- `.claude/skills/` → 按需注入的工作流（CR、debug、deploy），Agent 识别意图后自动加载
- `.claude/agents/` → 隔离执行的委派单元（子代理），独立上下文，并行执行，保护主会话不受污染
- `scripts/` → 工具支撑脚本（数据库重置、种子数据导入），Agent 直接调用而非手写

**可测试性 — Agent 能验证自己的改动**

测试套件是执行层的核心反馈机制。Agent 修改代码后，能立即运行测试并读取结果，判断改动是否正确——这让 Agent 形成"改→验→改"的自主闭环，而不是每次都等人检查。

- 测试命令必须可以无交互方式运行（`pytest`、`./gradlew test`、`npm test`），Agent 能直接调用
- 测试输出必须是机器可读的结构化结果（通过/失败/报错行号），而不是只有一个退出码
- 行为级测试比单元测试对 Agent 更有价值：行为测试的失败信息能直接告诉 Agent"哪个接口的哪个场景出错了"，而不是"哪行代码断言失败了"

**可观测性 — Agent 能看到系统的运行状态**

Agent 执行操作后需要确认效果，可观测性决定了它能"看"到多少：

- 结构化日志：应用运行时输出可解析的格式（JSON、明确的错误码），而不是只打印人类可读的字符串
- 脚本反馈：`scripts/` 中的工具脚本应在执行后输出明确的结果（"已重置数据库，导入 42 条记录"），让 Agent 能确认操作是否生效
- MCP 工具返回值：MCP Server 的返回应包含足够的状态信息，Agent 无需额外查询即可判断操作结果

---

## 改造优先级

**最小可行改造**：写好 `CLAUDE.md`（技术栈、架构约束、命名规范、SDD 约束），为每个模块创建 `README.md`。这两步的投入产出比最高，也是大多数项目的起点。

| 维度 | 改造成本 | Agent 收益 | 推荐顺序 |
|------|---------|-----------|---------|
| 文档层（CLAUDE.md + 模块 README + ADR） | 低 | 高 | **优先** |
| 约束层（Prompt SDD → CI/Lint → 工具化 SDD） | 低起步，按需升级 | 高 | **优先** |
| 代码库基础结构（DDD + OpenAPI） | 高 | 高 | 新项目从一开始就做；存量项目渐进重构 |
| 经验层（任务笔记 + Git 挖掘） | 中 | 中（随时间积累价值） | 持续投入，遇到问题再写 |
| 执行层（Skills + Sub-Agents + MCP + 测试/可观测性） | 中高 | 高（规模化后价值凸显） | 团队规模化后重点建设 |

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

团队成员风格差异是现实。解决思路：**分层覆盖**——每一层有明确的权威范围和冲突解决规则。

```
个人层（.claude/settings.local.json, memory/）
  ↓ 覆盖
项目层（.claude/settings.json, CLAUDE.md, hooks/, skills/）
  ↓ 引用
模块层（src/modules/*/EXPERIENCE.md, README.md）
  ↓ 被约束
强制约束（CI, import-linter, pyproject.toml）
```

| 层 | 修改方式 | 补充说明 |
|----|---------|---------|
| **强制约束** | 不可绕过 | CI、import-linter、pyproject.toml 是硬约束，代码合入的必要条件 |
| **项目层** | PR 博弈 | `CLAUDE.md`、`hooks/` 等团队级 Harness，增删改都要走 PR 并有理由 |
| **模块层** | PR 博弈 | `EXPERIENCE.md` 属于文档层，本质是建议。觉得某条过时或误导 → 提 PR 删除并附理由。经验条目建议**标注日期**，超过 6 个月标记待审查 |
| **个人层** | 自由调整 | `.claude/settings.local.json` 覆盖团队默认权限；不喜欢的 Skill 可以不调用。但**不能移除项目层的强制性约束** |

### 经验文件的质量管控

`EXPERIENCE.md` 最容易引发"洁癖 vs 实用"的争议。几条质量原则：

- **写"陷阱条件"，不写"个人偏好"**：`"当 token 为 None 时 refresh_token() 会抛未捕获异常"` ✅；`"不要用 async/await"` ❌
- **标日期**：过时经验不如没有经验
- **少而精**：5 条验证过的陷阱 > 50 条未经检验的"注意事项"
- **实验性经验走 Memory 先验证**：不确定是否普适 → 写入 `.claude/memory/`（个人、不提交），验证有效后再提炼到 `EXPERIENCE.md`（团队共享）

**总结**：Harness 治理的核心不是统一所有人的风格，而是建立清晰的**分层架构**——硬约束强制执行，软建议 PR 讨论，个人偏好有逃生舱。

---

## Memory：Agent 自管理的跨会话持久化

Memory 与上面的地基和四个层级有本质区别：

> **地基和四个层级是人写的、注入给 Agent 的；Memory 是 Agent 自己写的、自己维护的。**

- 代码库基础结构、文档、经验、约束、执行 —— 都是**人主动编写的工程制品**，回答"我们希望 Agent 遵守什么"
- `.claude/memory/`（`user.md` / `project.md` / `feedback.md` / `reference.md`）→ Agent 在对话中自动提取并持久化的跨会话记忆，回答"Agent 从这次会话中学到了什么"

Memory 不是第六层，而是**横切所有层的持久化机制**。Agent 可以在任何一层学到东西并写入 memory：

| 当 Agent 在… | 学到的东西 | 写入 memory 类型 |
|-------------|-----------|-----------------|
| 文档层 | 用户偏好的技术栈、项目约定 | `user.md`、`project.md` |
| 经验层 | 某个模块的陷阱被验证了 | `project.md` |
| 约束层 | 用户纠正了某种行为风格 | `feedback.md` |
| 执行层 | 某个外部系统的连接方式 | `reference.md` |

**关键类比**：地基和四个层级是 Agent 的"规章制度手册"（人写的）；Memory 是 Agent 的"工作笔记"（自己写的）。这也解释了为什么经验层和记忆容易混淆——**EXPERIENCE.md 是人写的陷阱预判，Memory 是 Agent 踩过坑之后自己记下的教训。** 前者是预防，后者是复盘。

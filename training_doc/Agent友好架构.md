# Agent 友好架构

> **核心思想**：让你的代码仓库成为 Agent 的"操作系统"——不是训练 Agent 适应混乱的项目，而是主动将项目改造成 Agent 能精准识别、高效协作的数字基座。

---

## 为什么需要"Agent 友好型"架构？

Agent 并非万能。它的表现上限，很大程度上取决于你提供给它的**上下文质量**。

在一个模糊的项目里，Agent 需要大量推理才能定位任务边界、推断接口约定、猜测命名规范。这不仅低效，还是幻觉（hallucination）的温床。而一个 Agent 友好型项目，会将这些隐式知识显式化——让 Agent 可以直接查阅，而不是反复推断。

改造的方向分五层：**架构层、文档层、流程层、经验层、约束层**。

---

## 4.1 架构层：模块化与边界清晰化

### 利用 DDD 划分限界上下文

Agent 处理的任务规模，应保持在模型推理能力的舒适区内。

过于庞杂的单体应用是 Agent 的噩梦。通过 DDD（领域驱动设计）划分微服务或明确的**限界上下文（Bounded Context）**，可以有效压缩 Agent 需要考虑的上下文空间。

**示例**：将一个巨大的 `UserService` 拆分为 `ProfileService`、`AuthService` 和 `NotificationService`。当 Agent 处理"修改头像"任务时，其关注点仅局限在 `ProfileService`，不需要理解整个用户体系。

### 接口契约标准化（OpenAPI / Protobuf）

**强类型协议**比弱类型描述更能防止 Agent 产生通讯幻觉。

强制使用 OpenAPI 或 Protobuf 描述所有内部和外部接口，给模型提供清晰的 Schema 描述，可以大幅提升 API 调用代码生成的成功率。

**对比**：

| 模糊描述 | 标准化描述 |
|---------|-----------|
| "传一个 id 给用户中心" | OpenAPI JSON：明确 `id` 为 UUID 格式，包含 404 错误响应示例、字段类型与校验规则 |

---

## 4.2 文档层：多层次上下文描述机制

> **原则**：Readme 驱动开发，将知识从工程师脑中同步到 Agent 的"磁盘"。

### 三层文档体系

```
系统级 MD（CLAUDE.md / README.md）
  └── 顶层架构、核心技术栈选型理由（Decision Log）、全局约束
      
模块级 MD（每个子目录的 README.md）
  └── 职责定位、对外接口、依赖关系、特殊约束
  
代码级辅助（Type Hints / JSDoc）
  └── 函数签名、参数含义、"为什么"而非"是什么"
```

### 模块级 README 标准模板

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

### 代码级类型提示的价值

类型定义是给 Agent 最直接的"强力暗示"。

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

---

## 4.3 流程层：Architecture as Code

### 用系统约束替代人工审查

将架构规则编写为 **Lint 规则或 CI 校验**，由机器代替人进行监控。

架构规则示例：
- 模块 A 不得直接调用模块 C 的私有方法
- API 路由层不得直接操作数据库（必须通过 Service 层）
- Fragment 不得包含业务逻辑（只做 UI 绑定）

使用 `ArchUnit`（Java/Kotlin）、`import-linter`（Python）等工具在 CI 环节自动拦截不符合架构设计的 PR。当 Lint 报错时，Agent 可以读取错误信息并自主修正其生成的代码结构——**约束本身就是 Agent 的引导信号**。

### 自动化任务定位机制

Agent 应具备在大型代码库中快速定位关联模块的能力。

**实战流程示例**：
```
任务："修改结算页折扣逻辑"
  ↓
定位 Agent 查询模块索引（基于模块 README 的语义检索）
  ↓
锁定 checkout/ 目录和 discount-calculator.js 文件
  ↓
执行 Agent 只读取相关文件，不扫描整个 Repo
```

这依赖于每个模块 README 中清晰的 `Purpose` 描述——模糊的描述会导致定位失败。

### 知识沉淀闭环（ADR）

**结构化的架构决策记录（ADR）** 是 Agent 进行长远演进的"营养来源"。

将架构选型、弃用的方案和踩过的坑记录在 ADR 中。当 Agent 重构代码时，通过阅读 ADR 可以自动规避团队已经尝试并证伪的技术方案——避免"3 年后重蹈覆辙"。

ADR 基本结构：
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

## 4.4 经验层：复杂任务的"知识注入"与提炼

> **重要前提**：经验层是"遇到问题后才引入"的应对手段，而非前置工程。模型能力在持续演进，Agent 未必像你想象的那么笨——不要把它能自己推理出来的东西写成知识文件，否则只是在制造维护负担。**先让 Agent 直接尝试，真的反复犯同一类错误时，再提炼经验注入。**

### 什么情况值得沉淀经验

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

### 经验的分层管理

经验可按适用范围分层存放，但**不必一开始就建立完整体系**，按需积累即可：

```
Team 级    — 团队公认的避坑指南（.claude/experience/team/）
Project 级 — 项目特有的业务陷阱（.claude/experience/project/）
Individual 级 — 个人偏好的实现模式（~/.claude/experience/）
```

---

## 4.5 约束层：开发习惯与步骤的 SDD 固化

### SOP 即规格（Steps as Constraints）

将团队的 SOP（标准作业程序）编写为 **SDD（Spec-Driven Development）约束**，强行规范 Agent 的行为轨迹。

强调"**过程正义**"：代码写得对不够，过程必须符合规范。最小可行的 SDD 约束写在 `CLAUDE.md` 中即可生效：

```markdown
## SDD 最小约束
1. 接受任务前，先阅读对应模块的 SPEC.md 中的验收标准（AC）
2. 生成代码后，逐条自检 AC，确保所有验收标准被覆盖
3. 修改 API 后运行测试，失败则禁止提交
4. 修改已有 AC 时标注 [Changed]，保留历史意图
```

这种"Prompt SDD"成本为零，适合早期项目和小团队快速切入。

### 从 Prompt SDD 到工具化 SDD

随着项目复杂度提升，Prompt SDD 的局限会显现：AC 自检依赖 Agent 自觉、变更追踪靠记忆、长任务上下文衰减难以避免。社区已有多款成熟的开源 SDD 框架可以引入，它们提供完整的规格→计划→执行→验证闭环，同时各阶段均有独立命令，工程师可按需调用，不必每次走完整流程。

> 各框架的对比与选型指南见 [SDD工具介绍.md](SDD工具介绍.md)。

### 打造团队专属 SDD

开源 SDD 框架提供的是通用骨架，团队可以在此基础上**扩展出自己的 SDD**，将项目特有的约束和知识内置进去：

```
开源 SDD 框架（骨架）
  + 团队技术规范（命名约定、禁止跨层调用等）
  + 项目特有检查点（必须更新 OpenAPI 文档、必须运行集成测试）
  + 领域经验（业务逻辑陷阱、历史踩坑的修复路径）
  = 团队专属 SDD
```

这与 [4.4 经验层](#44-经验层复杂任务的知识注入与提炼) 的经验库形成联动——经验层沉淀"做什么"的知识，约束层固化"怎么做"的流程，二者合力才能在高复杂度任务中持续保持 Agent 的输出质量。

---

## 总结：改造优先级

| 层级 | 改造成本 | Agent 收益 | 推荐顺序 |
|------|---------|-----------|---------|
| 文档层（CLAUDE.md + 模块 README） | 低 | 高 | **优先** |
| 约束层（Prompt SDD → 工具化 SDD） | 低起步，按需升级 | 高 | **优先** |
| 架构层（DDD + OpenAPI） | 高 | 高 | 新项目从一开始就做 |
| 经验层（任务笔记 + ADR） | 中 | 中（随时间积累价值） | 持续投入 |
| 流程层（Architecture as Code） | 高 | 中 | 成熟团队 |

**最小可行改造**：写好 `CLAUDE.md`（技术栈、架构约束、命名规范、SDD 约束），为每个模块创建 `README.md`。这两步的投入产出比最高，也是本项目实战的起点。

AI-Native 研发范式培训

# 课程大纲

## 第一部分：认知地图 — AI Native 的本质与 Harness Engineering（约 1h）

> **目标**：建立 AI Native 思维模型，理解 Harness Engineering 的概念与行业实践，明确"工程师能控制什么"。

**1.1 AI Native（AI 原生）的本质**

- 类比云原生：生产力跃升后围绕 Agent 重新设计研发架构，而非把 AI 当辅助工具叠加
- AI Powered（人驱动 1–2 个 Agent）vs AI Native（1 人并发 N 个 Agent）的关键差距
- 影响 Agent 应用深度的三要素：模型内核、Harness 项目空间、项目架构

**1.2 Harness Engineering — 概念与行业实践**

- 三层范式演进：Prompt 工程（怎么问）→ Context 工程（给模型看什么）→ Harness 工程（模型在什么机制里干活）
- 头部公司实践精华：生成—评估分离（Anthropic）、上下文工程 + 架构约束（OpenAI）、独立 Verifier 三角（Google DeepMind）、减少工具反升成功率（Vercel）
- Harness 六大核心模块：上下文管理、工具编排、验证机制、状态管理、可观测性、人类接管

**1.3 Agent 内核 vs 项目空间 — 工程师能控制什么**

- Agent 内核（厂商提供）：LLM + 感知 / 规划 / 推理 / 上下文 / 工具调用 / 权限 / 记忆 / 子代理
- 项目空间（工程师完全自主）：代码结构、文档、规则、工具、经验——Harness 工程主战场
- 工程师角色重塑：从"实现者"转向"Harness 设计师"
- [演示] 空白 vs 完善 Harness 下，Agent 完成同一任务的路径差异与幻觉率对比

---

## 第二部分：规格驱动开发 — 给 Agent 精确的任务边界和流程约束（约 1.5h）

> **目标**：掌握可执行 Spec 编写方法，理解 SDD 工具生态，深入掌握自定义 SDD 的设计与构建，从"描述需求"升级到"定义流程"。

**2.1 可执行 Spec — 格式、AC 质量与失败模式**

- 五段式：领域名词 → 前置条件 → 主流程 → 异常处理 → 验收标准（AC）
- AC 质量标准：可验证、无歧义、无实现细节；三方共用：开发者自检、Agent 自检、自动化测试
- 失败模式：Agent 填充错误实现；约束跨 Session 遗失；多 Agent 出现分歧
- [练习] 模糊 PRD → 可执行 Spec 全过程

**2.2 SDD 工具生态 — 工具如何突破 Prompt 的结构性限制**

- Prompt SDD 局限：强制验证 / 上下文隔离 / 审计追踪 / 变更隔离
- 主流工具定位与选型：OpenSpec（棕地变更隔离）、Superpowers（工程纪律层）等
- OpenSpec 剖析：三层架构；Schema 定义工件依赖图；Explore → Propose → Apply → Archive

**2.3 定制 SDD 工具 — 以 OpenSpec 为例**

- Schema 是 OpenSpec 的扩展单元：定义 artifact 列表、依赖链、apply 行为
- template vs instruction：template 控制工件输出结构，instruction 控制 AI 填充行为
- [演示] 定制 DramaFlow 的 schema

---

## 第三部分：结构化业务规则 — 从增量 PRD 到唯一事实来源（约 0.5h）

> **目标**：掌握将散文 PRD 改造为 Agent 可直接消费的结构化资产：每个业务概念一份常青文档，唯一事实来源，Git 管理历史。

**3.1 核心问题：Agent 为什么读不懂 PRD**

- 增量文档：功能全貌散落在多份版本文件，Agent 无法主动追溯拼出当前状态
- 边界模糊：同一句自然语言让 Agent 实现三次，得到三种不同错误文案
- AC 不可执行：散文验收标准无法被 Agent 自检或测试工具直接提取

**3.2 改造方案（参考 OKF）**

- [演示] 散文 PRD vs 结构化需求，展示 Agent 消费差异
- 一概念一文档：每个功能一份常青文档，迭代时更新而非叠加版本文件
- YAML 文件头：声明 ID、状态（approved / deprecated）、关联 Spec
- 正文结构化：业务流程 + 异常处理表格 + AC 块
- 行内约束标记：`[MUST]` / `[MUST NOT]` / `[SHOULD]` / `[CONSTRAINT:类型]`
- Git 管理历史：变更有 diff、有 log，正文不维护"修改记录"

**3.3 实施建议**

- PM 友好：Agent 辅助维护（PM 描述 → Agent 更新 → PM 确认），可反向生成散文 PRD 供汇报
- 存量处理：新旧双轨，触碰则改，从核心链路开始
- 分级落地：最小（AC 块）→ 中等（+YAML+异常表）→ 完整（常青文档+Git+Agent 维护）

---

## 第四部分：可执行设计系统 — 设计一处定义，人机共同执行（约 0.5h）

> **目标**：理解可执行设计系统，建立"代码即设计源"的工作流，将工程师的翻译工作降至最低。

**4.1 可执行设计系统的结构**

- 原型及设计系统演进：文档时代 → Figma时代 → 可执行设计系统时代
- AI 越能生成，设计约束越重要 —— 否则风格漂移、组件重复、UX 崩坏
- 设计系统五层结构：业务约束 → Design Token → 组件 Runtime → AI Generation Rules → Figma 协作层
- 原型生产方式：从 Figma 出发，从自然语言出发，从 Screen Spec 出发

**4.2 在设计系统约束下生成 UI**

- AI 读取设计系统文件后生成新页面，验证是否自动遵守 Token/组件/约束
- Prototype Skill 封装：将设计系统注入流程固化为 Skill
- [演示] 设计系统约束下的页面生成与约束验证

**4.3 三层视觉验收**

- 第一层（自动）：Skill 扫描 hardcoded 值 + ESLint/CI 拦截
- 第二层（工具辅助）：截图对比 + 像素级检查
- 第三层（人工）：视觉节奏、信息层级、交互情绪

---

## 第五部分：项目空间建设 — 让代码库成为 Agent 的操作系统（约 1h）

> **目标**：掌握 Harness 项目空间的四层架构，将项目改造成 Agent 可精准识别的数字基座。

**5.1 四层架构与即时可用的建设方法**

- 典型项目的完整 Harness 项目空间展示
- 文档层：全局行为规则及索引 + 模块 README
- 经验层（遇到问题后引入）：从历史提炼任务级变更模式
- 约束层：import-linter / ArchUnit + pre-commit hooks 自动拦截架构违规；Hooks / Plugin 事件自动验证
- 执行层：Skills + MCP + 自动化脚本

**5.2 Harness 团队治理**

- Git 管理边界：哪些纳入版本控制哪些不纳入
- 经验文件质量管控：防止"越来越长、Agent 开始忽略"的退化模式
- CODEOWNERS 设置：Harness 文件有指定审阅者，防止质量腐化，Harness 的补丁思维

**5.3 [练习] 为示例项目构建文档、经验及约束层**

- 为一个模块编写符合四段模板的 README.md，判断必要性
- 补充一条 Architecture as Code 约束，验证 CI 能拦截违规代码
- 从 Git History 提炼一条有价值的经验，判断必要性

---

## 第六部分：工具系统 — 为 Agent 构建可控工具链（约 1h）

> **目标**：掌握 Skills 与 MCP 的设计方法论，理解两者分工与组合，为组织沉淀可复用 AI 工具资产。

**6.1 Skill 工程设计**

- Skill 的本质：注入系统提示的指令，改变 Agent 怎么想（工作流与规则）
- 四大设计原则：参数最小化（从上下文推断）、结构化反馈（可自修复）、幂等性（反复调用一致）、错误恢复与降级
- 固定逻辑剥离：脚本承担确定性操作，Skill 只负责调用与结果解读——判断标准：能用 if/else 写死吗？
- [演示] rebuild-deploy Skill 的完整创建过程

**6.2 MCP 工程设计**

- MCP 三种原语：Tools（模型调用）、Resources（宿主读取）、Prompts（用户选择）；Agent 场景下通常只用 Tool
- 设计原则：Tool 描述比代码重要、返回值让模型能消化、接口防误用（不接受原始SQL、读写分离）
- [演示] 在示例项目中创建一个只读的 MCP Tool

**6.3 企业级工具体系**

- Skills vs MCP 选型框架：Skill 改变怎么想，MCP 增加能做什么，两者可组合
- 三层分级：个人级 → 项目级 → 企业级；Skill 边界设计：参数优先于复制，完整任务边界
- MCP 安全运营：只读账号 + 接口参数化 + 敏感字段脱敏 + 审计日志

---

## 第七部分：应对复杂项目的知识工程（约 1h）

> **目标**：理解知识工程的结构与价值，掌握 Skill / Knowledge / Router 三层分工，为复杂领域项目构建 Agent 可路由、可加载的知识资产。

**7.1 问题与方案全景**

- 复杂领域大量关键知识散落在代码库外（芯片手册、历史故障、隐性约定）；`Spec + Engineering Knowledge → Implementation`
- 双轨并行：SDD 定推理模式，Knowledge 定内容，Router 为 SDD 注入领域上下文，Skill 保持通用不变

**7.2 Skill vs Knowledge — 核心资产**

- Skill 是推理模式（价值 ~5–10%）；Knowledge 是领域沉淀（~90–95%）
- 常见误区：为每个场景建专用 Skill → 几十个结构相同文件；正确：Skill 只定推理模式，领域内容归入 Knowledge

**7.3 Knowledge 五层分层模型**

- 五层：架构知识 / 编码规范 / ADR / 领域知识 / 项目知识
- 存储选型：单项目 → `knowledge/` 目录；多项目共享 → 独立 repo + submodule；体量过大 → RAG；优先 git，而非 Wiki

**7.4 Router — 为 SDD 注入领域上下文**

- Router 三职责：**选择器**（识别场景）/ **加载器**（注入知识）/ **精化器**（细化步骤）
- 使用 OpenSpec 时，自定义 Schema 天然承担 Router 职责
- 演进路径：Skill 内嵌路由（初级）→ 独立 Router 文件（成熟）

---

## 第八部分：AI 原生的测试体系：Spec 驱动 + Agent 执行（约 1h）

> **目标**：建立 AI 时代的行为验证闭环，防止"10 倍代码速度 = 10 倍技术债"。

**8.1 Spec-TDD - 以 AC 为起点的开发循环**

- [练习] 创建 spec-validate Skill：从 Spec 提取 AC → 对比测试覆盖 → 输出覆盖矩阵
- [演示] 核心流程：AC 写入 Spec → 行为级测试 → 实现 → spec-validate 确认覆盖 → 自愈
- AC 质量 = 测试质量 = 代码验收质量，AC 最终确认必须由人完成（HITL）

**8.2 Agent 驱动的验收验收**

- 架构及框架：Agent CLI → ADB/UI Automator → 设备（无 Android 环境的学员使用 Web 版页面 + 浏览器自动化完成同等练习）
- Mission 文件直接对应 Spec AC；screen_knowledge/ 跨会话经验库避免重复踩坑
- [演示] 执行循环：案例应用的完整验收流程

**8.3 提升 Agent 驱动自动化的效果**

- **可观测性**：结构化日志让 Agent 自己读懂结果，避免人肉搬运
- **可测试性**：系统行为稳定可重复，并暴露接口（状态查询、Hook 等）供 Agent 感知与控制
- **Harness 积累经验**：失败模式沉淀为 screen_knowledge / Skill，而非靠感觉调整

---

## 第九部分：工程师不可让渡的能力 — 设计力与代码审美非常重要（约 0.5h）

> **目标**：打破"AI 会写代码，工程师只需审批"的误区——AI 提速的是实现，加速暴露的是设计缺陷；代码品质守护、架构判断、职业心法，是工程师在 AI 时代的核心竞争力。

**9.1 AI 代码高频错误模式 + CR 策略**

- 五类高频错误：重复逻辑、状态泄漏、命名混乱、架构违规、冗余注释
- [练习] cr-refactor Skill：扫描 diff → 按五类错误输出优先级清单
- 重构铁律：不改功能只改结构；先计划再执行；每步运行 spec-validate，失败回滚
- 决策框架：逻辑正确但结构混乱 → 重构；逻辑本身有缺陷 → 重写

**9.2 AI 时代工程师心法**

- 架构不外包：约束、权衡、边界由人决定，实现交给 Agent
- 约束必须显式：CLAUDE.md / AGENTS.md + Spec 一次写入永久生效，不让 AI 猜
- 干预是信号：每次纠正后问一句"这需要编码进 Harness 吗"
- 小步拆解：任务越大，本质是约束越缺失
- Git 是后悔药：大改前 commit，改完逐文件 diff，走偏立即回滚
- 必须看代码：AI 加速生成也加速技术债，每迭代一次 CR + 重构
- 管理上下文窗口：主动 compact、何时开新 Session、何时 fork、合理使用子代理
- 提升系统可观测性：结构化日志让 Agent 能自主定位问题，比每次手动整理日志更有杠杆
- 分清任务类型：目标明确可验证 → 放心给 AI；涉及权衡无唯一解 → 人来决策
- 保持 HITL：AC 确认、安全逻辑、数据模型重大变更、架构决策、合并前审阅——人工最终裁决

---

## 第十部分：刻意进化 — 让 Harness 越来越强（约 1h）

> **目标**：建立"干预是信号、纠正即 Harness 改进"的工程习惯，通过 Agentic Harness Engineering 让系统自主进化。

**10.1 两种工程师的分野**

- 路径 A：Agent 犯错 → 纠正 → 继续 → 等下一个模型。每月重复同样纠正
- 路径 B：Agent 犯错 → 纠正 → "这次教训，需要编码进 Harness 哪一层？"
- 核心认知：模型自然进步，Harness 不会——只在工程师主动决定时才进化

**10.2 三类进化场景（问题现象 → Harness 层级）**

- 操作安全：每次询问权限 → 权限配置（settings.json / opencode.json）；不询问删文件 → 安全规则；多 Agent 改同一文件 → Worktree 隔离
- 任务边界：直接写代码没澄清 → CLAUDE.md 任务启动规则；宣布完成但没验证 → DoD；长会话性能下降 → 上下文重置时机
- 经验沉淀：选了已排除的方案 → ADR；口头纠正下次又犯 → 写入永久规则；规则文件过长被忽略 → 封装为 Skill

**10.3 Agentic Harness Engineering**

- 规模瓶颈：模型和 Agent 持续迭代，手工优化跟不上——自动化是唯一出路
- 数据基础：本地 Session 记录是起点，从中提取高频失败模式
- [演示] 失败轨迹 → 分层映射 → 自动生成规则 → 验证改进效果

**10.4 飞轮与突围路径**

- 飞轮：干预 → Harness 改进 → 任务颗粒度增长 → 干预减少 → 更多 Agent
- 刻意修剪：定期清理过时规则，避免 Harness 腐化成负担
- 突围路径（范围 × 难度）：小范围简单 → 立即可做；小范围复杂 → 团队级 Spec；大范围简单 → 先单系统再跨系统；大范围复杂 → 隐性知识，长期目标
- [练习] 分析案例项目 Harness 的可优化内容

---

## 第十一部分：多 Agent 规模化 — 从单兵作战到 Agent 团队（约 1h）

> **目标**：掌握多智能体角色分工与并发编排，跑通"1 人 ↔ N 角色化 Agent"的吞吐量跃迁。

**11.1 Subagent vs Multi-Agent**

- Subagent：同会话内调度，并行度受限；适合独立子查询
- Multi-Agent：独立进程，无共享内存——靠外部制品（FD 文件、Git、任务单）+ 显式合同协作
- 跑不起来的根因：缺的不是工具，是跨 Agent 的协作合同与状态载体

**11.2 角色模型、编排模式与工具**

- 三角色链：PM → Planner → Worker；合同载体：FD 文件 + FEATURE_INDEX.md；人工评审在三个关键节点介入
- 三种编排：扇出-扇入（无依赖并行）、流水线（阶段串行）、竞合（多解择优）；HITL 在各模式关键节点介入
- 四件套：Tmux（终端隔离）+ Git Worktree（目录隔离）+ FD 文件（共享状态）+ 斜杠命令（生命周期卡口）
- [演示] 用四件套实现 1 人驱动多 Agent 并行开发

**11.3 规模化节奏与挑战**

- 递进：单 Agent → 2 串行 → 3-4 扇出 → 8 全矩阵
- 上限：1–4 并发为高效区，8 为极限；适用范围：FD 间无强依赖、不需要太多并发或全自动流水线
- 常见挑战：Token 放大（分层）、信息衰减（结构化传递）、文件冲突（Worktree 隔离）

---

## 第十二部分：生产力跃升后的组织进化 —— 角色、协作、度量与行业案例（约 1h）

> **目标**：理解生产力跃升带来的深层矛盾，从角色、协作、组织形态、效能度量四个维度看变革方向，结合国内外企业案例理解转型路径与常见陷阱。

**12.1 生产力悖论**

- DORA 2025：个人产出翻倍，组织交付指标几乎没动——瓶颈从"写代码"转移到"审代码"与决策链条
- 核心结论：个人技巧必须沉淀为团队 Harness，才能转化为组织产能；提效必须带动协作重构

**12.2 各角色价值重心迁移**

- **PM** → 规格架构；**设计师** → 体验判断 + 设计系统；**开发** → Harness 设计师；**测试** → 意图守护者；**运维** → 可观测性设计者
- 知识壁垒削薄后职能边界软化，新角色涌现：规格架构师、Harness 平台工程师、AI 质量工程师
- 行业案例：执行层与判断层的边界——某互联网金融企业的教训与修正

**12.3 协作与组织形态**

- 协作重构：串行交接 → Spec 驱动并行；HITL 检查点取代交接会议；协作产物转向 Spec/设计系统/ADR
- 组织形态：职能部门 → 双层模型（产品特性团队 + 平台 CoE）；人机配比成为组织设计参数
- 行业案例：Microsoft 协作单元重组、Duolingo AI-first 制度性重组、Moderna AI 统一编制规划
- 落地难点：AI 是放大器——隐性知识显式化是最难突破的天花板

**12.4 AI Native 效能度量**

- 度量核心：从"人完成了多少"到 **HAF**；警惕 Goodhart 定律——"AI 生成占比"当 KPI 驱动行为而非结果
- 五层指标：**AI 采纳** → **Agent 生产力** → **Harness 成熟度** → **工程质量** → **交付效率**；先行信号：人均管理 Agent 数、平均交付时间、线上缺陷率
- 落地原则：度量用于改进 Harness 而非考核个人；采纳与质量层联动，防止"快而烂"

---

# 规格驱动开发（Spec-Driven Development）- 给 Agent 精确的任务边界和流程约束

## Vibe Coding 的天花板

Vibe Coding 很爽——描述一个想法，AI 立刻给出代码。在小项目、一次性脚本上，这种方式效率惊人。

但它有一个致命的天花板：**AI 不知道"做到什么程度算完成"。**

```
你：做一个登录功能                              AI：好的 ✓
你：邮箱不存在时要返回 401                      AI：好的，修改了 ✓
你：错误文案不能暴露"邮箱不存在"                AI：好的，改了 ✓
你："记住我"勾选后要持久化 Token                AI：好的，加了 ✓（但之前的 401 逻辑又忘了）
```

每次对话都在"打地鼠"：改了 A，AI 忘了 B。多轮迭代后，没人知道当前状态是否满足所有需求。

**SDD 的回答是：在编码前，把"怎么做才算完成"写清楚。** 规格不再只是给人读的文档，而是**直接驱动 AI Agent 行为的可执行工件**。

---

## 三个核心概念的关系

| 概念 | 是什么 | 类比 |
|------|--------|------|
| **可执行 Spec** | 一份有结构、可被验证的规格文档（工件）| 单元测试文件 |
| **SDD / 规格驱动** | 用可执行 Spec 驱动 AI 开发的方法论 | TDD 方法论 |
| **SDD 工具** | 自动化执行 SDD 工作流的工具链 | JUnit / pytest 框架 |

你可以写可执行 Spec 但不做完整 SDD，就像你可以写单元测试但不做 TDD。  
但 SDD 没有可执行 Spec，就无从谈起。

---

## 可执行 Spec：规格驱动的基础工件

### 为什么 PRD 不够用

| 维度 | PRD.md | SPEC.md |
|------|--------|---------|
| **读者** | PM、设计师、管理者 | 开发者、AI Agent |
| **粒度** | 功能列表、用户故事 | 领域名词、前置条件、主流程、异常处理、AC |
| **是否可执行** | 否（意图层）| 是（验收层）|

PRD 的 gap 在人工开发时靠沟通弥补，**但 AI 没有机会问你**——SPEC.md 就是那个答案。

### 五段式格式

```
领域名词 → 前置条件 → 主流程 → 异常处理 → 验收标准（AC）
```

**领域名词**：统一概念定义，消除歧义。

```
| 术语           | 定义                               |
|---------------|-----------------------------------|
| Access Token  | 短期令牌（默认 2h），用于 API 请求鉴权 |
| Refresh Token | 长期令牌（默认 7d），用于静默续期      |
```

**前置条件**：系统在此流程开始前必须满足的状态。

```
- SQLite 数据库和 User 表已初始化
- FastAPI 服务已配置 JWT 密钥和过期时间
```

**主流程**：用户操作 + 系统响应，步骤化描述。

```
1. 用户输入邮箱 + 密码
2. 客户端提交 POST /api/auth/login
3. 服务端校验，通过 → 签发 Access Token + Refresh Token
4. 返回 200 OK + { access_token, refresh_token, user }
```

**异常处理**：穷举边界情况，每种情况给出明确的错误响应。

```
| 异常场景      | 错误响应                    |
|-------------|--------------------------|
| 邮箱不存在    | 401 + "邮箱或密码错误"      |
| 密码错误      | 401 + "邮箱或密码错误"      |
| 邮箱格式非法  | 422 + "邮箱格式不合法"      |
```

**验收标准（AC）**：每条 AC 必须是**可测试的**——开发者自测、AI 自检、自动化测试三路共用同一份标准。

```
AC-1：正确邮箱 + 正确密码 → 200 OK，响应体包含 access_token、refresh_token、user
AC-2：邮箱不存在 → 401，message 为"邮箱或密码错误"（不暴露具体原因）
AC-3：密码错误 → 同 AC-2
AC-4：邮箱格式非法 → 422
AC-5：勾选"记住我" → Token 写入 EncryptedSharedPreferences，重启 App 不需重新登录
```

### AC 是合同

一条写得好的 AC，可以被 AI 直接翻译成测试用例：

```
AC-2：邮箱不存在 → 401，message 为"邮箱或密码错误"
```
↓ AI 生成
```python
def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "x@x.com", "password": "abc"})
    assert resp.status_code == 401
    assert resp.json()["message"] == "邮箱或密码错误"
```

**AC 的质量 = 测试的质量 = 代码验收的质量。**

AC 是业务承诺，AI 可以从 PRD 草稿自动提取五段式 Spec 骨架，但**人工审核 AC 不可跳过**。

---

## SDD 工作流：用 Spec 驱动 AI 开发

### CLAUDE.md 中的最小约束（Prompt SDD）

最轻量的实现方式，零工具成本：

```markdown
## SDD 最小约束

1. 接受任务前，先阅读对应模块的 SPEC.md 中的验收标准（AC）
2. 生成代码后，逐条自检 AC，确保所有验收标准被覆盖
3. 修改已有 AC 时，在旁边标注 [Changed]，保留历史意图
```

写入 CLAUDE.md 后，Agent 在每次任务开始时会自动读取并遵循。

### `spec-validate` Skill：AC 覆盖自动检查

Prompt SDD 依赖 Agent 自觉性。为了把"自检"变成可验证的动作，可以实现 `spec-validate` Skill：

```
spec-validate 执行流程：
1. 读取 SPEC.md，提取所有 AC 编号和描述
2. 扫描测试文件，匹配每条 AC 是否有对应测试用例
3. 输出覆盖报告：已覆盖 / 缺失 / 测试存在但 AC 描述不匹配
4. 对缺失的 AC，自动生成对应测试用例并写入测试文件
```

以 SPEC.md 为唯一来源，spec-validate 是 SDD 的验收门禁——每次迭代结束前跑一遍，确保 AC 全覆盖。

---

## 增量 Spec：需求演进时怎么做

这是最容易被忽视、也是最容易出问题的环节。

**迭代 3 的真实场景**：首页从"按分类展示"改为"个性化推荐"。原来的 SPEC.md 里有 `AC-Home-3：分类 Tab 展示所有剧集分类`——这条 AC 现在不再适用了。怎么处理？

### 三种 AC 处理方式

**直接覆盖**：需求完全替换，旧逻辑作废。

```
AC-Home-3：首页展示个性化推荐列表，基于用户观看历史排序
           （原"分类 Tab"逻辑已移除）
```
历史由 git 记录，SPEC.md 始终反映当前意图。这是**推荐做法**——Spec 是当前真相，不是变更日志。

**追加**：在原功能基础上新增行为，旧 AC 仍然有效。

```
# 原 AC 保留
AC-Player-1：点击集数 → 加载视频，显示进度条

# 追加新 AC
AC-Player-6：播放中展示倍速按钮（0.5x / 1x / 1.5x / 2x）
AC-Player-7：切换倍速后立即生效，不中断播放
```

**废弃**：功能下线，不再验收。删除对应 AC，依赖 git 保留历史。

### 增量 Spec 的操作节奏

```
需求变更确认
   ↓
定位受影响的 AC（哪些要改 / 哪些要加 / 哪些要删）
   ↓
更新 SPEC.md（直接改，不保留"旧版本注释"）
   ↓ 人工确认变更范围 ← HITL 检查点
Spec 定稿
   ↓
Agent 读新 Spec 实现 → 自检新 AC
   ↓
spec-validate 验证覆盖率（新 AC 必须有测试）
   ↓
git commit（历史自动保留）
```

### 不要做的事

| 反模式 | 问题 |
|--------|------|
| `~~AC-3：旧逻辑~~` 加删除线保留在文件里 | Spec 变成变更日志，Agent 搞不清楚哪条有效 |
| 追加 `AC-3-v2` 版本号 | 版本管理是 git 的职责，不是 Spec 的 |
| 旧逻辑注释掉留着"以防万一" | AI 会读到注释并产生混淆 |

> **原则：SPEC.md 只反映当前意图。历史意图交给 git。**

---

## 工具化 SDD：何时升级、升级到哪里

Prompt SDD 够用，直到遇到这些信号：

| 信号 | 下一步 |
|------|--------|
| Agent 直接开干，方案考虑不周、遗漏边界情况 | 引入 **superpowers brainstorming**（行动前充分思考） |
| 改了 A 忘了 B，或多轮迭代后不清楚哪些需求已完成 | 引入 **OpenSpec**（开发内容和跟进的完整性） |

---

# OpenSpec 工作原理

## OpenSpec 是什么

在规格驱动开发（SDD）中，每个变更会产生 proposal、specs、design、tasks 等工件。变更多了，工件依赖、完成状态、同步逻辑就会失控。

OpenSpec 用 **Schema 定义工件依赖图**，用 **CLI 跟踪状态并返回下一步指令**，用 **Skills 把 CLI 包装成对话式命令**——让 Agent 知道"现在该干什么、接下来干什么"。

> 类比：SDD 工件是源代码，OpenSpec 是 Git——它不创造内容，但管理状态、依赖和生命周期。

---

## 三层架构

```
┌──────────────────────────────────────────────────┐
│  Skill 层 (explore / propose / apply / archive)   │
│  对话包装：选 change、展示进度、确认风险             │
├──────────────────────────────────────────────────┤
│  openspec CLI 层 (list / new / status / instructions) │
│  schema 感知 + 状态机 + 指令生成，不依赖特定 LLM    │
├──────────────────────────────────────────────────┤
│  文件系统层 (openspec/changes/*.md, .openspec.yaml)  │
│  持久化内容 + 元数据，纯 Git 管理                   │
└──────────────────────────────────────────────────┘
```

Skill 通过 `openspec instructions` 动态获取上下文，不假设具体文件路径——Schema 换了，Skill 不用改。

---

## Schema：变更的"蓝图"

每个 change 的 `.openspec.yaml` 声明使用哪个 schema。内置 schema `spec-driven` 的完整定义：

```yaml
name: spec-driven
version: 1

artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    instruction: "Create the proposal document..."
    requires: []                       # 无依赖，总是第一个

  - id: specs
    generates: "specs/**/*.md"
    template: spec.md
    requires: [proposal]

  - id: design
    generates: design.md
    template: design.md
    requires: [proposal]

  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, design]

apply:
  requires: [tasks]                    # tasks 写完才能开始实现
  tracks: tasks.md                     # 用 tasks.md 跟踪进度
```

CLI 判断依赖是否满足的逻辑很简单：`artifact.generates` 对应的文件存在 = 工件完成；文件不存在 = 下游 blocked。

每个 change 存储在 `openspec/changes/<name>/` 下，工件文件即上面 `generates` 字段对应的路径：`.openspec.yaml`（元数据）、`proposal.md`、`specs/`、`design.md`、`tasks.md`。

---

## 四个 Skill

一个 change 的完整生命周期：**Explore（可选）→ Propose → Apply → Archive**

### Explore — 探索模式

**触发**：`/opsx:explore [可选：主题/change名]`

只思考不实现的安全空间——可以读代码、画图、对比方案，但绝不能写应用代码。无固定步骤，无强制输出。探索后可能流入 Propose、更新已有工件、或只是澄清思路。可在任意时刻介入。

### Propose — 创建变更

**触发**：`/opsx:propose [change名或描述]`

创建变更目录 → 按拓扑顺序调用 `openspec instructions <artifact> --json` 获取模板和指引 → Agent 填充内容并写入文件 → 直到 `apply.requires` 全部完成。

### Apply — 执行变更

**触发**：`/opsx:apply [可选：change名]`

调用 `openspec instructions apply --json`，CLI 返回 state：

| 条件 | state | Agent 行为 |
|------|-------|-----------|
| 必需工件缺失 | `blocked` | 提示补充工件 |
| tracks 文件不存在或无 checkbox | `blocked` | 提示先生成 tasks |
| 全部 `- [x]` | `all_done` | 建议归档 |
| 有未完成 | `ready` | 读 contextFiles，逐任务实现，完成即勾掉 |

### Archive — 归档变更

**触发**：`/opsx:archive [可选：change名]`

将 change 目录移到 `archive/YYYY-MM-DD-<name>/`。归档前做三检查：工件完整性、任务完成度、delta spec 是否同步到主 spec。不拦死，但必告知。

---

## instructions 命令的内部原理

`openspec instructions` 是 Skill 与 CLI 之间的核心接口。

**Propose 阶段**（调用 artifact 指令）：

```
openspec instructions proposal --change "xxx" --json
  → 读 .openspec.yaml → 三层查找 schema.yaml
  → 构建工件 DAG，拓扑排序，检测已完成工件
  → 读取模板文件和项目 config.yaml
  → 返回 JSON: { template, instruction, context, rules, dependencies, unlocks }
```

| 字段 | 来源 | 是否写入文件 |
|------|------|-------------|
| `template` | schema 的 `templates/` 目录 | ✅ 是，结构骨架 |
| `context` | `openspec/config.yaml` | ❌ 否，只给 Agent 看的背景 |
| `rules` | `openspec/config.yaml` | ❌ 否，只给 Agent 看的约束 |

**Apply 阶段**（调用 apply 指令）：

```
openspec instructions apply --change "xxx" --json
  → 检查 apply.requires 工件是否存在
  → 解析 tasks.md 中的 checkbox（正则匹配 - [ ] / - [x]）
  → 遍历所有 artifacts，存在的文件加入 contextFiles
  → 返回 JSON: { state, contextFiles, tasks, progress }
```

---

## 自定义 Schema

查找优先级：**项目级**（`openspec/schemas/`）> **用户级**（`~/.local/share/openspec/schemas/`）> **内置**。

每个 artifact 有三个核心字段：

| 字段 | 作用 |
|------|------|
| `generates` | 输出文件路径模式，CLI 用它判断工件是否完成 |
| `template` | 模板文件，决定 AI 生成文档时的**结构** |
| `instruction` | AI 执行指令，决定 AI 生成文档时的**行为** |

`template` 控制输出格式，`instruction` 控制 AI 判断，两者均可按团队规范定制。

```bash
# fork 已有 schema 创建自定义版本
openspec new schema dramaflow --fork spec-driven

# 使用自定义 schema 创建变更
openspec new change add-payment --schema dramaflow
```

DramaFlow 的 `dramaflow` schema fork 自 `spec-driven`，定制了：

- **template**：proposal 要求标注 Scope 和 Endpoint
- **instruction**：Scenario 必须用 4 个 `#`；每个 Requirement 必须有至少一个 Scenario

每次 `/opsx:propose` 自动产出符合团队规范的工件，无需手动提醒 Agent。

也可以从零定义精简 schema，例如"只做调研"：

```yaml
name: spike
version: 1
artifacts:
  - id: research
    generates: research.md
    template: research.md
    instruction: "研究目标问题，输出结论和备选方案对比。"
    requires: []
apply:
  requires: [research]
  tracks: null
```

---

# 结构化业务规则 — 从增量描述到结构化唯一事实来源

---

## Agent 为什么读不懂 PRD

PRD 天然是增量文档：v1.0 写登录，v1.2 加"记住我"，v2.0 改 Token 策略——三份文档拼起来才是当前全貌。人工研发靠读完所有版本再问 PM 来脑补；Agent 只读被给到的上下文，无法主动追溯历史。

这带来三个具体问题：

**问题一：找不到当前全貌**

功能状态散落在多份历史 PRD，没有一处直接告诉 Agent 当前支持哪些场景和约束：

```
PRD v1.0：邮箱密码登录，成功跳首页，失败提示错误
PRD v1.2：增加"记住我"，Token 持久化 7 天
PRD v2.0：密码安全升级，最少 8 位，失败 5 次锁定

Agent 拿到 PRD v2.0 → 知道"密码最少 8 位"
Agent 不知道 → "邮箱不存在时错误文案是什么"（v1.0 的细节）
```

**问题二：边界模糊，AI 补全不可控**

自然语言概括留下歧义空间，同一句 PRD 让 Agent 实现三次会得到三种结果：

> "错误情况下要有合适的提示，注意安全"

- `"登录失败，请重试"` — 太模糊
- `"邮箱不存在"` — 暴露账号信息，违反安全要求
- `"邮箱或密码错误"` — 文案对了，但你要的可能是其他格式

**问题三：AC 无法被自动验证**

散文里的验收标准无法被 Agent 自检或测试工具提取：

> "登录成功后跳转首页，失败时显示错误提示。密码长度不够要告知用户。"

结构化 AC 可以被开发自检、Agent 验证、pytest 自动执行，三方共用一份合同：

```
AC-1: POST /api/auth/login，正确凭据 → 200 OK，响应含 access_token
AC-2: 邮箱不存在 → 401，message = "邮箱或密码错误"
AC-3: 密码少于 8 位 → 422，message = "密码至少 8 位"
```

**结构化业务规则的目标**：把为人准备的增量描述，改造成 Agent 能直接消费的结构化资产——让每个业务概念有且只有一个**唯一事实来源（Single Source of Truth）**。

---

## 结构化原则参考：OKF

OKF（Open Knowledge Format）是 Google Cloud 于 2026 年发布的开放规范，目标是"对人友好、对 Agent 友好"的知识表达格式——Markdown + YAML 文件头，唯一必填字段是 `type`，能 `cat` 一个文件就能读，能 `git clone` 一个仓库就能分发。

OKF 本身为数据资产设计，但其三个结构原则恰好对应需求文档的核心问题：

| OKF 原则 | 解决的需求文档问题 |
|---------|----------------|
| **一个概念一份文档**，描述该资产的完整当前状态 | 功能全貌不再散落在多份增量 PRD 里 |
| **结构化 YAML 文件头**，字段无歧义、工具可提取 | 元信息机器可读，无需解析正文散文 |
| **Git 仓库管理**，变更有 diff、有 log | 演进历史自动留存，无需在正文里维护"修改记录" |

知识库组织方式：每个概念一个文件，Concept ID = 文件路径去掉 `.md`；`index.md` 供 Agent 渐进导航，`log.md` 记录变更历史，概念间用 Markdown 链接互连。

---

## 改造方案

核心原则：**每个业务概念有且只有一份文档，作为该概念的唯一事实来源（SSoT），覆盖完整行为，用 Git 记录演进历史。**

### 以业务概念为单位的结构化文档

不再用版本化增量 PRD，改为常青文档——每个业务概念一份，文件路径即概念 ID：

```
requirements/
├── auth/
│   ├── login.md          # 邮箱密码登录的唯一事实来源（SSoT）
│   ├── token-refresh.md
│   └── password-reset.md
└── drama/
    ├── browse.md
    └── playback.md
```

每次迭代更新对应文档，git commit 记录本次变更，文档始终是该概念的唯一事实来源，历史通过 git log 查看。

**粒度如何选择？**

"业务概念"的边界不绑定大小，判断原则：

- **能独立出 3-7 条 AC** — AC 太少说明这是别的概念的子逻辑（太细），太多说明应该拆分（太粗）
- **单一变更原因** — 这个文档的内容通常因同一类决策而改变；总是一起改的合并，总是分开改的拆分
- **对用户有意义** — 对应用户能感知的一个完整行为或场景，而非技术实现细节

| 粒度 | 示例 | 问题 |
|------|------|------|
| 太粗 | `auth.md`（整个认证模块） | AC 太多太杂，变更原因不一致 |
| **合适** | `login.md`（邮箱密码登录） | 完整用户场景，AC 独立可验证 |
| 太细 | `password-validation.md`（密码格式校验） | 无法独立出有意义的 AC，是 login 的子逻辑 |

### YAML 文件头

```yaml
---
id: REQ-AUTH-001
title: 用户邮箱密码登录
status: approved          # draft | approved | deprecated
owner: pm-alice
updated: 2025-06-10
related:
  - REQ-AUTH-002          # Token 刷新
  - SPEC.md#auth-login    # 对应可执行 Spec
---
```

- `id`：提供稳定引用，SPEC 和测试用例可精确指向
- `status: deprecated`：Agent 知道这份需求已下线，不应实现
- `related`：显式连接关联文档，Agent 能沿链路找到完整上下文
- 脚本可扫描所有文件头，自动生成需求索引或检查哪些 approved 需求没有对应 SPEC

### 正文结构化

```markdown
## 业务流程

1. 用户输入邮箱 + 密码，提交 POST /api/auth/login
2. 服务端校验：通过 → 签发 Access Token（2h）+ Refresh Token（7d）；失败 → 返回错误
3. 登录成功后跳转首页

## 异常处理

| 场景 | HTTP | 提示文案 |
|------|------|---------|
| 邮箱不存在 | 401 | "邮箱或密码错误" |
| 密码错误   | 401 | "邮箱或密码错误" |
| 密码少于 8 位 | 422 | "密码至少 8 位" |
| 账号被禁用 | 403 | "账号已停用，请联系客服" |
| 连续失败 5 次 | 429 | "账号已锁定，30 分钟后重试" |

## 验收标准

AC-1: 正确凭据 → 200 OK，响应含 access_token、refresh_token、user 对象
AC-2: 邮箱不存在 → 401，message = "邮箱或密码错误"（不得暴露"邮箱不存在"）
AC-3: 密码错误 → 同 AC-2
AC-4: 密码少于 8 位 → 422，message = "密码至少 8 位"
AC-5: 连续失败 5 次 → 429，账号锁定 30 分钟
```

异常处理单独列表：这是最容易被散文略过的部分，表格让每个边界场景显式可见。

### 行内约束标记

```markdown
- 错误提示 [MUST NOT] 区分"邮箱不存在"和"密码错误"，防止账号枚举攻击
- Token [MUST] 写入 EncryptedSharedPreferences，[MUST NOT] 明文存储
- 登录页 [SHOULD] 在请求期间显示加载状态
- [CONSTRAINT:security] 连续失败 5 次后锁定 30 分钟
- [CONSTRAINT:perf] 登录接口 P99 响应时间 < 500ms
```

| 标记 | 含义 | 强制程度 |
|------|------|---------|
| `[MUST]` | 必须实现 | 硬性要求，有 AC 覆盖 |
| `[MUST NOT]` | 明确禁止 | 安全/合规红线 |
| `[SHOULD]` | 建议实现 | 不做需说明原因 |
| `[CONSTRAINT:类型]` | 非功能约束 | 按性能/安全/合规分类 |

Agent 读到 `[MUST NOT]` 知道是红线，读到 `[SHOULD]` 知道时间紧时可以降级。

### Git 管理

```bash
# 查看登录需求的完整演进历史
git log --oneline requirements/auth/login.md

d4a83bc  增加账号锁定机制（连续失败 5 次）
a3f21bc  记住我：Token 持久化 7 天，写入 EncryptedSharedPreferences
b12f45a  初始版本：邮箱密码登录，JWT Token

# 查看某次迭代改了什么
git show a3f21bc -- requirements/auth/login.md
```

附加能力：需求变更时，CI 脚本可检测哪些 SPEC 引用了这份需求，提示"可能需要更新对应 Spec"。

---

## 实施难点与建议

### 难点一：对 PM 不够友好

**方案 A — 工具包装：** 给 PM 提供表单界面（Notion Database、飞书多维表格），后台自动生成结构化 Markdown 并提交 Git。PM 不感知 Markdown 和 Git，但需要维护两套数据源的一致性。

**方案 B — Agent 辅助维护（推荐）：** PM 用自然语言描述需求，Agent 更新结构化文档，PM 确认后由 Agent 提交 Git：

```
PM：登录失败 5 次后要锁定账号，锁定 30 分钟，提示"账号已锁定，请稍后重试"
  ↓ Agent 更新 login.md
  - 在异常处理表格中新增一行
  - 新增 AC-5
  - 更新 YAML 文件头的 updated 字段
  ↓ PM 确认 → Agent 提交 git commit
```

额外收益：可从结构化需求反向生成传统 PRD——内部用结构化文档，对外汇报时由 Agent 生成可读散文，两者不冲突。

### 难点二：存量文档量大

**建议：新旧双轨，触碰则改。**

- 存量 PRD 保持现状，暂不动
- 新增功能严格执行结构化格式
- 迭代变更触碰到哪个功能，就补一份结构化文档整理当前全貌

优先级从核心流程出发（登录、支付、核心业务链路先行），长尾功能后补。

### 难点三：改造幅度选择

不必一步到位，按团队接受度分级：

| 做法 | 内容 | 效果 |
|------|------|------|
| **最小可行** | 每个概念文档末尾有结构化 AC 块 | Agent 输出质量显著提升 |
| **中等** | AC 块 + YAML 文件头 + 异常处理表格 | 覆盖 Agent 最需要的信息 |
| **完整** | 常青文档 + 结构化正文 + Git + Agent 维护 | 完整的结构化资产体系 |

---

## 与下游的关系

结构化业务规则不替代 SPEC.md，两者分工不同：

| | 结构化需求文档（requirements/） | SPEC.md（可执行 Spec）|
|---|---|---|
| 主导方 | PM | 开发 / AI |
| 描述对象 | "做什么"，业务全貌 | "怎么做才算对"，技术实现边界 |
| 包含内容 | 背景、动机、优先级、业务 AC 意图 | 前置条件、流程、可生成测试的 AC |

流转路径：

```
结构化需求文档（业务 AC 意图）
    ↓ Agent 提取 + 技术细化
SPEC.md 草案
    ↓ 人工确认 AC
SPEC.md 定稿
    ↓
开发实现 → Agent 自检 AC → 自动化测试
```

---

# 可执行设计系统 — 设计一处定义，人机共同执行

---

## 演进：三个时代与一个命题

| 阶段 | 代表工具 | 原型 | 设计系统 |
|------|---------|------|---------|
| 文档时代 | Axure、PRD | 沟通说明书，独立于实现 | 无系统，规范散落文档，靠人遵守 |
| Figma 时代 | Figma、Design System、Storybook | 高保真视觉稿，与代码平行存在 | 组件可复用，但需人工翻译为代码 |
| 可执行设计系统 | Token + 约束 + 组件规格 + 生成脚本 | 从规格派生的验收产物，与实现共源 | 格式可被机器直接消费，驱动多平台生成 |

这不只是"工具在变"，而是**设计权力中心的迁移**——从"谁画了稿子"转移到"谁定义了可执行规格"：

```
过去：Figma 是唯一入口 → 人工翻译 → 前端实现

未来：可执行设计系统是核心层（Token + 约束 + 组件规格）
         ↑ 可由 Figma / 自然语言 / Screen Spec 驱动
         ↓ 机器直接生成 HTML / Vue / Android XML
      Figma 转型为可视化协作与 UX 探索层
```

AI 生成工具（Bolt.new、v0、Lovable）暴露了关键矛盾：没有可执行的设计约束，AI 生成越多，系统越混乱。可执行设计系统正是对这个问题的回答。

---

## 可执行设计系统：五层架构

EDS 定义的是**中间层的格式**——只要设计意图最终被编码为 Token + 组件规格 + 约束，机器就能直接消费，产出多平台产物。入口可以从 Figma 出发（Tokens Studio 同步），从自然语言出发（注入 constraints.md 约束 AI），或从 Screen Spec 出发（YAML 三路生成 prototype / Vue / Android）。

五个层次从上到下依次定义约束：

```
Specification（业务约束）
    ↓ 定义规则
Design Token（品牌 / 主题）
    ↓ 驱动样式
Component Runtime（组件库）
    ↓ 提供构建块
AI Generation（页面生成）
    ↓ 输出结果
Visual Collaboration Layer（Figma 协作）
```

**第一层：Specification — 业务约束**

写给 AI 和团队成员共同参考的规则文档：

```markdown
<!-- constraints.md -->
- 主操作按钮同一页面只能出现一个
- 卡片标题最多两行，超出截断加省略号
- 所有异步操作必须有 loading 状态，禁止裸露骨架屏
- 禁用态不得使用品牌主色，一律使用 --color-disabled
```

**第二层：Design Token — 品牌变量**

用代码定义所有视觉常量，CSS 自定义属性为主要载体：

```css
/* design-system/tokens/tokens.css */
:root {
  --color-primary:       #6C5CE7;
  --color-primary-light: #A29BFE;
  --color-accent:        #FD79A8;
  --bg-primary:  #0F0F23;  --bg-card: #16163A;
  --text-primary: #FFF;    --text-muted: #555;
  --space-4: 16px;  --radius-card: 12px;
}
```

`tokens.css` 是权威源，`tokens.ts` 从它派生。Figma 通过 Tokens Studio 导出 DTCG JSON，再由脚本同步到 `tokens.css`。

**第三层：Component Runtime — 组件库**

以 `components.yaml` 为唯一源，用 `{token.path}` 语法引用 Token，自动生成各平台代码：

```yaml
# components.yaml
components:
  btn-primary:
    base:
      padding: "{spacing.md} {spacing.xl}"
      border-radius: "{radius.btn}"
      background:
        type: gradient-linear
        stops: ["{color.primary} 0%", "{color.primaryLight} 100%"]
    states:
      disabled: { background: "{text.muted}", cursor: not-allowed }
```

```
components.yaml → generate_css.py     → components.css   (H5 用 class="btn-primary")
components.yaml → generate_android.py → styles.xml       (Android 用 style="DramaFlow.Button.Primary")
```

**第四层：AI Generation — 从 Screen Spec 多路生成**

用平台无关的 YAML 描述页面结构：

```yaml
# specs/screens/home.yaml
screen: home
sections:
  - component: app-bar
    title: "DramaFlow"
  - component: continue-watching
    data: /api/watch-records/continue-watching
  - component: drama-grid
    data: /api/dramas?category={selected}
    layout: { columns: 2, gap: "{spacing.md}" }
```

```
specs/screens/home.yaml
    ├── generate_prototype.py   → prototype HTML     (给 PM 验收)
    ├── generate_h5_template.py → Vue 页面骨架       (给前端开发)
    └── generate_android.py     → Android XML        (给 Android 开发)
```

改一处，三端同步更新。对于新页面，将 tokens.css + constraints.md 注入 AI 上下文，让 AI 在约束下生成代码——**设计系统的遵守从"靠人记忆"变成"系统默认"**。

**第五层：Figma — 可视化协作**

设计师在 Figma 里操作和代码同源的 Token，PM 做 UX 走查与评审，非工程角色不需要看代码。

---

## 影响：Figma 与团队的角色变化

### Figma 未来最核心的四个价值

| # | 价值 | 说明 |
|---|------|------|
| 1 | 人类可视化理解层 | 老板、产品、运营不看代码，Figma 让非工程角色理解系统 |
| 2 | UX 微调层 | 视觉节奏、阅读层次、微交互，AI 难以处理，需要可视化探索 |
| 3 | AI Prompt 编辑层 | Figma 可能演化为可视化 Prompt IDE（"这个页面太拥挤，强化 CTA"→ AI 自动调整）|
| 4 | 跨角色协作层 | 评论、审阅、讨论、演示，Figma 仍然是多角色协作界面 |

### 团队能力转变

| 过去 | 未来 |
|------|------|
| 画页面 | 定义系统 |
| 标注规范 | 维护 Token + Component |
| 手工对稿 | 制定 AI Generation Rule |
| 重复适配 | 建立 UX Constraint |

真正需要人的部分——系统定义、UX 判断、品牌决策、跨角色协作——价值反而更高。

### 设计角色如何参与代码仓库

`tokens.css` 和 `constraints.md` 在代码仓库里，但设计师和 PM 可以不使用 Git 参与：

| 角色 | 方式 | 门槛 |
|------|------|------|
| PM / 设计师 | GitLab 网页编辑 `constraints.md`、`design-rules.md` → 提交 MR | 零 |
| 设计师 | Figma Tokens Studio 导出 DTCG JSON → 脚本更新 `tokens.css` | 低 |
| 设计负责人 | 成为 `design-system/` CODEOWNERS，所有变更需其 Approve | 中 |

过去规范写在 Figma 标注里，开发可以选择性遵守；未来规范写在仓库里，每次修改有 diff、有 review、有历史记录。

---

## 实践：DramaFlow 的可执行设计系统

### 完整目录结构

```
design-system/                     # 唯一视觉真相源
├── tokens/
│   ├── tokens.css                 # CSS 自定义属性（:root 上定义 60+ 变量）
│   └── tokens.ts                  # TypeScript 等价版（组件动态样式引用）
├── specs/
│   ├── constraints.md             # 业务约束（可自动检查）
│   ├── design-rules.md            # AI 生成规则（Skill 触发时自动注入 Prompt）
│   └── screens/                   # 屏幕规格（平台无关的页面描述）
│       ├── home.yaml
│       └── detail.yaml
├── components/
│   ├── components.yaml            # 平台无关组件定义（唯一源）
│   ├── components.css             # 生成：H5 & prototype 直接引用
│   └── index.html                 # 组件 Gallery（可视化验证渲染效果）
└── exports/
    ├── h5/designsystem.css        # 一键导入：tokens.css + components.css
    └── android/
        ├── colors.xml             # 从 tokens.css 生成
        └── styles.xml             # 从 components.yaml 生成

scripts/
├── design-system/
│   ├── figma_sync_tokens.py       # Figma Tokens Studio (DTCG JSON) → tokens.css + tokens.ts
│   ├── figma_sync_components.py   # Figma REST API → components.yaml
│   ├── figma_sync_screens.py      # Figma auto-layout pages → specs/screens/*.yaml
│   ├── generate_css.py            # components.yaml → components.css
│   ├── generate_android.py        # components.yaml + tokens.css → Android XML
│   ├── generate_prototype.py      # screen specs → HTML 原型
│   └── generate_h5_template.py    # screen specs → Vue 页面模板骨架
└── check/
    ├── check_tokens.py            # 硬编码色值 + 变量名合规
    ├── check_constraints.py       # 业务约束满足
    └── check_components.py        # 组件使用符合 components.yaml
```

### 核心流水线

**阶段一：Figma → 中间层**

```
                    ┌─ Figma ──────────────────────────────┐
                    │  Variables ──Tokens Studio──> DTCG JSON│
                    │  Components ──REST API──> Node Tree    │
                    │  Pages ──REST API──> Auto-layout Tree  │
                    └──┬────────────┬────────────┬───────────┘
                       │            │            │
          ┌────────────┘            │            └──────────────┐
          ▼                         ▼                           ▼
   figma_sync_tokens.py   figma_sync_components.py   figma_sync_screens.py
          │                         │                           │
          ▼                         ▼                           ▼
      tokens.css              components.yaml            specs/screens/
      tokens.ts                                              *.yaml
```

**阶段二：中间层 → 多平台产物**

```
tokens.css + components.yaml  → generate_css.py          → components.css
tokens.css + components.yaml  → generate_android.py      → colors.xml + styles.xml
specs/screens/*.yaml          → generate_prototype.py    → prototype/*.html（给 PM）
specs/screens/*.yaml          → generate_h5_template.py  → Vue 骨架（给前端）
```

### 平台使用示例

**H5：** 一次导入，全站可用；页面只用预定义 class，不重写组件样式。

```typescript
import '@design/exports/h5/designsystem.css'
```

```vue
<template>
  <button class="btn-primary" @click="play">▶ 立即观看</button>
  <div class="drama-card">
    <div class="thumb"><span class="badge">热播</span></div>
    <div class="info"><h4>{{ title }}</h4></div>
  </div>
</template>
<style scoped>/* 只写页面特有布局 */</style>
```

**Android：** 引用导出的 style 和 color 资源。

```xml
<Button style="@style/DramaFlow.Button.Primary" android:text="立即观看" />
<TextView android:textColor="@color/text_primary" android:background="@color/bg_primary" />
```

### 合规检查

CI/pre-commit 自动运行，也可手动执行：

```bash
python scripts/check/check_tokens.py --path h5/src          # 无硬编码色值，变量名合规
python scripts/check/check_constraints.py                    # 业务约束满足
python scripts/check/check_components.py                     # 组件使用符合 components.yaml
```

**改一处，全平台生效。Figma 是创作入口，design-system/ 是唯一真相源。**

---

# Harness 工程之项目空间 - 打造 Agent 友好型工程基座

---

> **核心思想**：让你的代码仓库成为 Agent 的"操作系统"——不是训练 Agent 适应混乱的项目，而是主动将项目改造成 Agent 能精准识别、高效协作的数字基座。

---

## 什么是项目空间

Harness 由两部分构成：**Agent 内核**（模型本身，厂商提供，无法干预）和**项目空间**（代码库结构、文档、规则文件、工具配置，团队完全自主管理）。**Harness Engineering 的实质，就是把项目空间建设好**——模型运行时能看到什么、调用什么、被什么规则约束，全由项目空间决定。一个精心建设的项目空间，普通模型也能稳定完成复杂任务；粗糙的项目空间，再强的模型也只能低效试探。

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
│   │   ├── profile/                   #    其他限界上下文，目录结构同上
│   │   └── notification/
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
│   ├── tokens/                        #       Design Token（CSS 变量 / TS 等价版）
│   ├── specs/                         #       约束 + 屏幕规格（平台无关，驱动多平台生成）
│   ├── components/                    #       组件规格 → 生成 CSS / Android XML
│   └── exports/                       #       平台导出产物（禁止手改，从 yaml 生成）
│
├── prototype/                         #    可交互 HTML 原型（引用 design-system，PM 验收用）
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

四个层级（文档、经验、约束、执行）都是可以独立建设的工程制品，但共同依赖一个前提：**代码库本身的结构质量**。目录怎么切、模块怎么拆、类型怎么定义——这些是 Harness 能否发挥作用的地基。混乱的单体代码库上，再精心的文档和约束都只能事倍功半；边界清晰的代码库，Agent 能自然地定位任务范围，甚至无需额外文档。

### 利用 DDD 划分模块边界

推荐基于 **DDD（领域驱动设计）** 来组织代码架构，它和 LLM 的运作方式天然契合：

- **限界上下文 → 模块边界**：每个上下文映射为一个模块目录（`auth/`、`profile/`、`notification/`），Agent 修改某一个时不会误入其他上下文的实现细节
- **通用语言（Ubiquitous Language）→ 命名体系**：目录名、类名、字段名共享同一套词汇，这与 LLM 基于语义匹配的推理模式高度一致，Agent 的"理解"和"生成"都更精准
- **聚合根 → 类型约束**：通过类型系统（OpenAPI Schema、Pydantic 模型、Type Hints）固化为代码级约束，Agent 无需跳转即可理解数据结构的边界和校验规则

**示例**：将一个巨大的 `UserService` 拆分为 `ProfileService`、`AuthService` 和 `NotificationService`。当 Agent 处理"修改头像"任务时，其关注点仅局限在 `ProfileService`，不需要理解整个用户体系。

### 接口契约标准化（OpenAPI / Protobuf）

强制用 OpenAPI 或 Protobuf 描述所有接口，而不是弱类型的自然语言（"传一个 id 给用户中心"）。明确的 Schema（字段类型、UUID 格式、404 响应示例）让 Agent 直接确认参数，不靠猜测——**强类型协议是防止 Agent 产生调用幻觉的最直接手段**。

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

Agent 不会一次性吞下所有文档，而是按任务范围按需查阅。底层逻辑是**渐进披露（Progressive Disclosure）**：任何时刻只加载当前任务所需的信息，无关内容不占推理窗口。

#### 三层文档体系

```
系统级 MD（CLAUDE.md / README.md）
  └── 顶层架构、核心技术栈选型理由（Decision Log）、全局约束

模块级 MD（每个子目录的 README.md）
  └── 职责定位、对外接口、依赖关系、特殊约束

代码级辅助（Type Hints / JSDoc）
  └── 函数签名、参数含义、"为什么"而非"是什么"
```

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

`Purpose` 是 Agent 语义定位的锚点——描述越精准，定位越快，进入上下文的噪音越少。

#### 代码级类型提示的价值

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

`docs/adr/` 记录选型背景、决策和被否决方案。Agent 重构时读 ADR，自动规避已被证伪的技术路径。关键字段是**被否决的方案**——这是最容易被后人（和 Agent）"重新发明"的部分。

```markdown
# ADR-001: 选择 SQLite 而非 PostgreSQL 作为开发环境数据库

## 状态：已采纳

## 背景 / 决策 / 后果
...

## 被否决的方案
- 方案 A（原因：...）
- 方案 B（原因：...）
```

---

### 2. 经验层 — 让 Agent 不踩同样的坑

经验层是团队与 Agent 之间的"错题本"。某段代码出过什么 Bug、踩过什么坑，沉淀为结构化经验文件，colocate 在对应模块目录下。

- `src/modules/*/EXPERIENCE.md` → 与模块代码 colocate，记录历史陷阱和反模式

> **重要前提**：先让 Agent 直接尝试，真的反复犯同一类错误时再提炼注入——过度前置文档只会制造维护负担。

#### 什么情况值得沉淀经验

以下信号说明某个任务适合提炼为经验文件：
- Agent 在同类任务上**反复遗漏同一个步骤**（如忘记注册路由、忘记更新 OpenAPI）
- 任务涉及**项目特有的隐性约定**，无法从代码结构本身推断
- 高复杂度长链路任务中，Agent 出现**顾此失彼**的情况

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

关键：按**任务**而非提交聚合——一个功能往往横跨多个提交，要把同一任务的多个提交当作整体分析，再让 LLM 识别每类任务的完整变更集。

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

新增经验只需更新 INDEX.md，不触碰 CLAUDE.md——保持 CLAUDE.md 精简的同时，不限制经验文件的数量。

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

纳入 CI 流水线后，每次提交自动执行——违规时 CI 报错，Agent 读取错误信息并自主修正，**约束本身就成了 Agent 的纠错信号**。

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

工具和反馈是一体的：**Agent 能调用程序，也必须能看到程序的结果**，否则执行就是盲目的。

**工具与委派**

- `.mcp.json` + `src/mcp/` → MCP 工具声明与实现，启动时自动发现
- `.claude/settings.json` → Tool 权限 allowlist / deny list，控制 Agent 能调用哪些系统命令
- `.claude/skills/` → 按需注入的工作流（CR、debug、deploy），Agent 识别意图后自动加载
- `.claude/agents/` → 隔离执行的委派单元（子代理），独立上下文，并行执行，保护主会话不受污染
- `scripts/` → 工具支撑脚本（数据库重置、种子数据导入），Agent 直接调用而非手写

**可测试性 — Agent 能验证自己的改动**

测试套件是执行层的核心反馈机制。Agent 修改代码后立即运行测试、读取结果，形成"改→验→改"的自主闭环。

- 测试命令无交互运行（`pytest` / `./gradlew test`），输出结构化结果（通过/失败/报错行号），让 Agent 能直接读取
- 行为级测试比单元测试对 Agent 更有价值：失败信息直接告诉 Agent"哪个接口的哪个场景出错了"，而非"哪行断言失败了"

**可观测性 — Agent 能看到系统的运行状态**

可观测性决定 Agent 能"看"到多少：

- 结构化日志：应用运行时输出可解析的格式（JSON、明确的错误码），而不是只打印人类可读的字符串
- 脚本反馈：`scripts/` 中的工具脚本应在执行后输出明确的结果（"已重置数据库，导入 42 条记录"），让 Agent 能确认操作是否生效
- MCP 工具返回值：MCP Server 的返回应包含足够的状态信息，Agent 无需额外查询即可判断操作结果

---

## 改造优先级

**最小可行改造**：写好 `CLAUDE.md` + 为每个模块创建 `README.md`——投入产出比最高，是大多数项目的起点。

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

其余所有 Harness 文件默认提交。

### Code Review 策略

**一个错误的 CLAUDE.md 比一行错误的代码破坏力更大**——代码出错是单点 Bug，提示词出错会让 Agent 系统性地产出有问题的代码。

| 级别 | 文件类型 | Review 要求 | 理由 |
|------|---------|------------|------|
| **严格 Review** | `CLAUDE.md`、`.claude/hooks/`、`.claude/skills/`、`.claude/agents/`、`.claude/settings.json` | 必须 PR + 至少一人 Approve | 直接影响 Agent 行为模式和安全边界 |
| **正常 Review** | `SPEC.md`、`EXPERIENCE.md`、`docs/adr/`、`design-system/` | 建议 PR Review | 影响团队知识对齐，但不直接改变 Agent 执行路径 |
| **低门槛** | `scripts/`、`.claude/experience/INDEX.md` | 变更通知即可 | 影响面可控 |

关键判断标准：**这个改动会让 Agent 在不知情的情况下做出不同的决策吗？** 如果是，就必须 Review。

### 个人偏好管理："分层覆盖"模型

解决思路：**分层覆盖**——每一层权威范围不同，冲突向下收敛。

```
个人层（.claude/settings.local.json, memory/）      # 自由调整，但不能移除项目层的强制约束
  ↓ 覆盖
项目层（.claude/settings.json, CLAUDE.md, hooks/, skills/）  # 增删改走 PR 并附理由
  ↓ 引用
模块层（src/modules/*/EXPERIENCE.md, README.md）     # EXPERIENCE.md 是建议，标注日期，超 6 个月标记待审查
  ↓ 被约束
强制约束（CI, import-linter, pyproject.toml）        # 不可绕过，代码合入的必要条件
```

### 经验文件的质量管控

`EXPERIENCE.md` 最容易引发"洁癖 vs 实用"的争议。几条质量原则：

- **写"陷阱条件"，不写"个人偏好"**：`"当 token 为 None 时 refresh_token() 会抛未捕获异常"` ✅；`"不要用 async/await"` ❌
- **少而精，标日期**：5 条验证过的陷阱 > 50 条未经检验的"注意事项"；条目超过 6 个月标记待审查
- **实验性经验走 Memory 先验证**：不确定是否普适 → 写入 `.claude/memory/`（个人、不提交），验证有效后再提炼到 `EXPERIENCE.md`（团队共享）

---

## Memory：Agent 自管理的跨会话持久化

Memory 与上面的地基和四个层级有本质区别：

> **地基和四个层级是人写的、注入给 Agent 的；Memory 是 Agent 自己写的、自己维护的。**

`.claude/memory/`（`user.md` / `project.md` / `feedback.md` / `reference.md`）是 Agent 在对话中自动提取并持久化的跨会话记忆，回答"Agent 从这次会话中学到了什么"。

Memory 不是第六层，而是**横切所有层的持久化机制**。Agent 可以在任何一层学到东西并写入 memory：

| 当 Agent 在… | 学到的东西 | 写入 memory 类型 |
|-------------|-----------|-----------------|
| 文档层 | 用户偏好的技术栈、项目约定 | `user.md`、`project.md` |
| 经验层 | 某个模块的陷阱被验证了 | `project.md` |
| 约束层 | 用户纠正了某种行为风格 | `feedback.md` |
| 执行层 | 某个外部系统的连接方式 | `reference.md` |

**关键类比**：地基和四个层级是 Agent 的"规章制度手册"（人写的）；Memory 是 Agent 的"工作笔记"（自己写的）。这也解释了为什么经验层和记忆容易混淆——**EXPERIENCE.md 是人写的陷阱预判，Memory 是 Agent 踩过坑之后自己记下的教训。** 前者是预防，后者是复盘。

---

# Skills 工程设计 - 从临时 Prompt 到跨会话可信赖的团队工具

---

## 什么是 Skill？

Skill 是 Claude Code 的功能扩展单元，将**特定领域的规则、上下文和工具**打包成可复用的模块。

调用方式：在对话中输入 `/skill-name`，Skill 内容会注入当前上下文，Claude 按其中的规则执行任务。

**适合封装成 Skill 的场景**：

| 适合 | 不适合 |
|------|--------|
| 步骤固定但需要 AI 推理的流程 | 纯机械操作（用 Shell 脚本更直接） |
| 需要专业上下文才能做对的任务 | 一次性任务，不会重复使用 |
| 团队希望标准化的操作规范 | 步骤每次都不同，无法归纳 |
| 跨会话需要一致行为的检查流程 | 简单到一句 prompt 就能描述清楚 |

**粒度把握原则**：一个 Skill 应该对应一个**有明确完成标准的任务**。太宽（"做所有测试工作"）会让 Skill 退化成 mega-prompt；太细（"运行一条命令"）则不如直接写脚本。

### Skill 的核心价值：为什么不直接问 Agent？

对于开发者来说，`/seed-data` 和直接对 Agent 说"添加测试数据"最终效果相似——Agent 都能找到 seed.py 并执行。Skill 的价值不在"替 Agent 找脚本"，而在以下四个更窄、更确定的场景：

**1. 权限隔离**：Skill 可以精确限定能做什么。`/seed-data` 只申请操作数据库的权限，不需要"Run Arbitrary Python"的全局权限。在权限敏感的环境中，这是安全层面的关键差异。

**2. 结构化输出**：Agent 的自然语言回复不稳定——有时说"导入完成"，有时说"数据已存在"。Skill 可以输出固定格式，让 CI pipeline 或测试框架程序化消费结果。

**3. 跨会话的确定性**：在新会话里说"加测试数据"，Agent 的行为有方差——正确找到 seed.py、自己写 INSERT 语句、用 SQLite CLI 直接操作、向用户追问数据格式，都有可能。Skill 消除这种方差，每次结果一致，不管当前上下文是什么。

**4. 低频操作者的记忆成本**：区分用户的不应是"非技术人员 vs 技术人员"，而是"天天用的人 vs 两周用一次的人"。Skill 为后者消除了每次重新摸索的成本。

---

## CLI Skill vs MCP Server 选型

| 维度 | CLI Skill | MCP Server |
|------|-----------|------------|
| 适用场景 | 确定性流程，本地工具编排 | 外部服务集成，生态对接 |
| 部署方式 | 项目目录内，随代码版本管理 | 独立进程，需要单独部署维护 |
| 调用方式 | `/skill-name`，进入 Claude 上下文 | Claude 通过 Tool Call 调用 |
| 推理介入程度 | 高（Claude 决策执行细节） | 低（确定性 API，Claude 只决定调用时机） |
| 适合团队 | 小团队，快速迭代，规范还在形成中 | 已有稳定服务需要接入的中大型团队 |

---

## 目录结构

```
.claude/commands/skill-name/
  SKILL.md          # 主文件：核心规则和索引，Claude 优先读取
  references/       # 参考资料（语料库、检查表等，按需读取）
  scripts/          # 辅助脚本（Shell/Python），承载无需推理的固定逻辑
  examples/         # 示例代码，供 Claude 参考实现模式
```

**渐进式披露**：SKILL.md 只放核心规则，详细内容放子目录。Claude 在主文件中拿到足够信息后，只有需要时才读子目录。这样可以控制单次注入的上下文量。

---

## 四大设计原则

### 参数最小化

每个额外参数都是一次出错机会。设计 Skill 时，优先让 Skill 自己从上下文（当前目录、git 状态、已有文件）中推断所需信息，而不是要求调用者传入。

```
# 差：需要调用者记住传参格式
/cr-refactor --path backend/app/api --depth 2 --format markdown

# 好：Skill 自己找
/cr-refactor
```

只有在 Skill 确实无法自动确定的信息上才要求参数（例如测试 mission 路径）。

### 结构化反馈

Skill 的输出应该让 Agent 能够**自修复**——即 Claude 看到输出后能判断是否成功、哪里失败、下一步如何处理。

好的结构化反馈包含：
- **状态**：SUCCESS / FAILURE / PARTIAL
- **变更明细**：做了什么（新增/修改/跳过了哪些）
- **错误上下文**：失败时输出足够的信息让 Claude 定位原因
- **下一步提示**：明确告知 Agent 后续应该做什么

```bash
# 示例：rebuild-deploy 的结构化输出
✅ H5 编译成功（dist/ 已更新）
✅ 后端启动（http://localhost:8000）
⚠️  模拟器未运行，请先启动 AVD 后重新执行
```

### 幂等性

同一个 Skill 反复调用，结果应该一致，不产生累积副作用。

实践要点：
- 创建资源前先检查是否已存在（`INSERT OR IGNORE`、`mkdir -p`）
- 数据导入用 upsert，不用 insert
- 临时文件写到固定路径，每次覆盖而非追加
- 启动服务前先检查端口是否已占用

### 错误恢复与降级

Skill 不应该在第一个错误处就停下来。设计时需要考虑：

- **可恢复错误**：例如依赖未安装，在 Skill 内部处理（自动 pip install）
- **需要人工介入的错误**：清晰说明原因和恢复步骤，而非让 Claude 猜测
- **降级逻辑**：部分步骤失败时，哪些可以跳过继续，哪些必须中止

---

## 课程 Skills 设计复盘

### `rebuild-deploy`
**目的**：H5 编译 → 后端启动 → 模拟器安装 App，一键部署到模拟器

**设计亮点**：
- 幂等——每次全量重新编译，状态清晰
- 结构化输出——每个步骤的成功/失败单独报告，Agent 可定位失败步骤

**可以改进的地方**：
- 可以增加增量编译检测，跳过没有变更的步骤，提高速度
- 模拟器启动超时的错误处理可以更明确

---

### `spec-validate`
**目的**：从 SPEC.md 提取 AC，对比现有测试覆盖，自动补充缺失的 API 测试

**设计亮点**：
- 参数最小化——只需指定路径，AC 提取和对比逻辑在 Skill 内完成
- 以 Spec 为唯一真相来源，避免测试与实现"互相验证"的陷阱

**可以改进的地方**：
- AC 提取依赖 Spec 格式规范，格式不一致时容易漏提
- 可以增加 `--check` 只读模式（不自动补测试，只报告缺口）

---

### `cr-refactor`
**目的**：输出 CR 清单 + 重构建议，参数最小化（只接受路径，自动定位问题）

**设计亮点**：
- 参数最小化做得好——Skill 自己定位问题，不要求调用者描述
- 输出分优先级（P0/P1/P2），帮助人工决策"做哪些，跳过哪些"

**可以改进的地方**：
- 对跨文件的重复模式识别能力有限，可以加 references 扩充检查维度
- 重构建议缺乏"重构后验证"步骤的指引

---

### `exploratory-test`（验收测试）
**目的**：编排"截图→观察→定位→操作→记录→检查"的执行循环，基于 test-agent CLI 实现自动化验收

**设计亮点**：
- Skill 定义了完整的感知-决策-行动循环，让 Claude 能真正"驾驶"测试执行
- 参数设计（mission 路径）使得测试场景可版本管理、可复用

**可以改进的地方**：
- 环境适配（不同 AVD 分辨率）的鲁棒性需要在 screen_knowledge 中持续积累
- 失败后的诊断指引可以更结构化

---

## 进阶：Skill 边界设计

Skill 的边界问题有两个维度：**纵向**（Skill 内部应该承担什么）和**横向**（什么时候拆成多个 Skill、什么时候合并）。两者本质上都是同一个问题：什么属于 Skill，什么不属于。

### 纵向边界：Skill 与脚本之间

一个反直觉但重要的原则：**Skill 中不该有不需要推理的逻辑**。

固定流程（检查端口、编译命令、文件路径拼接）用 Shell 脚本实现，Skill 调用脚本、处理异常、解读结果。这样：

- 脚本逻辑可以单独测试，不依赖 AI 上下文
- Skill 聚焦在"需要 AI 判断的部分"，上下文利用效率更高
- 维护时修脚本和改 Skill 规则分开，职责清晰

```
Skill（推理层）
  ├── 判断当前状态（需要 AI 读取上下文）
  ├── 调用 scripts/check-env.sh（固定检查逻辑）
  ├── 解读脚本输出，决定下一步（需要 AI 推理）
  └── 调用 scripts/deploy.sh（固定部署逻辑）
```

**判断标准**：这段逻辑用 `if/else` 写死能得到正确结果吗？能 → 脚本；需要读上下文、做判断 → Skill。

### 横向边界：Skill 与 Skill 之间

Skill 泛滥的根本原因是**相同的推理模式被重复封装成了不同的 Skill**。

**识别合并机会**：先写 Skill 的触发描述（description）。如果两个 Skill 的触发条件几乎一样，或者用户在想"该用哪个"时需要犹豫，说明它们是同一个 Skill，只是参数不同。

```
❌ 泛滥：三个 Skill，相同推理过程
/backend-code-review   → 读代码 → 找问题 → 分优先级
/frontend-code-review  → 读代码 → 找问题 → 分优先级
/api-code-review       → 读代码 → 找问题 → 分优先级

✅ 合并：一个 Skill，自动定位范围
/cr-refactor           → Skill 自己从 git diff 或当前目录推断范围
```

**五条实操判断**：

| 判断 | 说明 |
|------|------|
| 3 次规则 | 同一个推理流程手动执行 3 次以上再封装，1 次是偶发 |
| 参数优先于复制 | 能用参数区分的变体，不应该建新 Skill |
| Description 唯一性 | 两个 Skill 的触发描述有重叠？有重叠就合并 |
| 完整任务边界 | Skill 要有明确的"完成状态"，片段任务留给 prompt |
| 一句话可描述 | 一句 prompt 说清楚的操作写进 CLAUDE.md，不用单独建 Skill |

---

## 企业级 Skill 库

### 三层分级

| 层级 | 位置 | 适用范围 | 管理方式 |
|------|------|---------|---------|
| 个人 | `~/.claude/commands/` | 个人习惯和偏好 | 本地，不纳入版本控制 |
| 项目 | `.claude/commands/`（项目根目录）| 当前项目规范 | Git 管理，随项目演进 |
| 团队 | 共享仓库 + 安装脚本 | 跨项目通用规范 | 独立版本管理，显式安装 |

### 版本管理建议

- 项目级 Skill 随项目代码一起 commit，在 PR 中 review Skill 变更
- 团队级 Skill 用语义化版本号（semver），Breaking change 升大版本
- Skill 变更要同步更新 SKILL.md 中的使用说明和变更记录

### 共享机制

- 团队共享 Skill 库作为独立 Git 仓库维护，通过 install 脚本（`cp -r skills/ .claude/commands/`）安装到项目
- 在项目的 CLAUDE.md 中注明"已安装 XX 团队 Skill 库 vX.Y"，便于 onboarding

---

# MCP 工程设计 - 把外部系统变成 AI 可信赖的工具箱

## 什么是 MCP？

MCP（Model Context Protocol）是 Anthropic 提出的开放标准协议，本质是 **JSON-RPC 2.0 消息格式 + stdio 传输层**。它让 AI 能以统一接口调用外部工具和数据源。

---

## MCP 的三种原语

协议定义了三种 Server 可暴露的内容类型，称为**原语（primitives）**。

| 原语 | 谁控制调用时机 | 协议方法 |
|------|--------------|---------|
| **Tools** | 模型 | `tools/list` → `tools/call` |
| **Resources** | 宿主程序 | `resources/list` → `resources/read` (支持 `subscribe` 推送变更) |
| **Prompts** | 用户 | `prompts/list` → `prompts/get` |

---

## 设计初衷：LLM 作为传统程序的推理组件

三种原语的划分，不是为 Agent 设计的。MCP 最初面向的是**非 Agent 的宿主程序**——LLM 只是流程中负责推理的一环，宿主控制全局：

| 角色 | 谁做 | MCP 原语 |
|------|------|---------|
| 提供上下文 | 宿主（本来就知道用户是谁、在看什么） | Resources |
| 选择流程 | 用户（知道自己要干什么） | Prompts |
| 执行操作 | 模型提议，宿主确认后执行 | Tools |

### 真实场景：客服工单系统的 AI 辅助回复

工单系统（如 Intercom）的客服点击"智能回复"：

**① Resources — 宿主把已有数据直接喂给模型**

```
resources/read "customer://ticket-5542"     → 客户姓名、套餐、MRR
resources/read "customer://ticket-5542/chat" → 完整聊天记录
resources/read "knowledge://faq-billing"     → 计费 FAQ
```

宿主不等待模型来问——"查这个工单的数据"是它发起请求前就确定的。

**② Prompts — 用户从模板中选择操作类型**

```
prompts/list → ["回复客户", "升级主管", "推荐FAQ"]
客服选"回复客户"
prompts/get "reply-customer" →
  "你是客服{agent}。回复{客户}({套餐},${MRR}/月)。
   语气{tone}。参考FAQ: {faq}。对话: {chat}"
```

宿主拿 ① 的数据填入模板占位符，拼成最终 prompt 发给 LLM。

**③ Tools — 模型建议操作，人工确认后执行**

```
LLM 返回: "您好…建议发放 FIX50 优惠券安抚客户"
         [tool_suggestion: apply_coupon(customer=5542, coupon="FIX50")]

宿主弹出确认框 → 客服点确认
tools/call "apply_coupon" → ✅ 优惠券已发放
```

LLM 只是流水线中的推理组件，不是自主 Agent。

---

## Agent 场景：为什么通常只用 Tool

当宿主换成 Claude Code 这样的 Agent 时，编排职责被 LLM 自身接管：

```
传统宿主              Agent 的替代
────────────────     ──────────────────
读 Resources          → Agent 内核管理上下文（文件、git 等）
选 Prompts           → system prompt + slash 命令 + skill
调 Tools（模型建议）   → ⚠ 仍需要 MCP——外部系统 Agent 无法内建
```

Resources 和 Prompts 的编排角色已被 Agent 自身替代。**只有 Tool 在 Agent 场景下不可替代**——外部数据库、内部 API、第三方服务无法"内建"。

因此，MCP 在实践中几乎等同于 **Tool 调用协议**。

---

## Skill vs MCP：选型指南

| 维度 | Skill | MCP |
|------|-------|-----|
| 本质 | 注入 Claude 系统提示的**指令** | 外部进程暴露的**函数** |
| 作用 | 改变**怎么想**（工作流、规则） | 增加**能做什么**（查数据、调接口） |
| 是否引入新工具 | 否（只引导使用已有工具） | 是（提供新的可调用函数） |
| 跨平台 | 仅 Claude Code | Claude Code / Cursor / 自建 Agent |
| 适合 | 流程编排、规范固化、本地工具 | 外部系统集成、权限管控、跨平台复用 |

两者可组合：Skill 编排流程，调用 MCP Tool 完成数据访问。

---

## MCP Server 设计原则

### 1. Tool 描述比代码重要

模型只能通过 `description` 和 `inputSchema` 判断是否调用某个 Tool，描述要写明**干什么、何时用、参数含义**。

```python
# 差
@server.tool("query")  # 模型不知道什么时候该调
async def query(sql: str) -> str: ...

# 好
@server.tool("get_user_points")
async def get_user_points(user_id: int) -> str:
    """查询用户积分余额。当用户询问积分、余额时调用。"""
```

### 2. 返回值要让模型能消化

模型根据返回值做下一步决策——它不能消化原始数据库行，也不能从技术栈里推断原因。

```python
# 差：模型看不懂
return "(1023, 2350, 2024-01-15)"
raise Exception("mysql.connector.errors.DatabaseError: ...")

# 好：结构化 JSON + 语义化错误码
return json.dumps({"user_id": 1023, "balance": 2350, "status": "normal"})
return json.dumps({"error": "USER_NOT_FOUND", "message": "用户不存在，请确认 ID"})
```

语义化错误码（`USER_NOT_FOUND`、`INSUFFICIENT_PERMISSION`）让模型能判断下一步该追问用户还是尝试其他工具。

### 3. 接口防误用

MCP 是 AI 访问外部系统的入口，暴露得越少越安全：

- **不接受原始 SQL**，只接受结构化参数
- **数据库用只读账号**兜底
- **读 Tool 和写 Tool 分开**，写操作需确认机制
- **敏感字段脱敏**，不暴露手机号等个人数据

```python
# 差：整个数据库暴露给 AI
@server.tool("query_db")
async def query_db(sql: str) -> str: ...

# 好：固定查询逻辑，参数化接口
@server.tool("get_order_status")
async def get_order_status(order_id: int) -> str: ...
```

---

## 实战案例：积分商城 MCP

将积分商城的 MySQL 数据库以受控方式暴露给运营和开发，让 AI 可查积分、订单、库存，不给原始数据库权限。

```
src/mcp/
  server.py
  tools/
    points.py     # 查余额、查明细
    products.py   # 查库存
    orders.py     # 查订单状态
  db.py           # 只读连接
```

项目根目录 `.mcp.json`：

```json
{
  "mcpServers": {
    "pointshub": {
      "type": "stdio",
      "command": "python",
      "args": ["./src/mcp/server.py"],
      "env": { "DATABASE_URL": "mysql+pymysql://readonly:pass@localhost/pointshub" }
    }
  }
}
```

| Tool | 参数 | 用途 |
|------|------|------|
| `get_user_points` | `user_id: int` | 查询积分余额 |
| `get_points_history` | `user_id: int, limit: int = 10` | 查询积分流水 |
| `check_product_stock` | `product_id: int` | 查询商品库存 |
| `get_order_status` | `order_id: int` | 查询订单状态 |

调用效果：

```
用户：查一下用户 1023 的积分，他投诉积分少了

→ get_user_points(1023)          → 余额 2,350
→ get_points_history(1023, 10)   → 签到 +10, 兑换 -500 …

余额与明细一致，未发现异常。建议核实是否混淆账号。
```

---

## 企业级 MCP

| 层级 | 范围 | 示例 |
|------|------|------|
| 个人 | 个人工具 | 本地开发库调试 Server |
| 项目 | 项目业务系统 | 积分商城 `pointshub-mcp` |
| 企业 | 跨项目通用系统 | 连接 ERP / CRM 的统一 Server |

企业级 MCP 独立仓库维护，接口变更视为 Breaking change，需通知所有接入方。

---

# Harness 工程之知识工程 - 提升复杂项目的生成质量

## 适用场景

本文针对的场景是：**复杂领域项目的 Agent 代码生成质量不稳定**。典型领域包括嵌入式、汽车软件、AI 平台、交易系统，这类项目有两个共同特征：

- 大量关键工程知识分散在代码库之外（芯片手册、规范文档、历史故障、隐性约定）
- 通用 SDD 流程无法将这些知识有效传递给 Agent

提升生成质量有多种做法，本文推荐两者结合：

- **配合 SDD 工作流**：利用现成工具（如 OpenSpec、Superpowers/GSD）或自定义工作流，确保 Agent 按步骤推进、遇到不确定主动确认
- **构建知识工程**：将分散的领域知识系统化地组织为 Agent 可路由、可加载的结构

两者相辅相成——SDD 定义 Agent 如何推理，知识体系决定 Agent 推理时能看到什么。

---

## 诊断 — 复杂项目的生成质量瓶颈

### Agent 视角下的 SDD

Agent 执行时真正看到的只有两样东西：**Context** 和 **Instructions**。SDD 的各组成部分，对 Agent 而言本质上只有两类：

| SDD 组成 | Agent 视角 |
|----------|-----------|
| Spec / Template / Knowledge | Context |
| Skill / Workflow | Instructions |

所以 `Agent = Context + Reasoning`。

**Web Demo 场景**：实现用户登录。Spec + 通用代码知识足够。

**嵌入式场景**：实现 CAN 过滤功能。Agent 真正需要的是芯片手册与寄存器定义、驱动框架与板级设计、AUTOSAR 规范、项目编码规范、历史实现参考——这些关键知识**根本不在代码库里**。

这些关键知识**根本不在代码库里**。

流程因此不是 `Spec → Code`，而是：

```
Spec + Engineering Knowledge → Implementation
```

### Knowledge：最难积累的核心资产

Skill 本质是几十行 Prompt，可以快速编写和迭代。Knowledge 是团队多年的沉淀，无法快速复制。

| 维度 | Skill | Knowledge |
|------|-------|-----------|
| 构建成本 | 低（几小时） | 高（持续积累） |
| 价值占比 | ~5–10% | ~90–95% |
| 演进速度 | 快 | 慢但稳定 |
| 可迁移性 | 高（通用推理模式） | 低（领域专属） |

---

## 设计 — Skill、Knowledge 与 Router

三个组件的分工由一个核心约束推导出来：**Skill 只定义推理模式，不包含任何领域内容。**

这个约束决定了另外两层的必要性：

- 领域内容（规范、手册、历史约束）需要有地方存放 → **Knowledge**
- "当前任务该加载哪些知识、按什么步骤执行"需要有地方表达 → **Router**

### Skill：只定义推理模式

很多团队会为每个业务场景设计专用 Skill：

```
implement-can-driver
implement-spi-driver
implement-uart-driver
...（几十个）
```

这是常见误区：

- **推理模式高度相似**：理解需求 → 找相关模块 → 找类似实现 → 实现 → 验证
- **真正在变化的**：知识内容（寄存器名、配置顺序、历史约束），不是推理模式
- **后果**：把知识内容写进 Skill，复制出几十个结构几乎相同的文件

**Skill 的边界**：定义推理模式，不包含领域内容。"CAN 怎么过滤"、"哪个寄存器控制过滤器"不属于 Skill——正是这些内容的存在，才需要 Knowledge 和 Router。

| 情况 | 做法 |
|------|------|
| 已在使用 Superpowers/OpenSpec | 直接复用，无需重新设计 Skill |
| 需要领域专属步骤或阻断条件 | 通过 Router 注入，不改动 Skill |
| 现有 Skill 完全无法覆盖的全新交互模式 | 才新建 Skill，以现有 Skill 为子步骤编排 |

### Knowledge：五层分层模型

#### Layer 1：Architecture Knowledge

描述系统的整体结构，是 Agent 理解任何任务的基础。

**包含内容：** 架构图、模块关系、调用链、部署结构

```markdown
# 系统架构

语音唤醒 → ASR（语音识别）→ NLU（意图理解）→ TTS（语音合成）

## 模块边界
- ASR 只输出文本，不感知业务意图
- NLU 通过事件总线发布 Intent，不直接调用业务模块
- TTS 无状态，接收文本返回音频流
```

#### Layer 2：Coding Standards

规定项目内的统一编码规则，防止 Agent 生成风格不一致或违反约束的代码。

**包含内容：** 命名规范、日志规范、异常处理、线程模型、内存管理规则

```markdown
# 编码规范

## 内存
- 禁止使用 malloc/free，统一使用内存池 mem_pool_alloc()
- 禁止裸指针跨模块传递，使用 handle 机制

## 日志
- 统一使用 LOGI/LOGW/LOGE，禁止 printf
- 格式：[模块名][函数名] 消息内容

## 错误处理
- 所有返回值必须检查，不得忽略错误码
- 错误向上传递，不在中间层静默吞掉
```

#### Layer 3：ADR（Architecture Decision Record）

记录关键设计决策的**理由**，让 Agent 理解"为什么这么做"而不只是"做了什么"。

**包含内容：** 技术选型原因、被否决的方案、权衡取舍

```markdown
# ADR-003：采用事件总线替代直接调用

## 决策
模块间通信统一通过事件总线，禁止跨模块直接函数调用。

## 原因
- 直接调用导致模块间强耦合，历史上 NLU 改接口引发 5 个模块同步修改
- 事件总线解耦后，新增业务模块无需修改已有代码

## 被否决方案
- 共享内存：并发控制复杂，历史上出现过竞态 bug
- gRPC：引入网络开销，同进程内不必要
```

#### Layer 4：Domain Knowledge

嵌入式和汽车软件最重要的一层，存储领域专属的外部技术知识。

```markdown
# CAN 过滤器配置（STM32）

## 过滤模式
- 标识符屏蔽模式：用掩码匹配一组报文 ID
- 标识符列表模式：精确匹配指定 ID，不使用掩码

## 关键寄存器
- CAN_FMR：过滤器主控寄存器，初始化前必须置 FINIT 位
- CAN_FM1R：配置各过滤器为屏蔽/列表模式
- CAN_FS1R：配置过滤器位宽（16位/32位）

## 常见陷阱
- 过滤器激活前必须先进入初始化模式，否则写入无效
- 过滤器组编号从0开始，STM32F4 最多28组
```

#### Layer 5：Project Knowledge

企业最有价值的一层，记录在代码和文档中无法直接读出的隐性知识。

```markdown
# 模块地图

## CAN 子系统
- 入口：src/drivers/can/can_manager.c → can_manager_init()
- 过滤配置：src/drivers/can/can_filter.c
- 报文分发：通过事件总线，订阅者在 src/app/can_dispatcher.c
- Owner：张三（负责驱动层），李四（负责应用层分发）

## 历史 Bug
- [2024-03] 过滤器未在 FINIT 模式下配置，导致部分 ID 漏报
  修复：can_filter.c:45，增加 FINIT 位检查
- [2024-07] 报文队列满时丢帧无告警，线上静默丢数据
  修复：增加队列水位监控，超过 80% 触发 LOGW
```

#### 分层的实践意义

五层在三个维度上有实质差异，直接影响知识库的组织和 Router 的写法：

| 层 | 跨项目共享 | 变动频率 | Router 加载时机 |
|----|-----------|---------|----------------|
| L1 架构 | 否（项目专属） | 低 | 需要理解影响范围时 |
| L2 编码规范 | 部分（公司级可共享） | 低 | **每个任务都加载** |
| L3 ADR | 否 | 低 | 需要理解决策原因时 |
| L4 领域知识 | **是**（可建共享 repo） | 低 | 按技术领域按需加载 |
| L5 项目知识 | 否（项目专属） | **高**（持续更新） | 按模块按需加载 |

两个关键推论：

- **L4 可以跨项目共享**：STM32 手册、AUTOSAR 规范和具体项目无关，可以建独立 knowledge repo，多个项目通过 submodule 引用同一份，更新一次、全部受益。
- **L2 需要全量加载**：编码规范适用于所有任务，Router 的 load 字段应始终包含它；其余各层按任务需要按需加载，避免无关知识干扰 Agent 推理。

### Router：连接任务与知识

Router 的逻辑为什么不直接放进 Skill 或 Knowledge？

- 放进 **Skill**：Skill 就必须感知领域（"如果是 CAN 模块，加载 can.md；如果是 SPI，加载 spi.md"），每新增一个领域都要改 Skill，通用性消失
- 放进 **Knowledge**：Knowledge 是内容，路由规则是操作元数据，混在一起后内容文件变成充斥 if/else 逻辑的配置大杂烩
- 放进 **SDD 工作流**：工作流变成领域相关的，你就需要为嵌入式、汽车、AI 平台各维护一套 SDD，与"一套通用工作流 + 多个领域 Router"的目标背道而驰

Router 做这个隔离：Skill 不感知领域，Knowledge 不感知任务，Router 是"任务 × 领域"的映射层。改领域？改 router，不动 Skill。加知识？更新 router 的 load 列表，Skill 照常工作。

Router 的职责包含两项：**加载知识**（load）和**细化执行步骤**（steps）：

```yaml
task: implement-change
module: can

steps:
  - 阅读需求，确认是否涉及 CAN 过滤器、发送路径或报文分发
  - 进入 FINIT 模式前检查当前过滤器组占用情况
  - 按 can-filter.md 中的寄存器顺序配置，不得调换顺序
  - 退出 FINIT 模式，写入测试报文验证过滤行为
  - 逐条对照 AC，未覆盖项须列出并确认

load:
  - autosar
  - can
  - coding-standard
  - can-history
```

**Router 的成熟度演进：**

| 阶段 | 做法 |
|------|------|
| **初级**：知识体系刚建立 | Skill 内嵌 Routing 逻辑（识别领域 → 查找知识 → 实现） |
| **成熟**：知识库规模较大 | Router 独立：Task → Router → Context + Steps → Skill |

#### Router 字段的本质

Router 示例中的字段不是固定格式，而是从三个本质职责推导出来的：

| 职责 | 说明 | 必要性 |
|------|------|-------|
| **选择器** | 这个 Router 适用于什么场景（task、module 等标识） | 元数据，形式可以是字段、文件名或目录结构 |
| **加载器** | 注入哪些知识文件（`load`） | 核心，必须有 |
| **精化器** | 领域专属的步骤约束（`steps`） | 可选——只有领域有强约束执行顺序时才需要 |

设计具体 Router 格式时，从这三个职责出发按需设计字段即可，不必照搬示例。

#### 用 OpenSpec Schema 实现 Router

使用 OpenSpec 时，**自定义 Schema 天然承担了 Router 的职责**，三个职责在 OpenSpec 里都有对应位置：

| Router 职责 | 独立 Router 文件 | OpenSpec 实现 |
|------------|----------------|--------------|
| 选择器 | `task` / `module` 等字段 | Schema 名称本身（换场景 = 换 Schema） |
| 加载器 | `load` 字段 | `config.yaml` 的 `context` / `rules` 字段 |
| 精化器 | `steps` 字段 | 各 artifact 的 `instruction` 字段 |

例如为嵌入式 CAN 模块定义一个 `embedded-can` Schema：

- 在各 artifact 的 `instruction` 里写入寄存器配置顺序的约束（精化器）
- 在 `config.yaml` 的 `context` 里列出 `can.md`、`coding-standard.md` 等知识文件（加载器）
- 使用时只需 `openspec new change <name> --schema embedded-can`，两项职责同时激活

**不使用 OpenSpec 的场景**，Router 通常以 YAML 或 Markdown 文件存在于 `router/` 目录，Agent 执行前主动读取——格式不固定，按三个职责按需设计即可。

---

## 落地 — 知识工程与推荐架构

### 执行纪律：防止幻觉与跳步

有了知识体系还不够——还需要解决"Agent 是否真的做完了每一步"。幻觉完成（声称做了但没做）和跳步（遇到不确定直接假设）是复杂项目最常见的执行问题。

对策是在 Skill 里为每个步骤定义**完成标准**和**阻断条件**，不允许 Agent 靠自我声明推进：

| 步骤 | 完成标准 | 阻断条件 |
|------|---------|---------|
| 确认需求范围 | 列出涉及的所有模块和文件 | 影响范围不明确时，停下来确认，不得假设 |
| 查阅相关知识 | 列出查阅了哪些文件及关键约束 | 知识库无相关内容或有矛盾，向用户说明 |
| 实现变更 | 展示关键代码，说明每条约束如何满足 | 遇到规范未覆盖的情况，不得自行决策 |
| 逐条验收 | 每条 AC 注明"已覆盖/未覆盖/不适用" | 有未覆盖 AC 时不得声明完成 |
| 运行测试 | 粘贴实际测试输出 | 不得仅声明"测试通过" |

更系统的做法是引入**中间确认文档**——OpenSpec/Superpowers 的 propose → review → apply 就是这套机制：Agent 在实现前先输出一份包含"需求理解 / 影响范围 / 依据的知识 / **待确认项**"的结构化文档，用户确认后再开始写代码。"待确认项"强迫 Agent 在动手前把不确定的部分显式列出，而不是悄悄假设。

### 知识存储原则

对 Agent 来说，git repo 内的文件是最易访问的知识形式，优先于任何外部系统。知识的存储位置从两个维度判断：

| 维度 | 场景 | 推荐做法 |
|------|------|---------|
| **放入哪个 repo** | 体量可控，单项目使用 | 直接放入项目 repo（`knowledge/` 目录） |
| | 体量可控，多项目共享 | 建独立 knowledge repo，各项目通过 submodule 引用 |
| | 体量过大，git 不好用 | 使用 RAG（向量化知识库） |
| **是否与 src 混放** | ADR、架构文档、历史故障、外部规范 | repo 根目录下独立 `knowledge/` 目录 |
| | 接口定义、配置、Build 规则 | `src/` 内，与代码同目录 |

- 多项目共享不是 RAG 的理由——独立 git repo 同样可以共享，且版本可以 pin
- 历史故障、Review 经验等应在 git 里管理，而不是放 Wiki——Wiki 对 Agent 是额外的访问边界

### 推荐架构

目录结构对应五层模型（embedded/automotive 为领域示例，按实际领域替换）：

```
skills/
├── understand-system
├── implement-change
├── debug-issue
├── root-cause-analysis
├── review-change
└── investigate-performance

knowledge/
├── architecture/          # Layer 1：Architecture Knowledge
├── coding-standard/       # Layer 2：Coding Standards
├── adr/                   # Layer 3：ADR
├── embedded/              # Layer 4：Domain Knowledge
│   ├── stm32/
│   ├── freertos/
│   └── autosar/
└── project/               # Layer 5：Project Knowledge
    ├── module-map/
    ├── bug-history/
    └── owner-map/

router/
└── knowledge-router       # 不使用 OpenSpec 时的独立 Router 文件
```

---

## 结论

| 维度 | 传统认知 | AI Native 认知 |
|------|----------|----------------|
| 核心流程 | SDD → Skill → Code | SDD 工作流 + Engineering Knowledge System |
| 质量瓶颈 | Spec 写得够不够详细 | Engineering Knowledge 积累得够不够丰富 |
| 长期资产 | 流程文档 | Knowledge System |

三个组件各司其职：

- **Skill** — 决定 Agent 如何思考（推理模式）
- **Knowledge** — 决定 Agent 思考什么（领域内容）
- **Router** — 决定 Agent 在当前任务中应该看到什么（上下文装载）

知识工程与 SDD 工作流配合使用时效果最佳：SDD 是推理的骨架，Knowledge 是推理的血肉。

---

# Agent 驱动的探索性测试 - 用 Agent 代替人看护自动化过程

## 两个维度：驱动方式 × 执行工具

Android 端测试可以沿两个独立维度做选择：

**驱动方式**——测试由谁决策：
- **脚本驱动**：开发者提前写死操作步骤和断言，每次执行行为确定
- **Agent 驱动**：Claude 在运行时看截图决策，能处理未预期的 UI 状态

**执行工具**——测试通过什么操作设备：

| | ADB | UI Automator | Espresso |
|---|---|---|---|
| **耦合度** | 零耦合，无需源码 | 零耦合，无需源码 | 需要 View ID，依赖源码 |
| **范围** | 黑盒，任意 App | 黑盒，支持跨 App | 白盒，单 App 内 |
| **元素定位** | 像素坐标或解析 XML | 官方 API（By.text / By.res） | 声明式 Matcher（withId / withText） |
| **上手难度** | 最低，shell 命令即可 | 中，需部署 HTTP Server | 中，需编译测试 APK |

这两个维度可以自由组合：ADB、UI Automator、Espresso 都能用于脚本驱动，也都能作为 Agent 驱动的执行层。

---

## 脚本驱动

开发者提前写好测试用例，每次运行结果确定，适合 CI 回归守门。

### Espresso（单 App，白盒）

声明式：**找控件 → 执行操作 → 断言结果**

```kotlin
// 从 AC 直接映射到测试用例
@Test
fun login_success() {                          // 对应 AC-1
    onView(withId(R.id.username)).perform(typeText("test@test.com"))
    onView(withId(R.id.password)).perform(typeText("123456"))
    onView(withId(R.id.login_btn)).perform(click())
    onView(withId(R.id.home_title)).check(matches(isDisplayed()))
}

// 常用 Matcher：withId / withText / withTag / allOf
// 常用 Action：click / typeText / scrollTo / swipeLeft
// 常用 Assert：isDisplayed / withText / isEnabled / doesNotExist
// 异步等待：IdlingResource（自动等，不用 sleep）
```

### UI Automator（跨 App，黑盒）

```kotlin
val device = UiDevice.getInstance(instrumentation)
device.findObject(By.text("登录")).click()
device.findObject(By.res("com.dramaflow:id/btn")).click()
device.wait(Until.findObject(By.text("首页")), 5000)
```

### 运行

```bash
# 运行全部测试
adb shell am instrument -w com.dramaflow.test/androidx.test.runner.AndroidJUnitRunner

# 指定单个测试类
adb shell am instrument -w -e class com.dramaflow.LoginTest com.dramaflow.test/...
```

---

## Agent 驱动（以 test-agent 为例）

Claude 在运行时看截图决策，适合探索性验收——不需要提前知道 UI 结构，也能处理意外弹窗和布局变化。

test-agent 是项目使用的演示性质 Python CLI 工具集，以 ADB 为执行层，由 Claude Code 驱动测试循环。

### 架构：决策层 + 执行层

```
┌─────────────────────┐       HTTP (localhost)        ┌──────────────────────┐
│  Claude Agent       │  ─── POST /tap /type /swipe ─▶│  Android Device      │
│  (大脑: 看截图、     │  ◀── screenshot / hierarchy ──│  执行层（ADB 或      │
│   决策下一步)        │                               │  UI Automator 服务） │
└─────────────────────┘                               └──────────────────────┘
         │
         │  adb forward tcp:8711 tcp:8711（端口转发）
```

| 层 | 职责 | 特点 |
|----|------|------|
| **决策层** | 看截图判断状态、规划操作、验证结果 | 灵活，能处理意外弹窗和布局变化 |
| **执行层** | 找元素、点击、输入、截屏、获取 UI 树 | 可替换：ADB（当前）→ UI Automator Server（推荐） |

### 执行循环

```
Observe（截图 + UI 树）→ Plan（分析状态，决定下一步）→ Locate（定位目标元素）
   → Act（发送操作指令）→ Record（记录结果、截图存档）→ 循环直到完成或超时
```

核心模块：`adb_client / device / element_finder / crash_monitor / verifier / reporter`

### Mission 文件

Mission 直接对应 SPEC.md 中的主流程——**AC 定义验收标准，mission 定义验收任务**。

```yaml
# missions/login_flow.yaml
name: 登录流程验收
goal: 验证用户可以用正确凭证登录并进入首页
acceptance_criteria:
  - 登录后跳转到首页
  - 首页可见剧集列表
  - 顶部导航栏显示用户信息
steps_hint:
  - 找到邮箱输入框，输入测试账号
  - 找到密码输入框，输入密码
  - 点击登录按钮
  - 等待跳转，验证首页内容
```

### screen_knowledge：跨会话的操作经验库

Agent 探索中会遇到各种页面陷阱——键盘遮挡按钮、系统手势误触、单 Activity 架构导致的"Screen unchanged"误判等。如果不记录，每次新会话都要重新踩坑。

`screen_knowledge/` 目录以**页面名称为索引**存储这些经验。`info` 命令返回当前 Activity/Fragment 名称后，先查是否有对应的 `.md` 文件，有则读取再操作：

```
python test-agent/run.py info
→ Activity: LoginFragment

test-agent/screen_knowledge/LoginFragment.md 存在 → 读取
→ 陷阱：输入密码后键盘遮挡登录按钮，需先按 BACK 收起键盘
→ 带着这个认知再执行操作，不会重复踩坑
```

文件内容示例：

```markdown
# LoginFragment

## 陷阱
- 键盘遮挡：输入密码后按 BACK 收起键盘，再点登录按钮
- 单 Activity：tap 报 "Screen unchanged" 是正常的，登录成功标志
  是 nav_host_fragment 中出现 WebView 节点
- 底部导航栏始终可见：不要因为看到首页/发现/我的就以为已登录
```

---

## 执行层演进路线

Agent 驱动和脚本驱动的执行层都可以从 ADB 升级到 UI Automator Server，收益相同：

| | 纯 ADB（当前） | UI Automator Server（推荐） |
|---|---|---|
| **找元素** | `uiautomator dump` + 硬解析 XML | `By.res()`、`By.text()` 官方 API |
| **点击** | `input tap x y`（像素坐标） | `.click()` 元素级，自适应位置 |
| **输入** | `input text`（不支持中文） | `.text = "..."` 原生输入，支持中文 |
| **等待** | 轮询 Activity 名（不精确） | `device.wait(Until.findObject(...), 5000)` |
| **性能** | 每次启动新进程 | 内存常驻服务，毫秒级响应 |

将执行层替换为 UI Automator Server 时，决策层（Claude）不需要修改——这是最小代价获得最大执行稳定性的改进路径。

### WebView 内嵌 H5 的精确定位

ADB 和 UI Automator 都把 WebView 当作单个不透明节点处理——能看到截图，但无法获取 H5 内部 DOM 结构。通过 **Chrome DevTools Protocol（CDP）** 可以直接访问 WebView 的 DOM 层：

```kotlin
// App 中开启 WebView 远程调试（仅 DEBUG 构建）
WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
```

```bash
adb forward tcp:9222 localabstract:chrome_devtools_remote
curl http://localhost:9222/json    # 查看可调试的 WebView 列表
```

```python
# Playwright 连接到 Android WebView
browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
page = browser.contexts[0].pages[0]
await page.click("text=登录")
await page.fill("#username", "test@test.com")
```

| | ADB 坐标点击 | UI Automator Server | CDP（WebView 专用）|
|---|---|---|---|
| **H5 内部元素** | ❌ 无法区分 | ❌ WebView 是黑盒 | ✅ 完整 DOM 访问 |
| **API 请求拦截** | ❌ | ❌ | ✅ 可拦截/修改网络请求 |
| **JS 执行** | ❌ | ❌ | ✅ 可直接执行 JS |

在 test-agent 中的结合方式：原生层（登录页、播放器）继续用 ADB/UI Automator，进入 WebView 后切换到 CDP 通道操作 H5 内容，决策层不变。

---

## 与 SPEC 验收标准的关系

```
SPEC.md 中的 AC
   │
   ├─ 脚本驱动（Espresso / UI Automator / ADB）
   │    └─ 逐条 AC 对应一个 @Test 方法，CI 每次 PR 跑，结果确定
   │
   └─ Agent 驱动（test-agent）
        └─ AC 转为 mission 的验收目标，Claude 自主操作设备完成验收
```

同一条 AC，两种驱动方式各自消费：脚本驱动保证回归稳定性，Agent 驱动补充视觉和探索性验收。

---

# AI 时代的工程师心法 - 架构、判断与协作的 12 条朴素经验

---

> 以下 12 条来自实战，每条都有一个"反面教材"

---

## 架构先行，不能外包

**常见错误**：让 AI 直接决定架构

```
"帮我设计整个短剧 APP 的架构"
→ AI 给你一个"合理但通用"的方案
→ 3 周后发现不符合你的团队约束
```

**正确做法**：AI建议，人决策，AI 执行实现

```
和 AI 讨论：
  ├── SQLite vs PostgreSQL 各有什么利弊？结合我们的数据量给建议
  ├── H5 用 WebView 内嵌还是原生页面？考虑发版频率和包体积
  └── JWT 有效期的最佳实践是什么？短 token + refresh token 怎么搭配？

你拍板：
  ├── 选 SQLite（够用、零运维成本）
  ├── H5 WebView 内嵌（发版不受应用商店审核限制）
  └── access_token 15min + refresh_token 7d

AI 执行：
  ├── 写出符合架构的代码
  ├── 生成骨架文件
  └── 填充业务逻辑
```

> **结论**：架构隐含了众多背景信息和工程考量，不适合外包。个人小应用可以放手让 AI 决定架构，但企业应用必须人来做架构决策。

---

## 用 CLAUDE.md 或合适的 md 固化约束

**× 每次 Prompt 里重复写**
```
"记住，我们用 snake_case 命名，
 用 SQLAlchemy 2.0 ORM，
 不要直接在路由层操作数据库..."
（下次对话又要重新说一遍）
```

**✓ 写进 CLAUDE.md，一次写好，永久生效**
```markdown
## 命名规范
Python: snake_case 变量/函数, PascalCase 类

## 架构约束
禁止在 API 路由层直接操作数据库
必须通过 Service 层调用

## SDD 约束
接受任务前必须读对应 SPEC.md AC
生成代码后逐条自检 AC
```

**CLAUDE.md 是 Agent 的"宪法"**——不需要每次提醒，Agent 自动遵循

---

## 把需求写成结构化 Prompt

**× 口头描述**
```
"帮我做一个登录功能"
```

**✓ 结构化 Prompt**
```
任务：实现用户登录 API
输入：POST /api/auth/login，body: {email, password}
成功：返回 {access_token, refresh_token, expires_in}
失败：
  - 用户不存在 → 401 {"error": "invalid_credentials"}
  - 密码错误 → 401（不区分，防止枚举攻击）
  - 缺少字段 → 422 Pydantic 校验错误
约束：参考 SPEC.md Section 2.1，遵循 CLAUDE.md 命名规范
```

**为什么重要**：模型是"概率机器"，你给的信息越完整，它猜错的空间越小

---

## 小步拆解，每步可验证

**× 一次性大任务**
```
"帮我实现整个首页，包括 Banner、分类 Tab、剧集列表、
 Pinia 状态管理、Android WebView 加载、Loading 动画"
→ 写完发现 Banner 有问题
→ 不知道从哪里改起
```

一大步的本质问题：**约束严重缺失**

- 每个组件的数据格式、交互细节、错误处理全靠 AI 猜
- 猜错了你要一边纠错一边补约束，上下文越来越乱
- 同时处理 6 件事对模型能力要求极高，任何一环理解偏差都会向后扩散

**解决约束缺失有两条路：**

**✓ 方案 A：可验证的小步**（约束在步骤里）
```
Step 1：写后端 /api/dramas 接口 + 跑测试 ✓
Step 2：写 Vue3 剧集列表组件（mock 数据）✓
Step 3：接通真实 API 数据 ✓
Step 4：加 Banner 轮播 ✓
Step 5：加分类 Tab 筛选 ✓
Step 6：Android WebView 加载 ✓
```
每步范围小，约束自然清晰，出错也只在当前步骤内

**✓ 方案 B：先写详细 Spec，再统一开发**（约束在文档里）
```
先花 10 分钟写 SPEC.md：
  - Banner：数据格式、轮播间隔、点击跳转目标
  - 分类 Tab：来源、默认选中、切换行为
  - 剧集列表：字段、分页、空状态处理
  - 错误处理：网络失败的 UI 表现
然后把 Spec 作为上下文，AI 一次开发
```
同样有效——约束不在步骤里，就必须在 Spec 里

> **核心原则：约束必须显式存在，不能让 AI 去猜。**  
> 小步拆解是补足约束的一种手段，而非唯一手段。

**每一步的验证方式**：curl 测 API / 浏览器看 UI / adb 看 Log

---

## 用好 Git，随时掌握节奏

**Git 在 AI 时代的新用法**

```bash
# 做任何 AI 任务前：
git add -A && git stash   # 或 git commit -m "checkpoint: before AI changes"

# AI 改完后：
git diff                  # 逐行确认 AI 改了什么
git add <具体文件>         # 不要 git add .（避免 AI 顺手改了不该改的）
git commit -m "feat: ..."

# 发现走偏了：
git checkout <file>       # 撤销单文件
# 或在 Claude Code 中按 Esc Esc  回滚整个对话
```

> **关键心态**：Git 是你的"后悔药"，每次 AI 开始大改之前先存档

---

## 必须看代码，微观决策不能都外包，代码量增长后及时重构

**不看代码的后果**

- AI 写了 1000 行，你只看到"功能好像跑起来了"
- 之后发现大量重复 / 旧实现没清理 / 有安全漏洞 / 性能问题 / 与约定架构不符

**微观工程决策的例子**（AI 经常出错的地方）

- 错误码该用 400 还是 422？
- 这个字段该 nullable 还是必填？
- 这个 ViewModel 该是 `by viewModels()` 还是 `by activityViewModels()`？

> AI 会给一个"合理"的答案，但不一定符合你的系统约定——这类判断必须人来定

**AI 加速了技术债的积累速度**

```
传统开发：  写 100 行 / 天  →  技术债线性增长
AI 开发：  写 1000 行 / 天 →  技术债指数增长（10倍速）
```

**重构意识不是等问题出现才触发，而是持续的代码感知**

重构时机来自工程师对代码的主动审视，这也是初级和高级工程师的分水岭：

| 习惯 | 要问自己的问题 |
|------|--------------|
| 经常看整体结构 | 模块划分还合理吗？层次清晰吗？职责边界有没有模糊？ |
| 每次改动后感受合理性 | 这个改动放在这里对吗？会不会影响其他地方？ |
| 关注命名 | 这个函数/变量名能一眼读懂意图吗？有没有误导性？ |
| 追问重复逻辑 | 这段逻辑在别处出现过吗？能不能抽出来复用？ |
| 用 OO 眼光审视 | 职责单一吗？依赖方向对吗？有没有滥用继承或全局状态？ |

**AI 会生成代码，但 OO 概念、设计模式、分层思维这些判断力依然重要。**  
这部分能力在 AI 时代反而更值钱——AI 生成速度越快，缺乏这个判断力的工程师，技术债积累也越快。

> **建议**：每完成一个迭代，至少一次系统性 CR + 重构，不要等到"还不如重写"

---

## 管理好 Session 和上下文窗口

**上下文的生命周期**

```
新 Session 开始
    │
    ├── 0-50%：主要工作区间，Agent 理解上下文本身
    │          就会消耗相当一部分，不必过早 compact
    │
    ├── 70%：可以考虑 /compact，指明保留方向
    │         例："保留架构约束和当前任务进度"
    │
    └── 接近满：开新 Session，从文档重建上下文
               （不要等到真的撑满再处理）
```

注意：现代模型在上下文接近上限时不一定会出现明显的前后矛盾，  
更常见的是**悄悄忽略早期约束**，表面上看不出问题，实际已经偏离。  
不要靠"感觉有没有出错"来判断是否需要 compact 或开新 Session。

**实用技巧（Claude Code）**

```
/compact               → 压缩历史，保留关键信息
Esc Esc                → 中断当前任务，回退到上一个稳定状态
Shift+Tab              → 进入 Plan Mode，先规划再执行（复杂任务必用）
Fork Conversation      → 在当前节点分叉出新对话，探索不同方向；
                         不满意回到分叉点换路，主线上下文不被试错污染
```

**Subagent（子 Agent）** 也是上下文规划的手段：将独立子任务派发给新 Agent 执行，子 Agent 有自己的全新上下文窗口，不消耗主 Session 额度，也不带入噪音。适合并行任务、大量文件读取、反复试错等"脏活"。

> **整体原则**：compact 是压缩，fork 是分叉，subagent 是隔离，三者配合管理有限的上下文资源。

---

## 了解哪些任务 AI 不擅长

| 类型 | 为什么 AI 不擅长 | 正确做法 |
|------|-----------------|---------|
| 安全敏感逻辑 | 无法感知你的威胁模型 | 人工逐行审阅 |
| 性能调优 | 不了解你的数据量级和运行环境 | 人工 Profiling 后给 AI 针对性指令 |
| 有限状态机 | 容易遗漏状态转换边界 | 人工画出完整状态图后再让 AI 实现 |
| 架构重大决策 | 不了解团队约束和历史负债 | 人决策，AI 执行 |
| 跨会话上下文 | 每次对话重新开始 | 用文档（SPEC/CLAUDE.md）替代记忆 |
| 调试奇异 Bug | 缺乏运行时观测能力 | 给日志、给截图、给具体现象 |

---

## 分清执行类和架构类任务

| 任务类型 | 特征 | 正确姿势 |
|---------|------|---------|
| **执行类** | 目标明确，结果可验证 | 直接给 AI，看结果 |
| **架构类** | 涉及权衡，无唯一正解 | 对比提问，人决策 |

**对比提问示例**

```
× 直接问：
"我的 API 应该怎么设计分页？"

✓ 对比提问：
"以下两种分页方案，在我们的场景下（SQLite + 约 1 万条剧集数据）
 各有什么优缺点？
 方案 A：offset/limit
 方案 B：cursor-based（基于 id > last_id）"
```

→ AI 给出对比分析 → **你**做出决策

---

## 对 Agent 保持高可观测性

Agent 有工具调用能力，可以主动读日志、跑测试、查文件——缺失的信息它有时能自己补。  
所以"给足上下文"是原则，但更本质的问题是：**你的系统对 Agent 是否可观测？**

```
低可观测性（Agent 无从推进）：
  - 日志只有 "error occurred"，没有 stack trace
  - 错误被 try/except pass 静默吞掉
  - API 只返回 500，没有错误码和描述
  - 报错是截图，Agent 无法搜索或引用

高可观测性（Agent 可以自主推进）：
  - 结构化日志，含 timestamp / module / error_code
  - 完整 stack trace 输出到 stderr
  - API 返回明确的错误码和人可读的描述
  - 测试失败信息精确定位到文件和行号
```

可观测性好的系统，Agent 可以自己读日志、定位问题、提出修复，人只需确认根因。  
可观测性差的系统，人也调试得很痛苦——**AI 只是放大了这个问题**。

**仍需人工补充的场景**

- 问题只在真机 / 特定网络环境复现，Agent 无法访问
- 错误来自第三方 SDK，日志不透明
- 现象模糊，需要人先缩小范围再交给 Agent

> **结论**：提升系统可观测性，比每次 Debug 都手动整理上下文更有杠杆。

---

## 保持人类最终裁决权（HITL）

**必须人工确认的节点**

```
✅ 验收标准（AC）的最终确认
✅ 安全相关逻辑（Token 存储、权限校验）
✅ 数据模型的重大变更（加字段、改类型）
✅ 架构级决策（模块划分、通信方式）
✅ 重构中的结构性决定（职责划分、抽象边界）
✅ 合并到主分支前的代码审阅
```

**可以信任 AI 自主执行的**

```
✅ 根据 AC 生成代码
✅ 跑测试 + 修复测试错误
✅ 生成 Spec 骨架（人确认后）
✅ 执行已定义好的重构步骤
✅ 写文档、注释
```

> **原则**：AI 越快，人的判断越贵重。自动化执行层，人工决策层

---

## 设计能力是 AI 时代的驾驶执照

**常见错误**：以为 AI 能写代码了，就不用学设计模式和架构了

```
"AI 什么模式都懂，我需要的时候它自然会用"
→ 你看不懂 AI 生成的代码结构哪里不对
→ 你无法用精确的术语引导它走向正确的方向
→ 代码能跑，但结构在持续腐化
```

**设计能力在 AI 时代反而更值钱，三层原因：**

**第一层：共同话语体系。** 大模型对设计模式、架构原则有深度理解。你能说出"这里用策略模式"、"依赖方向反了"，AI 立刻精准调整——这是极简沟通。但前提是你得懂这些术语。

**第二层：判断力。** AI 会生成代码，但它不为你系统的长期健康负责。识别代码腐化、感知重构时机、判断职责边界——这些能力来自工程师的设计训练，AI 替代不了。

**第三层：引导力。** 当你想为旧系统添加新逻辑，又怕 Agent 乱改原有链路时，设计模式就是你的控制杆：

```
"为避免影响原有逻辑，请使用适配器模式（Adapter），
写一个新的 ExportAdapter 在外部包装原有的 ExportService，
而不是直接进去修改旧的 exportData 方法。"
```

一句模式名称，胜过一大段"你要注意这个、注意那个"的啰嗦约束。

**这也是区分高级工程师和新手的关键**：新手让 AI 自由发挥，高级工程师用设计语言精确引导 AI。

> **结论**：AI 懂设计，但只有你也懂，才能让它为你所用。设计能力不是可选的附加技能，它是你和 AI 的共同语言。

---

# Harness 工程之刻意进化 - 从人类看护到 Agent 自治

---

> **核心命题**：模型会自然进步，Harness 不会——它只在工程师主动决定"这次的教训不能白费"并付诸编码时才进化。每一次人类干预，都是一份等待被接收的 Harness 规格。**接不接收，是刻意的选择。**

---

## 前言

### 干预是信号，编码是选择

引入 Coding Agent 之后，工程师会走向两条路：

**第一条路**：Agent 犯错 → 纠正 → 等下一个模型版本。结果：每个月在不同功能上重复同样的纠正。

**第二条路**：Agent 犯错 → 纠正 → 多问一句"**这次纠正，我需要把什么编码进 Harness？**" 结果：同样的错误只发生一次，可管理的任务越来越大。

每一次人类干预，背后都有一个 Harness 缺口：

| 人类干预的原因 | Harness 工程的对应动作 |
|--------------|----------------------|
| Agent 不知道能不能执行这个命令 | 权限配置（settings.json）|
| Agent 不知道这个架构决策的历史背景 | 架构决策记录（ADR）|
| Agent 没有上次踩坑的记忆 | 经验文件（EXPERIENCE.md）|
| Agent 宣布完成但没有验证 | 验收技能（Skill）|
| Agent 要执行不可逆操作 | 人机交接协议（Hooks + Human Approval）|

### 任务 SPEC 也是 Harness

还有一类干预，在任务开始之前就已经注定：**任务本身定义不清晰。** "优化一下登录页"让 Agent 猜意图；执行到一半追加需求让 Agent 在移动目标上工作。刻意进化在这里意味着改变提任务的方式——每次分配任务前，主动回答：① 完成是什么样的（可逐条验证的 AC）② 边界在哪里（范围内/外各举一例）③ 交付物是什么格式（有无参考样本）。这三个答案就是任务的 SPEC，也是 Harness 的一部分。

### 约束强度原则

把干预编码进 Harness 时，要选哪一层？约束力从弱到强：

```
Memory（个人草稿）→ EXPERIENCE.md（依赖 Agent 读后遵守）→ CLAUDE.md（建议性质）→ CI/Lint（违规则失败）→ Hook（执行前拦截，不可绕过）
```

**用能覆盖问题的最强约束，而不是最方便的那个。** 在 CLAUDE.md 写"不要删文件"和用 Hook 拦截 `rm -rf`，解决的是同一个问题，效力相差一个数量级。每个场景的"编码原则"都在应用这个层级判断。

---

## L1 — 工具与权限：Agent 连"能不能做"都不清楚

---

### 场景：重复权限询问

你让 Agent 运行测试，它先问"可以执行 `pytest` 吗？"然后问 `python -m pytest`，批准了 12 次，大多数是同一类命令的变种。

**引入**：`.claude/settings.json` 的 `allowedTools` 配置：

```json
{
  "allowedTools": [
    "Bash(pytest*)",
    "Bash(python -m pytest*)",
    "Bash(git status)",
    "Bash(git diff*)",
    "Read",
    "Edit"
  ]
}
```

**编码原则**：每次批准"应当无需询问"的操作，就把它加进 allowlist——直到日常安全操作全部静默执行，只有高风险操作才弹出确认。

---

### 场景：危险操作无拦截 / 工具语义混淆

Agent 在重构时 `rm -rf` 了你没提交的本地配置。另一次，它因为 skill 名字里有"db"和"reset"就调用了 `db-reset`——测试数据被清空。两个根本原因：危险命令缺少拦截；工具描述不精确，破坏性工具没有访问控制。

**引入**：
1. `.claude/hooks/` PreToolUse 中间件：拦截 `rm -rf`、`DROP TABLE` 等模式，暂停并要求人工确认
2. Skill 描述精确化：标注 `[DESTRUCTIVE]`、使用前提、显式调用意图要求（不靠 Agent 自动推断）

**编码原则**：**确定性拦截 > 口头约束；工具描述是 Agent 的判断依据。** 语义歧义的工具，Agent 不会报编译错误，只会用错。

---

## L2 — 任务边界：Agent 知道自己该做什么范围吗

最基础的边界约束——在 CLAUDE.md 里声明 SDD 最小约束（接任务前读 SPEC.md AC，完成后逐条自检）。更复杂的边界问题：

---

### 场景：跨模块越权修改

你让 Agent 修复 `auth` 模块的一个 bug，它还"顺便"修改了 `profile/` 里一个它认为有关联的函数，破坏了一个调用约定，CI 红了。

**引入**：
1. **架构层**：每个模块的 `README.md` 明确声明 Interfaces 和 Constraints
2. **约束层**：`.importlinter` 配置模块依赖规则，违规则 CI 拦截

**编码原则**：目录结构即边界，但边界对 Agent 不是自动可见的——README 声明意图，import-linter 让违规有成本。

---

### 场景：硬编码设计值

Agent 新写了一个组件，用了 `background: #1a1a2e; color: #6c5ce7`。设计系统里有 `--bg-card` 和 `--color-primary`，等你发现时颜色值已散落在三个文件里。

**引入**：CLAUDE.md 明确引用规则（颜色必须用 CSS 变量）+ Token 合规检查脚本 + CI 集成（违规则无法合入）。

**编码原则**：**把"应该用设计 Token"的建议变成"不用就过不了 CI"的约束**——建议靠自觉，约束靠机制，效果不在一个量级。

---

## L3 — 微观工程决策：在任务范围内做出正确的设计判断

---

### 场景：Agent 选了团队明确排除过的方案

三个月前选了 SQLite（部署简单，单机性能足够）。今天 Agent 设计新模块时推断"应该用 PostgreSQL"，开始写 PG 的连接代码——它不知道这个决定三个月前已被否定。

**引入**：`docs/adr/`——架构决策记录，关键是记录**为什么不选另一个方案**：

```markdown
# ADR-001: 选择 SQLite 而非 PostgreSQL
状态：已采纳
决策：使用 SQLite
不选 PG 的理由：运维复杂度超出当前阶段价值。如规模超过 X，重新评估。
```

**编码原则**：ADR 是写给 Agent 看的——"为什么不选"是代码里看不出来的信息，也是 Agent 最容易走回头路的地方。

---

### 场景：超出任务范围的"顺便"改动

你让 Agent 给接口加一个参数，它加了，但顺便重构了错误处理、抽取了三个函数、修改了命名。改动有道理，但都超出任务范围，你需要 review 额外 300 行。

**引入**：在 CLAUDE.md 里加入 AC 边界约束：

```markdown
生成代码后：
1. 逐条自检 AC，确保覆盖
2. 范围外的改动，无论是否合理，都单独提出供人类决策
```

**编码原则**：SPEC 不仅是验收工具，也是任务范围的边界工具——AC 里没有的，标注"超出范围"而非直接实现。

---

### 场景：重复已知的反模式

两个月前修复了 `refresh_token()` 里 token 为 `None` 时抛未捕获异常的 bug，在 code review 里提到了。今天 Agent 写新的认证流程，同样的模式又出现了——这个陷阱只存在于 code review 记录和人的记忆里，对 Agent 等于不存在。

**引入**：`src/modules/auth/EXPERIENCE.md`——与模块代码 colocate 的经验文件：

```markdown
## refresh_token() 的 None 值陷阱（2025-11-12）
条件：token 参数为 None 时
症状：抛出未捕获的 AttributeError
修复：调用前必须显式检查 `if token is None: return None`
勿重现：新的认证流程中凡是调用 refresh 系列函数，都需要先做 None 检查
```

**编码原则**：经验文件记录"踩过的坑"，聚焦：触发条件 + 症状 + 修复 + 不重现要求——不写"注意 None 值处理"这样的废话。

---

## L4 — 跨会话与自我验证：Agent 能相信自己吗

---

### 场景：跨会话失忆 + 假完成

LLM 是无状态的：上次会话完成了 API 设计和数据模型，下次打开新对话 Agent 什么都不记得，重复做了已完成的部分。即使在同一会话里，Agent 也可能宣布"功能已实现，测试通过"，但你打开 App 发现搜索框根本没有出现——那是 AC 里的第 3 条。

**引入**：两类机制：
1. **状态外部化**：`PROGRESS.md` 记录会话间进度；Git 提交作为里程碑记录；`.claude/memory/project.md` 记录关键决策
2. **完成的操作定义**（CLAUDE.md）：逐条读 AC → 说明代码哪里覆盖了它 → 无法通过 review 验证的必须运行测试 → 所有 AC 验证前不允许宣布"完成"。也可实现为独立的 `spec-validate` skill。

**编码原则**：Agent 无法记住对话，但可以记住文件；"完成"这个词在 Harness 里必须有操作定义——否则 Agent 用最宽松的标准：代码存在 = 完成。

---

### 场景：长会话后期性能衰减

到第 40 轮对话后，Agent 开始忘了它两轮前才加的变量名，重复实现了已有的函数——上下文窗口膨胀，早期信息的注意力权重衰减。

**引入**：**子代理（Sub-Agents）——上下文防火墙**，不只是并行化工具：

```
主代理（维持任务状态和决策）
   ├─ 子代理 A（隔离上下文）→ 实现 Feature X → 返回结果
   ├─ 子代理 B（隔离上下文）→ 实现 Feature Y → 返回结果
   └─ 子代理 C（隔离上下文）→ 代码 Review  → 返回结果
```

**编码原则**：一个复杂任务超过 20 轮对话，就应该考虑用子代理隔离子任务，防止上下文膨胀影响主代理的判断质量。

---

## L5 — 经验沉淀：从纠正一次到永不再错

---

### 场景：纠正不持久化

你告诉 Agent 时区规则：所有时间字段必须用 UTC 存储，Agent 修改了。三天后在另一个功能里，它又用了本地时间——纠正只发生在那次对话里，没有被写到任何地方。

**引入**：**Memory → Experience 流水线**：

```
纠正 Agent 某个行为
    ↓ memory/feedback.md（个人层，不提交）
    ↓ 验证是否普适（多个功能都遇到了同样问题）
    ↓ 提炼到模块 EXPERIENCE.md（团队层，PR 提交）
    ↓ 影响所有模块时，提升到 CLAUDE.md（全局层，严格 Review）
```

**团队治理**：个人 memory 中验证为普适的教训，通过 PR 提炼到 EXPERIENCE.md，并在 `.claude/experience/INDEX.md` 建立关键词检索入口（`时区/UTC → time/EXPERIENCE.md`）。

**编码原则**：**纠正 Agent 的那一刻，就是写经验文件的时机**——Agent 纠正和 Harness 更新应该是同一个动作。

---

### 场景：经验文件退化为噪音

`auth/EXPERIENCE.md` 已经有 80 条记录，包括流水账和"注意边界条件"这样的废话。Agent 读到中途就停了，后面的关键陷阱它没有遵守。

**引入**：经验文件质量原则：

```
✅ 写"陷阱条件"：token 为 None 时 refresh_token() 抛未捕获异常
✅ 标日期：超过 6 个月标记待审查
✅ 少而精：5 条验证过的陷阱 > 50 条未经检验的"注意事项"
❌ 不写废话："注意空值处理"
❌ 不写过时内容：已修复的 bug 如不涉及类似场景，直接删除
```

**编码原则**：**经验文件的价值在于精准，不在于完整**——一条有触发条件、有症状、有修复方向的陷阱，价值等于十条"要注意 X"。

---

## L6 — 高风险操作：Agent 何时必须停下来

---

### 场景：不可逆副作用 + 无限重试

Agent 在自动化通知任务时，调用了生产环境邮件 API，向 500 个用户发送了格式未确认的通知。另一次，Agent 连续尝试了 15 次不同的安装方式，用了 20 分钟、消耗大量 token，最终还是没有解决——根本原因是网络被屏蔽，不是安装方式的问题。两个根本原因：对外可见的副作用操作没有人类确认门；缺少失败熔断机制。

**引入**：CLAUDE.md 明确两类规则，配合 Hook 自动暂停：

```markdown
## 必须人类确认的操作
- 向用户发送任何通知（邮件、推送、短信）
- 执行任何扣费或支付操作
- 删除数据库记录（非测试数据）
- 修改生产环境配置

## 任务挂起协议
遇到以下情况立即停止重试，请求人类判断：
- 同一类操作连续失败 3 次以上
- 遇到环境阻塞（网络配置、账号权限）
```

**编码原则**：**不可逆性和外部可见性是人类交接的核心判断标准；Agent 知道什么时候该"认输"，和知道如何解决问题一样重要。**

---

### 场景：并行 Agent 修改了同一个文件

两个 Agent 并行处理两个功能，都修改了 `shared/types.py`，产生冲突。合并时你需要手动判断哪些改动可以共存。

**引入**：**Git Worktree 隔离**——每个并行 Agent 在独立的 worktree 里工作：

```
main worktree（主线）
├─ worktree-feature-a（Agent A 的工作区）
└─ worktree-feature-b（Agent B 的工作区）
```

共享文件的修改通过主代理统一处理，子代理不直接改共享基础设施。

**编码原则**：**并行不等于混乱**——隔离的前提是有明确的工作区边界和共享资源协调机制。

---

## 综合：场景 → Harness 要素映射表

| 人类干预的场景类型 | 触发层级 | Harness 要素 | Harness 层 |
|-----------------|---------|-------------|-----------|
| 重复权限询问 | L1 | `settings.json` allowlist | 执行层 |
| 不可逆命令无警告 | L1 | `hooks/` 危险命令拦截 | 约束层 |
| 工具语义混淆 | L1 | 工具描述精确化 + 权限分级 | 执行层 |
| Agent 不读 SPEC | L2 | CLAUDE.md SDD 约束 | 文档层 |
| 跨模块越权修改 | L2 | 模块 README + import-linter + CI | 架构层 + 约束层 |
| 硬编码设计值 | L2 | Token 检查脚本 + CI | 约束层 |
| 走架构回头路 | L3 | `docs/adr/` ADR | 文档层 |
| 超出任务范围 | L3 | SPEC.md AC 边界约束 | 文档层 |
| 重复已知反模式 | L3 | 模块 `EXPERIENCE.md` | 经验层 |
| 跨会话失忆 + 假完成 | L4 | 进度文件 + Memory + 验收 Skill | 执行层 |
| 长会话性能衰减 | L4 | Sub-Agents 上下文隔离 | 执行层 |
| 纠正不持久化 | L5 | Memory → EXPERIENCE 流水线 | 经验层 |
| 经验文件退化 | L5 | 经验写作标准 | 经验层（治理）|
| 经验无法共享 | L5 | `.claude/experience/INDEX.md` | 经验层 |
| 不可逆副作用 + 无限重试 | L6 | 人机交接协议 + Hooks + 熔断规则 | 约束层 + 执行层 |
| 并行 Agent 冲突 | L6 | Git Worktree 隔离 | 执行层 |

```
架构层（软约束）：模块边界可见性 → 防止 L2 跨模块越权
文档层（软约束）：CLAUDE.md / SPEC / ADR → 防止 L2-L3 方向偏差
经验层（软约束）：EXPERIENCE.md / INDEX → 防止 L3-L5 重复踩坑
约束层（硬约束）：import-linter / CI / Hooks → 强制拦截 L1-L6 违规
执行层（硬约束）：Skills / Sub-Agents / Worktrees → 规范 L4-L6 工作流
```

---

## 刻意进化的飞轮

### 两个追问

> **每次干预结束后**：这次纠正，要把什么编码进 Harness 的哪一层？  
> **每次分配任务前**：AC 和边界清晰吗？还是在给 Agent 制造下一次干预的机会？

编码时优先选最强约束层（Hook > CI > CLAUDE.md > Experience > Memory）。

### 任务颗粒度增长路径

每覆盖一层，可以独立交给 Agent 的任务规模就扩大一级：

| Harness 成熟度 | 可独立处理的任务规模 | 典型任务 |
|-------------|------------------|---------|
| **L1 覆盖** | 单步工具调用 | 跑测试、格式化代码 |
| **L1-L2 覆盖** | 单模块功能实现 | 给某 API 加一个字段 |
| **L1-L3 覆盖** | 跨模块功能 | 完整的认证流程 |
| **L1-L4 覆盖** | 多日任务 | 完整的功能迭代（多会话）|
| **L1-L5 覆盖** | 自我改进 | Agent 遇到新陷阱后自动记录，下次不再犯 |
| **L1-L6 覆盖** | 多 Agent 并行 | 同时推进多个功能，人类只 review 关键节点 |

### 刻意修剪：Harness 也会腐化

刻意进化不只是"加"——也包括"删"：模型更强了（陷阱记录已过时），代码重构了（EXPERIENCE.md 的 bug 已消失），约束过时了（ADR 的理由已不成立）。过时的 Harness 不是中立的，它是阻力。

> **治理纪律**：每次模型版本升级，用裸奔基线测试审计 Harness——移除某条规则，观察 Agent 是否仍会犯错；如果不会，退役该规则。

---

> **结语**：Harness 进化的每一步，都来自于某个工程师在某次干预之后，选择多做那一步——分析根本原因，找到对应的 Harness 层，把这次的判断编码进去，让它永远不再需要人来做第二遍。这就是刻意进化：不是等待，而是主动把人类的每一次判断，转化为系统永久的能力。

---

# 多智能体并发开发

> 1 个开发者，多个并行 Agent——用 FD 状态机与斜杠命令驱动高并发 AI 开发。机器的执行能力已超过人类上下文切换极限；工程师的核心竞争力转向"将业务上下文精准翻译为 Agent 可执行的规格说明"。

**四件工具足以驱动高并发，复杂框架本身是认知负担：**

| 工具 | 职责 |
|------|------|
| **Claude Code** | 多终端并行 Agent 执行层 |
| **Tmux** | 多终端会话管理与角色隔离 |
| **Markdown** | 跨 Agent 的唯一真实数据源（Single Source of Truth）|
| **斜杠命令** | 纯文本指令驱动生命周期控制流 |

---

## FD：系统的唯一真相

**所有代码的编写均始于一份完成的 FD（Feature Design）。**

一份标准 FD 包含四个维度：

```markdown
FD-051: Multi-label document classification
Status: Open

## Problem
明确当前痛点与边界（现象 + 影响范围）

## Solution
最终方案（只写已决策的路径，不含备选方案）

## Files to Modify
精准列出所有将被新增/修改的文件

## Verification
明确的运行时验证步骤
```

> "Files to Modify" 强制在动手前思考影响范围，防止 Agent 随意扩散修改。

**FD 生命周期（`FEATURE_INDEX.md` 跨所有 FD 统一追踪）：**

```
Planned → Design → Open → In Progress → Pending Verification → Complete → Deferred → Closed
```

| FD | Title | Status | Effort |
|----|-------|--------|--------|
| FD-051 | Multi-label document classification | Open | Medium |
| FD-052 | Streaming classification pipeline | In Progress | Large |
| FD-050 | Confidence-based routing | Pending Verification | Medium |

代码提交完成后，Changelog 自动基于已关闭的 FD 累加，无需手写 Release Notes。

**初始化**：在任意新仓库运行 `/fd-init`，自动创建 `fd/FEATURE_INDEX.md` 和 `fd/templates/FD-template.md`（幂等）。

---

## 三角色工作台

每个终端窗口绑定特定角色，角色不混用：

| 角色 | 职责 |
|------|------|
| **PM** | 管理 Backlog、将需求转化为 FD |
| **Planner** | 加载代码库上下文，识别风险，完善 FD Solution |
| **Worker** | 先用 Plan mode 生成行级计划，确认后在 Worktree 中落地代码 |

```bash
# 终端 PM（在主项目目录）
claude
> /fd-new <需求描述>      # 生成 FD，自动填写四个维度
> /fd-status              # 随时查看全局进度

# 终端 Planner（在主项目目录）
claude
> /fd-explore FD-001      # 加载代码上下文，补全 Solution
# 确认文件无冲突后，创建 Worktree 交给 Worker

# 终端 Worker A（在各自 Worktree 目录）
cd ../project-fd001 && claude
> 实现 FD-001，完成后依次执行 /fd-verify 和 /fd-close

# 终端 Worker B（同时开启）
cd ../project-fd002 && claude
> 实现 FD-002，完成后依次执行 /fd-verify 和 /fd-close
```

**关键原则**：不同终端各自独立，通过 `fd/` 目录下的 Markdown 文件共享状态，不通过会话内存交互。

**物理布局建议（多屏环境）：**

- 屏幕 1：IDE——代码浏览、手动干预、跨模型校验
- 屏幕 2+：各角色终端（PM / Planner / Worker × N）

眼神落点即可判断当前上下文，无需脑力记忆"这个窗口在做什么"。多 Worktree 并行时可给常用目录配置短别名（如 `alias gfd001='cd ~/workspace/drama-flow-fd001'`），在对话中直接引用。

---

## 六大命令驱动生命周期

```
/fd-new       从需求描述创建新 FD
/fd-status    展示全局索引与进度状态
/fd-explore   加载代码库上下文、架构文档与开发指南
/fd-deep      启动并行推演（见第4节）
/fd-verify    校对代码，提出验证计划并提交
/fd-close     归档 FD 并自动更新 Changelog
```

> **设计哲学**：斜杠命令是生命周期的"卡口"，每个阶段转换必须显式触发——防止 Agent 越级执行，跳过规划直接写代码。

**三种编排模式：**

| 模式 | 适用场景 | HITL 介入点 |
|------|----------|------------|
| **扇出-扇入**（无依赖并行）| 多个 FD 的 Files to Modify 无重叠，可同时启动 N 个 Worker | 评审 FD 方案、确认实现计划、验收报告、合并 diff |
| **流水线**（阶段串行）| FD 之间存在逻辑依赖（B 的实现依赖 A 新增的 API）| 每个阶段交接点，上游关闭后再开启下游 |
| **竞合**（多解择优）| 技术方案不确定，需要探索多条路径后择优 | 择优节点；`/fd-deep` 在单会话内实现了这个模式的简化版 |

评审 FD 的 "Files to Modify" 节时，重叠与否决定了用扇出还是流水线；方案不确定时切入竞合模式。

**首次并发上手（以 2 个并行任务为例，扇出-扇入）：**

```bash
# ══ 终端：PM ════════════════════════════════════════════════
claude
> /fd-init                            # 初始化（一次性）
> /fd-new 优化短剧列表首屏渲染时间    # → 生成 FD-001（自动分配编号、填写四节、更新 FEATURE_INDEX.md）
> /fd-new 添加用户观看历史记录功能    # → 生成 FD-002

# ══ 终端：Planner ═══════════════════════════════════════════
claude                                # 新开终端，同一项目目录
> /fd-explore FD-001                  # 加载代码库上下文，补全 FD-001 Solution
> /fd-explore FD-002                  # 补全 FD-002 Solution

# 【人工评审 1】读两份 FD 的 Solution 和 Files to Modify
# 确认方案合理、无重叠文件 → 可并行；有重叠 → 调整为串行
# 以下是 shell 命令（在 Claude 会话外执行）：
git worktree add ../project-fd001 -b feature/FD-001
git worktree add ../project-fd002 -b feature/FD-002

# ══ 终端 A：Worker 1 ════════════════════════════════════════
cd ../project-fd001 && claude
> 读取 fd/ 目录下的 FD-001，先用 Plan mode 生成行级实现计划

# 【人工评审 2】确认实现计划无误后回复"继续"，Agent 开始执行
# Agent 完成实现后自动运行 /fd-verify FD-001，输出验收报告后停止等待

# 【人工评审 3】收到空闲通知后，检查验收报告
# 全部通过 → 在终端 A 继续：
> /fd-close FD-001

# ══ 终端 B：Worker 2（同时开启，不等 A 完成）═══════════════
cd ../project-fd002 && claude
> 读取 fd/ 目录下的 FD-002，先用 Plan mode 生成行级实现计划
# （同上，经过评审 2 → 执行 → 评审 3 → /fd-close FD-002）

# ══ 合并主干 ════════════════════════════════════════════════
cd <你的项目目录>
git merge feature/FD-001
git merge feature/FD-002
git worktree remove ../project-fd001
git worktree remove ../project-fd002
```

**完整工作流：**

```
/fd-new <描述>       ← PM：需求 → FD 文档
    ↓
/fd-explore <FD>     ← Planner：加载上下文，识别风险
    ↓（遇到复杂决策）
/fd-deep <FD>        ← 并行推演，汇总最优方案
    ↓
实现代码             ← Worker：在独立 Worktree 中实现
    ↓
/fd-verify <FD>      ← 逐条验收，运行测试
    ↓
/fd-close <FD>       ← 归档，追加 CHANGELOG

/fd-status           ← 随时查看全局进度
```

---

## /fd-deep：遇到难题时并行推演

FD Solution 写完后仍有未解决的 `%%` 批注，或技术方案不确定时，使用 `/fd-deep` 同时启动 4 个子 Agent 从不同角度独立推演。`/fd-deep` 底层使用 Claude Code 的 **Task 工具**——它是内置的子 Agent 调度器，允许在同一会话内并行启动多个独立推理任务。

```
主 Planner（遇到复杂问题）
    │ 调用 Task 工具 × 4（同时）
    ├── 子 Agent 1：算法视角
    ├── 子 Agent 2：架构视角
    ├── 子 Agent 3：风险视角
    └── 子 Agent 4：增量步骤
    │ 等待全部完成
主 Agent 汇总 → 写回 FD Solution 节
```

触发：`/fd-deep FD-003`

> 与 `/fd-explore` 的区别：explore 是加载上下文（读），deep 是并行推理（算）。

**内联批注技巧**：在 FD Solution 节用 `%%` 标注疑问——不只是 fd-deep 时，日常写 FD 时也适用。Agent 执行前先解决批注，避免带着未解决的假设落地代码：

```markdown
## Solution
Replace cron-based batch processing with an event-driven pipeline.
%% what's the max queue depth before we start dropping? need backpressure math
Failures go to the dead-letter queue.
%% what happens to in-flight items during cutover? need to confirm drain behavior
```

---

## 上下文管理：双层 CLAUDE.md

问题根源：智能体缺乏判断力（害怕报错、留存死代码）。解法：不让全局 CLAUDE.md 过载，按需读取深度指南。

```
CLAUDE.md（保持精简）          docs/dev_guide/（深度库，按需读取）
─────────────────              ──────────────────────────────────
代码格式规范                   1. 禁止静默回退：配置错误必须大声报错
Python / SQL 约定              2. 部署安全：破坏性操作必须等待运行任务完成
FD 生命周期规则                3. 严格解析：LLM JSON 必须宽容模式，禁止裸用 json.loads()
```

- **CLAUDE.md 精简** → 每次 Session 完整读取，不被截断
- **深度指南按需加载** → 减少上下文噪音，只在需要时读取相关规则

**让 Agent 知道何时读深度指南**：在 CLAUDE.md 末尾加一行引导，或在 FD 的 Solution 节直接点名：

```markdown
# CLAUDE.md 末尾
涉及部署操作时，读取 docs/dev_guide/deployment.md 再执行。
涉及 LLM 调用时，读取 docs/dev_guide/llm_patterns.md 中的解析规范。
```

---

## 系统边界与认知负荷

**并发上限：**

| 并发数 | 状态 | 建议 |
|--------|------|------|
| 1–3 | 高效区 | 正常推进 |
| 4–6 | 压力区 | 注意上下文切换成本 |
| 7–8 | 极限区 | 频繁要求总结是过载信号 |
| 8+  | 崩溃区 | 先完成一个再开新的 |

**四项物理限制：**

| 限制 | 描述 | 应对策略 |
|------|------|---------|
| **串行依赖冲突** | 强制并行存在顺序依赖的功能会导致 Merge 冲突 | 保持增量与原子化提交 |
| **上下文极速消耗** | 探索型任务快速消耗 Token，Compaction 丢失关键决策 | 大幅增加 Checkpoint 频率 |
| **黑名单博弈** | Agent 会绕过命令黑名单（拦截 `rm` 后用 `unlink`）| 黑名单按语义而非命令名设计 |

`/fd-status` 输出的 "Active Work" 数量是实时负荷指示器，超过 4 个 In Progress 时系统会主动提示。

---

## 开发者的新定位

核心竞争力不再是亲手写每一行代码，而是**将业务上下文精准翻译为 Agent 可执行的规格说明**：

| 过去的核心能力 | AI 时代的核心能力 |
|---|---|
| 写出正确的代码 | 写出正确的 FD（规格翻译能力）|
| 调试 Bug | 设计可观测的系统（让 Agent 自己调试）|
| 管理代码复杂度 | 管理 Agent 并发复杂度 |
| 执行实现 | 决策架构 + 验证结果 |

工程师不再是"代码生产者"，而是"规格定义者"与"质量裁判员"——这个角色反而更需要深厚的业务理解力与工程判断力。

---

## 适用范围

这套方案的核心取舍是**用人工审查换零依赖**——不依赖任何编排框架，任何项目 5 分钟内可以跑起来，代价是依赖人在三个关键节点介入，并发规模受认知负荷限制。

**适合：**
- 1–3 名开发者，2–6 个并发任务
- FD 之间相对独立（文件无重叠，逻辑无强依赖）
- 对工具链复杂度敏感、不想引入额外框架的团队

**不适合：**
- FD 之间有复杂逻辑依赖（A 的 API 未完成，B 无法测试）
- 需要 10+ 并发或全自动无人值守流水线
- 需要跨 Worker 实时共享发现（如公共抽象的协调）

---

## 附录 A：斜杠命令实现机制

斜杠命令本质是放在 `.claude/commands/` 下的 Markdown 文件，Claude Code 启动时自动扫描加载。键入 `/fd-new 优化首屏渲染` 时，Claude 读取 `fd-new.md` 的 prompt，将参数注入 `$ARGUMENTS`，按步骤执行。

**FD 不是独立安装的工具**，而是建立在这套机制上的工作流约定。本项目已内置完整命令文件，移植到其他项目直接复制 `.claude/commands/fd/` 目录即可。在 `.claude/commands/` 下新建任意 `.md` 文件也可封装自己的重复性操作。

```
.claude/commands/fd/          fd/
├── fd-init.md                ├── FEATURE_INDEX.md   ← 全局状态注册表
├── fd-new.md                 ├── templates/
├── fd-status.md              │   └── FD-template.md
├── fd-explore.md             ├── FD-001-<slug>.md
├── fd-deep.md                └── FD-002-<slug>.md
├── fd-verify.md
└── fd-close.md
```

每个命令文件顶部的 frontmatter 控制元数据和工具权限：

```markdown
---
name: fd:new
description: 从用户需求描述创建新 FD 文档
argument-hint: "<需求描述>"
allowed-tools:
  - Read
  - Write
  - Bash
---

（以下是 prompt 正文，描述 Agent 应该怎么做）
```

---

## 附录 B：空闲通知配置（可选）

让完成的终端窗口自动"亮起来"，避免轮询 8 个并发任务的状态。

**~/.claude/settings.json**：
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\a'"
          }
        ]
      }
    ]
  }
}
```

**~/.tmux.conf**：
```
set-option -g bell-action any
set-option -g monitor-bell on
setw -g window-status-bell-style reverse
```

效果：Claude Code 停止输出时，Tmux Tab 标题反色显示。

---

# 角色、组织、协作与度量

## 为什么这三件事要放在一起谈

DORA 2025 发现 AI 把个人产出翻倍，但组织交付指标几乎没动。**瓶颈转移了**，不在执行而在审查、决策、协作结构。

**生产力提升必须和组织结构、协作方式、度量体系同步重构，才能转化为组织产能。** 角色边界决定协作接口，协作接口决定组织结构，度量体系决定什么行为被激励。

---

## 一、各角色的定位演变

### 核心逻辑

Agent 接管大量执行性工作后，各角色的价值向 Agent 无法替代的部分集中：**领域判断力、体验直觉、系统级权衡、最终确认责任**。

各角色转型的共同结构：

| | 保留 | 新增 | 放下 |
|---|---|---|---|
| **PM** | 用户价值判断、业务优先级 | 将业务意图转化为可执行 Spec | 手工整理需求文档 |
| **设计师** | 交互体验、感知层审美判断 | 将设计约束系统化沉淀为 Design System | 逐一标注标注 Figma 参数 |
| **开发** | 复杂系统设计、架构判断 | Harness 设计、Spec 质量管理 | 重复性实现工作 |
| **测试** | AC 最终确认、验收策略设计 | 探索性验收 Agent 编排、质量门禁设计 | 手工回归用例执行 |
| **运维** | 可靠性标准制定、重大故障决策 | 可观测性基础设施设计、故障模式库建设 | 手工日志分析 |

### 角色融合趋势

执行层的技能门槛随 Agent 能力提升而降低，职能边界开始软化：

- **工程师参与设计**：在可执行设计系统的约束下，工程师不再需要专业设计背景就能做出符合品牌规范的 UI 决策，因为约束已被编码进 Harness
- **PM 动手验证**：PM 可以透过 Agent 快速实现一个概念性 Prototype，验证想法后再交给工程师精化，减少"说不清楚"的沟通损耗
- **全栈化不再要求全能**：全栈不是要求深度掌握每一层，而是靠 Agent + Harness 拉平技能门槛——开发者用统一的 Spec 和工具链跨越前后端边界
- **角色边界由判断力维持**：能被 Agent 替代的知识不再是护城河；架构权衡、用户价值判断、最终确认责任，才是角色存在的意义

### 新角色涌现

随着 Harness 成为组织基础设施，专职维护 Harness 的角色开始出现：

- **规格架构师**：负责跨系统的 Spec 体系设计与 AC 质量管控
- **Harness 平台工程师**：维护组织级 Skills、MCP 工具链、Agent 编排基础设施
- **AI 质量工程师**：设计评测体系、维护 Eval 框架、管理 AI 引入缺陷
- **设计系统工程师**：维护可执行设计系统，确保设计约束持续覆盖 AI 生成的 UI

---

## 二、组织与协作的进化

### 核心问题：为什么看不到组织提效

当个人写代码速度提升 2 倍，但 PR 进入 review 队列等待时间也翻倍，最终交付速度不变。这不是特例，是系统性现象：

```
个人执行加速 → 上游产出增加 → 下游审查/决策成为新瓶颈
```

三类常见瓶颈转移：
1. **Review 瓶颈**：代码生成加速，但每个 PR 仍需人工审阅，队列积压
2. **协作协议瓶颈**：个人技巧不共享，每个人的 Harness 不同，协作接口不一致
3. **决策瓶颈**：Agent 能生成选项，但最终判断的人没有增加

**解法不是"让人审得更快"，而是重新设计协作结构。**

### 组织形态演变

**从职能部门到双层模型**

```
传统：前端组 / 后端组 / 测试组 / 运维组（职能分工）
↓
AI Native：
  产品特性团队（feature team）：小团队，全栈化，端到端交付
  平台 CoE（Center of Excellence）：维护 Harness 基础设施、设计系统、工具链
```

平台 CoE 的核心价值：把优秀实践编码成 Harness，让每个 Feature Team 都能继承组织经验。

**团队规模变化**

- 执行实现类人手减少（Agent 承接）
- 判断类角色密度不变，甚至更集中
- 人机配比成为新的组织设计参数（每个判断者驾驭几个 Agent）

### 协作方式重构

**从串行交接到并行协作**

```
传统串行：需求完成 → 设计完成 → 开发 → 测试 → 上线
AI Native 并行：Spec 定稿（HITL 确认）→ 设计/开发/测试 Agent 并发 → 各自门禁检查
```

HITL 检查点成为新的协作时刻，取代"交接会议"：Spec 评审、方案确认、合入前审阅。

**个人技巧 vs 组织资产**

这是最容易被忽视的转型：

| 个人技巧 | 组织资产 |
|---|---|
| 某人会写好 Prompt | CLAUDE.md / AGENTS.md 里的规则 |
| 某人知道这个模块的坑 | EXPERIENCE.md 里的经验文件 |
| 某人写的 CR Skill | 团队 Skills 库 |
| 某人知道设计规范 | 可执行 Design System |

**个人提效只能持续到这个人离职；组织资产的效益随团队规模放大。**

### 企业案例参考

- **协作单元变化**（Microsoft）：静态 org chart 让位于围绕成果动态组队的 Work Chart，人机配比成为组织设计参数
- **组织结构重塑**（Moderna）：HR 与 IT 部门合并，人类员工与 AI Agent 在同一编制框架内规划
- **制度性重组**（Duolingo）：AI-first 重组后 headcount 只批给无法继续自动化的工作，AI 使用纳入招聘与绩效

---

## 三、AI Native 效能度量

### 度量视角的转变

旧视角：人完成了多少工作（代码行数、PR 数、任务数）

新视角：人能驾驭多少 Agent、放大多少组织产能

核心目标指标：**Human Amplification Factor（HAF）**

```
HAF = AI 介入后的有效产出 / 同等人力无 AI 时的产出
```

AI Native 组织的竞争力不在于有多少人，而在于每个人的产能放大倍数。

### Goodhart 定律陷阱

> "当一个指标成为目标，它就不再是好指标。"

典型扭曲案例：**AI 生成代码占比**作为 KPI
- 开发者把本来自己写的简单代码也交给 AI 生成，采纳率飙升
- 但代码质量、交付速度没变，甚至因为 review AI 代码的成本上升而下降

**度量必须追踪结果，而非行为本身。**

### 五层指标体系

每层回答一个递进问题：

**第一层：AI 采纳程度** — 大家是否在用 AI？容易追踪但也容易扭曲
- AI 活跃用户占比、AI 参与各研发环节的比例、建议采纳率

**第二层：Agent 生产力** — AI 是否真正替代了部分工作？
- Agent 完成任务数、自治率（无需人工干预完成的比例）、人均管理 Agent 数

**第三层：Harness 成熟度** — AI 为什么有效或无效？关注基建
- Agent 场景覆盖率、Agent 任务成功率、Context 命中率、自动评测通过率

**第四层：工程质量** — AI 生成的东西可靠吗？防止快而烂
- 缺陷率、回滚率、AI 引入缺陷率、测试覆盖率、Review 返工率

**第五层：交付效率** — 业务交付更快、更便宜了吗？最终目标
- Lead Time、吞吐量、单位功能成本、Engineering ROI

### 三个最重要的先行指标

在五层中，这三个指标对最终交付效率的预测性最强：

1. **人均管理 Agent 数**：衡量 Harness 成熟度和团队组织能力
2. **平均交付时间（Lead Time）**：衡量端到端流程是否真正加速
3. **线上缺陷率**：衡量质量是否在加速中守住

### 企业实践口径

- **Google**：公司级口径为"新增代码 AI 生成占比"，配套 Code Review 质量追踪
- **GitHub Copilot 官方研究**：任务完成提速 55%、建议采纳率约 30%、新增代码 41% AI 生成
- **DORA 2025**：工程体系成熟的组织把个体提效转化为交付改善；基础薄弱的组织 AI 加速技术债
- **国内企业**：腾讯/阿里/百度各有差异化口径，侧重点从"渗透率"到"代码生成占比"不等

### 落地原则

1. **度量用于改进 Harness，而非考核个人**：把指标作为诊断工具，而非绩效指标
2. **采纳层和质量层必须联动**：单看采纳率容易"快而烂"，单看质量层看不出 AI 贡献
3. **从先行指标开始**：优先建立 Lead Time + 缺陷率基线，再逐步补充 Harness 成熟度追踪
4. **接受度量本身需要迭代**：第一套指标不会完美，建立反馈闭环比追求精确更重要
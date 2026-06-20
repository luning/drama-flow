
## 适用场景

本文适用于以下三类场景：

- **复杂领域项目**：嵌入式、汽车软件、AI 平台、交易系统等，代码库之外存在大量隐性工程知识，通用 SDD 流程无法有效传递给 Agent，导致生成质量不稳定
- **自定义 SDD 设计**：团队希望在「规格驱动开发」基础上，针对本领域特点设计专属 SDD 工作流，需要理解 Skill 与 Knowledge 的分工边界
- **项目空间建设**：本文所描述的 Knowledge 分层和 Knowledge Router，是 Harness 项目空间的核心内容之一——项目空间不只是文件目录，而是一套可被 Agent 路由和加载的工程知识体系

> 对于复杂系统，提高代码生成质量的关键不是设计越来越复杂的 SDD 流程，而是构建可路由的**工程知识体系（Engineering Knowledge System）**。

---

# 一、重新理解 SDD

传统描述中，SDD 是一个线性流程：Spec → Design → Code → Test。

但对 Agent 来说，执行时真正看到的只有两样东西：**Context** 和 **Instructions**。

这意味着：

| 传统概念 | Agent 视角 |
|----------|-----------|
| Spec、Template、Knowledge | Context（上下文） |
| Skill、Workflow | Instructions（指令） |

因此，Agent 的本质是：

```
Agent = Context + Reasoning
```

SDD 的价值不在于流程步骤，而在于它能往 Context 里注入多少有效的工程知识。

---

# 二、为什么通用 SDD 对嵌入式不够

**Web Demo 场景**：实现用户登录。Agent 只需要 Spec + 通用代码知识即可完成。

**嵌入式场景**：实现 CAN 过滤功能。Agent 真正需要的是：

- 芯片手册与寄存器定义
- 驱动框架与板级设计
- AUTOSAR 规范
- DBC 文件
- 编码规范
- 历史实现参考

这些关键知识**根本不在代码库里**。因此对复杂系统来说，流程不是 `Spec → Code`，而是：

```
Spec + Engineering Knowledge + Code → Implementation
```

缺少 Engineering Knowledge 这一层，Spec 再详细也无法生成高质量代码。

---

# 三、Skill 应该怎么设计

很多团队会为每个业务场景设计专用 Skill：

```
implement-can-driver
implement-spi-driver
implement-uart-driver
implement-i2c-driver
...（几十个）
```

这是一个常见误区。这些 Skill 的**推理模式高度相似**：理解需求 → 找相关模块 → 找类似实现 → 实现 → 验证。真正在变化的是**知识内容**，不是推理模式。

**正确做法：Skill 按 Reasoning Pattern 拆分，而不是按业务名词拆分。**

推荐的 Skill 集（5~15 个即可覆盖绝大多数开发活动）：

| Skill | 职责 |
|-------|------|
| `understand-system` | 理解系统架构与模块关系 |
| `analyze-requirement` | 分析需求，识别影响范围 |
| `implement-change` | 实现变更 |
| `debug-issue` | 调试定位问题 |
| `root-cause-analysis` | 根因分析 |
| `review-change` | 代码审查 |
| `refactor-module` | 重构模块 |
| `investigate-performance` | 性能排查 |
| `write-tests` | 编写测试 |
| `release-delivery` | 发布交付 |

---

# 四、Knowledge 才是核心资产

Skill 本质是几十行 Prompt，可以快速编写和迭代。Knowledge 是团队几年到十几年的沉淀，无法快速复制。

| 维度 | Skill | Knowledge |
|------|-------|-----------|
| 构建成本 | 低（几小时） | 高（持续积累） |
| 价值占比 | ~5–10% | ~90–95% |
| 演进速度 | 快 | 慢但稳定 |
| 可迁移性 | 高（通用推理模式） | 低（领域专属） |

随着项目规模增长，真正持续积累价值的是 Knowledge，而不是 Skill 库。

---

# 五、Knowledge 分层模型

## Layer 1：Architecture Knowledge

描述系统的整体结构，是 Agent 理解任何任务的基础。

**包含内容：** 架构图、模块关系、调用链、部署结构

**示例（语音系统）：**
```
Wakeup → ASR → NLU → TTS
```

---

## Layer 2：Coding Standards

规定项目内的统一编码规则，防止 Agent 生成风格不一致或违反约束的代码。

**包含内容：** 命名规范、日志规范、异常处理、线程模型、内存管理规则

**示例（嵌入式）：** 禁止 `malloc`、统一使用 `LOGI`、禁止裸指针

---

## Layer 3：ADR（Architecture Decision Record）

记录关键设计决策的**理由**，让 Agent 理解"为什么这么做"而不只是"做了什么"。

**包含内容：** 技术选型原因、被否决的方案、权衡取舍

**示例：** 为什么不用 Kafka → 为什么采用 gRPC → 为什么采用事件总线

---

## Layer 4：Domain Knowledge

嵌入式和汽车软件最重要的一层，存储领域专属的外部技术知识。

| 领域 | 核心知识点 |
|------|-----------|
| STM32 | DMA、中断、寄存器、时钟树 |
| FreeRTOS | Task、Queue、Semaphore、Deadlock 案例 |
| CAN | DBC、仲裁、报文结构、错误处理 |
| AUTOSAR | RTE、ARXML、BSW、SWC |

---

## Layer 5：Project Knowledge

企业最有价值的一层，记录在代码和文档中无法直接读出的隐性知识。

**包含内容：**

- **模块地图**：CAN 入口在哪、语音入口在哪、OTA 入口在哪
- **Owner 关系**：各模块的负责人
- **优秀 PR**：值得参考的历史实现
- **历史 Bug**：踩过的坑和解决方案
- **故障案例**：线上事故的根因与教训
- **Review 经验**：高频问题与改进模式

---

# 六、Knowledge Router

Knowledge Router 是连接 Task 和 Knowledge 的关键组件，职责是：**识别任务 → 加载正确知识**。

**示例：**

Agent 收到任务：`实现 CAN 过滤功能`

Router 识别标签：`embedded`、`automotive`、`can`

Router 加载知识：

```
architecture + coding-standard + can + autosar + historical-pr + bug-history
```

Agent 最终看到的 Context：

```
Implement Change Skill
  + Architecture Knowledge
  + CAN Domain Knowledge
  + Coding Standards
  + Historical Examples
  + Bug History
```

这就是为什么同一个 `implement-change` Skill 可以处理完全不同领域的任务——Skill 提供推理框架，Knowledge 提供领域内容，Router 决定装载什么。

---

# 七、Router 是否应该独立

取决于团队成熟度：

| 阶段 | 做法 |
|------|------|
| **初级**：知识体系刚建立 | Skill 内嵌 Routing 逻辑（识别领域 → 查找知识 → 实现） |
| **成熟**：知识库规模较大 | Router 独立：Task → Router → Context → Skill |

成熟阶段，Skill 只关注"如何思考"，Router 负责"思考什么"，职责清晰，Skill 也更稳定。

---

# 八、知识同源性原则

知识的存储位置需要从两个维度来判断：**是否在同一 git repo**，以及**是否与 src 代码混放**。这是两个不同的问题，混在一起会导致错误的存储决策。

## 维度一：是否放入 git repo

对 agent 来说，**git repo 内的 markdown 文件是最易访问的知识形式**，优先级高于外部 Wiki 或知识库。判断知识是否放入 git，核心依据是归属权和体积，而不是知识类型：

| 类型 | 示例 | 是否入 git | 理由 |
|------|------|-----------|------|
| 项目自有知识 | ADR、架构说明、历史故障、Review 经验、最佳实践 | **是** | 随项目演进，需版本控制，agent 可直接检索 |
| 外部标准/规范 | STM32 手册、AUTOSAR 规范、ISO 26262 | **否** | 非自有、体积大、更新周期独立于项目 |

历史故障和 Review 经验**应该在 git 里**（作为 markdown），而不是放在 Wiki——Wiki 对 agent 来说是一个额外的访问边界。

外部规范放不进 git，但仍需要让 agent 能用，解决方案是**外部向量化知识库**（RAG），而不是直接引用原始 PDF。

## 维度二：是否与 src 混放

即使放在同一 repo，知识文件也**不应该放进 src/ 目录**，而应在独立目录中管理：

| 存储位置 | 适合的内容 | 理由 |
|----------|-----------|------|
| `src/` 内，与代码同目录 | 接口定义、配置、Build 规则 | 与代码强绑定，必须随代码变更同步 |
| repo 根目录下独立目录（`docs/`、`knowledge/`） | ADR、架构文档、历史故障、模块地图、Review 经验 | 随项目演进但与具体代码解耦，agent 可按需加载 |
| repo 外的向量知识库 | STM32 手册、AUTOSAR 规范等外部文档 | 体积和归属不适合入 repo，通过 RAG 访问 |

知识放在 `src/` 内会污染代码搜索结果，并在代码重构时引发不必要的移动；独立目录既保留版本控制，又保持与代码的清晰边界。

---

# 九、推荐的最终架构

```
skills/
├── understand-system
├── implement-change
├── debug-issue
├── root-cause-analysis
├── review-change
└── investigate-performance

knowledge/
├── architecture/
├── coding-standard/
├── adr/
├── embedded/
│   ├── stm32/
│   ├── freertos/
│   ├── linux-driver/
│   └── bsp/
├── automotive/
│   ├── autosar/
│   ├── can/
│   ├── diagnostics/
│   └── ota/
└── project/
    ├── module-map/
    ├── examples/
    ├── bug-history/
    └── owner-map/

router/
└── knowledge-router
```

---

# 结论

| 维度 | 传统认知 | AI Native 认知 |
|------|----------|----------------|
| 核心流程 | SDD → Skill → Code | Reasoning Skill + Knowledge Router + Engineering Knowledge |
| 质量瓶颈 | Spec 写得够不够详细 | Engineering Knowledge 积累得够不够丰富 |
| 长期资产 | 流程文档 | Knowledge System |

三个组件各司其职：

- **Skill** — 决定 Agent 如何思考（推理模式）
- **Knowledge** — 决定 Agent 思考什么（领域内容）
- **Router** — 决定 Agent 在当前任务中应该看到什么（上下文装载）

随着项目规模增长，Engineering Knowledge System 是复杂领域代码生成质量能否持续提升的决定性因素。

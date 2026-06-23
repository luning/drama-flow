# Harness 工程之工程知识体系 - 提升复杂项目的生成质量

## 适用场景

本文针对的场景是：**复杂领域项目的 Agent 代码生成质量不稳定**。典型领域包括嵌入式、汽车软件、AI 平台、交易系统，这类项目有两个共同特征：

- 大量关键工程知识分散在代码库之外（芯片手册、规范文档、历史故障、隐性约定）
- 通用 SDD 流程无法将这些知识有效传递给 Agent

提升生成质量有多种做法，本文推荐两者结合：

- **配合 SDD 工作流**：利用现成工具（如 OpenSpec、Superpowers/GSD）或自定义工作流，确保 Agent 按步骤推进、遇到不确定主动确认
- **构建工程知识体系**：将分散的领域知识系统化地组织为 Agent 可路由、可加载的结构

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

## 落地 — 知识管理与推荐架构

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

工程知识体系与 SDD 工作流配合使用时效果最佳：SDD 是推理的骨架，Knowledge 是推理的血肉。

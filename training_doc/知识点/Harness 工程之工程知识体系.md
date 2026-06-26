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

### Knowledge：五类知识模型

知识库不是文档堆，而是按**使用方式**分类的结构化上下文。五类知识的划分依据是"Agent 在什么情况下需要它"，这决定了加载时机、组织方式和维护策略。

#### 结构知识

描述系统现状——它是什么、由什么组成、各部分如何连接。Agent 需要分析影响范围或定位具体模块时加载。

结构知识有两个粒度，存储位置和加载时机都不同：

- **系统级**（架构图）：存放在 `knowledge/structure/`，任务可能跨模块时加载，帮助 Agent 判断影响范围
- **模块级**（模块地图）：**colocate 在 `src/[module]/MODULE.md`**，聚焦到具体模块后加载，帮助 Agent 找到正确的入口和 Owner

模块级与代码同源的理由：模块的入口、Owner、依赖关系随代码一起变化，文件放得越远越容易在重构时漏掉同步。与任务经验（EXPERIENCE.md）采用同一约定：进入某个模块目录，该模块的所有元数据都在这里。

```markdown
# knowledge/structure/architecture.md（系统级）

语音唤醒 → ASR（语音识别）→ NLU（意图理解）→ TTS（语音合成）

## 模块边界
- ASR 只输出文本，不感知业务意图
- NLU 通过事件总线发布 Intent，不直接调用业务模块
- TTS 无状态，接收文本返回音频流
```

```markdown
# src/drivers/can/MODULE.md（模块级，colocate）

- 入口：can_manager.c → can_manager_init()
- 过滤配置：can_filter.c
- 报文分发：通过事件总线，订阅者在 src/app/can_dispatcher.c
- Owner：张三（驱动层）、李四（应用层分发）
```

#### 编码规范

约束代码应该**写成什么样**——命名、日志、错误处理、内存管理等硬性规则。这是唯一需要在每个任务中全量加载的类别，因为任何代码生成任务都必须遵守它。

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

#### 设计决策

记录设计层面的**选择与理由**——为什么这么设计、否决了什么方案、项目形成了哪些设计惯例。

Agent 在做出新设计选择之前加载：无论是理解已有设计、引入新技术、还是重构某个模块，都需要先看已有的决策，避免走回头路或与项目设计惯例冲突。

```markdown
# 决策：采用事件总线替代跨模块直接调用

## 选择
模块间通信统一通过事件总线，禁止跨模块直接函数调用。

## 理由
- 直接调用导致强耦合，历史上 NLU 改接口引发 5 个模块同步修改
- 事件总线解耦后，新增业务模块无需修改已有代码

## 否决方案
- 共享内存：并发控制复杂，历史上出现过竞态 bug
- gRPC：引入网络开销，同进程内不必要

## 设计惯例
新增模块间通信时默认走事件总线，有充分理由才考虑例外，并记录在此。
```

#### 任务经验

记录**反复执行同类任务时积累的教训**——某类任务容易漏掉哪些步骤、有哪些项目特有的隐性约定无法从代码结构推断。

与其他四类不同，任务经验**不是事先写的**，而是 Agent 在同类任务上反复犯同一类错误后才提炼——过早写只会制造维护负担。按任务类型索引，开始执行特定类型任务时加载。

```markdown
# 新增 API 路由 — 执行检查清单
# （背景：Agent 多次遗漏步骤 4，接口不报错但返回 404）

每次新增 API 路由时，必须修改以下位置：
1. backend/app/api/        — 添加路由处理函数
2. backend/app/services/   — 添加对应 Service 方法
3. backend/app/schemas/    — 定义请求/响应模型
4. backend/app/api/__init__.py — 注册新路由 ← 常见遗漏点
5. tests/                  — 添加行为级测试
```

#### 领域知识

来自**软件系统之外**的技术知识——芯片手册、协议规范、框架文档等。它与具体项目无关，是外部世界的客观规则。

按技术领域按需加载；也可以在任务经验中被引用（例如任务清单里注明"配置 CAN 过滤器时参见领域知识：STM32 过滤器初始化顺序"）。领域知识是五类中唯一可以**跨项目高度复用**的，适合建独立仓库通过 submodule 共享。

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

#### 五类知识的加载策略

| 类别 | 加载时机 | 加载方式 | 跨项目复用 |
|------|---------|---------|-----------|
| 结构知识 | 分析影响范围 / 定位具体模块时 | 按粒度按需加载 | 否，项目专属 |
| 编码规范 | **每个任务** | 全量常驻 | 部分（公司级可共享） |
| 设计决策 | 做出新设计选择之前 | 按决策领域按需加载 | 否，项目专属 |
| 任务经验 | 开始执行特定类型任务时 | 按任务类型按需加载 | 否，依赖项目结构 |
| 领域知识 | 涉及该技术领域时 | 按技术领域按需加载 | **是**，建共享仓库 |

三个关键推论：

- **编码规范是唯一需要全量常驻的类别**：它约束所有代码生成任务，Router 的 load 字段应始终包含它。
- **设计决策和任务经验的触发时机不同**：任务经验在任务开始时按任务类型主动加载；设计决策则是在任务执行过程中遇到需要做出设计选择时才引入——同一个编码任务里两者可能都会用到。两者都不需要常驻，按需加载避免无关知识干扰推理。
- **领域知识可以被任务经验引用**：任务清单里可以写"参见领域知识 X"，不改变分类，但需要在索引里标注引用关系，确保 Agent 能一并加载。

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

使用 OpenSpec 时，自定义 Schema 天然承担 Router 职责：Schema 名称是选择器，`config.yaml` 的 `context` 字段是加载器，各 artifact 的 `instruction` 是精化器。`openspec new change <name> --schema embedded-can` 即可同时激活三项职责。

不使用 OpenSpec 时，Router 以 YAML 或 Markdown 文件存于 `router/` 目录，Agent 执行前主动读取，按三个职责按需设计字段即可。

---

## 落地 — 知识管理与推荐架构

### 知识存储原则

对 Agent 来说，git repo 内的文件是最易访问的知识形式，优先于任何外部系统。知识的存储位置从两个维度判断：

| 维度 | 场景 | 推荐做法 |
|------|------|---------|
| **放入哪个 repo** | 体量可控，单项目使用 | 直接放入项目 repo（`knowledge/` 目录） |
| | 体量可控，多项目共享 | 建独立 knowledge repo，各项目通过 submodule 引用 |
| | 体量过大，git 不好用 | 使用 RAG（向量化知识库） |
| **是否与 src 混放** | 设计决策、架构文档、外部规范 | repo 根目录下独立 `knowledge/` 目录 |
| | 接口定义、配置、Build 规则 | `src/` 内，与代码同目录 |

- 多项目共享不是 RAG 的理由——独立 git repo 同样可以共享，且版本可以 pin
- 历史故障、Review 经验等应在 git 里管理，而不是放 Wiki——Wiki 对 Agent 是额外的访问边界

### 推荐架构

目录结构对应五类知识（embedded/automotive 为领域示例，按实际领域替换）：

```
skills/
├── understand-system
├── implement-change
├── debug-issue
├── root-cause-analysis
├── review-change
└── investigate-performance

knowledge/                 # 集中存放：系统级、跨项目、稳定的知识
├── structure/             # 结构知识（系统级）：架构图、模块边界、调用链
├── coding-standard/       # 编码规范：每个任务常驻加载
├── decisions/             # 设计决策：为什么这么设计、否决了什么
└── embedded/              # 领域知识：外部技术规范（可跨项目共享）
    ├── stm32/
    ├── freertos/
    └── autosar/

src/                       # 模块级知识 colocate 在源码旁，随代码同步演化
└── drivers/can/
    ├── can_manager.c
    ├── MODULE.md          # 结构知识（模块级）：入口、Owner、依赖关系
    └── EXPERIENCE.md      # 任务经验：该模块的历史陷阱与执行清单

.claude/
├── structure/
│   └── INDEX.md           # 所有模块 MODULE.md 的中央索引（供纵览用）
└── experience/
    └── INDEX.md           # 所有模块 EXPERIENCE.md 的中央索引（供 Router 按任务类型加载）

router/
└── knowledge-router       # 不使用 OpenSpec 时的独立 Router 文件
```

---

## 结论

| 维度 | 传统认知 | AI Native 认知 |
|------|----------|----------------|
| 核心流程 | SDD → Skill → Code | SDD 工作流 + Engineering Knowledge System |
| 质量瓶颈 | Spec 写得够不够详细 | Engineering Knowledge 积累得够不够有效 |
| 长期资产 | 流程文档 | Knowledge System |

SDD 是推理的骨架，Knowledge 是推理的血肉。

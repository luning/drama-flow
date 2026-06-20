
## 适用场景

本文针对的场景是：**复杂领域项目的 Agent 代码生成质量不稳定**。典型领域包括嵌入式、汽车软件、AI 平台、交易系统等——这类项目的共同特征是，大量关键工程知识分散在代码库之外（芯片手册、规范文档、历史故障、隐性约定），通用 SDD 流程无法将这些知识有效传递给 Agent。

提升生成质量有多种做法，本文推荐两者结合：

- **配合 SDD 工作流**：利用现成工具（如 OpenSpec、Superpowers/GSD）或自定义工作流，确保 Agent 按步骤推进、遇到不确定主动确认
- **构建工程知识体系**：将分散的领域知识系统化地组织为 Agent 可路由、可加载的结构

两者相辅相成——工程知识体系单独存在时效果有限，与 SDD 配合才能充分发挥价值：SDD 定义 Agent 如何推理，知识体系决定 Agent 推理时能看到什么。

**不一定需要从头自定义 SDD**。OpenSpec 已经提供了 propose → review → apply 的确认机制，Superpowers/GSD 的 Skill 集本身就是按推理模式拆分的。对大多数团队来说，直接使用这些工具，重点投入在 Knowledge 层和 Router 文件的建设上，是更务实的起点——领域定制写在 Router 文件里，Skill 本身不需要改动。

---

# 诊断 — 复杂项目的生成质量瓶颈

## 从 Agent 视角重新理解 SDD

传统描述中，SDD 是一个线性流程：Spec → Design → Code → Test。

但对 Agent 来说，执行时真正看到的只有两样东西：**Context** 和 **Instructions**。

SDD 的各个组成部分，在 Agent 视角下本质上只有两类：

| SDD 组成 | 说明 | Agent 视角 |
|----------|------|-----------|
| Spec | 需求规格与验收标准 | Context |
| Template | 引导生成的结构化模板 | Context |
| Knowledge | 注入上下文的工程知识 | Context |
| Skill | 定义 Agent 如何推理的工作流 | Instructions |
| Workflow | 多步骤任务的编排流程 | Instructions |

因此，Agent 的本质是：

```
Agent = Context + Reasoning
```

SDD 的价值不在于流程步骤，而在于它能往 Context 里注入多少有效的工程知识。

## 通用 SDD 在复杂领域的局限

**Web Demo 场景**：实现用户登录。Agent 只需要 Spec + 通用代码知识即可完成。

**嵌入式场景**：实现 CAN 过滤功能。Agent 真正需要的是：

- 芯片手册与寄存器定义
- 驱动框架与板级设计
- AUTOSAR 规范与 DBC 文件
- 项目编码规范
- 历史实现参考

这些关键知识**根本不在代码库里**。因此对复杂系统来说，流程不是 `Spec → Code`，而是：

```
Spec + Engineering Knowledge + Code → Implementation
```

缺少 Engineering Knowledge 这一层，Spec 再详细也无法生成高质量代码。

## Knowledge 才是核心资产

Skill 本质是几十行 Prompt，可以快速编写和迭代。Knowledge 是团队几年到十几年的沉淀，无法快速复制。

| 维度 | Skill | Knowledge |
|------|-------|-----------|
| 构建成本 | 低（几小时） | 高（持续积累） |
| 价值占比 | ~5–10% | ~90–95% |
| 演进速度 | 快 | 慢但稳定 |
| 可迁移性 | 高（通用推理模式） | 低（领域专属） |

随着项目规模增长，真正持续积累价值的是 Knowledge，而不是 Skill 库。

---

# 设计 — Skill、Knowledge 与 Router

## Skill：按推理模式拆分

很多团队会为每个业务场景设计专用 Skill：

```
implement-can-driver
implement-spi-driver
implement-uart-driver
implement-i2c-driver
...（几十个）
```

其中 `implement-can-driver` 的内容大概是：

```markdown
# implement-can-driver

## 步骤
1. 查看 STM32 CAN 控制器寄存器手册
2. 配置 CAN_BTR 设置波特率
3. 配置过滤器 CAN_FMR / CAN_FM1R
4. 实现发送函数 HAL_CAN_AddTxMessage()
5. 实现接收中断 HAL_CAN_RxFifo0MsgPendingCallback()
```

`implement-spi-driver`、`implement-uart-driver` 的结构几乎一样，只是寄存器名字和 HAL 函数不同，于是不断复制出几十个 Skill。

这是一个常见误区。这些 Skill 的**推理模式高度相似**：理解需求 → 找相关模块 → 找类似实现 → 实现 → 验证。真正在变化的是知识内容，不是推理模式。

**正确做法：Skill 按 Reasoning Pattern 拆分，而不是按业务名词拆分。**

> 如果已经在使用 Superpowers 或 GSD，它们的 Skill 集已经是这个结构，不需要重新设计。可以直接复用，必要时在现有 Skill 上追加领域专属的阻断条件（如"遇到 AUTOSAR 接口定义不明确时必须停下来确认"）。

5~15 个 Skill 即可覆盖绝大多数开发活动：

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

**`implement-change` Skill 示例（极简）：**

```markdown
# implement-change

## 步骤
1. 阅读需求，确认影响范围
2. 在 knowledge/ 中查找相关模块文档和历史实现
3. 检查 coding-standard，确认约束
4. 实现变更，逐条对照 AC 自检
5. 运行测试，确认无回归

## 约束
- 不得跨模块直接调用内部实现
- 所有异常必须按 coding-standard 中的规范处理
```

Skill 本身不包含任何领域知识——"CAN 怎么过滤"、"哪个寄存器控制过滤器"这些由 Knowledge 提供。

## Knowledge：五层分层模型

### Layer 1：Architecture Knowledge

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

### Layer 2：Coding Standards

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

### Layer 3：ADR（Architecture Decision Record）

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

### Layer 4：Domain Knowledge

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

### Layer 5：Project Knowledge

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

## Router：连接任务与知识

Knowledge Router 的职责不只是"加载知识"，还包括**为当前任务细化执行步骤**。一个 router 文件同时定义了 steps 和 load，Skill 读到后按 router 提供的步骤执行，而不是按自己的通用步骤——两者不冲突，router 的 steps 是对 Skill 通用步骤的具体化。

```yaml
task: implement-change
repo: embedded
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

Skill 本身无需修改——它提供通用推理框架，Router 文件提供领域专属的步骤细化和知识装载。**需要为新领域或新模块定制行为时，新增或修改 router 文件，而不是改 Skill**。

**Router 的成熟度演进：**

| 阶段 | 做法 |
|------|------|
| **初级**：知识体系刚建立 | Skill 内嵌 Routing 逻辑（识别领域 → 查找知识 → 实现） |
| **成熟**：知识库规模较大 | Router 独立：Task → Router → Context + Steps → Skill |

成熟阶段，Skill 保持稳定，所有领域定制都在 Router 层完成。

## 各模块分工与步骤约束的应对方案

三个层次各司其职，不同的定制需求对应不同的层次：

| 层次 | 工具 | 职责 | 定制方式 |
|------|------|------|---------|
| **工作流** | OpenSpec/Superpowers | 多任务编排、用户确认节点、交互模式 | Propose 时读入 Router，生成的开发步骤自然满足领域要求；极少数情况才需写新 Skill |
| **任务** | Knowledge Router | 单任务内步骤细化 + 知识装载 | 新增或修改 router 文件，Skill 不动 |
| **内容** | Knowledge 文件 | 领域知识本身 | 按五层模型组织，持续积累 |

**不同场景下步骤约束的具体应对：**

| 场景 | 应对方式 |
|------|---------|
| 单任务需要领域专属步骤顺序（如 CAN 寄存器配置顺序） | 写入 router 的 `steps` 字段 |
| 单任务需要加载特定领域知识 | 写入 router 的 `load` 字段 |
| 多阶段流程需要用户在关键节点确认 | OpenSpec/Superpowers propose 读入 router，proposal 文档包含 router 定义的步骤，用户 review 后再 apply |
| 跨所有任务的项目级约束（如安全关键模块必须留审计记录） | 写入 Knowledge 文件（如 `coding-standard.md`），作为 router load 的内容之一 |
| 真正需要不同交互模式的全新流程 | 新建 Skill 文件，以现有 Skill 为子步骤进行编排 |

Skill 文件本身几乎不需要修改——它是通用推理框架，领域定制通过 Router 和 Knowledge 注入。

## 执行纪律：防止幻觉与跳步

知识体系解决了"Agent 知道什么"，但复杂项目还需要解决"Agent 是否真的做完了每一步"。幻觉完成（声称做了但没做）和跳步（遇到不确定直接假设）是复杂项目最常见的执行问题。

对策是在 Skill 里为每个步骤定义**完成标准**和**阻断条件**，不允许 Agent 靠自我声明推进：

| 步骤 | 完成标准 | 阻断条件 |
|------|---------|---------|
| 确认需求范围 | 列出涉及的所有模块和文件 | 影响范围不明确时，停下来确认，不得假设 |
| 查阅相关知识 | 列出查阅了哪些文件及关键约束 | 知识库无相关内容或有矛盾，向用户说明 |
| 实现变更 | 展示关键代码，说明每条约束如何满足 | 遇到规范未覆盖的情况，不得自行决策 |
| 逐条验收 | 每条 AC 注明"已覆盖/未覆盖/不适用" | 有未覆盖 AC 时不得声明完成 |
| 运行测试 | 粘贴实际测试输出 | 不得仅声明"测试通过" |

更系统的做法是引入**中间确认文档**——OpenSpec/Superpowers 的 propose → review → apply 模式就是这套机制，Agent 在实现前先产出一份结构化文档，用户确认后再开始写代码。Propose 时读入 router，生成的文档步骤自然包含领域专属的约束：

```markdown
# 变更确认文档：实现 CAN 过滤功能

## 需求理解
支持按报文 ID 过滤 CAN 帧，仅将指定 ID 的报文传递给应用层。

## 影响范围
- 修改：src/drivers/can/can_filter.c
- 新增：can_filter_init() / can_filter_set_mask() 两个接口
- 不涉及：CAN 发送路径、应用层分发逻辑

## 依据的知识
- architecture/can-subsystem.md、embedded/stm32/can-filter.md、coding-standard.md

## 待确认项
1. 过滤模式：标识符屏蔽模式（一组 ID）还是标识符列表模式（精确匹配）？
2. 过滤器组编号：当前已占用 0~3 组，从第 4 组开始配置，是否正确？
3. 初始化时机：在 CAN 总线 init 之前还是之后配置过滤器？

## 实现计划
进入 FINIT 模式 → 配置寄存器 → 写入 ID 和掩码 → 退出 FINIT → 运行测试

---
**请确认以上内容后继续，或指出需要修正的地方。**
```

"待确认项"是关键——它强迫 Agent 在动手前把不确定的部分显式列出，而不是悄悄假设一个答案往下走。

---

# 落地 — 知识管理与推荐架构

## 知识存储原则

知识的存储位置需要从两个维度判断：**放入哪个 git repo**，以及**是否与 src 代码混放**。

### 维度一：用哪个 git repo

对 Agent 来说，git repo 内的文件是最易访问、最确定性的知识形式，优先于任何外部系统。外部标准/规范（STM32 手册、AUTOSAR 规范等）并非"不能入 git"，关键判断是**体量**和**共享范围**：

| 场景 | 推荐做法 |
|------|---------|
| 体量可控，单项目使用 | 直接放入**项目 repo**（`knowledge/` 目录） |
| 体量可控，多项目共享 | 建**独立 knowledge repo**，各项目通过 submodule 或路径引用 |
| 体量过大，git 不好用 | 使用 **RAG**（向量化知识库） |

"体量可控"的参考线大约是几十 MB 以内。多项目共享不是 RAG 的理由——独立 git repo 同样可以共享，且版本可以 pin。历史故障、Review 经验等也应在 git 里管理，而不是放 Wiki——Wiki 对 Agent 是额外的访问边界。

### 维度二：是否与 src 混放

知识文件**不应放进 `src/` 目录**，即使在同一 repo 里也要独立管理：

| 存储位置 | 适合的内容 | 理由 |
|----------|-----------|------|
| `src/` 内，与代码同目录 | 接口定义、配置、Build 规则 | 与代码强绑定，必须随代码变更同步 |
| repo 根目录下独立目录（`knowledge/`） | ADR、架构文档、历史故障、模块地图、外部规范 | 与代码解耦，Agent 可按需加载，不污染代码搜索 |
| 独立 knowledge repo | 多项目共享的领域知识、外部规范 | 集中维护，各项目按版本引用 |
| RAG | 体量过大的外部文档集合 | git 性能不可接受时的兜底方案 |

## 推荐架构

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
| 核心流程 | SDD → Skill → Code | 自定义 SDD + Engineering Knowledge System |
| 质量瓶颈 | Spec 写得够不够详细 | Engineering Knowledge 积累得够不够丰富 |
| 长期资产 | 流程文档 | Knowledge System |

三个组件各司其职：

- **Skill** — 决定 Agent 如何思考（推理模式）
- **Knowledge** — 决定 Agent 思考什么（领域内容）
- **Router** — 决定 Agent 在当前任务中应该看到什么（上下文装载）

工程知识体系与自定义 SDD 配合使用时效果最佳：SDD 是推理的骨架，Knowledge 是推理的血肉。随着项目规模增长，持续积累 Engineering Knowledge System 是复杂领域代码生成质量能否持续提升的决定性因素。

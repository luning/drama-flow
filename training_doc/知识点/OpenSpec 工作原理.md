# OpenSpec 工作原理 - Schema、CLI、Skills三层协作让 Agent 知道"该干什么"

## 目录

1. [OpenSpec 是什么](#openspec-是什么)
2. [Schema：变更的"蓝图"](#schema变更的蓝图)
3. [四个 Skill 速览](#四个-skill-速览)
4. [instructions 命令的内部原理](#instructions-命令的内部原理)
5. [三层架构与设计哲学](#三层架构与设计哲学)

---

## OpenSpec 是什么

在规格驱动开发（SDD）中，每个变更都会产生 proposal、specs、design、tasks 等工件。变更多了，工件之间的依赖、完成状态、同步逻辑就会失控。

OpenSpec 用 **schema 定义工件依赖图**，用 **CLI 跟踪工件状态并返回下一步指令**，用 **Skills 把 CLI 包装成对话式命令**。三层分工协作，让 Agent 知道"现在该干什么、接下来干什么"。

> 类比：SDD 工件是源代码，OpenSpec 是 Git——它不创造内容，但管理状态、依赖和生命周期。

一个 Change 的生命周期：`/opsx:propose`（创建工件）→ `/opsx:apply`（逐任务实现）→ `/opsx:archive`（归档），`/opsx:explore` 可在任意时刻介入思考。

每个 Change 存储在 `openspec/changes/<name>/` 下：

| 工件文件 | 作用 |
|---------|------|
| `.openspec.yaml` | 元数据：`schema: spec-driven` |
| `proposal.md` | 为什么做、范围是什么 |
| `specs/` | 增量规格（delta specs） |
| `design.md` | 技术方案 |
| `tasks.md` | 任务清单 `- [ ]` / `- [x]` |

---

## Schema：变更的"蓝图"

所有 change 的 `.openspec.yaml` 都写 `schema: spec-driven`——这是目前 openspec CLI 内置的唯一 schema。它的完整定义：

```yaml
name: spec-driven
version: 1
description: Default OpenSpec workflow - proposal → specs → design → tasks

artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    instruction: "Create the proposal document..."
    requires: []                       # 无依赖，总是第一个

  - id: specs
    generates: "specs/**/*.md"
    template: spec.md
    requires: [proposal]               # 必须有 proposal

  - id: design
    generates: design.md
    template: design.md
    requires: [proposal]               # 必须有 proposal

  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, design]          # 依赖 specs + design

apply:
  requires: [tasks]                    # tasks 写完才能开始实现
  tracks: tasks.md                     # 用 tasks.md 跟踪进度
```

### 工件依赖是怎么判断的

```
schema.yaml 定义:    requires 字段声明"A 依赖 B"
                         │
                         ▼
CLI 运行时判断:       detectCompleted() 扫描 openspec/changes/<name>/ 目录
                     检查 artifact.generates 对应的文件是否存在
                         │
                         ▼
                     文件存在 = 工件 done = 依赖满足
                     文件不存在 = 工件未完成 = 下游 blocked
```

例如 `tasks.requires: [specs, design]`，CLI 检查 `specs/**/*.md` 和 `design.md` 在磁盘上是否存在。都在 → tasks 可用；缺一个 → tasks 阻塞，提示缺少哪个。

### Schema 的关键概念

| 概念 | 含义 |
|------|------|
| `artifacts` | 变更过程中要生成的工件列表 |
| `generates` | 工件对应的文件名（支持 glob：`specs/**/*.md`） |
| `requires` | 依赖关系——必须先完成哪些工件才能创建当前工件 |
| `template` | 工件模板（在 schema 的 `templates/` 目录下） |
| `instruction` | 给 Agent 的创建指引 |
| `apply.requires` | 哪些工件完成才能开始写代码 |
| `apply.tracks` | 进度跟踪文件，解析其中的 checkbox |

### 自定义 Schema

你可以定义自己的 schema，查找优先级：**项目级**（`openspec/schemas/`）> **用户级**（`~/.local/share/openspec/schemas/`）> **内置**。例如一个"只做调研"的 schema：

```yaml
name: spike
version: 1
artifacts:
  - id: research
    generates: research.md
    template: research.md
    requires: []
apply:
  requires: [research]
  tracks: null         # 无任务跟踪，写完 research 就结束
```

换 schema 时 Skill 层不用改——因为 Skill 通过 `openspec instructions` 动态获取 contextFiles，不假设具体文件名。

---

## 四个 Skill 速览

每个 Skill = 对话指令 + openspec CLI 调用的组合。

### 1. Propose — 创建变更

**触发**：`/opsx:propose [change名或描述]`

**职责**：根据需求描述，按 schema 依赖顺序逐个创建 proposal.md → specs → design.md → tasks.md。

**关键 CLI**：

| 命令 | 作用 |
|------|------|
| `openspec new change "<name>"` | 创建变更目录和 .openspec.yaml |
| `openspec status --change "<name>" --json` | 获取工件依赖图和完成状态 |
| `openspec instructions <artifact> --change "<name>" --json` | 获取工件的 template + instruction + dependencies |

**流程**：创建目录 → 获取依赖图 → 按拓扑顺序逐个调用 `openspec instructions` 获取模板和指引 → Agent 填充内容并写入文件 → 重新 status 确认进度 → 直到 `apply.requires` 全部 done。

---

### 2. Explore — 探索模式

**触发**：`/opsx:explore [可选：主题/change名]`

**职责**：只思考不实现的安全空间。可以读代码、画图、对比方案，但**绝不能写应用代码**。

**关键 CLI**：

| 命令 | 作用 |
|------|------|
| `openspec list --json` | 查看活跃变更 |

**特点**：无固定步骤，无强制输出。Agent 的角色是思考伙伴。探索后可能流入 Propose、更新已有工件、或只是澄清思路。

---

### 3. Apply — 执行变更

**触发**：`/opsx:apply [可选：change名]`

**职责**：读取工件 → 按 tasks.md 逐条实现代码 → 完成后勾掉 checkbox。

**关键 CLI**：

| 命令 | 作用 |
|------|------|
| `openspec list --json` | 选择 change |
| `openspec status --change "<name>" --json` | 检查工件状态 |
| `openspec instructions apply --change "<name>" --json` | 获取 contextFiles、任务列表、state |

**流程**：选定 change → `openspec instructions apply` → CLI 返回 state：
- `blocked` → 缺少工件，提示补充
- `all_done` → 已完成，建议归档
- `ready` → 读 contextFiles，逐任务实现；每完成一个就 `- [ ]` → `- [x]`；遇到不清楚的任务暂停询问

---

### 4. Archive — 归档变更

**触发**：`/opsx:archive [可选：change名]`

**职责**：将 change 目录移到 `archive/YYYY-MM-DD-<name>/`，归档前做三检查。

**关键 CLI**：

| 命令 | 作用 |
|------|------|
| `openspec list --json` | 选择要归档的 change |
| `openspec status --change "<name>" --json` | 检查工件是否全部 done |
| `mkdir -p openspec/changes/archive` | 创建归档目录 |
| `mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>` | 移动完成归档 |

**三检查**：
1. 工件完整性（artifacts 是否都 done？未完成则警告）
2. 任务完成度（tasks.md 有无剩余 `- [ ]`？未勾完则警告）
3. Delta spec 同步（是否同步到主 spec？未同步则提醒）

不拦死，但必告知。这是一道"安全门"。

---

## instructions 命令的内部原理

`openspec instructions` 不是简单读目录——它内部有一套完整的处理链。

### 调用 artifact 指令时（Propose 用）

```
openspec instructions proposal --change "xxx" --json
      │
      ▼
loadChangeContext()
  ├─ 读 .openspec.yaml → schema: "spec-driven"
  ├─ resolveSchema() → 三层查找 schema.yaml → Zod 校验字段
  │    → validateNoDuplicateIds()
  │    → validateRequiresReferences()  (每个 requires 必须指向存在的 artifact)
  │    → validateNoCycles()            (DFS 检测循环依赖)
  ├─ ArtifactGraph.fromSchema() → 构建 DAG，Kahn 拓扑排序
  └─ detectCompleted() → 扫描 change 目录，文件存在 = 工件完成
      │
      ▼
generateInstructions()
  ├─ loadTemplate() → 读取 templates/ 下的模板文件
  ├─ getDependencyInfo() → 返回依赖工件的 {id, done, path}
  ├─ readProjectConfig() → 读取 openspec/config.yaml 的 context 和 rules
  └─ 返回 JSON: { template, instruction, context, rules, dependencies, unlocks }
      │
      ▼
Agent 收到后：读依赖工件 → 按 template 结构填充 → 写入 outputPath
```

**template / context / rules 三者区别**：

| 字段 | 来源 | 是否写入文件 |
|------|------|-------------|
| `template` | schema 的 `templates/` 目录 | ✅ 是，结构骨架 |
| `context` | `openspec/config.yaml` | ❌ 否，只给 Agent 看的背景 |
| `rules` | `openspec/config.yaml` | ❌ 否，只给 Agent 看的约束 |

### 调用 apply 指令时（Apply 用）

```
openspec instructions apply --change "xxx" --json
      │
      ▼
generateApplyInstructions()
  ├─ loadChangeContext() → 同上
  ├─ 读 apply.requires → 检查必需工件是否存在（否则 blocked）
  ├─ 读 apply.tracks   → 正则 /^[-*]\s*\[([ xX])\]\s*(.+)\s*$/
  │                        解析 tasks.md 中的 checkbox
  ├─ 构建 contextFiles → 遍历所有 artifacts，文件存在的加入列表
  └─ 返回 JSON: { state, contextFiles, tasks, progress }
```

**状态机分支**：

| 条件 | state | Agent 行为 |
|------|-------|-----------|
| 必需工件缺失 | `blocked` | 提示补充工件 |
| tracks 文件不存在 | `blocked` | 提示先生成 |
| tracks 无 checkbox | `blocked` | 提示补充任务 |
| 全部 `- [x]` | `all_done` | 祝贺，建议归档 |
| 有未完成 | `ready` | 读 contextFiles，逐任务实现 |

---

## 三层架构与设计哲学

```
┌──────────────────────────────────────────────┐
│  Skill 层 (propose / explore / apply / archive) │
│  职责：对话包装，选 change、展示进度、确认风险    │
├──────────────────────────────────────────────┤
│  openspec CLI 层 (list / new / status / instructions) |
│  职责：schema 感知 + 状态机 + 指令生成           │
│        不依赖任何特定 LLM                       │
├──────────────────────────────────────────────┤
│  文件系统层 (openspec/changes/*.md, .openspec.yaml) │
│  职责：持久化内容 + 元数据，纯 Git 管理           │
└──────────────────────────────────────────────┘
```

**关注点分离让换 schema 零成本**：Skill 从 CLI 动态获取 contextFiles，不假设一定有 proposal.md。Schema 变了，Skill 不用改。

| 原则 | 体现 |
|------|------|
| **Schema 驱动** | 工件依赖图由 schema 定义，CLI 执行状态机，Skill 做对话包装 |
| **动态适配** | Skill 不假设文件路径，由 CLI 实时告知 |
| **HITL 关键节点** | 选 change、跳过警告、delta spec 同步——全问用户 |
| **渐进式完整性** | Archive 三检查，不拦死但必告知 |
| **工具优先** | 核心逻辑在 CLI 中，不绑定特定 LLM |
| **文件系统即数据库** | 状态在 Markdown 和 YAML 中，Git 就是时间机器 |

> **OpenSpec 是用 schema 定义"变更长什么样"，用 CLI 跟踪"变更走到了哪一步"，用 Skills 让 Agent 在对话中自然地驱动整个流程。**

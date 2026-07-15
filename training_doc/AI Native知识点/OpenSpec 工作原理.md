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

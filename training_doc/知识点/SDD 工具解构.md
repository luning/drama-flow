# SDD 工具解构 - 状态机 × 工件驱动 × 三种实现路径的设计解剖

## 目录

1. [从需求到工具：先问三个问题](#从需求到工具先问三个问题)
2. [SDD 工具的本质：三件事](#sdd-工具的本质三件事)
3. [核心设计模式](#核心设计模式)
   - [状态机：工具的骨架](#状态机工具的骨架)
   - [工件驱动：文件就是数据库](#工件驱动文件就是数据库)
   - [上下文工程：给 Agent 喂什么](#上下文工程给-agent-喂什么)
   - [HITL 关键节点：哪里必须问人](#hitl-关键节点哪里必须问人)
4. [最小可用 SDD 工具的解剖](#最小可用-sdd-工具的解剖)
5. [三种实现路径](#三种实现路径)
   - [路径一：纯 Skill（零基础设施）](#路径一纯-skill零基础设施)
   - [路径二：Skill + 脚本（轻量状态）](#路径二skill--脚本轻量状态)
   - [路径三：Skill + CLI（完整状态机）](#路径三skill--cli完整状态机)
6. [动手实现：从零构建一个 Spike 工具](#动手实现从零构建一个-spike-工具)
   - [需求分析](#需求分析)
   - [Step 1：定义工件与状态机](#step-1定义工件与状态机)
   - [Step 2：实现 CLI 状态查询](#step-2实现-cli-状态查询)
   - [Step 3：编写 Skill](#step-3编写-skill)
   - [Step 4：验证闭环](#step-4验证闭环)
7. [常见陷阱与对策](#常见陷阱与对策)
8. [延伸：让工具更健壮的进阶技巧](#延伸让工具更健壮的进阶技巧)

---

## 从需求到工具：先问三个问题

在动手写任何代码之前，先想清楚这三个问题。它们决定你需要的是一个 Prompt、一个 Skill，还是一个完整工具。

**问题一：你在省什么？**

SDD 工具本质上是在省"重复提醒"——每次任务前你都要告诉 Agent "先读 spec、改完自检"，工具把这个动作变成自动发生的事。

如果你只是省一个口头提醒，一段 CLAUDE.md 约束就够了。如果你要省多个步骤、管理跨对话状态、或者隔离多个并行变更，才需要写工具。

**问题二：你的痛点是什么阶段的问题？**

| 阶段 | 典型痛点 | 解法 |
|------|---------|------|
| **探索** | 没有固定输入格式，Agent 乱猜意图 | Explore Skill：非结构化思考空间 |
| **规划** | 任务粒度不对，Agent 一次改太多 | Propose Skill：强制拆解工件 |
| **执行** | 长任务中 Agent 忘记早期决策 | Execute Skill：每次从文件重建上下文 |
| **验证** | 改完不知道 AC 是否全覆盖 | Verify Skill：逐条比对 AC |
| **归档** | 历史变更无迹可查 | Archive Skill：移动 + 检查完整性 |

**问题三：你愿意维护多少基础设施？**

一个 300 行的 Skill 文件几乎零维护成本；一个 CLI 工具需要持续迭代。选择最小够用的方案，不要为假想的未来需求过度设计。

---

## SDD 工具的本质：三件事

所有 SDD 工具，无论多复杂，都在做三件事：

```
① 告诉 Agent 当前状态          →   "你在哪一步"
② 告诉 Agent 下一步该做什么    →   "你接下来做什么"
③ 记录 Agent 做了什么          →   "你做到哪了"
```

这三件事对应三个核心机制：

| 机制 | 作用 | 实现载体 |
|------|------|---------|
| **状态感知** | 读取当前工件，判断处于哪个阶段 | 文件存在检查 / checkbox 解析 |
| **指令生成** | 根据状态返回下一步操作的 Prompt | Skill 模板 / CLI instructions 命令 |
| **状态持久化** | 将 Agent 的产出写入文件系统 | Markdown 工件 / YAML 元数据 |

OpenSpec 把这三件事清晰地分到三层：**文件系统**（持久化）、**CLI**（状态感知 + 指令生成）、**Skill**（对话包装）。GSD 也是同样的分层，只是把更多编排逻辑放在了 CLI 侧。

理解这个本质，就能理解为什么 OpenSpec 的 Schema 那么简单——它只需要声明"哪些文件存在 = 哪个工件完成"，不需要数据库，不需要服务器。

---

## 核心设计模式

### 状态机：工具的骨架

每个 SDD 工具的核心都是一个状态机。状态机决定"在什么条件下允许做什么"。

以一个最小的 Spike 工具为例：

```
           ┌─────────────┐
           │   CREATED   │  ← change 目录存在，但 research.md 不存在
           └──────┬──────┘
                  │ research.md 写入
                  ▼
           ┌─────────────┐
           │  RESEARCHED │  ← research.md 存在
           └──────┬──────┘
                  │ conclusion.md 写入
                  ▼
           ┌─────────────┐
           │  CONCLUDED  │  ← 可以归档
           └─────────────┘
```

状态的判断永远应该基于**文件是否存在**，而不是数据库字段或内存变量。原因：

1. **Git 就是时间机器**：文件历史即变更历史，不需要额外的版本管理
2. **崩溃安全**：任何时候 Agent 中断，重启后扫描文件就能恢复状态
3. **可调试**：状态一目了然，`ls openspec/changes/my-feature/` 就知道做到哪了

**设计状态机的三个原则：**

- **前驱约束要明确**：`conclusion.md` 需要 `research.md` 先存在，否则 Agent 没有输入
- **状态数量要最小**：不要为"进行中"创建额外状态，进行中就是"前驱满足 + 后继不存在"
- **终态要触发归档**：所有工件完成后，工具应提示用户考虑归档，防止目录无限增长

---

### 工件驱动：文件就是数据库

SDD 工具中，每个工件都是一个 Markdown 文件。Markdown 的优势不只是"可读"，而是它的结构天然适合被 Agent 增量修改：

```markdown
# Research: 用户认证方案调研

## 背景
...

## 调研结论
- [ ] JWT 方案：无状态，适合水平扩展
- [x] Session 方案：有状态，实现简单

## 风险
...
```

`- [ ]` / `- [x]` checkbox 是状态机的核心原语——用正则 `/^[-*]\s*\[([ xX])\]/` 可以解析任意 Markdown 中的任务完成度。

**工件设计的四个要素：**

| 要素 | 说明 | 示例 |
|------|------|------|
| **generates** | 工件对应哪个文件（支持 glob） | `research.md`、`specs/**/*.md` |
| **requires** | 依赖哪些工件先完成 | `[proposal]`、`[research, design]` |
| **template** | Agent 填充内容时的骨架 | 二级标题结构、必填字段占位符 |
| **instruction** | 告诉 Agent"如何填充这个工件" | "基于 proposal 列出技术方案..." |

工件模板不应该太空（Agent 不知道写什么），也不应该太满（没有填充空间）。好的模板是"骨架 + 示例"：

```markdown
# Design: {{change name}}

## 背景
<!-- 从 proposal.md 摘要，一段话 -->

## 方案选型
| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 方案 A | ... | ... | ☑ |

## 实现路径
1. 步骤一
2. 步骤二
```

---

### 上下文工程：给 Agent 喂什么

Agent 在每个阶段只需要"当前阶段必需"的上下文，给太多反而增加噪声、消耗 token。

**上下文分层原则：**

```
┌─────────────────────────────────────────────────────────┐
│  全局约束（每次都加载）                                    │
│  ← CLAUDE.md 架构约束、命名规范                           │
├─────────────────────────────────────────────────────────┤
│  阶段上下文（当前阶段加载）                                │
│  ← 当前 change 的 proposal.md、上游工件                   │
├─────────────────────────────────────────────────────────┤
│  任务上下文（当前任务加载）                                │
│  ← tasks.md 当前任务、相关代码文件                        │
└─────────────────────────────────────────────────────────┘
```

OpenSpec 的 `instructions` 命令通过 `contextFiles` 字段返回当前阶段需要读取的文件列表，而不是把文件内容直接塞进 Prompt。这种设计让 Agent 按需读取，而不是一次性加载整个变更目录。

**实现上下文列表的最简方式：**

```python
def get_context_files(change_dir: Path) -> list[str]:
    """返回当前 change 目录中所有已存在的工件文件"""
    patterns = ["proposal.md", "design.md", "specs/**/*.md"]
    files = []
    for pattern in patterns:
        files.extend(str(p) for p in change_dir.glob(pattern) if p.exists())
    return files
```

这个函数只返回"已经存在的文件"，天然跳过未完成的工件，Agent 不会读到空文件或半成品。

---

### HITL 关键节点：哪里必须问人

HITL（Human-in-the-Loop）不是越多越好——每次打断用户都是摩擦。好的 SDD 工具只在**决策不可逆、影响范围大**的节点停下来问人。

| 节点 | 为什么要问 | 典型做法 |
|------|-----------|---------|
| **选择 change** | 多个活跃变更时，Agent 无法猜测用户意图 | 列出所有 change，用户选择 |
| **删除 / 归档** | 不可逆操作 | 展示三检查结果，用户确认 |
| **跳过警告** | "工件未完成但强制继续"——Archive 的安全门 | 明确提示风险，用户确认跳过 |
| **delta spec 同步** | 增量 spec 是否要合并进主 SPEC.md | 列出变更，用户决定是否合并 |

**不应该问人的地方：**

- 工件创建（根据模板自动填充，不需要审批）
- 状态查询（`list`、`status` 命令应该直接输出）
- checkbox 更新（每完成一个任务就自动勾，不需要确认）

---

## 最小可用 SDD 工具的解剖

把上面的设计模式拼在一起，一个最小可用的 SDD 工具只需要四个部件：

```
your-sdd-tool/
├── skill.md                  ← 对话层：Skill 文件，定义触发词和对话流程
├── schema.yaml               ← 配置层：工件定义、依赖关系、模板引用
├── templates/
│   ├── research.md           ← 工件模板
│   └── conclusion.md
└── scripts/
    └── status.py             ← 可选：CLI 状态查询脚本（也可以用 shell）
```

**skill.md 骨架：**

```markdown
---
name: spike
description: 探索性调研工具——收集信息、形成结论
triggers: ["spike", "调研", "探索性调研"]
---

## 流程

1. **选择或创建 change**
   - 运行 `ls openspec/changes/` 列出活跃变更
   - 如果已有同名目录，继续；否则 `mkdir -p openspec/changes/<name>`

2. **检查状态**
   - 扫描目录，判断当前处于哪个阶段（CREATED / RESEARCHED / CONCLUDED）

3. **按阶段执行**
   - CREATED → 读 research.md 模板，填充调研内容，写入文件
   - RESEARCHED → 读 conclusion.md 模板 + research.md，写入结论
   - CONCLUDED → 提示可以归档

4. **每完成一个工件**，重新检查状态并告知用户进度
```

**schema.yaml 骨架：**

```yaml
name: spike
version: 1
artifacts:
  - id: research
    generates: research.md
    template: templates/research.md
    instruction: "基于用户输入，调研背景、现有方案、关键约束。"
    requires: []

  - id: conclusion
    generates: conclusion.md
    template: templates/conclusion.md
    instruction: "基于 research.md，给出明确结论和推荐行动。"
    requires: [research]

apply:
  requires: [conclusion]
  tracks: null
```

这就是一个完整的 Spike 工具雏形。约 100 行配置，无需额外代码。

---

## 三种实现路径

### 路径一：纯 Skill（零基础设施）

**适用场景**：单个重复动作，无跨对话状态需求

**实现方式**：一个 Markdown 文件，描述步骤、引用文件路径约定

```markdown
---
name: ac-check
description: 逐条验证 AC 覆盖
---

1. 读取 SPEC.md 中所有 `**AC-xxx**` 格式的验收标准
2. 对照最近修改的代码文件，逐条标注：✅ 已覆盖 / ❌ 未覆盖 / ⚠️ 部分覆盖
3. 对所有 ❌ 项，说明缺少什么测试或代码
```

**优点**：零维护，立即可用  
**缺点**：无状态持久化，对话重启后需重新执行

---

### 路径二：Skill + 脚本（轻量状态）

**适用场景**：需要解析文件状态，但工件结构固定

**实现方式**：Skill 调用一个 shell/python 脚本做状态判断

```bash
#!/bin/bash
# scripts/spike-status.sh
CHANGE_DIR="openspec/changes/$1"

if [ ! -d "$CHANGE_DIR" ]; then
  echo '{"state": "not_found"}'
  exit 0
fi

RESEARCH=$([ -f "$CHANGE_DIR/research.md" ] && echo "true" || echo "false")
CONCLUSION=$([ -f "$CHANGE_DIR/conclusion.md" ] && echo "true" || echo "false")

if [ "$CONCLUSION" = "true" ]; then
  echo '{"state": "concluded"}'
elif [ "$RESEARCH" = "true" ]; then
  echo '{"state": "researched", "next": "write conclusion.md"}'
else
  echo '{"state": "created", "next": "write research.md"}'
fi
```

Skill 中调用：

```markdown
2. **检查状态**
   运行 `bash scripts/spike-status.sh <change-name>`，根据返回的 `state` 决定下一步
```

**优点**：状态判断精确，可在 CI 中复用  
**缺点**：需要维护脚本

---

### 路径三：Skill + CLI（完整状态机）

**适用场景**：多种 schema、多个工具共享一套状态机、需要复杂依赖检查

**实现方式**：参考 OpenSpec 的三层架构——文件系统 + CLI + Skill

CLI 的核心命令只需要三个：

| 命令 | 作用 |
|------|------|
| `mytool list` | 列出所有活跃变更 |
| `mytool status --change <name>` | 返回工件状态 JSON |
| `mytool instructions <artifact> --change <name>` | 返回模板 + 依赖信息 JSON |

用 Python + Typer 构建 CLI 大约需要 200-300 行代码。JSON 输出格式让 Skill 可以用 `jq` 或直接解析结果。

**优点**：高度可扩展，schema 可插拔  
**缺点**：需要持续维护，有学习成本

---

## 动手实现：从零构建一个 Spike 工具

下面是一个完整的实战示例：用**路径二**（Skill + 脚本）实现一个 Spike 调研工具。

### 需求分析

**问题**：每次让 Agent 做技术调研，产出质量参差不齐——有时只是列条目，有时信息量不够支撑决策。

**期望**：调研有固定结构（背景、现有方案、推荐、风险），结论可追溯，调研结果可以作为后续 Design 的输入。

**工件**：
- `research.md`：调研过程（背景、方案对比、关键发现）
- `conclusion.md`：调研结论（推荐方案、风险、下一步）

---

### Step 1：定义工件与状态机

创建目录结构：

```
spike-tool/
├── templates/
│   ├── research.md
│   └── conclusion.md
├── scripts/
│   └── spike-status.sh
└── skills/
    └── spike.md
```

`templates/research.md`：

```markdown
# Research: {{change_name}}

## 调研背景
<!-- 说明为什么做这次调研，要解决什么问题 -->

## 现有方案对比

| 方案 | 适用场景 | 优点 | 缺点 | 成本估算 |
|------|---------|------|------|---------|
| 方案 A | ... | ... | ... | ... |
| 方案 B | ... | ... | ... | ... |

## 关键约束
<!-- 项目现有架构、团队能力、时间限制等约束 -->

## 关键发现
<!-- 调研过程中发现的非显而易见的信息 -->
```

`templates/conclusion.md`：

```markdown
# Conclusion: {{change_name}}

## 推荐方案
**推荐**：方案 X

**理由**（3 条以内）：
1. ...
2. ...
3. ...

## 主要风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| ... | 中 | 高 | ... |

## 下一步行动
- [ ] 行动 1
- [ ] 行动 2
```

---

### Step 2：实现 CLI 状态查询

`scripts/spike-status.sh`：

```bash
#!/bin/bash
# 用法: bash scripts/spike-status.sh <change-name>
# 返回: JSON 格式的状态信息

CHANGE_NAME="$1"
BASE_DIR="spike/changes"
CHANGE_DIR="$BASE_DIR/$CHANGE_NAME"

if [ -z "$CHANGE_NAME" ]; then
  # 列出所有活跃变更
  echo '{"changes": ['
  FIRST=true
  for dir in "$BASE_DIR"/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    research=$([ -f "$dir/research.md" ] && echo "true" || echo "false")
    conclusion=$([ -f "$dir/conclusion.md" ] && echo "true" || echo "false")
    [ "$FIRST" = "true" ] || echo ","
    echo "  {\"name\": \"$name\", \"research\": $research, \"conclusion\": $conclusion}"
    FIRST=false
  done
  echo ']}'
  exit 0
fi

if [ ! -d "$CHANGE_DIR" ]; then
  echo "{\"state\": \"not_found\", \"change\": \"$CHANGE_NAME\"}"
  exit 0
fi

RESEARCH=$([ -f "$CHANGE_DIR/research.md" ] && echo "true" || echo "false")
CONCLUSION=$([ -f "$CHANGE_DIR/conclusion.md" ] && echo "true" || echo "false")

if [ "$CONCLUSION" = "true" ]; then
  echo "{\"state\": \"concluded\", \"change\": \"$CHANGE_NAME\", \"contextFiles\": [\"$CHANGE_DIR/research.md\", \"$CHANGE_DIR/conclusion.md\"]}"
elif [ "$RESEARCH" = "true" ]; then
  echo "{\"state\": \"researched\", \"change\": \"$CHANGE_NAME\", \"next\": \"write conclusion.md\", \"contextFiles\": [\"$CHANGE_DIR/research.md\"]}"
else
  echo "{\"state\": \"created\", \"change\": \"$CHANGE_NAME\", \"next\": \"write research.md\", \"contextFiles\": []}"
fi
```

---

### Step 3：编写 Skill

`skills/spike.md`：

```markdown
---
name: spike
description: 系统性技术调研工具
triggers: ["spike", "技术调研", "调研一下"]
---

## 你是什么

你是一个技术调研助手。你帮助用户系统性地完成技术调研，产出结构化的 research.md 和 conclusion.md，而不是在对话中随意列条目。

**关键约束**：在 `research.md` 写完之前，不能写 `conclusion.md`。结论必须基于调研事实，不能凭空给出。

---

## 流程

### 1. 确认调研主题

如果用户没有提供 change 名称，询问：「这次调研的主题是什么？用 2-4 个英文单词描述（如 `auth-strategy`、`db-migration`）。」

### 2. 初始化目录

```bash
mkdir -p spike/changes/<change-name>
bash scripts/spike-status.sh <change-name>
```

### 3. 根据状态执行

**state = created（尚未开始）**：
- 读取 `templates/research.md`
- 结合用户输入，填充完整调研内容，写入 `spike/changes/<name>/research.md`
- 重新运行状态查询，确认文件已创建

**state = researched（调研完成，待结论）**：
- 读取 `spike/changes/<name>/research.md`（从 contextFiles 中获取）
- 读取 `templates/conclusion.md`
- 基于调研内容，写入 `spike/changes/<name>/conclusion.md`
- 重新运行状态查询

**state = concluded（调研结束）**：
- 展示 conclusion.md 摘要
- 提示：「调研已完成。如需归档，运行 `mv spike/changes/<name> spike/archive/$(date +%Y-%m-%d)-<name>`。」

### 4. 完成后汇报

每完成一个工件，告知用户：「✓ research.md 已写入，调研阶段完成。运行结论生成时告诉我。」
```

---

### Step 4：验证闭环

安装完成后，用下面的场景测试工具是否按预期工作：

**场景一：正常流程**
```
用户：spike auth-strategy
→ 创建目录 → 写 research.md → 状态变为 researched
用户：继续
→ 读 research.md → 写 conclusion.md → 状态变为 concluded
```

**场景二：中断后恢复**
```
# 模拟对话中断
用户：spike auth-strategy   ← 新对话
→ 脚本检测到 research.md 存在 → 直接进入 researched 状态 → 提示写结论
```

**场景三：依赖阻断**
```
# 直接尝试写结论（没有 research）
用户：spike my-topic，直接写结论
→ state = created → Skill 拒绝，提示先完成调研
```


---

## 常见陷阱与对策

**陷阱一：在 Skill 里硬编码文件路径**

```markdown
❌ 读取 openspec/changes/my-feature/research.md
✅ 读取 `bash scripts/spike-status.sh <name>` 返回的 contextFiles 列表
```

硬编码路径在 schema 变化时会全部失效；动态获取的路径跟着状态机走，不需要修改 Skill。

---

**陷阱二：把"进行中"建模成一个状态**

很多初学者会设计 `RESEARCHING` 状态，对应"正在写 research.md"。这是多余的——文件写到一半时，`research.md` 要么不存在，要么存在一个半成品。工具应该把"存在但不完整"的情况视为 `created`（前驱未完成），而不是创造一个新状态。

状态数量应该等于"已完成工件的组合数"，不要添加过程状态。

---

**陷阱三：Skill 太长，Agent 忽略关键约束**

Skill 超过 500 行后，Agent 开始"选择性阅读"——前面的约束被遵循，后面的被忽略。

对策：
- 把不变的全局约束放在 CLAUDE.md 中，Skill 只放流程步骤
- 用 `**关键约束**` 加粗标注不可跳过的规则，放在 Skill 顶部
- 每个步骤保持在 3 行以内，超过就拆分或移入 CLAUDE.md

---

**陷阱四：归档是最后一步，所以最容易被跳过**

如果不强制归档，`spike/changes/` 目录会堆积几十个废弃的调研，下次 `list` 命令结果噪声极大。

对策：把归档纳入 Skill 流程的最后一步，在 `concluded` 状态时主动提示归档命令，而不是让用户自己记得。

---

**陷阱五：模板太空，Agent 填出垃圾**

```markdown
❌ ## 调研结果
<!-- 写你的发现 -->

✅ ## 调研结果
<!-- 列出 3-5 个关键发现，每条说明：发现了什么 + 为什么重要 + 来源/依据 -->
<!-- 示例：Redis 官方文档显示 Cluster 模式下不支持跨 slot 事务，影响我们的分布式锁方案 -->
```

模板的注释行是给 Agent 的 instruction，要比给人读的文档更具体。"写你的发现"完全没有约束，"列 3-5 条、每条包含发现+重要性+来源"才是有效约束。

---

## 延伸：让工具更健壮的进阶技巧

### 技巧一：JSON Schema 校验工件完整性

不只检查文件是否存在，还检查文件是否包含必填字段：

```python
import re

def validate_research(path: str) -> list[str]:
    """返回缺失的必填章节列表"""
    required = ["## 调研背景", "## 现有方案对比", "## 关键发现"]
    content = open(path).read()
    return [h for h in required if h not in content]
```

在 `status` 命令中调用，如果工件存在但不完整，返回 `"state": "incomplete"` 而非 `"state": "researched"`。

---

### 技巧二：用 config.yaml 注入项目全局约束

工件模板是通用的，但项目约束是特定的。把项目约束分离到 `spike/config.yaml`：

```yaml
context: |
  这是一个 FastAPI + SQLite 的后端项目，Python 3.10+。
  不引入新的数据库依赖，不破坏现有 API 契约。

rules:
  - 所有调研方案必须评估是否与 SQLAlchemy 2.0 兼容
  - 推荐方案必须在 4 小时内可以 PoC 验证
```

Skill 在调用 `instructions` 时读取 config.yaml，将 `context` 和 `rules` 作为 Agent 的背景约束注入 Prompt，而不是写死在 Skill 里。这样同一套工具可以在不同项目中复用，只改 config.yaml。

---

### 技巧三：delta spec 与主 spec 的同步提醒

每次归档变更时，自动检查是否有 delta spec 需要合并进 SPEC.md：

```bash
# 在归档命令中添加
if [ -d "$CHANGE_DIR/specs/" ]; then
  echo "⚠️  该变更包含 delta spec，归档前请确认是否已同步到 SPEC.md："
  ls "$CHANGE_DIR/specs/"
  echo "确认后输入 y 继续归档："
  read confirm
  [ "$confirm" = "y" ] || exit 1
fi
```

这是一道"安全门"而不是硬拦截——用户可以选择跳过，但必须知道自己在跳过什么。

---

### 技巧四：让工具可观测

在每个关键操作后输出结构化日志，方便排查问题：

```bash
# 写入工件后
echo "[spike] ✓ research.md 写入完成 ($(wc -l < research.md) 行, $(date '+%H:%M:%S'))"

# 状态变化时
echo "[spike] 状态变更: created → researched"
```

这些日志在对话中显示，让用户能看到工具在做什么，也能在出问题时快速定位到哪一步失败了。

---

> **一句话总结**：SDD 工具的核心是"状态机 + 工件驱动 + 精准上下文"。在动手实现之前，先想清楚你的状态机有几个状态、每个状态对应哪个文件的存在与否。其余都是围绕这个状态机的包装。从最小可用版本开始，遇到新痛点再扩展，不要为假想的需求过度设计。

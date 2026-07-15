# SDD 工具解构 - 状态机 × 工件驱动 × 三种实现路径

---

## SDD 工具的本质：三件事

所有 SDD 工具，无论多复杂，都在做三件事：

```
① 告诉 Agent 当前状态          →   "你在哪一步"
② 告诉 Agent 下一步该做什么    →   "你接下来做什么"
③ 记录 Agent 做了什么          →   "你做到哪了"
```

| 机制 | 作用 | 实现载体 |
|------|------|---------|
| **状态感知** | 读取当前工件，判断处于哪个阶段 | 文件存在检查 / checkbox 解析 |
| **指令生成** | 根据状态返回下一步操作的 Prompt | Skill 模板 / CLI instructions 命令 |
| **状态持久化** | 将 Agent 的产出写入文件系统 | Markdown 工件 / YAML 元数据 |

OpenSpec 把这三件事分到三层：**文件系统**（持久化）、**CLI**（状态感知 + 指令生成）、**Skill**（对话包装）。GSD 是同样的分层，只是把更多编排逻辑放在了 CLI 侧。

---

## 核心设计模式

### 状态机：工具的骨架

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

**状态的判断永远基于文件是否存在**，而不是数据库字段或内存变量：Git 就是时间机器；崩溃安全（重启后扫描文件即可恢复）；可调试（`ls` 一眼看清状态）。

**设计状态机的三个原则：**

- **前驱约束要明确**：`conclusion.md` 需要 `research.md` 先存在，否则 Agent 没有输入
- **状态数量要最小**：不要为"进行中"创建额外状态——进行中就是"前驱满足 + 后继不存在"
- **终态要触发归档**：所有工件完成后提示用户归档，防止目录无限增长

---

### 工件驱动：文件就是数据库

`- [ ]` / `- [x]` checkbox 是状态机的核心原语，用正则 `/^[-*]\s*\[([ xX])\]/` 可解析任意 Markdown 中的任务完成度。

**工件设计的四个要素：**

| 要素 | 说明 | 示例 |
|------|------|------|
| **generates** | 工件对应哪个文件（支持 glob） | `research.md`、`specs/**/*.md` |
| **requires** | 依赖哪些工件先完成 | `[proposal]`、`[research, design]` |
| **template** | Agent 填充内容时的骨架 | 二级标题结构、必填字段占位符 |
| **instruction** | 告诉 Agent"如何填充这个工件" | "基于 proposal 列出技术方案..." |

好的模板是"骨架 + 示例"，不要太空（Agent 不知道写什么），也不要太满（没有填充空间）。

---

### 上下文工程：给 Agent 喂什么

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

OpenSpec 的 `instructions` 命令通过 `contextFiles` 字段返回当前阶段需要读取的文件列表，而不是把文件内容直接塞进 Prompt。Agent 按需读取，天然跳过未完成的工件。

---

### HITL 关键节点：哪里必须问人

| 应该问 | 不应该问 |
|--------|---------|
| 选择 change（多个活跃变更时 Agent 无法猜测意图） | 工件创建（根据模板自动填充） |
| 删除 / 归档（不可逆操作） | 状态查询（直接输出） |
| 跳过警告（"工件未完成但强制继续"） | checkbox 更新（完成一个任务就自动勾） |
| delta spec 同步（是否合并进主 SPEC.md） | |

---

## 三种实现路径

| 路径 | 适用场景 | 维护成本 |
|------|---------|---------|
| **纯 Skill** | 单个重复动作，无跨对话状态需求 | 零 |
| **Skill + 脚本** | 需要解析文件状态，工件结构固定 | 低 |
| **Skill + CLI** | 多 schema、多工具共享状态机、复杂依赖检查 | 高 |

**路径二**——脚本负责状态判断，Skill 调用脚本获取 `state` 后决定下一步：

```bash
#!/bin/bash
# scripts/spike-status.sh
CHANGE_DIR="openspec/changes/$1"

[ ! -d "$CHANGE_DIR" ] && echo '{"state": "not_found"}' && exit 0

RESEARCH=$([ -f "$CHANGE_DIR/research.md" ] && echo "true" || echo "false")
CONCLUSION=$([ -f "$CHANGE_DIR/conclusion.md" ] && echo "true" || echo "false")

if   [ "$CONCLUSION" = "true" ]; then echo '{"state": "concluded"}'
elif [ "$RESEARCH"   = "true" ]; then echo '{"state": "researched", "next": "write conclusion.md"}'
else                                   echo '{"state": "created", "next": "write research.md"}'
fi
```

**路径三**参考 OpenSpec 三层架构：CLI 暴露 `list`、`status --change <name>`、`instructions <artifact> --change <name>` 三个命令，Skill 调用 CLI 获取状态和模板，约需 200-300 行 Python。

---

## 动手实现：用路径二构建 Spike 工具

### 工件模板

`templates/research.md`：

```markdown
# Research: {{change_name}}

## 调研背景
<!-- 说明为什么做这次调研，要解决什么问题 -->

## 现有方案对比

| 方案 | 适用场景 | 优点 | 缺点 | 成本估算 |
|------|---------|------|------|---------|
| 方案 A | ... | ... | ... | ... |

## 关键约束
<!-- 项目现有架构、团队能力、时间限制等约束 -->

## 关键发现
<!-- 列 3-5 条：发现了什么 + 为什么重要 + 来源/依据 -->
```

`templates/conclusion.md`：

```markdown
# Conclusion: {{change_name}}

## 推荐方案
**推荐**：方案 X

**理由**（3 条以内）：
1. ...

## 主要风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|

## 下一步行动
- [ ] 行动 1
```

### Skill 文件

`skills/spike.md`：

```markdown
---
name: spike
description: 系统性技术调研工具
triggers: ["spike", "技术调研", "调研一下"]
---

**关键约束**：`research.md` 写完之前，不能写 `conclusion.md`。

## 流程

### 1. 确认调研主题
如果用户没有提供 change 名称，询问：「主题是什么？用 2-4 个英文单词描述。」

### 2. 初始化并检查状态
```bash
mkdir -p spike/changes/<change-name>
bash scripts/spike-status.sh <change-name>
```

### 3. 根据状态执行

- **created** → 读 `templates/research.md`，填充完整调研内容，写入 `spike/changes/<name>/research.md`
- **researched** → 读 `research.md` + `templates/conclusion.md`，写入 `conclusion.md`
- **concluded** → 展示结论摘要，提示归档：`mv spike/changes/<name> spike/archive/$(date +%Y-%m-%d)-<name>`

### 4. 每完成一个工件，重新检查状态并告知进度
```

---

## 常见陷阱

**① 在 Skill 里硬编码文件路径**
- ❌ `读取 openspec/changes/my-feature/research.md`
- ✅ 读取脚本返回的 `contextFiles` 列表——schema 变化时路径自动跟着走，不需要改 Skill

**② 把"进行中"建模成一个状态**
- 状态数量 = 已完成工件的组合数。`research.md` 写到一半时视为 `created`（前驱未完成），不需要 `RESEARCHING` 状态。

**③ 约束精度不对，导致 Agent 输出质量差**
- Skill 超过 500 行后 Agent 开始选择性阅读——全局约束放 CLAUDE.md，关键规则用 `**加粗**` 放 Skill 顶部
- 模板注释太空 Agent 填出垃圾——`<!-- 列 3-5 条：发现了什么 + 为什么重要 + 来源 -->` 而非 `<!-- 写你的发现 -->`

**④ 归档被跳过，目录无限堆积**
- 在 `concluded` 状态时主动提示归档命令，而不是让用户自己记得。

---

## 进阶技巧

- **工件完整性校验**：不只检查文件是否存在，还用正则检查必填章节是否存在。存在但不完整时返回 `"state": "incomplete"`，阻止进入下一阶段。
- **config.yaml 注入项目约束**：把项目特定的架构约束（技术栈、禁用依赖）放在单独的 config 文件，Skill 运行时注入为背景约束，同一套工具可在不同项目复用。
- **delta spec 同步提醒**：归档时自动检查变更目录是否包含 delta spec，有则要求用户确认是否已同步到 SPEC.md，再继续归档。

---

> **一句话总结**：SDD 工具的核心是"状态机 + 工件驱动 + 精准上下文"。先想清楚状态机有几个状态、每个状态对应哪个文件的存在与否，其余都是包装。从最小可用版本开始，遇到新痛点再扩展。

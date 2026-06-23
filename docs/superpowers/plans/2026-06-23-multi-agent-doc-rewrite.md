# 多智能体并发开发文档重写实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `training_doc/知识点/多智能体并发开发.md` 从"概念层+实践层双线并行"重组为"单线贯穿"，字数从 ~2000 字精简至 ~1100 字。

**Architecture:** 原文档概念和实践重复讲两遍，新文档按读者认知路径单线组织——每个核心话题只讲一次，概念与操作步骤合并在同一节内。

**Tech Stack:** Markdown 编辑（无代码变更）

## Global Constraints

- 目标文件：`training_doc/知识点/多智能体并发开发.md`（原地覆盖）
- 设计文档：`docs/superpowers/specs/2026-06-23-multi-agent-doc-rewrite-design.md`
- 删除内容：三屏幕物理布局、路径别名、开发者新定位（独立章节）、所有重复解释、口号性 callout
- 保留内容：FD 四维度模板、状态机八阶段、六大命令、/fd-deep Task 工具图、Worktree 操作步骤、双层 CLAUDE.md 示例、认知负荷表格
- 附录内容：文件结构参考、空闲通知配置（保留原文代码块，不修改）
- 语言风格：极简，去掉口号性描述，保留操作性内容

---

### Task 1：引言 + 第1节（FD：系统的唯一真相）

**Files:**
- Modify: `training_doc/知识点/多智能体并发开发.md`（全量覆盖，从文档开头写起）

**来源映射（原文 → 新文）：**
- 引言：原第12节开头一句 + 原 > 1 个开发者，8 个并行智能体
- FD 模板：原第3节代码块
- 状态机八阶段：原第4节 `Planned → ... → Closed` + FEATURE_INDEX.md 示例
- /fd-init 说明：原第13节"快速开始 Step 1"

- [ ] **Step 1：写出新版文档头部 + 第1节内容**

用以下内容替换原文件全部内容（后续 Task 追加）：

```markdown
# 多智能体并发开发

> 1 个开发者，多个并行 Agent——用 FD 状态机与斜杠命令驱动高并发 AI 开发。机器的执行能力已超过人类上下文切换极限；工程师的核心竞争力转向"将业务上下文精准翻译为 Agent 可执行的规格说明"。

---

## 1. FD：系统的唯一真相

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
```

- [ ] **Step 2：验证第1节内容完整性**

对照原文检查以下内容均已覆盖：
- [ ] FD 四维度模板代码块存在
- [ ] 状态机八阶段字符串存在
- [ ] FEATURE_INDEX.md 表格示例存在
- [ ] /fd-init 说明存在
- [ ] "Files to Modify"的核心价值说明存在

- [ ] **Step 3：提交**

```bash
git add training_doc/知识点/多智能体并发开发.md
git commit -m "docs: rewrite multi-agent doc - Task 1 引言+FD节"
```

---

### Task 2：第2节（三角色）+ 第3节（六大命令）

**Files:**
- Modify: `training_doc/知识点/多智能体并发开发.md`（追加）

**来源映射：**
- 三角色：原第2节（Tmux 角色分配）+ 原第13节 Step 3（终端配置）合并
- 六大命令：原第5节命令列表 + 原第13节"完整工作流一览"合并

- [ ] **Step 1：追加第2节和第3节内容**

在文件末尾追加：

```markdown
---

## 2. 三角色工作台

每个终端窗口绑定特定角色，角色不混用：

| 角色 | 职责 |
|------|------|
| **PM** | 管理 Backlog、将需求转化为 FD |
| **Planner** | 加载代码库上下文，识别风险，完善 FD Solution |
| **Worker** | 严格依据确定的 FD 执行代码落地 |

```bash
# 终端 1（Worker A）
claude --model claude-opus-4-7
> /fd-explore FD-001
> 实现 FD-001

# 终端 2（Worker B）
claude --model claude-opus-4-7
> /fd-explore FD-002
> 实现 FD-002

# 终端 3（Planner / PM）
claude
> /fd-new 下一个需求描述
```

**关键原则**：不同终端各自独立，通过 `fd/` 目录下的 Markdown 文件共享状态，不通过会话内存交互。

---

## 3. 六大命令驱动生命周期

```
/fd-new       从需求描述创建新 FD
/fd-status    展示全局索引与进度状态
/fd-explore   加载代码库上下文、架构文档与开发指南
/fd-deep      启动并行推演（见第4节）
/fd-verify    校对代码，提出验证计划并提交
/fd-close     归档 FD 并自动更新 Changelog
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
```

- [ ] **Step 2：验证内容完整性**

- [ ] 三角色表格存在
- [ ] 终端配置代码块（三个终端）存在
- [ ] 六大命令速查列表存在
- [ ] 完整工作流图存在
- [ ] 原第13节"关键原则"（共享状态通过 fd/ 目录）存在

- [ ] **Step 3：提交**

```bash
git add training_doc/知识点/多智能体并发开发.md
git commit -m "docs: rewrite multi-agent doc - Task 2 三角色+六大命令"
```

---

### Task 3：第4节（/fd-deep）+ 第5节（Worktree）

**Files:**
- Modify: `training_doc/知识点/多智能体并发开发.md`（追加）

**来源映射：**
- /fd-deep：原第6节 + 原第13节"/fd-deep 的并行子 Agent 机制"合并
- Worktree：原第7节"执行期" + 原第13节"并行执行：Worktree 隔离"合并

- [ ] **Step 1：追加第4节和第5节内容**

在文件末尾追加：

```markdown
---

## 4. /fd-deep：遇到难题时并行推演

FD Solution 写完后仍有未解决的 `%%` 批注，或技术方案不确定时，使用 `/fd-deep` 同时启动 4 个子 Agent 从不同角度独立推演：

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

**内联批注技巧**：在 FD Solution 节用 `%%` 标注疑问，Agent 执行前先解决：

```markdown
## Solution
Replace cron-based batch processing with an event-driven pipeline.
%% what's the max queue depth before we start dropping? need backpressure math
Failures go to the dead-letter queue.
%% what happens to in-flight items during cutover? need to confirm drain behavior
```

---

## 5. Worktree：隔离爆炸半径

多个 Worker 同时修改代码时，用 Git Worktree 隔离，避免冲突。**FD 的 "Files to Modify" 节就是提前声明爆炸半径**——两个 FD 若没有文件重叠，可安全并行；有重叠的必须串行或手动协调。

```bash
# 为每个 FD 创建独立工作区
git worktree add ../drama-flow-fd001 -b feature/FD-001
git worktree add ../drama-flow-fd002 -b feature/FD-002

# 各自启动 Claude Code
cd ../drama-flow-fd001 && claude
cd ../drama-flow-fd002 && claude

# 完成后合并主干
cd drama-flow
git merge feature/FD-001
git merge feature/FD-002
git worktree remove ../drama-flow-fd001
git worktree remove ../drama-flow-fd002
```
```

- [ ] **Step 2：验证内容完整性**

- [ ] /fd-deep Task 工具机制图存在（4个子Agent）
- [ ] 触发命令示例存在
- [ ] 与 /fd-explore 的区别说明存在
- [ ] %% 内联批注示例存在
- [ ] git worktree 完整操作步骤（add + 启动 + merge + remove）存在
- [ ] "Files to Modify 声明爆炸半径"说明存在

- [ ] **Step 3：提交**

```bash
git add training_doc/知识点/多智能体并发开发.md
git commit -m "docs: rewrite multi-agent doc - Task 3 fd-deep+Worktree"
```

---

### Task 4：第6节（上下文管理）+ 第7节（系统边界）

**Files:**
- Modify: `training_doc/知识点/多智能体并发开发.md`（追加）

**来源映射：**
- 上下文管理：原第8节（建立"机器品味"）
- 系统边界：原第11节（四项限制表格）+ 原第13节"认知负荷管理"表格合并为一节

- [ ] **Step 1：追加第6节和第7节内容**

在文件末尾追加：

```markdown
---

## 6. 上下文管理：双层 CLAUDE.md

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

---

## 7. 系统边界与认知负荷

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
| **认知负荷极限** | 超过 8 个并发进入崩溃区 | 保持并发数 ≤ 8 |

`/fd-status` 输出的 "Active Work" 数量是实时负荷指示器，超过 4 个 In Progress 时系统会主动提示。
```

- [ ] **Step 2：验证内容完整性**

- [ ] 双层 CLAUDE.md 对比示意图存在
- [ ] 两层设计价值说明存在
- [ ] 并发数状态表（4行）存在
- [ ] 四项物理限制表格存在
- [ ] /fd-status 说明存在

- [ ] **Step 3：提交**

```bash
git add training_doc/知识点/多智能体并发开发.md
git commit -m "docs: rewrite multi-agent doc - Task 4 上下文管理+系统边界"
```

---

### Task 5：附录A（文件结构）+ 附录B（空闲通知）

**Files:**
- Modify: `training_doc/知识点/多智能体并发开发.md`（追加结尾）

**来源映射：**
- 附录A：原第13节"文件结构参考"（原文复制）
- 附录B：原第13节"空闲通知配置"（原文复制）

- [ ] **Step 1：追加附录内容**

在文件末尾追加：

```markdown
---

## 附录 A：文件结构参考

```
fd/
├── FEATURE_INDEX.md              ← 全局状态注册表
├── templates/
│   └── FD-template.md            ← FD 文档模板
├── FD-001-<slug>.md
└── FD-002-<slug>.md

.claude/commands/fd/
├── fd-init.md
├── fd-new.md
├── fd-status.md
├── fd-explore.md
├── fd-deep.md
├── fd-verify.md
└── fd-close.md
```

斜杠命令本质是 `.claude/commands/` 下的 Markdown 文件。键入 `/fd-new 描述` 时，Claude 读取 `fd-new.md` 中的 prompt，将 `$ARGUMENTS` 注入后执行。

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
```

- [ ] **Step 2：最终验证整个文档**

- [ ] 运行字数估算：`wc -w training_doc/知识点/多智能体并发开发.md`（目标 < 1400 字）
- [ ] 检查无重复内容：每个核心概念（FD、角色、命令、/fd-deep、Worktree、CLAUDE.md、认知负荷）只出现在一个章节中
- [ ] 检查已删除内容不存在：搜索"三个屏幕"、"gpipeline"、"g*"、"开发者的新定位"均不出现
- [ ] 目录编号连续（1-7节 + 两个附录）

- [ ] **Step 3：最终提交**

```bash
git add training_doc/知识点/多智能体并发开发.md
git commit -m "docs: rewrite multi-agent doc - Task 5 附录 + 完成"
```

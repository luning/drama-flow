---
name: fd:new
description: 从用户需求描述创建新 FD 文档，并注册到 FEATURE_INDEX.md
argument-hint: "<需求描述>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
---
<objective>
将用户的需求描述转化为一份完备的 FD（Feature Design）文档。

输出：
1. `fd/FD-XXX-<slug>.md` — 完整 FD 文档
2. `fd/FEATURE_INDEX.md` — 新增一行记录
</objective>

<context>
用户需求：$ARGUMENTS

@CLAUDE.md
@SPEC.md
@fd/FEATURE_INDEX.md
</context>

<process>

## Step 1 — 确定 FD 编号

读取 `fd/FEATURE_INDEX.md`，找到当前最大编号，新 FD 编号 = 最大编号 + 1。
若 FEATURE_INDEX 为空，从 FD-001 开始。

## Step 2 — 生成 FD 文档

基于用户需求，填写以下四个维度。**禁止模糊**：

**Problem**：明确痛点，写出"现在的行为"和"期望的行为"的差距。

**Solution**：只写已决策的方案，不写备选。若需求不够清晰，先向用户确认再写。

**Files to Modify**：
- 结合 CLAUDE.md 的项目结构，列出所有受影响文件
- 每个文件注明做什么改动
- 这是"爆炸半径"声明，必须完整

**Verification**：写出可执行的验证步骤，每条都是可勾选的行动项。

## Step 3 — 生成文件名 slug

将 FD 标题转为 kebab-case，截取前 5 个词，例如：
`FD-012-add-watch-history-api.md`

## Step 4 — 写入文件

将完整 FD 写入 `fd/FD-XXX-<slug>.md`。

## Step 5 — 更新 FEATURE_INDEX.md

在表格末尾追加一行：
```
| FD-XXX | <Title> | Open | <Effort> | — |
```

## Step 6 — 输出确认

展示创建的文件路径，并提示用户：
- 检查 Files to Modify 是否完整
- 确认后可用 `/fd-explore` 加载代码上下文开始规划

</process>

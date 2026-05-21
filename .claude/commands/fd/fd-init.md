---
name: fd:init
description: 初始化多智能体并行开发工作台——创建 fd/ 目录结构、FEATURE_INDEX.md、FD 模板
allowed-tools:
  - Read
  - Write
  - Bash
---
<objective>
在当前项目中初始化 FD（Feature Design）工作台。幂等操作：已存在的文件不覆盖。

完成后输出操作摘要，告知用户接下来如何开始第一个 FD。
</objective>

<process>

## Step 1 — 检查现有状态

```bash
ls fd/ 2>/dev/null && echo "exists" || echo "new"
```

## Step 2 — 创建目录结构

确保以下目录存在：
- `fd/` — FD 文档根目录
- `fd/templates/` — FD 模板

## Step 3 — 创建 FEATURE_INDEX.md（若不存在）

写入到 `fd/FEATURE_INDEX.md`：

```markdown
# Feature Index

| FD | Title | Status | Effort | Owner |
|----|-------|--------|--------|-------|
```

状态合法值：`Planned` `Design` `Open` `In Progress` `Pending Verification` `Complete` `Deferred` `Closed`

## Step 4 — 创建 FD 模板（若不存在）

写入到 `fd/templates/FD-template.md`：

```markdown
# FD-XXX: <Title>

**Status**: Open  
**Effort**: Small | Medium | Large  
**Created**: YYYY-MM-DD  
**Owner**: <name>

---

## Problem

> 描述当前痛点与边界：现象 + 影响范围。

## Solution

> 已决策的方案路径（不写备选，只写要做的）。

## Files to Modify

> 列出所有将被新增或修改的文件，框定爆炸半径。

- `path/to/file.py` — 做什么改动
- `path/to/another.ts` — 做什么改动

## Verification

> 如何证明这个 FD 已完成——可执行的验证步骤。

- [ ] 步骤一
- [ ] 步骤二
```

## Step 5 — 输出摘要

告知用户：
1. 初始化完成，哪些文件被创建/跳过
2. 下一步：用 `/fd-new <需求描述>` 创建第一个 FD

</process>

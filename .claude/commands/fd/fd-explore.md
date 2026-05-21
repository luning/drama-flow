---
name: fd:explore
description: 加载指定 FD 的代码库上下文，为规划和实现做准备（读取，不写代码）
argument-hint: "<FD编号，如 FD-012>"
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---
<objective>
为指定 FD 加载足够的代码库上下文，让 Planner 或 Worker 能够做出准确的实现决策。

这是"读取"阶段，不写代码、不修改文件。输出：一份上下文摘要 + 潜在风险清单。
</objective>

<context>
目标 FD：$ARGUMENTS

@CLAUDE.md
@SPEC.md
</context>

<process>

## Step 1 — 读取 FD 文档

从 `fd/` 目录找到目标 FD 文件，读取完整内容，重点关注：
- **Files to Modify**：需要理解哪些文件
- **Solution**：实现方案是否依赖已有代码模式

## Step 2 — 探索相关代码

根据 Files to Modify 列表，逐一读取相关文件。对于每个文件：
- 理解现有结构和模式
- 识别与方案相关的函数/类
- 注意可能的副作用（如修改一个 Service 会影响哪些 API）

同时搜索相关符号：
```bash
grep -r "<关键词>" backend/ h5/ android/ --include="*.py" --include="*.ts" --include="*.kt" -l
```

## Step 3 — 检查测试覆盖

```bash
source backend/drama-flow/bin/activate && python -m pytest --collect-only 2>/dev/null | grep "<相关模块>"
```

了解已有测试的边界，避免实现破坏已有行为级测试。

## Step 4 — 输出上下文摘要

格式化输出：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Context for FD-XXX: <Title>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  涉及文件
  ─────────────────────────────
  - path/to/file.py（当前状态描述）
  - path/to/another.ts（当前状态描述）

  关键代码模式
  ─────────────────────────────
  - 发现的现有模式（可复用）

  潜在风险
  ─────────────────────────────
  ⚠️  风险一：描述
  ⚠️  风险二：描述

  未解决问题（用 %% 标记的疑问）
  ─────────────────────────────
  - 问题一
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

若 FD Solution 中有 `%%` 批注（未解决疑问），列出并建议在开始实现前解决。

## Step 5 — 建议下一步

根据上下文复杂度建议：
- 简单（已有明确模式可复用）→ 可直接进入 Worker 实现
- 复杂（涉及多模块/架构决策）→ 建议先运行 `/fd-deep FD-XXX` 做并行推演

</process>

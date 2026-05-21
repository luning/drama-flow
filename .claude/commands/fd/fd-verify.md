---
name: fd:verify
description: 对照 FD Verification 节校验实现是否完成，运行测试，生成验收报告
argument-hint: "<FD编号，如 FD-012>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---
<objective>
对照 FD 的 Verification 节，逐条验证实现是否达标。
运行相关测试，输出结构化的验收报告，并将 FD 状态更新为 Pending Verification 或 Complete。
</objective>

<context>
目标 FD：$ARGUMENTS

@CLAUDE.md
</context>

<process>

## Step 1 — 读取 FD

找到并读取 `fd/` 下对应的 FD 文档，提取：
- Solution（预期实现方案）
- Files to Modify（应该被修改的文件）
- Verification（验收步骤列表）

## Step 2 — 检查文件修改

对照 Files to Modify，检查每个文件是否被修改（`git diff` 或直接读取）：
```bash
git diff HEAD -- <file>
```
记录：已修改 / 未修改 / 额外修改了未列出的文件（需关注）。

## Step 3 — 运行后端测试

```bash
source backend/drama-flow/bin/activate && python -m pytest -x -v 2>&1 | tail -30
```

记录：通过 / 失败 / 新增测试覆盖情况。

## Step 4 — 逐条执行 Verification 步骤

对 FD Verification 节的每个勾选项，逐条执行验证。对于可自动验证的：
- API 端点：`curl` 测试
- 数据库变更：查询验证
- 逻辑行为：pytest 断言

对于需要人工验证的（UI 交互、视觉效果等），列出并标记"需人工确认"。

## Step 5 — 生成验收报告

输出格式：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Verification Report: FD-XXX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  文件修改检查
  ─────────────────────────────
  ✅ backend/app/api/xxx.py — 已修改
  ✅ backend/app/services/xxx.py — 已修改
  ⚠️  h5/src/api/xxx.ts — 未修改（预期需要修改）

  测试结果
  ─────────────────────────────
  ✅ 全部通过（X passed, X ms）
  或
  ❌ X 个失败：[失败测试名称]

  Verification 步骤
  ─────────────────────────────
  ✅ 步骤一 — 已验证
  ✅ 步骤二 — 已验证
  🔲 步骤三 — 需人工确认

  结论
  ─────────────────────────────
  状态：PASS / PARTIAL / FAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 6 — 更新 FD 状态

**若全部通过**：
1. 修改 FD 文件顶部 `Status: Pending Verification`
2. 更新 `fd/FEATURE_INDEX.md` 对应行状态
3. 提示用户可运行 `/fd-close FD-XXX` 完成归档

**若部分失败**：
1. 保持状态为 `In Progress`
2. 在 FD 末尾追加 `## Verification Failures` 节，列出失败项和建议修复方向

</process>

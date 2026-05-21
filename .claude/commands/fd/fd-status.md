---
name: fd:status
description: 展示所有 FD 的全局状态索引与进度概览
allowed-tools:
  - Read
  - Bash
  - Grep
---
<objective>
读取 `fd/FEATURE_INDEX.md` 和各 FD 文件，输出格式化的进度仪表盘。
</objective>

<process>

## Step 1 — 读取索引

读取 `fd/FEATURE_INDEX.md`。若文件不存在，提示用户先运行 `/fd-init`。

## Step 2 — 统计各状态数量

按以下状态分组统计：
- 🔴 In Progress
- 🟡 Open / Design / Planned
- 🟢 Pending Verification
- ✅ Complete / Closed
- ⏸️ Deferred

## Step 3 — 输出仪表盘

格式：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FD Status Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔴 In Progress    X
  🟡 Open           X
  🟢 Pending Verify X
  ✅ Done           X
  ⏸️  Deferred       X

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Active Work
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [FD-XXX] Title — In Progress (Effort: Medium)
  [FD-XXX] Title — Open (Effort: Small)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Ready to Start (Open)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [FD-XXX] Title — Open (Effort: Large)
```

## Step 4 — 并行建议

若当前 In Progress 数量 < 4，列出建议并行启动的 Open FD（按 Effort 从小到大排列）。
若 In Progress 数量 ≥ 4，提示注意认知负荷，建议先完成一个再开新的。

</process>

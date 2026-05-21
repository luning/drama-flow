---
name: fd:close
description: 归档已完成的 FD，更新状态为 Closed，并自动追加 CHANGELOG 记录
argument-hint: "<FD编号，如 FD-012>"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---
<objective>
将 FD 正式关闭：状态标记为 Closed，FEATURE_INDEX.md 更新，CHANGELOG.md 追加记录。
这是 FD 生命周期的终点，只有通过 /fd-verify 验证后才应调用。
</objective>

<context>
目标 FD：$ARGUMENTS
</context>

<process>

## Step 1 — 前置检查

读取 FD 文件，确认：
- Status 是否为 `Pending Verification` 或 `Complete`

若 Status 仍为 `In Progress` 或 `Open`，警告用户："该 FD 尚未通过验证，建议先运行 /fd-verify。是否仍要强制关闭？"

## Step 2 — 更新 FD 文件状态

修改 FD 文档顶部：
```
Status: Closed
Closed: YYYY-MM-DD
```

## Step 3 — 更新 FEATURE_INDEX.md

将对应行的 Status 列改为 `Closed`。

## Step 4 — 追加 CHANGELOG.md

若 `CHANGELOG.md` 不存在则创建。在文件顶部（`# Changelog` 标题后）追加：

```markdown
## [FD-XXX] <FD Title> — YYYY-MM-DD

**变更类型**：feat | fix | refactor | docs（根据 FD 内容判断）

**修改内容**：
- 一句话描述核心变更

**影响文件**：
- `path/to/file.py`
- `path/to/another.ts`
```

## Step 5 — Git 提交（可选）

询问用户："是否要提交这次关闭操作？(y/n)"

若确认，执行：
```bash
git add fd/FD-XXX-*.md fd/FEATURE_INDEX.md CHANGELOG.md
git commit -m "close(FD-XXX): <FD Title>"
```

## Step 6 — 输出摘要

```
✅ FD-XXX 已关闭
   状态：Closed
   FEATURE_INDEX：已更新
   CHANGELOG：已追加
   
下一步：/fd-status 查看全局进度
```

</process>

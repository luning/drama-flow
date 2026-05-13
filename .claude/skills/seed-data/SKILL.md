---
name: seed-data
description: 幂等导入 DramaFlow 测试数据。当用户说"添加测试数据"、"重置测试数据"、"运行 seed"、"导入数据"、"seed 一下"时触发。可重复调用，不会重复插入。
---

# seed-data

幂等导入 DramaFlow 测试数据（5 个分类、9 部剧集、90 集）。

## 执行步骤

1. 确认当前在 `backend/` 目录，激活虚拟环境 `drama-flow`
2. 执行 `python -m app.db.seed`
3. 解析输出并报告结果

## 结构化输出

运行完成后，输出以下格式的报告：

```json
{
  "status": "imported | skipped | error",
  "summary": "导入完成：9 部剧集，90 集" | "数据已存在（{n} 部剧集），跳过导入",
  "details": {}
}
```

## 回滚

seed-data 是幂等操作，不提供回滚。如需重置数据请使用 `db-reset` Skill。

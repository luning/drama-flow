---
name: db-reset
description: 重置 DramaFlow SQLite 数据库——删除现有数据库文件并重新导入测试数据。当用户说"重置数据库"、"清空数据"、"db reset"、"数据库重置"、"重新导入"时触发。
---

# db-reset

删除现有 SQLite 数据库文件并重新 seed 测试数据。适合在调试时快速重置数据状态。

## 执行步骤

1. 进入 `backend/` 目录
2. 关闭所有使用数据库的连接（如正在运行的 uvicorn 服务器）
3. 删除 `dramaflow.db` 文件
4. 运行 seed-data（自动创建数据库并导入数据）

```bash
rm -f dramaflow.db && python -m app.db.seed
```

## 结构化输出

```json
{
  "status": "reset_and_seeded | error",
  "action": "已删除 dramaflow.db 并重新导入测试数据",
  "summary": "导入完成：5 部剧集，50 集"
}
```

## 注意事项

- 此操作不可逆！所有现有数据将被删除
- 如果 uvicorn 开发服务器正在运行，重置后需要重启服务器才能使用新数据
- 测试数据库 `test.db` 不受影响（由 conftest.py 自动管理）

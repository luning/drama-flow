---
name: preview-deploy
description: 启动 DramaFlow 预览环境——启动 FastAPI 后端开发服务器，供 PM 或开发者在浏览器中验收 API。当用户说"启动预览"、"预览环境"、"启动后端"、"跑起来看看"、"preview"时触发。
---

# preview-deploy

启动 FastAPI 后端开发服务器，提供可访问的预览 URL 供验收使用。

## 执行步骤

### 1. 启动后端服务

1. 激活虚拟环境 `source backend/drama-flow/bin/activate`
2. 进入 `backend/` 目录
3. 确认数据库已初始化（如果 dramaflow.db 不存在，先运行 seed-data）
4. 启动 Uvicorn 开发服务器

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 输出预览信息

```json
{
  "status": "running",
  "api_base_url": "http://localhost:8000",
  "docs_url": "http://localhost:8000/docs",
  "health_url": "http://localhost:8000/health",
  "available_endpoints": [
    "POST /api/auth/register",
    "POST /api/auth/login",
    "GET /api/dramas",
    "GET /api/categories",
    "GET /api/banners",
    "..."
  ]
}
```

### 3. 注意事项

- 服务器在后台运行，使用 `--reload` 模式，修改代码后自动重启
- 数据使用已有的 dramaflow.db，如需重置数据请先运行 `db-reset`
- 后端默认绑定 `0.0.0.0:8000`，局域网设备也可访问

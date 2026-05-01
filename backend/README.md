# DramaFlow Backend

Python FastAPI 后端服务。

## 技术栈

- Python 3.10+ / FastAPI
- SQLAlchemy 2.0 ORM + SQLite
- JWT (python-jose) 认证
- Pydantic v2 数据校验

## 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 入口，路由注册
│   ├── config.py             # 配置（JWT/数据库/CDN）
│   ├── api/                  # API 路由层
│   │   ├── auth.py           # 注册/登录/登出/刷新
│   │   ├── dramas.py         # 剧集列表/详情/Banner/分类
│   │   ├── episodes.py       # 集数列表/视频签名
│   │   └── watch_records.py  # 播放记录 CRUD
│   ├── models/               # SQLAlchemy ORM 模型
│   ├── schemas/              # Pydantic 请求/响应模型
│   ├── services/             # 业务逻辑层
│   ├── db/
│   │   ├── database.py       # 引擎与会话
│   │   └── seed.py           # 测试数据导入
│   └── middleware/
│       └── auth_middleware.py # JWT 鉴权中间件
├── tests/                    # pytest 集成测试
└── requirements.txt
```

## 快速开始

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API 文档： http://localhost:8000/docs

## 架构约束

- API 路由层不直接操作数据库，调用 Service 层
- Service 层依赖 Repository 模式，不直接使用 Session
- 所有输入输出经由 Pydantic Schema 校验
- 跨模块调用必须通过 API（禁止 import 其他模块的 model 直接操作）

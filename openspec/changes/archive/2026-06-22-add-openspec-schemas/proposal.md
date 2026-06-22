## Why

DramaFlow 采用 Android + H5 + FastAPI 三端架构，但目前 OpenSpec 使用通用的 `spec-driven` 模板，缺少针对 API 接口、Pydantic 数据模型、JSBridge 协议的结构化描述规范。现有 spec 在描述 REST 接口、请求/响应 Schema 和跨端协议时格式不统一，导致 AI 生成代码时缺乏足够的约束上下文。

## What Changes

- 为项目创建本地自定义 schema `dramaflow`，fork 自 `spec-driven`
- 新增 `api-spec` artifact，专门描述 REST API 接口（路径、方法、请求体、响应体、错误码）
- 新增 `data-schema` artifact，描述 Pydantic/SQLAlchemy 数据模型字段定义与约束
- 调整 `spec` artifact 模板，增加「端」标注（Backend / Android / H5 / JSBridge）
- 为尚未建立 spec 的核心能力补充 OpenSpec spec 文件：用户认证、剧目浏览、观看记录、JSBridge 通信协议

## Capabilities

### New Capabilities

- `user-auth`: 用户注册/登录/Token 刷新/登出的完整认证流程（Backend API + Android EncryptedSharedPreferences + H5 登录页）
- `drama-catalog`: 剧目首页列表、分类筛选、搜索、详情页的数据获取与展示（Backend API + H5）
- `watch-record`: 继续观看进度记录、上报与查询（Backend API + Android + H5）
- `jsbridge-protocol`: H5 与 Android 原生 `window.DramaFlowBridge` 通信协议定义（方法签名、事件列表、错误处理）

### Modified Capabilities

（无现有 spec 需要修改）

## Impact

- `openspec/schemas/dramaflow/` — 新增本地 schema 目录（fork 自 spec-driven）
- `openspec/specs/user-auth/spec.md` — 新增
- `openspec/specs/drama-catalog/spec.md` — 新增
- `openspec/specs/watch-record/spec.md` — 新增
- `openspec/specs/jsbridge-protocol/spec.md` — 新增
- 不影响现有 `player-state-machine`、`video-player`、`video-sign-url` spec

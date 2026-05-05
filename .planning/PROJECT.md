# DramaFlow

## What This Is

DramaFlow 是一款面向海外市场的短剧观看平台。支持 Android 原生 App（含 ExoPlayer 视频播放器）+ 内嵌 Vue3 H5 页面（首页、详情页）的双端架构，后端基于 Python FastAPI + SQLite 提供 API 服务。

## Core Value

用户能流畅地发现和观看短剧，播放进度跨会话保持。

## Requirements

### Validated

已完成的迭代 1-3 功能：

- ✓ 用户注册/登录/登出（JWT Token） — 迭代 1
- ✓ Drama/Episode 数据模型 + 测试数据 — 迭代 1
- ✓ 首页 Banner + 分类 Tab + 剧集列表（按分类查询） — 迭代 1
- ✓ Drama Detail 详情页（简介 + 集数列表 + 评分） — 迭代 2
- ✓ ExoPlayer 视频播放器 + 自定义控制条 — 迭代 2
- ✓ 播放进度持久化（WatchRecord upsert） — 迭代 2
- ✓ 播放器状态机（IDLE/BUFFERING/READY/PLAYING/PAUSED/ENDED/ERROR） — 迭代 2
- ✓ 个性化推荐（基于 WatchRecord 的排序逻辑） — 迭代 3
- ✓ 倍速播放控制（0.5x~2.0x） — 迭代 3
- ✓ Auth 增强（记住我 + Token 自动刷新） — 迭代 3

### Active

- [ ] **首页推荐改版验收**：确保个性化推荐在现有代码中完整工作，包括后端排序逻辑和 H5 首页数据绑定

### Out of Scope

- 画质切换 — 可选进阶，非核心体验
- 首页 A/B 测试开关 — 可选进阶
- 播放进度跨设备同步 — 可选进阶

## Context

项目已完成三轮迭代的核心开发。迭代 3 中的"首页推荐改版"（AC-DRAMA-07/08/09）已在 SPEC.md 中定义：已登录用户首页列表基于观看历史进行个性化排序（同类优先、已看完降权），未登录用户不受影响。当前目标是确认此功能在现有代码中正确实现并覆盖所有验收标准。

## Constraints

- **Python 3.10+ / FastAPI**: 后端技术栈固定
- **Kotlin + Android SDK 34**: Android 端技术栈固定
- **Vue 3 + Vite + TypeScript**: H5 技术栈固定
- **SQLite**: 数据库固定，无迁移工具
- **Volcengine TOS**: 视频 CDN 固定

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| WatchRecord-based personalization | 利用已有观看记录数据实现推荐，无需额外推荐引擎 | ✓ 已实现 |
| 可选用户认证（get_optional_user） | 未登录用户不受个性化影响，保持向后兼容 | ✓ 已实现 |

---
*Last updated: 2026-05-05 after initialization*

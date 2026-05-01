# DramaFlow 海外短剧 APP — 产品需求文档 (PRD)

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | DramaFlow |
| 产品定位 | 海外市场短剧观看平台 |
| 目标用户 | 海外华人及全球短剧爱好者 |
| 技术栈 | Python FastAPI 后端 + Kotlin Android 原生 + Vue3 H5 |
| 版本 | v1.0 |

## 2. 产品背景与目标

### 2.1 市场背景
短剧（Short Drama）在海外市场快速增长，用户对碎片化、高浓度剧情的短视频内容需求旺盛。现有产品如 Viki、WeTV、DramaBox 已验证市场，但仍有差异化空间。

### 2.2 产品目标
- 为海外用户提供流畅的短剧观看体验
- 支持短视频播放、进度追踪、个性化推荐等核心功能
- 通过三轮迭代快速构建 MVP 并演进

### 2.3 成功指标
- 用户注册完成率 > 80%
- 视频播放成功率 > 95%
- 播放进度同步成功率 > 90%

## 3. 目标用户

| 用户类型 | 描述 |
|---------|------|
| 普通观众 | 通过 Android 设备观看短剧，浏览发现内容 |
| 注册用户 | 拥有账号，可追踪观看进度、获得个性化推荐 |
| 重度用户 | 高频使用，期望倍速播放、跨设备同步等进阶体验 |

## 4. 功能范围（三轮迭代）

### 4.1 迭代 1 — 用户认证 + 首页

| 编号 | 模块 | 功能 | 实现端 | 优先级 |
|------|------|------|--------|--------|
| F-01 | Auth | JWT 用户注册 | Python + Android | P0 |
| F-02 | Auth | JWT 用户登录 | Python + Android | P0 |
| F-03 | Auth | JWT 用户登出 | Python + Android | P1 |
| F-04 | Auth | 第三方 OAuth 登录（进阶） | 可选 | P2 |
| F-05 | Home | Banner 轮播图 | Vue3 H5 | P0 |
| F-06 | Home | 分类 Tab 切换 | Vue3 H5 | P0 |
| F-07 | Home | 剧集列表展示 | Vue3 H5 | P0 |
| F-08 | Home | 骨架屏加载效果（进阶） | 可选 | P2 |
| F-09 | Data | Drama/Episode SQLite 数据模型 | Python 后端 | P0 |
| F-10 | Data | 测试数据填充 | Python 后端 | P0 |
| F-11 | Data | 数据分页加载（进阶） | 可选 | P2 |

### 4.2 迭代 2 — 内容消费核心

| 编号 | 模块 | 功能 | 实现端 | 优先级 |
|------|------|------|--------|--------|
| F-12 | Detail | 剧集详情页（简介 + 集数列表 + 评分） | Vue3 H5 | P0 |
| F-13 | Detail | 用户评论区（进阶） | 可选 | P2 |
| F-14 | Player | ExoPlayer 视频播放器 | Android 原生 | P0 |
| F-15 | Player | 播放进度控制条 | Android 原生 | P0 |
| F-16 | Player | 横屏全屏播放（进阶） | 可选 | P2 |
| F-17 | Player | 手势快进/快退（进阶） | 可选 | P2 |
| F-18 | Progress | 播放进度持久化 | Python + Android | P0 |
| F-19 | Progress | 断点续播提示 UI（进阶） | 可选 | P2 |

### 4.3 迭代 3 — 需求演进与功能改造

| 编号 | 模块 | 功能 | 实现端 | 优先级 |
|------|------|------|--------|--------|
| F-20 | Recommend | 个性化推荐（基于观看历史） | Python + Vue3 H5 | P0 |
| F-21 | Player+ | 倍速播放控制 | Android 原生 | P0 |
| F-22 | Player+ | 画质切换（进阶） | 可选 | P2 |
| F-23 | Auth+ | "记住我" 持久化 Token | Python + Android | P0 |
| F-24 | Auth+ | JWT Token 自动刷新 | Python + Android | P0 |
| F-25 | A/B Test | 首页 A/B 测试开关（进阶） | 可选 | P2 |
| F-26 | Sync | 播放进度跨设备同步（进阶） | 可选 | P2 |

## 5. 非功能需求

| 编号 | 类别 | 要求 |
|------|------|------|
| N-01 | 性能 | 视频 CDN 秒开，首帧 < 2s |
| N-02 | 性能 | API 响应 < 500ms（P95） |
| N-03 | 安全 | JWT Token 安全存储（EncryptedSharedPreferences） |
| N-04 | 安全 | Token 刷新机制防重放 |
| N-05 | 兼容 | Android WebView 内嵌 H5 通信正常 |
| N-06 | 可用性 | 播放器状态机覆盖：加载/播放/暂停/缓冲/错误/结束 |

## 6. 技术架构概要

| 层次 | 方案 |
|------|------|
| 移动端 | Kotlin + Android Studio + ExoPlayer |
| H5 内嵌页 | Vue3 + Vite + Pinia |
| 后端 API | Python 3.10+ + FastAPI + JWT |
| 数据库 | SQLite + SQLAlchemy ORM |
| 视频 CDN | 七牛云 |
| 状态管理 | ViewModel + LiveData (Android) / Pinia (Vue3) |
| AI 工具链 | Claude Code + GLM |

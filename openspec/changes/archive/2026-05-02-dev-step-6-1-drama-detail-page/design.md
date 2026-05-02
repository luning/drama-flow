## Context

迭代 1 已完成首页（H5 WebView + 剧集列表展示）和用户认证。当前状态：

- 后端 `/api/dramas/{id}` 和 `/api/dramas/{id}/episodes` 接口已完成，测试覆盖 AC-DRAMA-04/05
- H5 Detail.vue 页面框架已完成（标题/描述/评分/集数列表渲染），但 `playFirst()` 为空函数，未接入播放流程
- H5 EpisodeList.vue 仅展示集数，点击无响应
- Android HomeFragment 使用 WebView 加载 H5，但未配置 JSBridge 导航（用户从首页点击剧集卡片后跳转到详情页）
- Android DetailViewModel 已存在但无对应 UI
- 现有 Detail.vue 和 EpisodeList.vue 中存在硬编码颜色值（未使用 Design Token）
- 详情页缺乏加载状态和错误状态处理

## Goals / Non-Goals

**Goals:**
- 用户从首页点击剧集 → 进入详情页（H5 渲染，WebView 承载）
- 详情页展示完整剧集信息（简介 / 评分 / 集数列表）
- "立即观看"按钮播放第一集（通过 JSBridge 调用 Android ExoPlayer）
- 集数列表中点击任意集可播放
- 加载状态和错误处理覆盖（loading / error / empty 三态）
- Design Token 替换硬编码色值

**Non-Goals:**
- 不涉及播放器本身（PlayerActivity 已在迭代 2 步骤 6.2 负责）
- 不涉及播放进度持久化（步骤 6.4）
- 不涉及评论区（PRD F-13，P2 可选）
- 不修改后端 API

## Decisions

### 1. 架构方案：纯 H5 内路由，不新增 Android Fragment
- **方案选型**：H5 使用 Vue Router hash 模式，Detail 路由已在 H5 内配置；Android 无需新增 Detail Fragment，在现有 HomeFragment WebView 内做 H5 内导航
- **理由**：复用了迭代 1 已搭建的 WebView 容器架构，无需引入新的 Android 组件层；详情页 UI 逻辑集中在 H5 维护，迭代 2 中后续功能改造更方便
- **替代方案**：新增 Android DetailFragment + 原生渲染 —— 否决，因为工作量翻倍且 UI 一致性维护成本高
- **JSBridge 导航**: H5 内点击剧集卡片 → `router.push('/detail/' + id)` 即可在 WebView 内导航到详情

### 2. 播放触发：JSBridge 通道
- H5 点击播放按钮/集数 → `window.DramaFlowBridge.playVideo(episodeId, videoUrl, title)`
- Android JSBridge 已实现 `playVideo()` 方法，可直接复用
- 需要后端在 episode 列表中返回 `video_url` 字段（由七牛云签名，步骤 6.2 完善），当前先传占位 URL

### 3. 状态管理：Pinia drama store
- 现有 `useDramaStore` 已封装 `fetchDetail(id)` 方法（并行请求 detail + episodes）
- 当前无 loading/error 状态变量，需补充
- 无需新增 store

### 4. Design Token 引用
- H5 项目已定义 CSS 变量在 `:root` 中（根据 `design_system.md`）
- 替换 Detail.vue 和 EpisodeList.vue 中的硬编码色值为 `var(--primary)`、`var(--bg-card)` 等

## Risks / Trade-offs

- **[体验] H5 内导航较慢**：详情页需串行或并行请求 detail + episodes 接口，在弱网环境下体验不佳 → 添加骨架屏加载状态
- **[耦合] playFirst 依赖 video_url 字段**：当前 episode 可能不含 video_url（等步骤 6.2 完成后才有签名 URL） → 先传空字符串，播放器端处理无 URL 场景
- **[测试] H5 端暂无可执行的 E2E 测试**：现有测试仅覆盖后端 API → 本轮暂不引入 H5 E2E（Cypress），但确保 AC 可人工验证


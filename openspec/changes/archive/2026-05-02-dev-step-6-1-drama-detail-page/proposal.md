## Why

迭代 1 已完成用户认证和首页展示，但用户点击剧集后无法查看详情信息和集数列表。实现 Drama Detail 页是迭代 2 的核心入口，打通首页 → 详情 → 播放的用户路径，使内容消费闭环成型。

## What Changes

- H5 Detail.vue 完善：接入 JSBridge 实现"立即观看"按钮的一键播放能力
- H5 Detail.vue 添加加载状态和错误处理，提升用户体验
- H5 Detail.vue 使用 Design Token 替换硬编码颜色值
- EpisodeList.vue 添加集数点击播放（通过 JSBridge）
- Android HomeFragment WebView 添加 JSBridge 导航支持（H5 内点击剧集卡片跳转到详情路由）
- 修复现有 Drama 详情接口测试覆盖不足的问题

## Capabilities

### New Capabilities
- `drama-detail-page`: 剧集详情页完整展示（简介/评分/集数列表），支持从首页导航到详情，以及从详情一键播放

### Modified Capabilities
<!-- 无存量 spec 变更，本轮不涉及领域模型或接口协议调整 -->

## Impact

- **H5**: Detail.vue、EpisodeList.vue — 完善交互逻辑和样式
- **Android**: HomeFragment.kt — WebView 导航支持；JSBridge.kt — 无需修改（已有 `playVideo` 方法）
- **后端**: 无需修改，`/api/dramas/{id}` 已在迭代 1 完成
- 涉及 Design Token 引用规范（`design_system.md`）


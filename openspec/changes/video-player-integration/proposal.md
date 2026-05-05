## Why

DramaFlow 迭代 2 的核心功能是内容消费体验。用户从首页选择剧集后，需要能查看剧集详情并播放视频。当前项目已包含基础的 ExoPlayer 集成和 TOS 签名 URL 支持，但需要在以下方面补全：1）后端提供专用的视频签名 URL 接口（SPEC.md AC-EP-03/04）；2）Android 端从详情页到播放器的完整跳转链路；3）自定义控制条的完善。

## What Changes

### Backend
- 新增 `GET /api/episodes/{episode_id}/video-url` 接口，返回独立的视频签名 URL 和过期时间
- 确保 TOS 签名 URL 服务在密钥未配置时有清晰的降级行为

### Android
- 完善 PlayerActivity 自定义控制条 UI（进度条 Seeker、当前时间/总时长显示）
- 详情页（WebView/H5）通过 JSBridge 或 Intent 集成到 PlayerActivity 的导航链路
- 确保 PlayerViewModel 状态机与 ExoPlayer 回调同步
- 添加横屏全屏的配置支持（AndroidManifest）

## Capabilities

### New Capabilities
- `video-sign-url`: 后端视频签名 URL 接口，为指定剧集单集生成有时效性的 CDN 签名播放地址
- `video-player`: Android ExoPlayer 播放器集成包含自定义控制条、全屏、倍速、状态同步

### Modified Capabilities
- None（新增能力，不修改现有 Spec 中的行为要求）

## Impact

- **Backend**: `app/api/episodes.py` — 新增 Video URL 路由；`app/services/episode_service.py` — 可能需新增视频 URL 专用方法
- **Android**: `player/` 模块 — PlayerActivity 控制条增强；`player/viewmodel/` — PlayerViewModel 状态同步；`detail/` — 详情页到播放器的导航
- **Android Manifest**: 添加 Activity 横屏配置
- **SPEC.md**: 对应 AC-EP-03/04 的验收标准已存在，无需修改

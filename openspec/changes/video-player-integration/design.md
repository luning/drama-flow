## Context

DramaFlow 使用火山引擎 TOS 作为视频存储和 CDN，已在 `tos_service.py` 中封装预签名 URL 生成逻辑。后端 episode API 返回的数据已包含签名 URL，但缺少专用的视频 URL 刷新接口。Android 端已有基础的 ExoPlayer 集成（PlayerActivity + PlayerViewModel），具有播放/暂停、倍速、全屏等功能，但控制条缺少进度拖动和时间显示。从 H5 详情页到 PlayerActivity 的导航链路尚未完整建立。

## Goals / Non-Goals

**Goals:**
- 后端提供 `GET /api/episodes/{episode_id}/video-url` 独立签名 URL 接口，满足 AC-EP-03/04
- Android 自定义控制条增加进度 seekbar 和当前时间/总时长显示
- 实现从剧集详情页（WebView/H5）通过 Intent 跳转到 PlayerActivity 的导航链路
- PlayerViewModel 状态机与 ExoPlayer 实际回调同步
- AndroidManifest 配置 Activity 横屏支持

**Non-Goals:**
- 不修改 TOS 服务底层实现
- 不实现离线缓存或视频下载
- 不实现画质切换

## Decisions

1. **Option A: 独立 video-url 接口 vs Option B: 复用 episode detail 接口**
   - Decision: Option A — 新增 `GET /api/episodes/{episode_id}/video-url`
   - Rationale: 独立的 URL 刷新接口语义清晰，客户端只需请求该端点即可刷新签名（URL 过期时不需要重新获取整集详情）；返回结构包含 `{ url, expires_at }` 便于客户端判断是否需要重新请求
   - Alternative: 复用 episode detail 接口虽减少端点数量，但返回数据量更大，语义不精确

2. **自定义控制条实现方式: Media3 默认 ControlLayout vs 完全自建**
   - Decision: 保留 PlayerView 接管 player，自定义控制条使用独立的 View 层叠加在 PlayerView 之上
   - Rationale: 完全自建控制条可获得最大定制灵活性，不依赖 Media3 默认 UI 组件
   - Trade-off: 需要自行处理手势、事件分发

3. **详情页到播放器导航: JSBridge vs 直接 Intent**
   - Decision: H5 详情页通过 JSBridge 调用 `window.DramaFlowBridge.openPlayer(episodeId, dramaId, episodeNumber)` → Android 原生侧解析后启动 PlayerActivity Intent
   - Rationale: 保持一致使用已有 JSBridge 通信机制（CLAUDE.md 架构约束要求 H5 与 Android 通过 JSBridge 通信）
   - Alternative: 直接 URL Scheme 拦截，但破坏架构一致性

4. **全屏模式: Activity 横屏 vs 窗口 Flag**
   - Decision: 保留现有窗口 Flag 方式（全屏隐藏状态栏）+ 添加 AndroidManifest 中 `configChanges` 防止横屏 Activity 重启
   - Rationale: Flag 方式控制灵活，不需要重新创建 Activity；`configChanges` 防止旋转时状态丢失

## Risks / Trade-offs

- **[Risk] 视频 URL 过期导致播放中断**: 播放时签名 URL 过期 → Player 报错 → 需要捕获错误后自动重新请求新签名 URL
  - Mitigation: PlayerActivity 中监听 `onPlayerError`，如果是 HTTP 401/403 错误，触发重新请求 video-url 后更新 MediaItem
- **[Risk] TOS 密钥未配置时服务崩溃**: `tos_service.py` 中 `_client = None` 时 `signed_url()` 返回空字符串
  - Mitigation: video-url 接口检测 TOS 是否可用，不可用时返回 503 和明确错误信息
- **[Trade-off] 控制条与 PlayerView 的事件冲突**: 自定义控制条覆盖在 PlayerView 之上，点击事件可能被 PlayerView 拦截
  - Mitigation: 控制条容器设置 `android:clickable="true"` 拦截上层事件

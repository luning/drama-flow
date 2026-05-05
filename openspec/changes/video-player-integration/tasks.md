## 1. Backend — 视频签名 URL 接口

- [x] 1.1 在 `episodes.py` 中新增 `GET /api/episodes/{episode_id}/video-url` 路由
- [x] 1.2 在 `episode_service.py` 中新增 `get_video_url()` 方法，调用 TOS 签名并返回 `{ url, expires_at }`
- [x] 1.3 处理异常：单集不存在返回 404，TOS 不可用时返回 503
- [x] 1.4 运行 `pytest` 确认已有测试不破坏

## 2. Android — 自定义控制条增强

- [x] 2.1 修改 `activity_player.xml` 布局，在控制条区域增加 SeekBar、当前时间/总时长 TextView
- [x] 2.2 在 `PlayerActivity.kt` 中绑定 SeekBar 进度更新和拖动跳转逻辑
- [x] 2.3 实现播放/暂停按钮状态同步（图标随播放状态切换）
- [x] 2.4 实现时间格式化工具方法（毫秒 → mm:ss）

## 3. Android — 详情页到播放器导航

- [x] 3.1 在 JSBridge 中实现 `openPlayer(episodeId, dramaId, episodeNumber)` 方法，启动 PlayerActivity
- [x] 3.2 在 H5 详情页的播放按钮点击事件中调用 JSBridge 方法
- [x] 3.3 确认 PlayerActivity 通过 Intent 接收参数并正确初始化播放

## 4. Android — 播放器状态机同步与全屏配置

- [x] 4.1 在 `PlayerViewModel.kt` 中添加 `setState()` 方法支持 ExoPlayer 状态更新
- [x] 4.2 在 `PlayerActivity.kt` 中将 ExoPlayer.Listener 回调与 ViewModel 状态关联
- [x] 4.3 在 `AndroidManifest.xml` 中为 PlayerActivity 添加 `configChanges` 配置防止横屏重启
- [x] 4.4 修复全屏/返回按钮图标（照相机→全屏图标、跳上一曲→返回箭头）
- [x] 4.5 实现全屏模式控制条自动隐藏（3秒无操作后隐藏，点击画面切换）
- [x] 4.6 添加上一集/下一集切换按钮及导航逻辑

## 5. 集成验证

- [x] 5.1 运行 `pytest` 验证后端接口
- [x] 5.2 构建 Android App 并安装到模拟器验证播放流程

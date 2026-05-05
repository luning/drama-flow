## 1. Android 周期性进度上报

- [x] 1.1 PlayerViewModel 新增 `progressReportJob` 协程，每 15 秒调用 `reportProgress()`
- [x] 1.2 PlayerViewModel 暴露 `startPeriodicReporting(episodeId)` 和 `stopPeriodicReporting()` 方法
- [x] 1.3 PlayerActivity 在播放状态变为 PLAYING 时启动周期性上报，暂停时停止
- [x] 1.4 PlayerActivity 在 `onStop()` 中先即时上报进度，再取消周期性上报

## 2. Android 续播恢复

- [x] 2.1 PlayerViewModel 新增 `fetchLastPosition(episodeId)` 方法，调用 GET /api/watch-records/{episode_id}
- [x] 2.2 PlayerActivity 在播放器 STATE_READY 回调中调用续播逻辑，Seek 到上次播放位置
- [x] 2.3 续播请求失败时静默处理，从头开始播放

## 3. 验证

- [x] 3.1 运行 `pytest` 确保后端测试均通过
- [x] 3.2 确认 Android 编译通过（gradlew assembleDebug）

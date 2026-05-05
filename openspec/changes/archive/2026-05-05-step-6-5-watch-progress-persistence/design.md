## Context

WatchRecord 后端 API（PUT/GET/List/ContinueWatching）和 Android Retrofit 接口已完成。Android 端在播放结束时通过 `PlayerViewModel.reportProgress()` 上报进度，但缺少：

1. 播放期间的周期性上报（SPEC 要求每 15 秒）
2. 暂停/退出播放器时的即时上报
3. 播放器初始化时从服务端获取上次播放位置并自动续播

## Goals / Non-Goals

**Goals:**
- Android 端每 15 秒上报播放进度到服务端
- 用户暂停或退出播放器时立即上报当前进度
- 播放器打开时获取上次播放位置，自动 Seek 到该位置续播
- 上报和续播逻辑与 PlayerViewModel 的 UI 状态更新解耦

**Non-Goals:**
- 后端 WatchRecord API 改造（已有接口完全满足）
- 跨设备进度同步
- 播放进度冲突合并策略

## Decisions

| 决策 | 方案 | 理由 |
|------|------|------|
| 定时器位置 | PlayerViewModel 新增 `progressReportJob` | 与 UI 更新协程（`progressJob`）分离，职责单一，ViewModel 生命周期安全 |
| 上报间隔 | 固定 15 秒 | 符合 SPEC 要求，避免过于频繁的请求 |
| 续播时机 | Player STATE_READY 回调中 Seek | 确保播放器已就绪，直接跳转位置不中断首次播放体验 |
| 暂停上报 | PlayerActivity.onStop() + onPause 回调 | 覆盖退出 Activity（正常退出、按 Home 键等）和手动暂停场景 |

## Risks / Trade-offs

- [协程竞态] 15 秒定时器触发时用户刚好退出页面 → `viewModelScope.launch` 在 ViewModel 清除时自动取消，已有 try-catch 兜底，无实际风险
- [网络失败] 进度上报失败不应阻塞 UI → 已在 `reportProgress` 中 catch Exception 静默处理
- [快速切集] 上报进行中用户切到下一集 → 旧协程自动取消，新任务立即开始

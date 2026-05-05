## Why

用户播放剧集时，播放进度需要持久化存储，以便下次播放时从上次位置续播，并在首页"继续观看"列表中展示未看完的剧集。这是短剧 App 的核心体验闭环——后端 API 和模型已完成，但 Android 端仅实现了播放结束时的进度上报，缺少周期性上报和续播恢复。

## What Changes

- **Android PlayerActivity**: 新增周期性播放进度上报（每 15 秒），以及在暂停/退出播放器时立即上报
- **Android PlayerActivity**: 播放器初始化时通过 WatchRecord API 获取上次播放位置，自动 Seek 到该位置实现续播
- **Android PlayerViewModel**: 新增专用协程任务管理进度上报周期，避免与 UI 更新任务耦合
- **后端**: 无需新增接口，已有 PUT/GET WatchRecord 接口完全满足需求

## Capabilities

### New Capabilities
- `android-watch-progress-reporting`: Android 端周期性（15秒）播放进度上报，以及在暂停、退出播放器时的即时上报逻辑
- `android-playback-resume`: Android 端播放器初始化时获取上次播放位置并自动续播

### Modified Capabilities
- （无）

## Impact

- **Android** (`player/`): 修改 PlayerActivity.kt 和 PlayerViewModel.kt
- **后端**: 无变更，已有接口可用
- **Spec**: 无需新增 SPEC.md AC，已有 AC-WR-01～AC-WR-08 覆盖

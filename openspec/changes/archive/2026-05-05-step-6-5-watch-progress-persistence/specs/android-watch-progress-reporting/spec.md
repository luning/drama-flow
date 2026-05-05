# Android Watch Progress Reporting

## ADDED Requirements

### Requirement: 周期性播放进度上报

Android 端在播放剧集期间，每 15 秒自动调用后端 PUT /api/watch-records/{episode_id} 上报当前播放进度。

#### Scenario: 播放期间每 15 秒上报
- **WHEN** 用户开始播放剧集且播放状态为 PLAYING
- **THEN** 系统每 15 秒自动上报 progress、last_position、completed 到后端

#### Scenario: 上报不阻塞 UI
- **WHEN** 进度上报请求进行中
- **THEN** 播放器 UI 不受影响，网络异常时不显示错误提示

#### Scenario: 暂停后取消定时器
- **WHEN** 播放器暂停或退出
- **THEN** 取消 15 秒定时器，避免暂停期间继续上报

### Requirement: 暂停/退出时即时上报

用户暂停播放或退出播放器时，立即上报当前进度。

#### Scenario: 暂停时上报
- **WHEN** 用户点击暂停按钮或系统暂停播放
- **THEN** 立即上报当前播放位置

#### Scenario: 退出播放器时上报
- **WHEN** 用户退出 PlayerActivity 或按 Home 键
- **THEN** 在 onStop() 中立即上报当前播放位置

### Requirement: 播放结束时上报 completed

剧集播放结束后（ExoPlayer STATE_ENDED），上报 completed=true。

#### Scenario: 播放结束上报
- **WHEN** 剧集播放完毕进入 ENDED 状态
- **THEN** 上报 progress=100, completed=true（已有实现，确保不被周期性上报覆盖）

## MODIFIED Requirements

（无）

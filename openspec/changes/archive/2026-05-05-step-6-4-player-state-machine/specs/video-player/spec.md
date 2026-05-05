## MODIFIED Requirements

### Requirement: 播放器状态机同步

PlayerViewModel 状态机 SHALL 与 ExoPlayer 实际状态同步。状态转换 SHALL 覆盖 7 个状态：IDLE（初始）、BUFFERING（缓冲）、READY（就绪）、PLAYING（播放中）、PAUSED（暂停）、ERROR（出错）、ENDED（播放结束）。

状态转换规则：
- IDLE → BUFFERING：prepare() 调用后
- BUFFERING → READY：缓冲完成
- READY → PLAYING：playWhenReady 为 true
- READY → PAUSED：playWhenReady 为 false
- PLAYING → PAUSED：用户暂停
- PAUSED → PLAYING：用户恢复播放
- PLAYING/PAUSED → BUFFERING：seek 或重新缓冲
- PLAYING/PAUSED → ENDED：播放完成
- ANY → ERROR：发生播放错误
- ERROR → BUFFERING：调用 recover() 恢复
- ANY → IDLE：player 释放

#### Scenario: 状态跟随 ExoPlayer 回调完整变化
- **WHEN** PlayerViewModel 创建
- **THEN** 初始状态为 IDLE
- **WHEN** ExoPlayer prepare() 被调用
- **THEN** 状态切换到 BUFFERING
- **WHEN** 缓冲完成后 playWhenReady 为 true
- **THEN** 状态切换到 PLAYING
- **WHEN** 缓冲完成后 playWhenReady 为 false
- **THEN** 状态切换到 PAUSED
- **WHEN** 用户点击暂停
- **THEN** 状态切换到 PAUSED
- **WHEN** 用户点击播放
- **THEN** 状态切换到 PLAYING
- **WHEN** 视频播放完成
- **THEN** 状态切换到 ENDED
- **WHEN** 播放出错
- **THEN** 状态切换到 ERROR
- **WHEN** 调用 recover() 恢复
- **THEN** 状态从 ERROR 切换到 BUFFERING
- **WHEN** player release
- **THEN** 状态切换到 IDLE

#### Scenario: 状态仅由 onPlaybackStateChanged 驱动
- **WHEN** ExoPlayer 处于 BUFFERING
- **WHEN** onIsPlayingChanged(true) 被回调
- **THEN** PlayerState 保持 BUFFERING，不被覆盖为 PLAYING

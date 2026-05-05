## ADDED Requirements

### Requirement: Player 状态定义

PlayerViewModel SHALL 定义 7 个状态：IDLE / BUFFERING / READY / PLAYING / PAUSED / ERROR / ENDED，覆盖 ExoPlayer 全部生命周期。

#### Scenario: 状态枚举完整
- **WHEN** 检查 PlayerState 枚举定义
- **THEN** 包含 IDLE、BUFFERING、READY、PLAYING、PAUSED、ERROR、ENDED 七个枚举值

### Requirement: 合法状态转换

PlayerViewModel SHALL 只允许以下合法状态转换序列：

```
IDLE → BUFFERING → READY → PLAYING ↔ PAUSED
READY → PLAYING/PAUSED (取决于 playWhenReady)
PLAYING → BUFFERING (seek/rebuffer)
PAUSED → BUFFERING (seek/rebuffer)
PLAYING/PAUSED → ENDED (播放完成)
ANY → ERROR (onPlayerError)
ERROR → BUFFERING (recover)
ANY → IDLE (player release)
```

#### Scenario: 初始状态为 IDLE
- **WHEN** PlayerViewModel 创建
- **THEN** playerState 为 IDLE

#### Scenario: prepare 后进入 BUFFERING
- **WHEN** ExoPlayer prepare() 被调用
- **THEN** onPlaybackStateChanged(STATE_BUFFERING) 触发，状态切换到 BUFFERING

#### Scenario: 缓冲完成进入 READY
- **WHEN** ExoPlayer 缓冲完成
- **THEN** onPlaybackStateChanged(STATE_READY) 触发，状态切换到 READY

#### Scenario: READY 时 playWhenReady=true 进入 PLAYING
- **WHEN** player 处于 READY 状态且 playWhenReady 为 true
- **THEN** 状态立即切换到 PLAYING

#### Scenario: READY 时 playWhenReady=false 进入 PAUSED
- **WHEN** player 处于 READY 状态且 playWhenReady 为 false
- **THEN** 状态立即切换到 PAUSED

#### Scenario: PLAYING 时 pause 进入 PAUSED
- **WHEN** 用户点击暂停
- **THEN** ExoPlayer 回调 onPlaybackStateChanged(STATE_READY) + playWhenReady=false
- **THEN** 状态切换到 PAUSED

#### Scenario: PAUSED 时 play 进入 PLAYING
- **WHEN** 用户点击播放
- **THEN** ExoPlayer 回调 onPlaybackStateChanged(STATE_READY) + playWhenReady=true
- **THEN** 状态切换到 PLAYING

#### Scenario: seek 操作进入 BUFFERING 后恢复
- **WHEN** 用户拖动 seekbar
- **THEN** ExoPlayer 先进入 STATE_BUFFERING，状态切换到 BUFFERING
- **WHEN** 缓冲完成进入 STATE_READY
- **THEN** 根据 playWhenReady 恢复到 PLAYING 或 PAUSED

#### Scenario: 播放完成进入 ENDED
- **WHEN** 视频播放到末尾
- **THEN** 状态切换到 ENDED

#### Scenario: 播放出错进入 ERROR
- **WHEN** ExoPlayer 发生播放错误（网络异常、URL 过期、解码失败等）
- **THEN** onPlayerError 触发，状态切换到 ERROR
- **THEN** 控制条显示（auto-hide 取消）

#### Scenario: ERROR 恢复
- **WHEN** 调用 recover() 刷新视频 URL 并重新 prepare
- **THEN** 先从 ERROR 切换回 BUFFERING
- **THEN** 重新进入 READY → PLAYING

#### Scenario: player release 回到 IDLE
- **WHEN** PlayerActivity onDestroy 调用 player.release()
- **THEN** onPlaybackStateChanged(STATE_IDLE) 触发，状态切换到 IDLE

### Requirement: 状态同步唯一数据源

PlayerViewModel 的状态 SHALL 仅由 onPlaybackStateChanged 驱动，onIsPlayingChanged 回调 SHOULD NOT 修改 PlayerState。

#### Scenario: onIsPlayingChanged 不覆盖状态
- **WHEN** ExoPlayer 处于 BUFFERING 状态
- **WHEN** onIsPlayingChanged(true) 被回调
- **THEN** PlayerState 保持 BUFFERING，不切换到 PLAYING

### Requirement: 状态日志输出

PlayerViewModel SHALL 在每次状态转换时输出日志，格式为 `PlayerStateMachine: <from> → <to> [reason: <reason>]`。

#### Scenario: 状态转换时输出日志
- **WHEN** 任何合法状态转换发生
- **THEN** Log.d("PlayerStateMachine", "IDLE → BUFFERING [reason: prepare]") 被输出

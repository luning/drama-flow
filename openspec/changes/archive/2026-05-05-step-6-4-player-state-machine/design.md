## Context

Step 6.3 集成了 ExoPlayer 和基本控制条。当前的 PlayerViewModel 虽然定义了 PlayerState 枚举（IDLE/BUFFERING/READY/PLAYING/PAUSED/ERROR/ENDED），但状态转换实现存在三类问题：

1. **回调覆盖不全**：`onPlaybackStateChanged` 未处理 `Player.STATE_IDLE`
2. **状态映射冲突**：`onIsPlayingChanged` 与 `onPlaybackStateChanged` 可独立触发，导致 BUFFERING 态下 `onIsPlayingChanged(true)` 将状态覆盖为 PLAYING
3. **ERROR 无恢复路径**：ERROR 态后无 recovery 方法，播放器卡死

## Goals / Non-Goals

**Goals:**
- 完整实现 PlayerState 七个状态的合法转换
- 消除 onPlaybackStateChanged / onIsPlayingChanged 状态冲突
- 提供 ERROR 恢复路径
- 每次状态转换可观测（日志输出），便于教学演示和调试

**Non-Goals:**
- 不添加新 UI 功能（倍速/全屏/集数切换已在 6.3 完成）
- 不修改后端接口
- 不做进度持久化（在 6.5 完成）

## Decisions

### 1. 状态管理以 ExoPlayer 回调为唯一状态源
- `onPlaybackStateChanged` 作为主状态机驱动，衍生 PLAYING/PAUSED 依赖 `playWhenReady`
- `onIsPlayingChanged` 降级为仅控制播放/暂停图标切换，不再写入 PlayerState
- **原因**：消除两个独立回调间的竞态；`onPlaybackStateChanged` 覆盖完整状态集，是可信源

### 2. ERROR 恢复方法
- 在 PlayerViewModel 暴露 `recover(episodeId: Int)` 方法，调用后端刷新 video-url 后重新 prepare
- 错误从"终态"变为"可恢复态"，符合 ExoPlayer 实际能力（replaceMedia + prepare）
- **原因**：视频签名 URL 过期导致的 401/403 是运行时常态，不应永久卡住

### 3. 状态日志
- 每次状态转换通过 `android.util.Log.d` 输出 tag "PlayerStateMachine"，格式：`IDLE → BUFFERING [reason: prepare]`
- **原因**：教学场景需要肉眼观察状态序列以识别缺陷；正式发布时可移除

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| onPlaybackStateChanged 和 onIsPlayingChanged 时序不确定，降级后仍可能短暂显示错误图标 | 播放/暂停图标直接绑定 player.isPlaying，不依赖状态机 |
| recover() 期间用户操作导致竞态 | 在 BUFFERING 态时禁用操作按钮 |
| 移除 onIsPlayingChanged 的状态逻辑后，暂停时退出 APP 再恢复可能状态漂移 | ViewModel 在 init 时不预设状态，等到第一个 onPlaybackStateChanged 回调再确认 |

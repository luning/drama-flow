## 1. PlayerViewModel 状态机核心修复

- [x] 1.1 在 `onPlaybackStateChanged` 中添加 `Player.STATE_IDLE` 分支映射到 `PlayerState.IDLE`
- [x] 1.2 在 `onPlaybackStateChanged` 中添加 `Player.STATE_READY` 分支，根据 `playWhenReady` 映射到 `PlayerState.PLAYING` 或 `PlayerState.PAUSED`（不再跳过 READY）
- [x] 1.3 简化 `onIsPlayingChanged` 回调：移除设置 PlayerState 的逻辑，仅保留播放/暂停图标切换

## 2. ERROR 恢复

- [x] 2.1 在 `PlayerViewModel` 添加 `recover(episodeId: Int)` 方法，将状态从 ERROR 切换回 BUFFERING
- [x] 2.2 在 `PlayerActivity` 的 `refreshVideoUrl()` 完成后调用 `viewModel.setState(PlayerState.BUFFERING)` 重新进入播放流程

## 3. 状态日志

- [x] 3.1 在 `PlayerViewModel.setState()` 中添加 `Log.d("PlayerStateMachine", "→ [reason: ]")`, 记录每次状态转换

## 4. SPEC.md 更新

- [x] 4.1 在 SPEC.md Player 领域的 AC 中补充状态机转换矩阵验收标准
- [x] 4.2 更新 AC-PLAYER-10 描述，明确覆盖 7 个状态及其合法转换

## 5. 验证

- [x] 5.1 编译 Android 项目，确认无编译错误
- [x] 5.2 安装 APK 到模拟器，手动验证播放/暂停/seek/error 场景的状态表现

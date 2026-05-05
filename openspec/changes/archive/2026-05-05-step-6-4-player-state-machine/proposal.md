## Why

<!-- Explain the motivation for this change. What problem does this solve? Why now? -->

Step 6.4 要求在 ExoPlayer 集成的基础上（6.3）实现播放器状态机。当前 PlayerViewModel 虽已定义 PlayerState 枚举和基本状态字段，但状态转换存在缺陷：IDLE 状态未被回调覆盖、READY 状态被跳过直接映射到 PLAYING/PAUSED、onPlaybackStateChanged 与 onIsPlayingChanged 存在竞态冲突、ERROR 后无恢复路径。这些缺陷会导致 UI 状态与播放器实际状态不同步、缓冲态和错误态被遗漏，需要在进入更复杂的功能（集数切换、进度上报）前完成状态机修复。

## What Changes

<!-- Describe what will change. Be specific about new capabilities, modifications, or removals. -->

1. **PlayerViewModel 状态机完善**：补充 Player.STATE_IDLE 处理，暴露 READY 状态，消除两个回调间的状态冲突
2. **PlayerActivity 状态同步修复**：重构 onPlaybackStateChanged / onIsPlayingChanged / onPlayerError 的逻辑，确保唯一状态源
3. **ERROR 恢复路径**：从 ERROR 状态提供 recovery 方法（重新加载视频）
4. **状态转换日志**：增加状态转换日志，便于调试和教学演示状态机缺陷
5. **SPEC Player 领域 AC 更新**：补充状态机转换图（状态 → 触发事件 → 目标状态）

## Capabilities

### New Capabilities
- `player-state-machine`: 播放器状态机的完整实现，覆盖 IDLE/BUFFERING/READY/PLAYING/PAUSED/ENDED/ERROR 七个状态及合法转换

### Modified Capabilities
<!-- Existing capabilities whose REQUIREMENTS are changing (not just implementation). -->
- Player（SPEC.md 第六节）: 补充状态机转换矩阵作为验收标准，明确每个状态的触发条件和目标转换

## Impact

<!-- Affected code, APIs, dependencies, systems -->

- **Android**: PlayerViewModel.kt 状态管理逻辑重构、PlayerActivity.kt 状态回调修正
- **SPEC**: Player 领域 AC 新增状态机相关验收标准
- **测试**: 新增状态机行为验证（通过模拟 ExoPlayer 回调验证状态转换）

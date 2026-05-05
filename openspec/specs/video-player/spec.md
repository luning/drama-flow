## ADDED Requirements

### Requirement: 视频播放器基础播放

Android 端 SHALL 使用 ExoPlayer (Media3) 实现视频播放功能，支持从指定 URL 播放视频内容。

#### Scenario: 播放器初始化并播放视频
- **WHEN** 用户从详情页点击某集进入播放器
- **THEN** PlayerActivity 启动，ExoPlayer 初始化并开始缓冲播放该集视频

#### Scenario: 播放状态反馈
- **WHEN** 视频处于缓冲状态
- **THEN** 显示 loading 指示器
- **WHEN** 播放出错（网络异常、URL 过期）
- **THEN** 显示 toast 错误提示

### Requirement: 自定义控制条

播放器控制条 SHALL 包含播放/暂停、进度拖动、当前时间/总时长、倍速选择、全屏切换、返回按钮。剧集模式下（有多集）SHALL 包含上/下一集切换按钮。

#### Scenario: 播放/暂停切换
- **WHEN** 用户点击播放按钮
- **THEN** 视频暂停播放，按钮图标切换到播放图标
- **WHEN** 用户再次点击暂停按钮
- **THEN** 视频继续播放，按钮图标切换到暂停图标

#### Scenario: 进度拖动
- **WHEN** 用户拖动进度 seekbar
- **THEN** 视频跳转到对应播放位置
- **WHEN** 拖动过程中
- **THEN** 实时显示当前拖动位置的时间

#### Scenario: 时间显示
- **WHEN** 视频正在播放
- **THEN** 控制条实时显示当前播放时间和视频总时长

#### Scenario: 倍速切换
- **WHEN** 用户点击倍速按钮
- **THEN** 弹出倍速选择列表（0.5x、0.75x、1.0x、1.25x、1.5x、2.0x）
- **WHEN** 用户选择某个倍速
- **THEN** 播放器按该倍速播放

#### Scenario: 全屏切换
- **WHEN** 用户点击全屏按钮
- **THEN** 播放器进入全屏模式（隐藏状态栏，横屏显示）
- **THEN** 全屏后控制条在 3 秒后自动隐藏
- **WHEN** 用户点击视频画面
- **THEN** 控制条重新显示
- **WHEN** 用户再次点击退出全屏按钮
- **THEN** 播放器退出全屏模式（显示状态栏，竖屏显示）
- **THEN** 退出全屏后控制条保持可见

### Requirement: 与详情页导航集成

Android 端 SHALL 支持从 H5 详情页通过 JSBridge 跳转到原生播放器。

#### Scenario: H5 点击播放跳转原生播放器
- **WHEN** 用户在 H5 详情页点击某集播放按钮
- **THEN** H5 通过 `window.DramaFlowBridge.openPlayer(episodeId, dramaId, episodeNumber)` 调用 Android 原生
- **THEN** Android 原生打开 PlayerActivity 并传入对应的剧集参数

### Requirement: 上/下一集导航

剧集模式下（drama_id > 0），播放器 SHALL 提供上/下一集切换按钮，支持用户手动切换剧集。

#### Scenario: 下一集
- **WHEN** 用户点击下一集按钮
- **THEN** 播放器切换到下一集并开始播放
- **WHEN** 用户已在最后一集
- **THEN** 提示"已是最后一集"

#### Scenario: 上一集
- **WHEN** 用户点击上一集按钮
- **THEN** 播放器切换到上一集并开始播放
- **WHEN** 用户已在第一集
- **THEN** 提示"已是第一集"

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

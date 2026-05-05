# Android Playback Resume

## ADDED Requirements

### Requirement: 播放器初始化时获取上次播放位置

Android 端播放器初始化时，通过 GET /api/watch-records/{episode_id} 获取该集的上次播放位置。

#### Scenario: 有播放记录时自动续播
- **WHEN** 播放器完成初始化进入 READY 状态
- **THEN** 自动 Seek 到上次保存的 last_position 位置开始播放

#### Scenario: 无播放记录时从头播放
- **WHEN** 播放器初始化且该集无播放记录
- **THEN** 从 0 开始正常播放

#### Scenario: 续播请求失败不阻塞播放
- **WHEN** 获取上次播放位置的网络请求失败
- **THEN** 从 0 开始正常播放，不显示错误提示

## MODIFIED Requirements

（无）

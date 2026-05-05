# Requirements: DramaFlow — v1.1 播放器增强 + Auth 增强

**Defined:** 2026-05-05
**Core Value:** 用户能流畅地发现和观看短剧，播放进度跨会话保持

## v1.1 Requirements

### 播放器 — Player

- [ ] **PLAYER-01**: 速度选择浮层包含完整 6 档选项（0.5x / 0.75x / 1.0x / 1.25x / 1.5x / 2.0x），缺少的 0.75x 和 1.25x 按钮需添加到 speed_menu 布局和点击绑定 — AC-PLAYER-05
- [ ] **PLAYER-02**: 播放器状态机逐条审查 AC-PLAYER-10~21（12 条），确保所有合法转换被覆盖、状态仅由 `onPlaybackStateChanged` 驱动、倍速不影响状态机 — AC-PLAYER-10~21
- [ ] **PLAYER-03**: `recover()` 方法验证：ERROR 状态下调用 `recover()` 切换到 BUFFERING 后 ExoPlayer 能正确重置并重新播放 — AC-PLAYER-17
- [ ] **PLAYER-04**: player release 后状态回到 IDLE，ViewModel 监听 ExoPlayer 释放事件 — AC-PLAYER-18

### Auth — 认证

- [ ] **AUTH-01**: 在 `ApiClient` 中添加 OkHttp `Authenticator`，当 API 返回 401 时自动拦截 → 读取 Refresh Token → 调用 `/api/auth/refresh` 获取新 Token → 重试原始请求 — AC-USER-11
- [ ] **AUTH-02**: Refresh Token 失效（refresh 也返回 401）时，清除本地会话并静默跳转登录页，不产生白屏或崩溃 — AC-USER-12
- [ ] **AUTH-03**: 未勾选"记住我"时，Token 仅存内存（AuthRepository.currentToken），App 退出后需重新登录 — AC-USER-10 验证

### 测试 — Tests

- [ ] **TEST-01**: 后端 pytest 覆盖 auth refresh 流程（正常刷新、refresh token 过期、无效 token 场景）
- [ ] **TEST-02**: Android 端播放器 ViewModel 单元测试（状态机转换、速度切换、recover 路径）

## v2 Requirements

(无)

## Out of Scope

| Feature | Reason |
|---------|--------|
| 画质切换 | 可选进阶，非核心体验 |
| 首页 A/B 测试开关 | 可选进阶 |
| 播放进度跨设备同步 | 可选进阶 |
| 协同过滤/ALS 推荐 | 基于 WatchRecord 的简单排序已满足需求 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLAYER-01 | Phase 2 | Complete |
| PLAYER-02 | Phase 2 | Complete |
| PLAYER-03 | Phase 2 | Complete |
| PLAYER-04 | Phase 2 | Complete |
| AUTH-01 | Phase 3 | Complete |
| AUTH-02 | Phase 3 | Complete |
| AUTH-03 | Phase 3 | Complete |
| TEST-01 | Phase 4 | Pending |
| TEST-02 | Phase 4 | Pending |

**Coverage:**
- v1.1 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0

---
*Requirements defined: 2026-05-05*

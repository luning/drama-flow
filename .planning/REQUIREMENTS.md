# Requirements: DramaFlow

**Defined:** 2026-05-05
**Core Value:** 用户能流畅地发现和观看短剧，播放进度跨会话保持

## v1 Requirements

### 首页推荐改版

- [ ] **REC-01**: 已登录用户访问首页时，剧集列表基于观看历史进行个性化排序（同类优先）— AC-DRAMA-07
- [ ] **REC-02**: 用户已看完的剧集在推荐列表中权重降低，避免重复推荐 — AC-DRAMA-08
- [ ] **REC-03**: 未登录用户不受个性化推荐影响，按默认排序展示全量剧集 — AC-DRAMA-09
- [ ] **REC-04**: 首页推荐逻辑包含适当的降级处理（当观看记录不足时回退到默认排序）— 稳健性

## Existing (Already Implemented)

以下需求已在之前迭代中实现：

### 用户认证
- **AUTH-01**: 用户可以使用邮箱+密码注册新账号
- **AUTH-02**: 用户可以使用邮箱+密码登录，获取 JWT Token
- **AUTH-03**: 用户可以登出，登出后 Token 失效
- **AUTH-04**: Access Token 过期时自动使用 Refresh Token 续期
- **AUTH-05**: 登录勾选"记住我"后 Token 持久化存入 EncryptedSharedPreferences
- **AUTH-06**: Refresh Token 失效后静默跳转登录页

### 首页浏览
- **HOME-01**: 首页展示 Banner 轮播
- **HOME-02**: 首页支持分类 Tab 切换筛选
- **HOME-03**: 首页剧集列表支持分页加载
- **HOME-04**: 已登录用户首页展示个性化推荐排序

### 剧集详情
- **DETL-01**: 详情页展示剧集信息（标题/描述/封面/分类/评分/集数）
- **DETL-02**: 详情页展示集数列表，支持点击播放

### 视频播放
- **PLAY-01**: 点击播放进入 ExoPlayer 播放器
- **PLAY-02**: 支持播放/暂停、SeekBar 进度控制
- **PLAY-03**: 支持倍速播放（0.5x~2.0x）
- **PLAY-04**: 支持横屏全屏模式
- **PLAY-05**: 播放器状态机覆盖 7 个状态
- **PLAY-06**: 非最后一集播放结束后自动连播

### 播放进度
- **WATC-01**: 播放进度每 15s 自动上报
- **WATC-02**: 再次播放时从上次位置续播
- **WATC-03**: 继续观看列表不包含已完成的剧集
- **WATC-04**: 同一用户重复上报同一集只保留最新记录

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
| REC-01 | Phase 1 | Pending |
| REC-02 | Phase 1 | Pending |
| REC-03 | Phase 1 | Pending |
| REC-04 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 4 total
- Mapped to phases: 4
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-05*
*Last updated: 2026-05-05 after initial definition*

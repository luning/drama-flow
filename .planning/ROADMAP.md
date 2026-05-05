# Roadmap: DramaFlow

## Milestones

- ✅ **v1.0 首页推荐改版验收** — Phase 1 (shipped 2026-05-05)
- 🚧 **v1.1 播放器增强 + Auth 增强** — Phases 2-4 (in progress)

## Phases

<details>
<summary>✅ v1.0 首页推荐改版验收 (Phase 1) — SHIPPED 2026-05-05</summary>

- [x] Phase 1: Homepage Recommendation Validation (2/2 plans) — completed 2026-05-05

</details>

### 🚧 v1.1 播放器增强 + Auth 增强 (In Progress)

**Milestone Goal:** 对照 SPEC 验收标准审查并完善播放器和认证功能的现有实现

- [ ] **Phase 2: Player State Machine Audit** - Verify and fix ExoPlayer state machine compliance against SPEC AC-PLAYER-10~21
- [ ] **Phase 3: Auth Token Refresh Enhancement** - Implement OkHttp Authenticator auto-refresh and verify remember-me behavior
- [ ] **Phase 4: Test Coverage** - Add pytest and unit tests covering auth refresh and player state machine

## Phase Details

### Phase 2: Player State Machine Audit
**Goal**: ExoPlayer state machine fully complies with SPEC AC-PLAYER-10~21
**Depends on**: Phase 1
**Requirements**: PLAYER-01, PLAYER-02, PLAYER-03, PLAYER-04
**Success Criteria** (what must be TRUE):
  1. Speed menu shows all 6 speed options (0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x) and each triggers correct playback speed change
  2. Player state machine transitions only via `onPlaybackStateChanged` and all 12 AC-PLAYER-10~21 transitions are correctly implemented
  3. Calling `recover()` in ERROR state transitions to BUFFERING and resumes playback normally
  4. Player release causes ViewModel state to reset to IDLE
**Plans**: 2 plans
**UI hint**: yes

**Plan list:**
- [x] `02-01-PLAN.md` -- Add 0.75x/1.25x speed buttons, refactor click handler to id-based binding (PLAYER-01)
- [x] `02-02-PLAN.md` -- Audit AC-PLAYER-10~21 transitions, fix recover() ExoPlayer reset, add IDLE on release (PLAYER-02/03/04)

### Phase 3: Auth Token Refresh Enhancement
**Goal**: Auth system automatically refreshes expired tokens and handles refresh failure gracefully
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03
**Success Criteria** (what must be TRUE):
  1. When API returns 401, OkHttp Authenticator intercepts the response, reads Refresh Token, calls `/api/auth/refresh`, and retries the original request with the new token
  2. When Refresh Token is also expired (refresh returns 401), local session is cleared and user is silently redirected to login page without crash or white screen
  3. When "remember me" is unchecked, Token exists only in memory (AuthRepository.currentToken) and is lost on app exit
**Plans**: 2 plans
**UI hint**: no

**Plan list:**
- [x] `03-01-PLAN.md` -- Create TokenProvider, fix remember-me conditional persistence, update JSBridge (AUTH-03)
- [x] `03-02-PLAN.md` -- Implement OkHttp Authenticator for auto-refresh + session expiry redirect (AUTH-01, AUTH-02)

### Phase 4: Test Coverage
**Goal**: Auth refresh and player state machine have automated test coverage
**Depends on**: Phase 2, Phase 3
**Requirements**: TEST-01, TEST-02
**Success Criteria** (what must be TRUE):
  1. Backend pytest covers auth refresh flow: normal refresh, refresh token expired, invalid token -- all scenarios pass
  2. Android ViewModel unit tests cover: state machine transitions, speed switching, recover() path -- all tests pass
**Plans**: 2 plans

**Plan list:**
- [ ] `04-01-PLAN.md` -- Backend pytest for auth refresh flow (normal, expired, invalid) -- TEST-01
- [ ] `04-02-PLAN.md` -- Android ViewModel unit tests (state machine, speed, recover) -- TEST-02

## Progress

**Execution Order:**
Phases execute in numeric order: 2 -> 3 -> 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|---------------|--------|-----------|
| 1. Homepage Recommendation Validation | v1.0 | 2/2 | Complete | 2026-05-05 |
| 2. Player State Machine Audit | v1.1 | 2/2 | Complete | 2026-05-05 |
| 3. Auth Token Refresh Enhancement | v1.1 | 2/2 | Complete | 2026-05-05 |
| 4. Test Coverage | v1.1 | 0/2 | Planned | - |

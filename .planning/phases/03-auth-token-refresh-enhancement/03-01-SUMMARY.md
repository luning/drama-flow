---
phase: 03-auth-token-refresh-enhancement
plan: 01
subsystem: auth
tags: token, remember-me, jwt, shared-preferences

requires:
  - phase: 01-foundation
    provides: auth infrastructure (login, register, session restore)
provides:
  - TokenProvider singleton with memory-first token resolution
  - Conditional token persistence based on remember-me flag
  - JSBridge token reads via TokenProvider (memory-first)
affects: Phase 03-02 (OkHttp Authenticator), Phase 4 (test coverage)

tech-stack:
  added: []
  patterns:
    - "TokenProvider: memory-first token resolution with @Volatile fields"
    - "Conditional persistence: persist flag controls writes to EncryptedSharedPreferences"

key-files:
  created: []
  modified:
    - android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt
    - android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt
    - android/app/src/main/java/com/dramaflow/common/JSBridge.kt

key-decisions:
  - "TokenProvider lives in ApiClient.kt (same file, same package) — co-located with authInterceptor"
  - "PreferencesManager constructor parameter pattern retained — TokenProvider methods take explicit prefs param"
  - "tryRestoreSession() uses persist=true since it only runs when isRemembered=true"

requirements-completed: [AUTH-03]

duration: 12min
completed: 2026-05-05
---

# Phase 03 Plan 01: TokenProvider + Remember-Me Conditional Persistence Summary

**Memory-first token resolution via TokenProvider singleton with @Volatile fields; login() persists tokens only when remember=true; JSBridge reads from TokenProvider**

## Performance

- **Duration:** 12 min
- **Started:** 2026-05-05T20:00:00Z
- **Completed:** 2026-05-05T20:12:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created `TokenProvider` singleton with `@Volatile` memory fields for thread-safe token access
- `getAccessToken()`/`getRefreshToken()`: in-memory first, fall back to EncryptedSharedPreferences
- `setTokens()`: conditional persistence — writes to prefs only when `persist=true`
- `AuthRepository.login()` now calls `TokenProvider.setTokens(persist=remember)` instead of always persisting
- `AuthRepository.logout()` clears both memory tokens (TokenProvider) and persisted tokens (prefs)
- `AuthRepository.tryRestoreSession()` sets in-memory tokens after successful refresh
- `authInterceptor` reads via `TokenProvider.getAccessToken(prefs)` — memory-first
- `JSBridge.getAccessToken()`/`getRefreshToken()` read via TokenProvider — fixes H5 token access when remember=false

## Task Commits

Each task was committed atomically:

1. **Task 1: Add TokenProvider singleton and update authInterceptor** - `7937ec0` (feat)
2. **Task 2: Add remember-me conditional persistence in AuthRepository** - `ad5ecb3` (feat)
3. **Task 3: Update JSBridge to use TokenProvider for token reads** - `e26b126` (feat)

## Files Modified

- `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt` — Added TokenProvider object, updated authInterceptor
- `android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt` — login/logout/tryRestoreSession use TokenProvider
- `android/app/src/main/java/com/dramaflow/common/JSBridge.kt` — getAccessToken/getRefreshToken use TokenProvider

## Decisions Made

- TokenProvider placed in ApiClient.kt (same file, co-located with authInterceptor) rather than a separate file — reduces file count and keeps token-related code together
- TokenProvider methods take explicit `prefs: PreferencesManager` parameter rather than creating their own instance — consistent with existing code pattern
- `tryRestoreSession()` passes `persist=true` since it only runs when `prefs.isRemembered == true` — tokens should survive app restart after session restore

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Self-Check: PASSED

- ✅ `object TokenProvider` in ApiClient.kt
- ✅ `@Volatile` on both memoryAccessToken and memoryRefreshToken
- ✅ `getAccessToken`/`getRefreshToken`/`setTokens`/`clear` methods
- ✅ authInterceptor uses `TokenProvider.getAccessToken(prefs)`
- ✅ login() uses `TokenProvider.setTokens(persist=remember)`
- ✅ logout() calls `TokenProvider.clear()` before `prefs.clearSession()`
- ✅ tryRestoreSession() calls `TokenProvider.setTokens(persist=true)`
- ✅ JSBridge uses `TokenProvider.getAccessToken`/`getRefreshToken`
- ✅ No remaining direct `prefs.accessToken` reads in authInterceptor or JSBridge

## Next Phase Readiness

Ready for Plan 03-02: OkHttp Authenticator with auto-refresh and session expiry redirect (AUTH-01, AUTH-02)

---
*Phase: 03-auth-token-refresh-enhancement*
*Completed: 2026-05-05*

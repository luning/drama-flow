---
phase: 03-auth-token-refresh-enhancement
plan: 02
subsystem: auth
tags: okhttp, authenticator, token-refresh, session, navigation

requires:
  - phase: 03-01
    provides: TokenProvider singleton with memory-first token resolution
provides:
  - OkHttp Authenticator for automatic 401 token refresh
  - SessionManager singleton for session expiry signaling
  - Global nav action for session-expired redirect to login
affects: Phase 4 (test coverage)

tech-stack:
  added: []
  patterns:
    - "OkHttp Authenticator: synchronous token refresh with synchronized thundering-herd guard"
    - "SessionManager: SharedFlow-based cross-component event bus for session expiry"

key-files:
  created: []
  modified:
    - android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt
    - android/app/src/main/java/com/dramaflow/MainActivity.kt
    - android/app/src/main/res/navigation/nav_graph.xml

key-decisions:
  - "Authenticator uses org.json.JSONObject instead of Moshi for response parsing — avoids Moshi adapter config for synchronous calls"
  - "Authenticator builds a minimal fresh OkHttpClient for the refresh call (no interceptors/authenticator) to prevent recursion"
  - "synchronized(lock) with re-check pattern prevents thundering herd on concurrent 401s"
  - "auth/refresh endpoint excluded via path check guard"

requirements-completed: [AUTH-01, AUTH-02]

duration: 10min
completed: 2026-05-05
---

# Phase 03 Plan 02: OkHttp Authenticator + Session Expiry Redirect Summary

**OkHttp Authenticator for automatic 401 token refresh with synchronized thundering-herd protection; SessionManager SharedFlow for session expiry signaling; global nav action clears back stack on redirect**

## Performance

- **Duration:** 10 min
- **Started:** 2026-05-05T20:12:00Z
- **Completed:** 2026-05-05T20:22:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- OkHttp `Authenticator` intercepts 401 responses and calls `/api/auth/refresh` synchronously
- Three guards prevent edge cases: (1) auth/refresh path exclusion prevents recursion, (2) Bearer header check ensures only auth-protected requests trigger refresh, (3) `synchronized(lock)` with re-check prevents thundering herd on concurrent 401s
- On refresh success: new tokens stored via `TokenProvider.setTokens(persist=true)`, original request retried with new access token
- On refresh failure or network error: `TokenProvider.clear()` + `prefs.clearSession()` + `SessionManager.notifySessionExpired()`
- `SessionManager` singleton with `MutableSharedFlow<Unit>` for cross-component session expiry events
- Global nav action `action_global_to_login` with `popUpTo="@id/nav_graph"` + `popUpToInclusive="true"` clears entire back stack
- `MainActivity` lifecycle observer collects `sessionExpired` events and navigates to login fragment

## Task Commits

Each task was committed atomically:

1. **Task 1: Add OkHttp Authenticator with token refresh and SessionManager** - `3a98ecb` (feat)
2. **Task 2: Add session expiry redirect with global nav action** - `7bcd2e9` (feat)

## Files Modified

- `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt` — Added SessionManager object, Authenticator with refresh logic, registered on OkHttpClient
- `android/app/src/main/java/com/dramaflow/MainActivity.kt` — Added navController property, sessionExpired observer
- `android/app/src/main/res/navigation/nav_graph.xml` — Added global action `action_global_to_login` with back stack clear

## Decisions Made

- Used `org.json.JSONObject` for Authenticator response parsing instead of Moshi — avoids adapter configuration complexity for the synchronous call path
- Built a minimal fresh `OkHttpClient` inside the Authenticator for the refresh call (no interceptors, no Authenticator) — prevents infinite recursion if the refresh call itself triggers Authenticator logic
- `synchronized(lock)` with re-check pattern: after acquiring the lock, re-reads the refresh token. If another thread already refreshed it, retries with the new token instead of making a duplicate refresh call
- `auth/refresh` path exclusion as first guard (before any token reads) — minimal overhead for the most common non-retryable endpoint

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Self-Check: PASSED

- ✅ `SessionManager` object defined in ApiClient.kt with `MutableSharedFlow<Unit>` + `notifySessionExpired()`
- ✅ `authenticator` property in ApiClient with synchronized refresh logic
- ✅ `auth/refresh` endpoint excluded from Authenticator handling
- ✅ On refresh failure: `TokenProvider.clear()` + `prefs.clearSession()` + `SessionManager.notifySessionExpired()`
- ✅ `.authenticator(authenticator)` registered on OkHttpClient builder
- ✅ `action_global_to_login` in nav_graph.xml with `popUpTo="@id/nav_graph"` + `popUpToInclusive="true"`
- ✅ MainActivity observes `SessionManager.sessionExpired` and navigates via `R.id.action_global_to_login`
- ✅ `navController` as class property (not local val)

## Next Phase Readiness

Phase 3 complete — both AUTH-01 (auto-refresh) and AUTH-02 (session expiry redirect) implemented. Ready for Phase 4: test coverage.

---
*Phase: 03-auth-token-refresh-enhancement*
*Completed: 2026-05-05*

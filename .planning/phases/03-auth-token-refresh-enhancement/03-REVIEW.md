---
phase: 03-auth-token-refresh-enhancement
reviewed: 2026-05-05T21:55:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt
  - android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt
  - android/app/src/main/java/com/dramaflow/common/JSBridge.kt
  - android/app/src/main/java/com/dramaflow/MainActivity.kt
  - android/app/src/main/res/navigation/nav_graph.xml
findings:
  critical: 3
  warning: 7
  info: 3
  total: 13
status: issues_found
---

# Phase 3: Auth Token Refresh Enhancement — Code Review Report

**Reviewed:** 2026-05-05T21:55:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed 5 Android native layer files implementing automatic 401 token refresh via OkHttp Authenticator, conditional token persistence based on remember-me flag, and session expiry redirect. Found 3 blocker-level bugs, 7 warnings, and 3 info items.

The core issues fall into two categories: (1) the Authenticator's refresh logic violates the remember-me contract by unconditionally persisting tokens on refresh, and (2) transient network failures during refresh destroy the user session, forcing an unnecessary login. Additionally, the token state between `AuthRepository.currentToken` and `TokenProvider` is unsynchronized, creating a window where stale tokens can be returned.

---

## Critical Issues

### CR-01: Authenticator unconditionally persists tokens on refresh, breaking remember-me semantics

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:177-182`
**Issue:** When the OkHttp Authenticator successfully refreshes tokens on a 401, it calls `TokenProvider.setTokens(..., persist = true, ...)` unconditionally (line 180). This means even when the user logged in with `remember = false`, after the first automatic 401+refresh cycle, the tokens get written to `EncryptedSharedPreferences`. On the next cold app start, `tryRestoreSession()` will not run (it checks `prefs.isRemembered` which is still `false`), but `JSBridge.getAccessToken()` and `JSBridge.getRefreshToken()` call `TokenProvider.getAccessToken(prefs)` / `TokenProvider.getRefreshToken(prefs)` which read from `prefs` when memory is null — so stale persisted tokens can be leaked to the WebView. More importantly, the user's explicit "don't remember me" preference is silently overridden.

**Fix:** The Authenticator does not know whether the user chose "remember me" — that information is in `prefs.isRemembered`. Read the flag before persisting:

```kotlin
// In ApiClient.kt authenticator, replace line 180-181:
val shouldPersist = prefs.isRemembered
TokenProvider.setTokens(
    access = newAccessToken,
    refresh = newRefreshToken,
    persist = shouldPersist,
    prefs = prefs
)
```

Alternatively, remove `persist` from `setTokens` entirely and have the setter decide based on `prefs.isRemembered`.

---

### CR-02: Session destroyed on transient network error during token refresh

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:194-199`
**Issue:** The catch block catches all `Exception` types (including `SocketTimeoutException`, `UnknownHostException`, `IOException`) and immediately calls `TokenProvider.clear()`, `prefs.clearSession()`, and `SessionManager.notifySessionExpired()`. This means a temporary network glitch (e.g., flaky cellular connection, DNS timeout) destroys the user's session and forces them to log in again. Valid credentials are discarded due to a transient infrastructure issue.

**Fix:** On network error (not authentication failure), the Authenticator should return `null` (give up on retrying this particular request) but NOT clear the session. Only clear on a confirmed authentication failure (e.g., HTTP 401/403 from the refresh endpoint):

```kotlin
// Replace the catch block with:
} catch (e: Exception) {
    // Network/IO error — do NOT destroy session, just give up on this request
    return@Authenticator null
}
```

The session-clearing logic should remain only in the `else` branch (non-successful HTTP response from refresh endpoint), where the server has definitively rejected the refresh token.

---

### CR-03: Response body resource leak on failed refresh

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:168-192`
**Issue:** When `refreshResponse.isSuccessful` is `false` (lines 187-192), the response body is never consumed or closed. OkHttp requires the response body to be closed to return the connection to the connection pool. On repeated refresh failures under load, this leaks connections.

**Fix:** Consume the body in the failure path:

```kotlin
} else {
    // Consume body to release connection
    refreshResponse.close()
    // Failure: clear session, signal UI, give up
    TokenProvider.clear()
    prefs.clearSession()
    SessionManager.notifySessionExpired()
    return@Authenticator null
}
```

---

## Warnings

### WR-01: Lock held across blocking network call — thread contention risk

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:139-201`
**Issue:** The `synchronized(lock)` block beginning at line 139 is held during the entire HTTP request to the refresh endpoint (lines 162-168). With a 15-second timeout, if multiple threads enter the Authenticator concurrently with 401s, they all block on `synchronized` until the first thread's network call completes. OkHttp's dispatcher thread pool can be starved under high concurrency.

**Fix:** Only synchronize the critical sections (re-check if another thread refreshed, and store the result). Move the network call outside the lock:

```kotlin
synchronized(lock) {
    val currentRefreshToken = TokenProvider.getRefreshToken(prefs)
    if (currentRefreshToken != originalRefreshToken) {
        val newAccessToken = TokenProvider.getAccessToken(prefs) ?: return@Authenticator null
        return@Authenticator response.request.newBuilder()
            .header("Authorization", "Bearer $newAccessToken")
            .build()
    }
    // Capture token value to use for refresh, then release lock
}
// Do network call OUTSIDE lock
val refreshResponse = refreshClient.newCall(refreshRequest).execute()
// Re-acquire lock to store result
synchronized(lock) {
    // ...store result...
}
```

---

### WR-02: `AuthRepository.currentToken` becomes stale after Authenticator refresh

**File:** `android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt:83`
**Issue:** `AuthRepository` maintains a `currentToken` field (line 16) that is only updated in `login()` (line 42) and `tryRestoreSession()` (line 73). When the OkHttp Authenticator (in `ApiClient.kt`) refreshes tokens on a 401, `TokenProvider` is updated but `AuthRepository.currentToken` is not. The `getAccessToken()` method (line 83) returns `currentToken?.access_token` first, which is now stale — it returns the old, potentially expired access token.

**Fix:** Check `TokenProvider` before `currentToken`:

```kotlin
fun getAccessToken(): String? {
    val prefs = PreferencesManager(DramaFlowApp.instance)
    return TokenProvider.getAccessToken(prefs) ?: currentToken?.access_token
}
```

Or better, remove `currentToken` entirely since `TokenProvider` is the single source of truth.

---

### WR-03: Unsafe URL concatenation — missing trailing slash in `API_BASE_URL` produces malformed URL

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:158`
**Issue:** The refresh URL is constructed via string interpolation: `"${BuildConfig.API_BASE_URL}auth/refresh"`. If `API_BASE_URL` does not end with a `/`, the resulting URL is malformed (e.g., `https://api.example.comapi/auth/refresh`). The Retrofit builder at line 219 uses `baseUrl()` which enforces a trailing slash via OkHttp's `HttpUrl`, but the raw Authenticator bypasses Retrofit and constructs the URL manually.

**Fix:** Use OkHttp's `HttpUrl` to resolve the path safely, or ensure a trailing slash:

```kotlin
val baseUrl = BuildConfig.API_BASE_URL
val normalizedBase = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
val refreshUrl = "${normalizedBase}auth/refresh"
```

Or better, construct via `HttpUrl`:

```kotlin
val refreshUrl = okHttpClient.newBuilder()
    .build()
    .let { /* or use HttpUrl.parse */ }
```

---

### WR-04: Null assertion (`!!`) on response body causes NPE on success-with-null-body

**File:** `android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt:41,66`
**Issue:** Both `login()` (line 41) and `tryRestoreSession()` (line 66) use `resp.body()!!` to force-unwrap the response body. If the server returns HTTP 200 with a `null` body (which is technically allowed by Retrofit), the app crashes with a `NullPointerException`. This is especially dangerous for `tryRestoreSession()` which runs during app startup.

**Fix:** Use `?: return` or `?: throw` instead:

```kotlin
// login(), line 41:
val token = resp.body() ?: throw Exception("Login succeeded but response body was empty")

// tryRestoreSession(), line 66:
val token = resp.body() ?: return null
```

---

### WR-05: Refresh token exposed to WebView JavaScript

**File:** `android/app/src/main/java/com/dramaflow/common/JSBridge.kt:53-56`
**Issue:** The `getRefreshToken()` method on `JSBridge` exposes the long-lived refresh token to JavaScript running in the WebView via `window.DramaFlowBridge.getRefreshToken()`. If any XSS vulnerability exists in the H5 layer (Vue3), an attacker can exfiltrate the refresh token and generate new access tokens indefinitely. The project's CLAUDE.md mandates `EncryptedSharedPreferences` for token storage, but this pattern makes the token accessible outside the secure storage boundary.

**Fix:** Either (a) remove `getRefreshToken()` from JSBridge if the H5 does not need it directly, or (b) if the H5 needs refresh capability, expose a method that calls the refresh endpoint on Android's side (using OkHttp) and returns only the new access token, never the raw refresh token:

```kotlin
@JavascriptInterface
suspend fun requestAccessToken(): String {
    // Call refresh endpoint on Android side
    // Return only new access_token
}
```

---

### WR-06: `isRemembered` flag set after token persistence creates inconsistent state on crash

**File:** `android/app/src/main/java/com/dramaflow/data/repository/AuthRepository.kt:45-53`
**Issue:** In `login()`, tokens are persisted at line 45-50, then `prefs.isRemembered = true` is set at line 52. If the app crashes between these two operations (lines 50-52), the tokens are stored in `EncryptedSharedPreferences` but `isRemembered` is `false`. On the next cold start, `tryRestoreSession()` checks `isRemembered` first (line 59) and returns `null`, so the persisted tokens are never used. The user loses their session despite having valid persisted tokens.

**Fix:** Set `isRemembered` before persisting tokens, or persist both atomically via a single `SharedPreferences.edit()` commit:

```kotlin
if (remember) {
    // Set the flag FIRST, then persist tokens
    prefs.isRemembered = true
}
TokenProvider.setTokens(
    access = token.access_token,
    refresh = token.refresh_token,
    persist = remember,
    prefs = prefs
)
```

---

### WR-07: Unchecked `findFragmentById` cast can crash on startup

**File:** `android/app/src/main/java/com/dramaflow/MainActivity.kt:23-24`
**Issue:** `supportFragmentManager.findFragmentById(R.id.nav_host_fragment)` returns a nullable `Fragment?`. The forced `as NavHostFragment` cast will throw a `ClassCastException` (or NPE) if the fragment is not present or of a different type. While unlikely in normal operation, any layout misconfiguration makes this a startup crash.

**Fix:** Use a safe cast with error handling:

```kotlin
val navHost = supportFragmentManager
    .findFragmentById(R.id.nav_host_fragment) as? NavHostFragment
    ?: throw IllegalStateException("nav_host_fragment not found or wrong type")
navController = navHost.navController
```

---

## Info

### IN-01: Session expiry signal lost during lifecycle transitions

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:30` and `MainActivity.kt:29-34`
**Issue:** `SessionManager.sessionExpired` is a `SharedFlow` with `replay=0` and `extraBufferCapacity=1`. If the session expires before `MainActivity`'s `lifecycleScope.launch` in `onCreate()` has started collecting, the signal is dropped (never buffered because flow has no subscribers). The clearing of `TokenProvider` and `prefs` still happens, so subsequent API calls will fail, but the UI will not navigate to the login screen until the user triggers an action that requires auth.

**Fix:** Use `replay = 1` so the session-expired event survives Activity recreation:

```kotlin
private val _sessionExpired = MutableSharedFlow<Unit>(replay = 1, extraBufferCapacity = 1)
```

---

### IN-02: Old tokens linger in prefs when logging in with `remember=false`

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:60-67` and `AuthRepository.kt:44-53`
**Issue:** When `login()` is called with `remember=false`, `TokenProvider.setTokens()` sets memory tokens but does NOT clear old persisted tokens from `EncryptedSharedPreferences`. While `tryRestoreSession()` respects `isRemembered=false` and won't restore them, direct readers like `JSBridge.getAccessToken()`/`getRefreshToken()` will return stale tokens because they fall back to `prefs.accessToken` when memory is null.

**Fix:** In `TokenProvider.setTokens()`, when `persist=false`, clear any existing persisted tokens:

```kotlin
fun setTokens(access: String, refresh: String, persist: Boolean, prefs: PreferencesManager) {
    memoryAccessToken = access
    memoryRefreshToken = refresh
    if (persist) {
        prefs.accessToken = access
        prefs.refreshToken = refresh
    } else {
        prefs.clearSession()  // or just remove access/refresh tokens
    }
}
```

---

### IN-03: Duplicate refresh endpoint definition

**File:** `android/app/src/main/java/com/dramaflow/data/remote/ApiClient.kt:153-168` vs `AuthApi.kt:17-18`
**Issue:** The OkHttp Authenticator defines the refresh request inline (URL, body construction, response parsing) rather than reusing `AuthApi.refresh()`. This duplicates knowledge of the refresh endpoint contract in two places. If the endpoint changes (URL, request body field, response structure), both locations must be updated in sync.

**Fix:** The Authenticator could use a lazily-created Retrofit instance specifically for the refresh call, reusing `AuthApi.refresh()`:

```kotlin
private val refreshApi: AuthApi by lazy {
    Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .client(OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build())
        .addConverterFactory(MoshiConverterFactory.create(moshi))
        .build()
        .create(AuthApi::class.java)
}
```

---

_Reviewed: 2026-05-05T21:55:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

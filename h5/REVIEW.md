---
phase: h5-unified-frontend
reviewed: 2026-06-25T00:00:00Z
depth: deep
files_reviewed: 26
files_reviewed_list:
  - h5/src/App.vue
  - h5/src/main.ts
  - h5/src/router/index.ts
  - h5/src/shims-jsbridge.d.ts
  - h5/src/api/auth.ts
  - h5/src/api/client.ts
  - h5/src/api/dramas.ts
  - h5/src/api/episodes.ts
  - h5/src/api/watchRecord.ts
  - h5/src/stores/auth.ts
  - h5/src/stores/drama.ts
  - h5/src/stores/home.ts
  - h5/src/stores/watchRecord.ts
  - h5/src/components/Banner.vue
  - h5/src/components/BannerCarousel.vue
  - h5/src/components/CategoryTabs.vue
  - h5/src/components/ContinueWatching.vue
  - h5/src/components/DramaCard.vue
  - h5/src/components/EpisodeList.vue
  - h5/src/components/NavBar.vue
  - h5/src/components/VideoPlayer.vue
  - h5/src/pages/Home.vue
  - h5/src/pages/Detail.vue
  - h5/src/pages/Login.vue
  - h5/src/pages/Register.vue
  - h5/src/pages/Player.vue
  - h5/src/pages/History.vue
findings:
  critical: 7
  warning: 9
  info: 6
  total: 22
status: issues_found
---

# H5 Unified Frontend: Code Review Report

**Reviewed:** 2026-06-25
**Depth:** deep
**Files Reviewed:** 26
**Status:** issues_found

## Summary

The H5 codebase is a Vue 3 + TypeScript + Pinia app intended to serve both Android WebView (token via JSBridge, native player) and browser users (full auth flow, H5 VideoPlayer). The dual-path design is conceptually sound, but several correctness bugs, security gaps, and design problems exist. The most severe issues are: credentials logged to console in production, an open redirect vulnerability in the auth guard, the `loading` state not being set during the WebView path in `Player.vue` (leaving the page permanently showing the spinner), broken progress calculation in `ContinueWatching.vue`, and the orphaned `Banner.vue` component that duplicates `BannerCarousel.vue`.

---

## Critical Issues

### CR-01: Access token and partial token value logged to console in production

**File:** `h5/src/api/client.ts:13-14`, `h5/src/main.ts:21`

**Issue:** Every outgoing HTTP request logs the first 10 characters of the Bearer token to the browser console. `main.ts` does the same at boot. These logs appear in production builds and may be visible in Android WebView's remote debugging interface. Any developer or QA with DevTools access can harvest partial tokens. Additionally the console output in `client.ts` reveals the full URL and method for every API call.

**Fix:**
```typescript
// client.ts — remove or guard with env flag
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // only log in dev
    if (import.meta.env.DEV) {
      console.log(`[client.ts] ${config.method?.toUpperCase()} ${config.url}`)
    }
  }
  return config
})

// main.ts — remove the token log line entirely
const synced = auth.syncTokenFromNative()
if (import.meta.env.DEV) {
  console.log(`[main.ts] syncTokenFromNative=${synced}`)
}
```

---

### CR-02: Open redirect vulnerability in auth guard

**File:** `h5/src/router/index.ts:20`

**Issue:** The router guard stores `to.fullPath` in the `redirect` query parameter and `Login.vue` unconditionally redirects to it after login. An attacker can craft a link such as `/#/login?redirect=%2F%2Fevil.com%2Fphish` (or any path beginning with `//`). When hash routing is involved the `//` scheme-relative URL will redirect the user off-site after authentication.

**Fix:**
```typescript
// Login.vue — validate redirect before using it
const redirect = route.query.redirect as string | undefined
const safe = redirect && redirect.startsWith('/') && !redirect.startsWith('//')
  ? redirect
  : '/'
router.push(safe)
```

---

### CR-03: Player.vue — WebView path never sets `loading = false`, page stays in loading state forever

**File:** `h5/src/pages/Player.vue:54-63`

**Issue:** When `window.DramaFlowBridge` is detected, the code fetches episode detail, calls `openPlayer()`, then calls `router.back()`. However `loading` starts as `true` and is only set to `false` inside the `finally` block of the browser path (lines 81-83). The WebView path returns early before that `finally` block. If `router.back()` has no history (e.g. user navigates directly to a player URL), the page remains visible with the "加载中..." spinner indefinitely. Even when `router.back()` succeeds, the `loading` spinner is shown during the async `episodeApi.detail()` fetch — any delay makes the UI look broken.

**Fix:**
```typescript
onMounted(async () => {
  if (window.DramaFlowBridge) {
    try {
      const { data: ep } = await episodeApi.detail(episodeId)
      window.DramaFlowBridge.openPlayer(episodeId, dramaId, ep.episode_number)
    } catch (e) {
      console.error('openPlayer failed', e)
    } finally {
      loading.value = false  // <-- add this
    }
    router.back()
    return
  }
  // ... browser path unchanged
})
```

---

### CR-04: `tryRestoreSession` calls `refreshToken` with access_token present but sends refresh_token — wrong token used as gate condition

**File:** `h5/src/stores/auth.ts:56-68`

**Issue:** `tryRestoreSession` checks `if (token)` where `token` is the `access_token`. It then passes `localStorage.getItem('refresh_token') || ''` to `refreshToken()`. When the access token exists but the refresh token does not (e.g. cleared by another tab, or was never stored), the function calls the API with an empty string as the refresh token. The server will reject this, the `catch` block will call `logout()` which removes the valid access token, and the user is silently logged out on every app start even though their session may still be valid.

**Fix:**
```typescript
async function tryRestoreSession() {
  const refreshTkn = localStorage.getItem('refresh_token')
  if (!refreshTkn) return  // nothing to restore
  try {
    const resp = await refreshToken(refreshTkn)
    const { access_token, refresh_token: newRefresh, user: userData } = resp.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', newRefresh)
    user.value = userData
    isLoggedIn.value = true
  } catch {
    logout()
  }
}
```

---

### CR-05: `ContinueWatching.vue` — progress bar width calculation is wrong, always ≥ 100%

**File:** `h5/src/components/ContinueWatching.vue:15`

**Issue:** The backend `WatchRecordPayload` defines `progress` as a value between 0 and 100 (see `h5/src/api/watchRecord.ts:4`). The template multiplies it by 100 again: `:style="{ width: \`${Math.round(item.progress * 100)}%\` }"`. This means a 50% complete episode renders as `5000%` width — the progress bar is always full. The `History.vue` page correctly uses `item.progress + '%'` (line 20), confirming the intended range.

**Fix:**
```html
<!-- ContinueWatching.vue line 15 — remove the * 100 -->
<div class="cw-progress-fill" :style="{ width: `${Math.round(item.progress)}%` }" />
```

---

### CR-06: `client.ts` — 401 handler does not attempt token refresh before redirecting

**File:** `h5/src/api/client.ts:23-27`

**Issue:** On any 401 response, the client immediately clears tokens and redirects to `/login`. The spec (CLAUDE.md) explicitly requires: "Token 过期后自动尝试刷新，刷新失败再跳转登录页，不能直接闪退或白屏". This behaviour violates the stated product requirement. A user mid-session whose access token expires will be forcibly logged out rather than getting a seamless refresh.

**Fix:**
```typescript
let isRefreshing = false

client.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    if (error.response?.status === 401 && !isRefreshing) {
      isRefreshing = true
      const refreshTkn = localStorage.getItem('refresh_token')
      if (refreshTkn) {
        try {
          const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshTkn })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          isRefreshing = false
          return client.request(error.config)
        } catch {
          // fall through to logout
        }
      }
      isRefreshing = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/#/login'
    }
    return Promise.reject(error)
  },
)
```

---

### CR-07: `Detail.vue` — `goEpisode` uses `ep.id` as the route `ep` param, but `Player.vue` reads it as `episodeId` and passes it to `openPlayer` — JSBridge receives episode.id not episode_number

**File:** `h5/src/pages/Detail.vue:55`, `h5/src/pages/Player.vue:33`, `h5/src/shims-jsbridge.d.ts:3`

**Issue:** `Detail.vue` builds the route as `/drama/${dramaId}/episode/${ep.id}`. `Player.vue` reads `route.params.ep` as `episodeId` (the database ID). In the WebView path, `Player.vue` correctly calls `episodeApi.detail(episodeId)` to obtain `ep.episode_number` before calling `openPlayer`. This is correct. However, the route definition at `router/index.ts:8` names the param `:ep` and `Player.vue` line 33 names the local variable `episodeId = Number(route.params.ep)`. This is fine. No bug here in the WebView path specifically.

**Revise:** On closer tracing this is not a bug — reclassify as INFO (see IN-06 below).

---

## Warnings

### WR-01: `Banner.vue` is dead code — completely unused, duplicates `BannerCarousel.vue`

**File:** `h5/src/components/Banner.vue:1-62`

**Issue:** `Banner.vue` is not imported by any file in the codebase. `Home.vue` imports and uses `BannerCarousel.vue` exclusively. `Banner.vue` implements the same banner carousel concept with different styling, a hardcoded `getSubtitle` function using `sort_order` as an array index, and slightly worse structure. It also uses the deprecated CSS variable `var(--primary)` (line 61) instead of `var(--color-primary)` required by the design system. This is dead code that will confuse future developers.

**Fix:** Delete `h5/src/components/Banner.vue`.

---

### WR-02: Router guard uses `localStorage` directly instead of Pinia store — bypasses store initialization order

**File:** `h5/src/router/index.ts:18`

**Issue:** The guard reads `localStorage.getItem('access_token')` directly. In the WebView case, `main.ts` calls `auth.syncTokenFromNative()` which writes to `localStorage`. The guard runs on every navigation, so on the initial navigation the write from `syncTokenFromNative` will have already happened. This is coincidentally safe. However, if the store ever changes how tokens are stored (e.g. in-memory only for security), the guard will silently stop working. More immediately, the guard and the store now have two independent sources of truth: the store `isLoggedIn` ref and `localStorage`. These can drift (e.g. after `logout()` in `NavBar.vue`, `isLoggedIn` is cleared but the guard checks `localStorage` which the logout function also clears — consistent here, but fragile).

**Fix:**
```typescript
// router/index.ts
import { useAuthStore } from '@/stores/auth'

router.beforeEach((to) => {
  const auth = useAuthStore()
  const hasToken = auth.isLoggedIn || !!localStorage.getItem('access_token')
  // ...
})
```

---

### WR-03: `home.ts` store — `fetchBanners` and `fetchCategories` have no error handling; failures are silent and swallow exceptions

**File:** `h5/src/stores/home.ts:14-22`

**Issue:** `fetchBanners()` and `fetchCategories()` have no try/catch. If the network request fails, the unhandled Promise rejection propagates to the caller `Home.vue:17` which uses `Promise.all(...)` without a catch. This will cause an unhandled promise rejection that silently leaves the home page with empty banners and no categories, with no user feedback.

**Fix:**
```typescript
async function fetchBanners() {
  try {
    const resp = await getBanners()
    banners.value = resp.data
  } catch {
    banners.value = []
  }
}

async function fetchCategories() {
  try {
    const resp = await getCategories()
    categories.value = resp.data
  } catch {
    categories.value = []
  }
}
```
Also add try/catch in `Home.vue`'s `onMounted` or use `.catch()` chaining on the `Promise.all`.

---

### WR-04: `drama.ts` store — `listEpisodes` (from `dramas.ts`) is used instead of `episodeApi.list` (from `episodes.ts`), creating two duplicate episode-fetching code paths

**File:** `h5/src/stores/drama.ts:3`, `h5/src/api/dramas.ts:30-31`

**Issue:** `drama.ts` imports `listEpisodes` from `@/api/dramas`, which is a bare `client.get` with no return type annotation (line 31 in dramas.ts). `episodes.ts` exports `episodeApi.list` which is properly typed as `client.get<Episode[]>`. As a result, `episodes.value` in `drama.ts` is typed as `any[]` through the entire store, and the `enrichedEpisodes` computed in `Detail.vue` uses `any[]`. The duplicate in `dramas.ts` (line 30-31) should be removed and `drama.ts` should use the canonical `episodeApi`.

**Fix:**
```typescript
// drama.ts
import { getDramaDetail } from '@/api/dramas'
import { episodeApi } from '@/api/episodes'
import type { Episode } from '@/api/episodes'

const episodes = ref<Episode[]>([])

// in fetchDetail:
const [detailResp, epResp] = await Promise.all([
  getDramaDetail(id),
  episodeApi.list(id),
])
episodes.value = epResp.data
```

---

### WR-05: `Player.vue` — `onProgress` is called every 10 seconds indiscriminately and fires an API call even when the user has paused

**File:** `h5/src/components/VideoPlayer.vue:41`, `h5/src/pages/Player.vue:41-43`

**Issue:** `VideoPlayer` fires a `progress` event on a 10-second interval regardless of whether the video is paused or playing. `Player.vue` calls `wrStore.saveProgress()` on every such event, triggering a `PUT /watch-records/:id` call. If the user pauses for several minutes, the timer still fires and makes repeated API calls with an unchanged `currentTime`. The `emitProgress` function does check `currentTime === lastSavedTime` (line 58 of VideoPlayer.vue), which guards against no-op saves. However the guard is on `VideoPlayer` side only — if the same time-position is reached from a different direction the guard will miss it. More practically: `onPause` (line 63) calls `emitProgress` which also fires the `progress` event, leading to two saves on every pause: one from `onPause` and one from the 10-second timer firing shortly after. This doubles write traffic on pauses.

**Fix:** Pause and resume the interval timer when the video is paused/playing:
```typescript
// In VideoPlayer.vue
function onPause() {
  emitProgress()
  if (progressTimer) clearInterval(progressTimer)
}
function onPlay() {
  progressTimer = setInterval(emitProgress, 10000)
}
// Add @play="onPlay" to <video> element
```

---

### WR-06: `auth.ts` store — `syncTokenFromNative` writes native tokens to `localStorage`, defeating the purpose of `EncryptedSharedPreferences`

**File:** `h5/src/stores/auth.ts:41`

**Issue:** CLAUDE.md states: "安全存储 — EncryptedSharedPreferences（禁止明文存储 Token）". The Android side stores tokens in `EncryptedSharedPreferences`. `syncTokenFromNative` extracts these tokens via JSBridge and writes them to `localStorage`, which is plaintext storage accessible to any JavaScript on the page. This means every token bridged from Android is immediately downgraded to unencrypted storage. While this may be an accepted trade-off for WebView operation, it violates the stated security constraint and should be explicitly documented. If the WebView page ever loads external content or is victim of XSS, the tokens in `localStorage` are fully exposed.

**Fix (if localStorage is required for operation):** At minimum, add a comment documenting the security trade-off. Preferably, redesign so the token is read from the bridge on each request rather than persisted to localStorage:
```typescript
// In client.ts interceptor — check bridge first, fall back to localStorage
const token = window.DramaFlowBridge?.getAccessToken() || localStorage.getItem('access_token')
```
Then remove the `localStorage.setItem` calls in `syncTokenFromNative`. This avoids persistent plaintext storage while still authenticating requests.

---

### WR-07: `NavBar.vue` — `logout()` is synchronous but is awaited; logout API call is never made

**File:** `h5/src/components/NavBar.vue:19-21`

**Issue:** `NavBar.vue` calls `await authStore.logout()`. The `logout()` function in `auth.ts` is synchronous (no `async`, no API call). The API function `auth.ts:logout()` (which calls `POST /auth/logout`) is never invoked. The backend session/token is never invalidated. This means refresh tokens remain valid server-side after the user logs out, allowing reuse if captured.

**Fix:**
```typescript
// stores/auth.ts
async function logout() {
  try {
    await apiLogout()  // import { logout as apiLogout } from '@/api/auth'
  } catch {
    // best-effort; proceed with local cleanup regardless
  }
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  user.value = null
  isLoggedIn.value = false
}
```

---

### WR-08: `dramas.ts` and `watchRecord.ts` each have dual API styles (functional + object), creating confusing duplication

**File:** `h5/src/api/dramas.ts:18-37`, `h5/src/api/watchRecord.ts:19-40`

**Issue:** Both files export both a functional API (loose functions) and an object-style API (`dramaApi`, `watchRecordApi`). These duplicate implementations call the same endpoints. Different parts of the codebase use different styles: stores use the object API, some components use the functional API. The `listEpisodes` function in `dramas.ts` duplicates `episodeApi.list` in `episodes.ts`. This creates maintenance risk: a future endpoint change must be made in two places.

**Fix:** Pick one style per module and remove the other. The object style is preferable (explicit, tree-shakeable, consistent with `episodes.ts`). Remove the loose function exports and update callers.

---

### WR-09: `BannerCarousel.vue` navigates to `/drama/:id` but the router defines `/detail/:id` — broken navigation

**File:** `h5/src/components/BannerCarousel.vue:9`

**Issue:** Clicking a banner slide triggers `$router.push('/drama/${item.drama_id}')`. The router at `router/index.ts:7` defines the detail page as `/detail/:id`. There is no `/drama/:id` route defined. Clicking any banner slide will result in a navigation to a non-existent route, which Vue Router will silently fail (no route match) or display a blank page.

`Banner.vue` (the unused component) correctly uses `router.push('/detail/${id}')`. The new `BannerCarousel.vue` has a typo/regression in the route path.

**Fix:**
```html
<!-- BannerCarousel.vue line 9 -->
@click="$router.push(`/detail/${item.drama_id}`)"
```

---

## Info

### IN-01: `DramaCard.vue` — `drama` prop typed as `any`, losing all type safety

**File:** `h5/src/components/DramaCard.vue:22`

**Issue:** `defineProps<{ drama: any }>()` discards the `DramaListItem` type available from `@/api/dramas`. Typos in property access (e.g. `drama.category_slug` — a field not present in `DramaListItem`) will not be caught at compile time.

**Fix:**
```typescript
import type { DramaListItem } from '@/api/dramas'
defineProps<{ drama: DramaListItem & { category_slug?: string } }>()
```

---

### IN-02: `CategoryTabs.vue` — uses deprecated CSS variable `var(--primary)` instead of `var(--color-primary)`

**File:** `h5/src/components/CategoryTabs.vue:22`

**Issue:** `.tabs button.active { background: var(--primary); }` uses the deprecated variable name. Per CLAUDE.md: "❌ 错误 — 旧版变量名（已废弃）: color: var(--primary)". `EpisodeList.vue` (lines 29, 30) also uses `var(--primary)`, `var(--text)`, `var(--text-muted)`, `var(--text-secondary)`, `var(--rating)` — several of which may be deprecated names.

**Fix:** Replace `var(--primary)` with `var(--color-primary)` and audit all other var() references against `design-system/tokens/tokens.css`.

---

### IN-03: `main.ts` — `console.log` in production bootstrap

**File:** `h5/src/main.ts:21`

**Issue:** Already flagged in CR-01 for the security concern. As a separate info note: even without the token value, this log line means every user sees a synchronous console log on every page load in production.

---

### IN-04: `stores/drama.ts` and `stores/home.ts` — store state typed as `any` / `any[]` throughout

**File:** `h5/src/stores/drama.ts:7-9`, `h5/src/stores/home.ts:7-10`

**Issue:** `detail`, `episodes`, `banners`, `categories`, `dramas`, `continueWatchingList` are all typed as `any` or `any[]`. The corresponding types exist in the API layer (`DramaDetail`, `Episode[]`, `Banner[]`, etc.) and should be used. This prevents TypeScript from catching property access errors in templates and computed properties.

---

### IN-05: `VideoPlayer.vue` — `load()` not called after setting `videoEl.value.src` on mount

**File:** `h5/src/components/VideoPlayer.vue:39`

**Issue:** In `onMounted`, the code sets `videoEl.value.src = props.src` but does not call `videoEl.value.load()`. The `watch` handler for `props.src` (line 33) correctly calls `load()`. The omission in `onMounted` relies on the browser auto-loading when `src` is set — this is generally reliable in modern browsers but is inconsistent with the watcher's behavior.

**Fix:**
```typescript
onMounted(() => {
  if (!videoEl.value || !props.src) return
  videoEl.value.src = props.src
  videoEl.value.load()  // add this for consistency
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
  progressTimer = setInterval(emitProgress, 10000)
})
```

---

### IN-06: `Player.vue` — `onEnded` saves progress with `last_position=0` and `duration=1`, creating misleading data

**File:** `h5/src/pages/Player.vue:46`

**Issue:** When a video ends, `onEnded` calls `wrStore.saveProgress(episodeId, 0, 1, true)`. This saves `last_position: 0` and computes `progress = min(100, 0/1 * 100) = 0`. A completed episode is stored with `progress: 0%` and `last_position: 0s`. While `completed: true` is set, the `continueEp` logic in `Detail.vue` checks `rec.progress > 0 && !rec.completed`, so completed episodes correctly won't show as "continue watching". The data is misleading for analytics though. A better approach is to save the actual final position.

**Fix:**
```typescript
// VideoPlayer.vue should emit actual duration on ended
function onEnded() {
  if (videoEl.value) {
    emit('progress', videoEl.value.duration, videoEl.value.duration)
  }
  emit('ended')
}

// Player.vue onEnded — no manual progress save needed; rely on the progress event emitted above
async function onEnded() {
  if (nextEpisode.value) {
    router.push(`/drama/${dramaId}/episode/${nextEpisode.value.id}`)
  }
}
```

---

_Reviewed: 2026-06-25_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_

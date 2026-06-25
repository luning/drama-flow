# h5/ 统一前端实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除 `web/`，以 `h5/` 为唯一前端，同时服务 Android WebView 和浏览器两个入口。

**Architecture:** `h5/` 保持 hash 路由和 JSBridge 集成，补入 Login/Register/Player/History 四个页面及所需组件。Player 页面运行时检测 `window.DramaFlowBridge`：WebView 中委托原生播放，浏览器中渲染 H5 VideoPlayer。认证双轨：WebView 由 JSBridge 在 `main.ts` 中同步 token，浏览器走 Login 页。

**Tech Stack:** Vue 3 + TypeScript + Vite + Pinia + Vue Router (hash mode) + Axios + design-system CSS tokens

## Global Constraints

- 所有颜色/间距必须用 `var(--token-name)` CSS 变量，禁止硬编码色值
- 路由模式：`createWebHashHistory`（不改变）
- h5/ 的 API 层保持函数式风格，新增 TypeScript interface 作为类型补充
- JSBridge 类型定义已在 `h5/src/shims-jsbridge.d.ts`，`openPlayer(episodeId, dramaId, episodeNumber)` 为正确签名
- 不引入新的 npm 依赖
- 不修改 `h5/src/stores/auth.ts`、`h5/src/api/auth.ts`、`h5/src/api/client.ts` 的核心逻辑（除 Task 8 中的 401 跳转修复）

---

## File Structure

| 操作 | 文件 | 说明 |
|---|---|---|
| 修改 | `h5/src/api/dramas.ts` | 新增 TypeScript interfaces + `dramaApi.banners()` |
| 新建 | `h5/src/api/episodes.ts` | Episode 类型 + episodeApi |
| 修改 | `h5/src/api/watchRecord.ts` | 新增 WatchRecord 类型 + watchRecordApi 对象 |
| 新建 | `h5/src/stores/watchRecord.ts` | watchRecord 状态管理 |
| 新建 | `h5/src/components/NavBar.vue` | 顶部导航（登出、历史记录）|
| 新建 | `h5/src/components/VideoPlayer.vue` | H5 视频播放器 |
| 新建 | `h5/src/components/BannerCarousel.vue` | 轮播图（已在 web/ 未提交）|
| 新建 | `h5/src/pages/Login.vue` | 登录页（浏览器用）|
| 新建 | `h5/src/pages/Register.vue` | 注册页（浏览器用）|
| 新建 | `h5/src/pages/History.vue` | 观看历史页 |
| 新建 | `h5/src/pages/Player.vue` | 播放页（双端适配）|
| 修改 | `h5/src/pages/Home.vue` | 替换 Banner → BannerCarousel |
| 修改 | `h5/src/router/index.ts` | 新增路由 + auth guard |
| 修改 | `h5/src/api/client.ts` | 修复 401 跳转为 `/#/login` |
| 删除 | `web/` | 整个目录 |

---

## Task 1: API 层——新增 TypeScript 类型和 episodes 模块

**Files:**
- Modify: `h5/src/api/dramas.ts`
- Create: `h5/src/api/episodes.ts`
- Modify: `h5/src/api/watchRecord.ts`

**Interfaces produced (consumed by Tasks 2, 3, 5, 6, 7):**
- `Banner` — `{ drama_id, title, image_url, sort_order }`
- `DramaListItem`, `DramaDetail`, `PaginatedDramas`
- `Episode` — `{ id, drama_id, episode_number, title, duration, video_url, cover_url }`
- `VideoUrlResponse` — `{ url, expires_at }`
- `episodeApi.detail(episodeId)` → `Promise<AxiosResponse<Episode>>`
- `episodeApi.videoUrl(episodeId)` → `Promise<AxiosResponse<VideoUrlResponse>>`
- `episodeApi.list(dramaId)` → `Promise<AxiosResponse<Episode[]>>`
- `WatchRecord`, `ContinueWatchingItem`, `WatchRecordPayload`
- `watchRecordApi.upsert(episodeId, data)`, `.get(episodeId)`, `.continueWatching()`

- [ ] **Step 1: 更新 `h5/src/api/dramas.ts`，新增 interfaces 和 `dramaApi` 对象**

完整替换文件内容：

```typescript
import client from './client'

export interface DramaListItem {
  id: number; title: string; category_id: number; rating: number
  cover_url: string; year: number | null; status: string; episode_count: number
}
export interface DramaDetail extends DramaListItem {
  description: string; category_name: string; created_at: string
}
export interface PaginatedDramas {
  items: DramaListItem[]; total: number; page: number; size: number
}
export interface Banner {
  drama_id: number; title: string; image_url: string; sort_order: number
}

// 函数式 API（现有，保留）
export function listDramas(category?: string, page = 1, size = 20) {
  return client.get<PaginatedDramas>('/dramas', { params: { category, page, size } })
}
export function getDramaDetail(id: number) {
  return client.get<DramaDetail>(`/dramas/${id}`)
}
export function getBanners() {
  return client.get<Banner[]>('/banners')
}
export function getCategories() {
  return client.get<{ id: number; name: string; slug: string }[]>('/categories')
}
export function listEpisodes(dramaId: number) {
  return client.get(`/dramas/${dramaId}/episodes`)
}

// 对象式 API（BannerCarousel 等新组件使用）
export const dramaApi = {
  banners: () => client.get<Banner[]>('/banners'),
}
```

- [ ] **Step 2: 创建 `h5/src/api/episodes.ts`**

```typescript
import client from './client'

export interface Episode {
  id: number; drama_id: number; episode_number: number
  title: string; duration: string; video_url: string; cover_url: string
}
export interface VideoUrlResponse { url: string; expires_at: number }

export const episodeApi = {
  list: (dramaId: number) =>
    client.get<Episode[]>(`/dramas/${dramaId}/episodes`),
  detail: (episodeId: number) =>
    client.get<Episode>(`/episodes/${episodeId}`),
  videoUrl: (episodeId: number) =>
    client.get<VideoUrlResponse>(`/episodes/${episodeId}/video-url`),
}
```

- [ ] **Step 3: 更新 `h5/src/api/watchRecord.ts`，新增类型和对象 API**

完整替换文件内容：

```typescript
import client from './client'

export interface WatchRecordPayload {
  progress: number      // 0-100
  last_position: number // seconds
  completed?: boolean
}
export interface WatchRecord {
  id: number; user_id: number; episode_id: number
  progress: number; last_position: number; completed: boolean; updated_at: string
}
export interface ContinueWatchingItem {
  drama_id: number; drama_title: string; drama_cover: string
  episode_id: number; episode_number: number; episode_title: string
  progress: number; last_position: number; updated_at: string
}

// 函数式 API（现有，保留）
export function upsertRecord(episodeId: number, data: WatchRecordPayload) {
  return client.put<WatchRecord>(`/watch-records/${episodeId}`, data)
}
export function getRecord(episodeId: number) {
  return client.get<WatchRecord>(`/watch-records/${episodeId}`)
}
export function listRecords(page = 1, size = 20) {
  return client.get('/watch-records', { params: { page, size } })
}
export function continueWatching() {
  return client.get<ContinueWatchingItem[]>('/watch-records/continue-watching')
}

// 对象式 API（stores 使用）
export const watchRecordApi = {
  upsert: (episodeId: number, data: WatchRecordPayload) =>
    client.put<WatchRecord>(`/watch-records/${episodeId}`, data),
  get: (episodeId: number) =>
    client.get<WatchRecord>(`/watch-records/${episodeId}`),
  continueWatching: () =>
    client.get<ContinueWatchingItem[]>('/watch-records/continue-watching'),
}
```

- [ ] **Step 4: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误（或只有与新文件无关的已有警告）

- [ ] **Step 5: 提交**

```bash
git add h5/src/api/dramas.ts h5/src/api/episodes.ts h5/src/api/watchRecord.ts
git commit -m "feat(h5): add TypeScript interfaces and episodes API module"
```

---

## Task 2: 新建 watchRecord Store

**Files:**
- Create: `h5/src/stores/watchRecord.ts`

**Interfaces consumed:** `watchRecordApi`, `WatchRecord`, `ContinueWatchingItem` from `@/api/watchRecord`
**Interfaces produced:** `useWatchRecordStore` — `{ history, fetchRecord, saveProgress, fetchHistory }`（History.vue 和 Player.vue 依赖）

- [ ] **Step 1: 创建 `h5/src/stores/watchRecord.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { watchRecordApi, type WatchRecord, type ContinueWatchingItem } from '@/api/watchRecord'

export const useWatchRecordStore = defineStore('watchRecord', () => {
  const records = ref<Record<number, WatchRecord>>({})
  const history = ref<ContinueWatchingItem[]>([])

  async function fetchRecord(episodeId: number): Promise<WatchRecord> {
    const { data } = await watchRecordApi.get(episodeId)
    records.value[episodeId] = data
    return data
  }

  async function saveProgress(episodeId: number, lastPosition: number, duration: number, completed = false) {
    const progress = duration > 0 ? Math.min(100, (lastPosition / duration) * 100) : 0
    const { data } = await watchRecordApi.upsert(episodeId, { progress, last_position: lastPosition, completed })
    records.value[episodeId] = data
  }

  async function fetchHistory() {
    const { data } = await watchRecordApi.continueWatching()
    history.value = data
  }

  return { records, history, fetchRecord, saveProgress, fetchHistory }
})
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 3: 提交**

```bash
git add h5/src/stores/watchRecord.ts
git commit -m "feat(h5): add watchRecord store"
```

---

## Task 3: 新增共享组件（NavBar、VideoPlayer、BannerCarousel）

**Files:**
- Create: `h5/src/components/NavBar.vue`
- Create: `h5/src/components/VideoPlayer.vue`
- Create: `h5/src/components/BannerCarousel.vue`

**Interfaces consumed:** 
- `NavBar` 消费 `useAuthStore().logout()`
- `VideoPlayer` props: `{ src: string, startPosition: number }`，emits: `progress(currentTime, duration)`, `ended()`
- `BannerCarousel` props: `{ items: Banner[] }`，消费 `Banner` from `@/api/dramas`

- [ ] **Step 1: 创建 `h5/src/components/NavBar.vue`**

```vue
<template>
  <nav class="navbar">
    <router-link to="/" class="brand">DramaFlow</router-link>
    <div class="links">
      <router-link to="/">首页</router-link>
      <router-link to="/history">观看历史</router-link>
      <button class="logout" @click="handleLogout">退出</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-3) var(--space-6); background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.brand { font-size: 1.25rem; font-weight: 700; color: var(--color-primary); text-decoration: none; }
.links { display: flex; align-items: center; gap: var(--space-4); }
.links a { color: var(--text-secondary); text-decoration: none; }
.links a.router-link-active { color: var(--color-primary); }
.logout {
  background: none; border: 1px solid var(--border);
  color: var(--text-secondary); padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm); cursor: pointer;
}
</style>
```

- [ ] **Step 2: 创建 `h5/src/components/VideoPlayer.vue`**

```vue
<template>
  <div class="video-wrapper">
    <video
      ref="videoEl"
      controls
      class="video"
      @ended="onEnded"
      @pause="onPause"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  src: string
  startPosition: number
}>()

const emit = defineEmits<{
  progress: [currentTime: number, duration: number]
  ended: []
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
let progressTimer: ReturnType<typeof setInterval> | null = null
let lastSavedTime = 0

watch(() => props.src, (newSrc) => {
  if (!videoEl.value || !newSrc) return
  videoEl.value.src = newSrc
  videoEl.value.load()
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
})

onMounted(() => {
  if (!videoEl.value || !props.src) return
  videoEl.value.src = props.src
  videoEl.value.addEventListener('loadedmetadata', applyStartPosition, { once: true })
  progressTimer = setInterval(emitProgress, 10000)
})

onBeforeUnmount(() => {
  if (progressTimer) clearInterval(progressTimer)
  emitProgress()
})

function applyStartPosition() {
  if (videoEl.value && props.startPosition > 0) {
    videoEl.value.currentTime = props.startPosition
  }
}

function emitProgress() {
  if (!videoEl.value) return
  const { currentTime, duration } = videoEl.value
  if (currentTime === lastSavedTime || !duration) return
  lastSavedTime = currentTime
  emit('progress', currentTime, duration)
}

function onPause() { emitProgress() }
function onEnded() { emit('ended') }
</script>

<style scoped>
.video-wrapper { width: 100%; background: #000; }
.video { width: 100%; max-height: 70vh; display: block; }
</style>
```

- [ ] **Step 3: 创建 `h5/src/components/BannerCarousel.vue`**

```vue
<template>
  <div class="banner-wrapper" v-if="items.length > 0">
    <div class="banner-track">
      <div
        v-for="(item, i) in items"
        :key="i"
        class="banner-slide"
        :class="{ active: i === current }"
        @click="$router.push(`/drama/${item.drama_id}`)"
      >
        <img class="banner-img" :src="item.image_url" :alt="item.title" />
        <div class="banner-overlay">
          <h2 class="banner-title">{{ item.title }}</h2>
          <span class="banner-tag">{{ tags[item.sort_order] ?? '精彩不容错过' }}</span>
        </div>
      </div>
    </div>
    <div class="banner-dots">
      <span
        v-for="(_, i) in items"
        :key="i"
        class="dot"
        :class="{ active: i === current }"
        @click="goTo(i)"
      />
    </div>
    <button class="arrow left" @click="prev">‹</button>
    <button class="arrow right" @click="next">›</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Banner } from '@/api/dramas'

const props = defineProps<{ items: Banner[] }>()

const tags = ['🏆 本周必追', '🔥 热播榜第一', '✨ 新剧上线', '⭐ 高分推荐', '💎 编辑精选']
const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function goTo(i: number) { current.value = i }
function next() { current.value = (current.value + 1) % props.items.length }
function prev() { current.value = (current.value - 1 + props.items.length) % props.items.length }

onMounted(() => { timer = setInterval(next, 4000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.banner-wrapper {
  position: relative; width: 100%; aspect-ratio: 16 / 5;
  overflow: hidden; background: #111;
}
.banner-track { position: relative; width: 100%; height: 100%; }
.banner-slide {
  position: absolute; inset: 0; opacity: 0;
  transition: opacity 0.6s ease; cursor: pointer;
}
.banner-slide.active { opacity: 1; }
.banner-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.banner-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.7) 0%, transparent 60%);
  display: flex; flex-direction: column; justify-content: center; padding: 0 60px;
}
.banner-title {
  color: #fff; font-size: clamp(20px, 3vw, 36px); font-weight: 700;
  margin-bottom: 10px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.banner-tag { color: #ddd; font-size: clamp(12px, 1.5vw, 16px); }
.banner-dots {
  position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 6px; z-index: 2;
}
.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.3s;
}
.dot.active { width: 22px; border-radius: 4px; background: var(--color-primary); }
.arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(0,0,0,0.4); color: #fff; border: none;
  width: 40px; height: 40px; border-radius: 50%; font-size: 22px;
  cursor: pointer; z-index: 2; transition: background 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.arrow:hover { background: rgba(0,0,0,0.7); }
.arrow.left { left: 16px; }
.arrow.right { right: 16px; }
</style>
```

- [ ] **Step 4: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 5: 提交**

```bash
git add h5/src/components/NavBar.vue h5/src/components/VideoPlayer.vue h5/src/components/BannerCarousel.vue
git commit -m "feat(h5): add NavBar, VideoPlayer, BannerCarousel components"
```

---

## Task 4: 新增 Login 和 Register 页面

**Files:**
- Create: `h5/src/pages/Login.vue`
- Create: `h5/src/pages/Register.vue`

**注意：** h5 的 `authStore.login(data: LoginData)` 接受对象 `{ email, password }`，不是 3 个分开的参数。h5 的 `authStore.register(data: RegisterData)` 接受 `{ nickname, email, password }`（不用 `authApi.register`）。

- [ ] **Step 1: 创建 `h5/src/pages/Login.vue`**

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>DramaFlow</h1>
      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="link">没有账号？<router-link to="/register">注册</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login({ email: email.value, password: password.value })
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || '/')
  } catch (e: any) {
    const msg = e.response?.data?.detail
    error.value = typeof msg === 'string' ? msg : '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center; background: var(--bg-primary);
}
.auth-card {
  background: var(--bg-card); border-radius: var(--radius-card);
  padding: var(--space-8); width: 360px; display: flex;
  flex-direction: column; gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--text-secondary); }
.field input {
  padding: var(--space-2) var(--space-3); background: var(--surface-mid);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  color: var(--text-primary); font-size: 1rem;
}
.error { color: var(--color-danger); font-size: 0.875rem; }
.btn-primary {
  width: 100%; padding: var(--space-3); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-size: 1rem; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--text-secondary); }
.link a { color: var(--color-primary); }
</style>
```

- [ ] **Step 2: 创建 `h5/src/pages/Register.vue`**

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>注册账号</h1>
      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>昵称</label>
          <input v-model="nickname" type="text" placeholder="请输入昵称" required />
        </div>
        <div class="field">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="请输入邮箱" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="至少 8 位，含字母和数字" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="link">已有账号？<router-link to="/login">登录</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const nickname = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (password.value.length < 8 || !/[A-Za-z]/.test(password.value) || !/\d/.test(password.value)) {
    error.value = '密码至少 8 位，需包含字母和数字'
    return
  }
  loading.value = true
  try {
    await authStore.register({ nickname: nickname.value, email: email.value, password: password.value })
    router.push('/login')
  } catch (e: any) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      error.value = detail.map((d: any) => d.msg).join('；')
    } else {
      error.value = typeof detail === 'string' ? detail : '注册失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center; background: var(--bg-primary);
}
.auth-card {
  background: var(--bg-card); border-radius: var(--radius-card);
  padding: var(--space-8); width: 360px; display: flex;
  flex-direction: column; gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--text-secondary); }
.field input {
  padding: var(--space-2) var(--space-3); background: var(--surface-mid);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  color: var(--text-primary); font-size: 1rem;
}
.error { color: var(--color-danger); font-size: 0.875rem; }
.btn-primary {
  width: 100%; padding: var(--space-3); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-size: 1rem; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--text-secondary); }
.link a { color: var(--color-primary); }
</style>
```

- [ ] **Step 3: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 4: 提交**

```bash
git add h5/src/pages/Login.vue h5/src/pages/Register.vue
git commit -m "feat(h5): add Login and Register pages"
```

---

## Task 5: 新增 History 页面

**Files:**
- Create: `h5/src/pages/History.vue`

**Interfaces consumed:** `useWatchRecordStore().history`（`ContinueWatchingItem[]`），`useWatchRecordStore().fetchHistory()`

- [ ] **Step 1: 创建 `h5/src/pages/History.vue`**

```vue
<template>
  <div class="page">
    <NavBar />
    <main class="container">
      <h1>观看历史</h1>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="!wrStore.history.length" class="empty">暂无观看记录</div>
      <div v-else class="history-list">
        <div
          v-for="item in wrStore.history"
          :key="item.episode_id"
          class="history-item"
          @click="goPlay(item)"
        >
          <img :src="item.drama_cover" :alt="item.drama_title" class="cover" />
          <div class="info">
            <p class="title">{{ item.drama_title }}</p>
            <p class="sub">第 {{ item.episode_number }} 集</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: item.progress + '%' }" />
            </div>
            <p class="time">{{ formatTime(item.updated_at) }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchRecordStore } from '@/stores/watchRecord'
import type { ContinueWatchingItem } from '@/api/watchRecord'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const wrStore = useWatchRecordStore()
const loading = ref(true)

function goPlay(item: ContinueWatchingItem) {
  router.push(`/drama/${item.drama_id}/episode/${item.episode_id}`)
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString('zh-CN', {
    month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(async () => {
  try {
    await wrStore.fetchHistory()
  } catch (e) {
    console.error('fetchHistory failed', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
h1 { font-size: 1.5rem; color: var(--text-primary); margin-bottom: var(--space-4); }
.loading, .empty { color: var(--text-secondary); text-align: center; padding: var(--space-8); }
.history-list { display: flex; flex-direction: column; gap: var(--space-3); }
.history-item {
  display: flex; gap: var(--space-4); padding: var(--space-3);
  background: var(--bg-card); border-radius: var(--radius-md);
  cursor: pointer; border: 1px solid var(--border);
}
.history-item:hover { border-color: var(--color-primary); }
.cover { width: 80px; height: 110px; object-fit: cover; border-radius: var(--radius-sm); flex-shrink: 0; }
.info { flex: 1; display: flex; flex-direction: column; gap: var(--space-1); }
.title { font-weight: 600; color: var(--text-primary); }
.sub { font-size: 0.875rem; color: var(--text-secondary); }
.progress-bar { height: 3px; background: var(--border); border-radius: 2px; margin: var(--space-1) 0; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; }
.time { font-size: 0.75rem; color: var(--text-secondary); }
</style>
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 3: 提交**

```bash
git add h5/src/pages/History.vue
git commit -m "feat(h5): add History page"
```

---

## Task 6: 新增 Player 页面（双端适配）

**Files:**
- Create: `h5/src/pages/Player.vue`

**Interfaces consumed:**
- `episodeApi.detail(episodeId)` → `Episode`（用于获取 `episode_number` 给 JSBridge）
- `episodeApi.videoUrl(episodeId)` → `VideoUrlResponse`
- `episodeApi.list(dramaId)` → `Episode[]`（用于找下一集）
- `useWatchRecordStore().fetchRecord(episodeId)` → `WatchRecord`
- `useWatchRecordStore().saveProgress(episodeId, lastPosition, duration, completed)`
- `window.DramaFlowBridge.openPlayer(episodeId, dramaId, episodeNumber)` — JSBridge 签名（见 `shims-jsbridge.d.ts`）

**路由参数：** `/drama/:id/episode/:ep` → `route.params.id`（dramaId），`route.params.ep`（episodeId）

- [ ] **Step 1: 创建 `h5/src/pages/Player.vue`**

```vue
<template>
  <div class="player-page">
    <NavBar />
    <div v-if="loading" class="loading">加载中...</div>
    <main v-else class="player-container">
      <VideoPlayer
        :src="videoUrl"
        :startPosition="startPosition"
        @progress="onProgress"
        @ended="onEnded"
      />
      <div class="info">
        <h2>{{ episode?.title }}</h2>
        <p v-if="nextEpisode" class="next-hint">下一集：{{ nextEpisode.title }}</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { episodeApi, type Episode } from '@/api/episodes'
import { useWatchRecordStore } from '@/stores/watchRecord'
import VideoPlayer from '@/components/VideoPlayer.vue'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const wrStore = useWatchRecordStore()

const dramaId = Number(route.params.id)
const episodeId = Number(route.params.ep)

const loading = ref(true)
const videoUrl = ref('')
const startPosition = ref(0)
const episode = ref<Episode | null>(null)
const nextEpisode = ref<Episode | null>(null)

async function onProgress(currentTime: number, duration: number) {
  await wrStore.saveProgress(episodeId, currentTime, duration, false)
}

async function onEnded() {
  await wrStore.saveProgress(episodeId, 0, 1, true)
  if (nextEpisode.value) {
    router.push(`/drama/${dramaId}/episode/${nextEpisode.value.id}`)
  }
}

onMounted(async () => {
  // WebView 环境：委托原生播放器，不渲染 H5 VideoPlayer
  if (window.DramaFlowBridge) {
    try {
      const { data: ep } = await episodeApi.detail(episodeId)
      window.DramaFlowBridge.openPlayer(episodeId, dramaId, ep.episode_number)
    } catch (e) {
      console.error('openPlayer failed', e)
    }
    router.back()
    return
  }

  // 浏览器环境：加载签名 URL，渲染 H5 VideoPlayer
  try {
    const [urlResp, recordResp, episodesResp] = await Promise.all([
      episodeApi.videoUrl(episodeId),
      wrStore.fetchRecord(episodeId),
      episodeApi.list(dramaId),
    ])

    videoUrl.value = urlResp.data.url
    startPosition.value = recordResp.last_position ?? 0

    const episodes = episodesResp.data
    episode.value = episodes.find((ep: Episode) => ep.id === episodeId) ?? null
    const idx = episodes.findIndex((ep: Episode) => ep.id === episodeId)
    nextEpisode.value = idx >= 0 && idx < episodes.length - 1 ? episodes[idx + 1] : null
  } catch (e) {
    console.error('Player load failed', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.player-page { min-height: 100vh; background: var(--bg-primary); }
.loading { text-align: center; padding: var(--space-8); color: var(--text-secondary); }
.player-container { max-width: 1000px; margin: 0 auto; padding: var(--space-4); }
.info { padding: var(--space-4) 0; }
.info h2 { color: var(--text-primary); }
.next-hint { margin-top: var(--space-2); color: var(--text-secondary); font-size: 0.875rem; }
</style>
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 3: 提交**

```bash
git add h5/src/pages/Player.vue
git commit -m "feat(h5): add Player page with WebView/browser dual-path"
```

---

## Task 7: 更新 Home.vue（替换 Banner → BannerCarousel）

**Files:**
- Modify: `h5/src/pages/Home.vue`

将 `<Banner :items="store.banners" />` 替换为 `<BannerCarousel :items="store.banners" />`，并更新 import。

- [ ] **Step 1: 编辑 `h5/src/pages/Home.vue`**

在 `<script setup>` 中：
- 移除：`import Banner from '@/components/Banner.vue'`
- 新增：`import BannerCarousel from '@/components/BannerCarousel.vue'`

在 `<template>` 中：
- 将 `<Banner :items="store.banners" />` 替换为 `<BannerCarousel :items="store.banners" />`

完整更新后的文件：

```vue
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useHomeStore } from '@/stores/home'
import BannerCarousel from '@/components/BannerCarousel.vue'
import CategoryTabs from '@/components/CategoryTabs.vue'
import DramaCard from '@/components/DramaCard.vue'
import ContinueWatching from '@/components/ContinueWatching.vue'

const store = useHomeStore()

const tabs = computed(() => [
  { key: 'all', label: '全部' },
  ...store.categories.map((c: any) => ({ key: c.slug, label: c.name })),
])

onMounted(async () => {
  await Promise.all([
    store.fetchBanners(),
    store.fetchCategories(),
    store.fetchDramas(),
    store.fetchContinueWatching(),
  ])
})
</script>

<template>
  <div class="home-page">
    <header class="app-bar">
      <span class="logo">DramaFlow</span>
    </header>

    <BannerCarousel :items="store.banners" />

    <ContinueWatching :items="store.continueWatchingList" />

    <CategoryTabs
      :tabs="tabs"
      :active="store.currentCategory"
      @change="store.setCategory"
    />

    <div v-if="store.loading" class="skeleton-grid">
      <div v-for="i in 6" :key="i" class="skeleton-card" />
    </div>
    <div v-else-if="store.dramas.length === 0" class="empty">暂无剧集</div>
    <div v-else class="drama-grid">
      <DramaCard v-for="drama in store.dramas" :key="drama.id" :drama="drama" />
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-bottom: 24px;
}
.app-bar {
  display: flex;
  align-items: center;
  padding: 16px 16px 8px;
}
.logo {
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.drama-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 8px 16px 0;
}
.skeleton-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 8px 16px 0;
}
.skeleton-card {
  aspect-ratio: 3/4;
  border-radius: 14px;
  background: linear-gradient(90deg, #1a1a2e 25%, #252540 50%, #1a1a2e 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.empty {
  text-align: center;
  color: #555;
  padding: 48px 0;
  font-size: 14px;
}
</style>
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 3: 启动开发服务器，手动验证首页渲染**

```bash
cd h5 && npm run dev
```

访问 `http://localhost:5173`，确认轮播图（BannerCarousel）正常显示，CategoryTabs 和 DramaCard 网格正常。

- [ ] **Step 4: 提交**

```bash
git add h5/src/pages/Home.vue
git commit -m "feat(h5): replace Banner with BannerCarousel on Home page"
```

---

## Task 8: 更新路由 + auth guard + 修复 client 401 跳转

**Files:**
- Modify: `h5/src/router/index.ts`
- Modify: `h5/src/api/client.ts`

**Auth guard 设计：**
- 检查 `localStorage.getItem('access_token')` 而非 `auth.isLoggedIn`（避免 async `tryRestoreSession` 的竞态问题）
- WebView 环境：`syncTokenFromNative()` 已在 `main.ts` 同步写入 localStorage，guard 自然通过
- 已登录用户访问 `/login`、`/register` 时重定向到 `/`

**client 401 修复：**
- hash 路由下 `window.location.href = '/login'` 会跳到不存在的路径，改为 `'/#/login'`

- [ ] **Step 1: 完整替换 `h5/src/router/index.ts`**

```typescript
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/pages/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/pages/Register.vue'), meta: { public: true } },
  { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
  { path: '/detail/:id', name: 'Detail', component: () => import('@/pages/Detail.vue') },
  { path: '/drama/:id/episode/:ep', name: 'Player', component: () => import('@/pages/Player.vue') },
  { path: '/history', name: 'History', component: () => import('@/pages/History.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const hasToken = !!localStorage.getItem('access_token')
  if (!to.meta.public && !hasToken) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && hasToken) {
    return { path: '/' }
  }
})

export default router
```

- [ ] **Step 2: 修复 `h5/src/api/client.ts` 中的 401 跳转**

将响应拦截器中的跳转由 `/login` 改为 `/#/login`：

找到这一行：
```typescript
window.location.href = '/login'
```
替换为：
```typescript
window.location.href = '/#/login'
```

- [ ] **Step 3: TypeScript 编译检查**

```bash
cd h5 && npx tsc --noEmit
```

期望：0 错误

- [ ] **Step 4: 端到端手动验证**

```bash
cd h5 && npm run dev
```

验证以下场景：
1. 访问 `http://localhost:5173`（无 token）→ 自动跳转到 `http://localhost:5173/#/login`
2. 输入正确邮箱/密码登录 → 跳转到 `/#/`（首页）
3. 访问 `/#/history` → 显示观看历史列表
4. 访问 `/#/login`（已登录）→ 自动跳转回 `/#/`
5. 点击退出 → 跳转到 `/#/login`

- [ ] **Step 5: 提交**

```bash
git add h5/src/router/index.ts h5/src/api/client.ts
git commit -m "feat(h5): add auth guard and new routes, fix 401 redirect for hash routing"
```

---

## Task 9: 删除 web/ 目录

**注意：删除前再次确认 h5/ 开发服务器正常运行，所有功能可用。**

- [ ] **Step 1: 再次启动 h5/ 并确认所有路由可访问**

```bash
cd h5 && npm run dev
```

逐一访问并确认无报错：`/#/login`、`/#/register`、`/#/`（登录后）、`/#/history`

- [ ] **Step 2: 删除 web/ 目录**

```bash
rm -rf web
```

- [ ] **Step 3: 确认项目根目录结构**

```bash
ls
```

期望输出中不含 `web`，包含 `h5`、`backend`、`android`、`design-system` 等。

- [ ] **Step 4: 确认 h5/ 仍可正常构建**

```bash
cd h5 && npm run build
```

期望：构建成功，无错误。

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "chore: remove web/ - h5/ is now the single frontend codebase"
```

---

## 验收检查清单

完成所有 Task 后，对照 spec 逐条验证：

- [ ] 浏览器访问 `http://localhost:5173/#/`，未登录时跳转到 `/#/login`
- [ ] 浏览器登录后可正常浏览首页、剧集详情、历史记录
- [ ] 浏览器 Player 页面能播放视频（H5 VideoPlayer 渲染）
- [ ] Android WebView 加载 H5，token 由 JSBridge 注入，无需经过登录页
- [ ] Android WebView 进入 Player 页面时调用 `DramaFlowBridge.openPlayer()`，不渲染 H5 VideoPlayer
- [ ] `web/` 目录已删除，`ls` 根目录不含 `web`

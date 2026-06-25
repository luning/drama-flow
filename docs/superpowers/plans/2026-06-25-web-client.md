# Web 客户端 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在项目根目录新建 `web/` 目录，构建一个可在本地浏览器访问的完整 Vue3 Web 客户端，复刻 Android 的登录/注册、剧集列表、剧集详情、视频播放、观看历史五大功能。

**Architecture:** 独立 Vue3 + Vite + TypeScript 应用，不依赖 H5（JSBridge）。Pinia 管理状态，Axios 拦截器自动处理 Token 刷新，HTML5 `<video>` 播放视频并同步进度到后端。

**Tech Stack:** Vue3, Vite 5, TypeScript, Pinia 2, Vue Router 4, Axios 1.x, HTML5 Video API

## Global Constraints

- 后端地址：`http://localhost:8000`，开发时通过 Vite proxy 代理 `/api` 路径
- 设计 token 从 `../design-system/tokens/tokens.css` 引入，禁止硬编码颜色/间距
- 密码校验规则：至少 8 位，含字母且含数字（与后端 Pydantic validator 一致）
- "记住我" 勾选 → `localStorage`，未勾选 → `sessionStorage`
- 进度保存间隔：播放过程中每 10 秒调用一次 `PUT /api/watch-records/{episode_id}`
- `progress` 字段为 0–100 百分比，`last_position` 字段为秒数（浮点）
- Web 端 `web/` 目录完全独立，不 import H5 `h5/` 的任何文件
- 不自动 git commit，由用户决定何时提交

---

## File Map

```
web/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── App.vue                        # 顶部导航 + <router-view>
│   ├── api/
│   │   ├── client.ts                  # axios 实例 + request/response 拦截器
│   │   ├── auth.ts                    # login, register, logout, refresh
│   │   ├── dramas.ts                  # listDramas, getDrama, getCategories
│   │   ├── episodes.ts                # listEpisodes, getEpisode, getVideoUrl
│   │   └── watchRecords.ts            # upsertRecord, getRecord, listRecords, continueWatching
│   ├── stores/
│   │   ├── auth.ts                    # 登录态 + token 存取 + initFromStorage
│   │   ├── drama.ts                   # 剧集列表 + 详情缓存
│   │   └── watchRecord.ts             # 观看进度缓存
│   ├── router/
│   │   └── index.ts                   # 路由表 + 导航守卫
│   ├── pages/
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Home.vue
│   │   ├── Detail.vue
│   │   ├── Player.vue
│   │   └── History.vue
│   └── components/
│       ├── NavBar.vue                 # 顶部导航栏（Home / History / 登出）
│       ├── DramaCard.vue              # 剧集卡片（封面 + 标题 + 评分）
│       ├── EpisodeList.vue            # 分集列表（含进度条）
│       └── VideoPlayer.vue            # HTML5 video 封装（进度恢复 + 事件上报）
```

---

### Task 1: 项目脚手架与配置

**Files:**
- Create: `web/package.json`
- Create: `web/index.html`
- Create: `web/vite.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/src/main.ts`
- Create: `web/src/App.vue`（最小骨架，后续 Task 10 完善）

**Interfaces:**
- Produces: `web/` 可通过 `npm run dev` 启动，访问 `http://localhost:5174` 显示 `<router-view>`

- [ ] **Step 1: 初始化项目**

在项目根目录执行：
```bash
cd /Users/ninglu/CodeFromGithub/drama-flow
npm create vite@latest web -- --template vue-ts
```
选择：Vue → TypeScript（如果交互式询问则选这两项）。

- [ ] **Step 2: 安装依赖**

```bash
cd web
npm install pinia vue-router axios
```

- [ ] **Step 3: 写 vite.config.ts**

完整替换 `web/vite.config.ts`：
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@design': resolve(__dirname, '../design-system'),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: 引入设计 token**

在 `web/src/main.ts` 顶部加 import（其余内容后续步骤填充，这里先写骨架）：
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import '@design/tokens/tokens.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 5: 写最小 App.vue 骨架**

```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg-page); color: var(--color-text-primary); font-family: sans-serif; }
#app { min-height: 100vh; }
</style>
```

- [ ] **Step 6: 验证启动**

先启动后端（另一个终端）：
```bash
cd /Users/ninglu/CodeFromGithub/drama-flow
source backend/drama-flow/bin/activate && uvicorn backend.app.main:app --reload --port 8000
```

启动 web dev server：
```bash
cd web && npm run dev
```
预期：终端输出 `Local: http://localhost:5174/`，浏览器访问该地址不报编译错误。

---

### Task 2: API 层

**Files:**
- Create: `web/src/api/client.ts`
- Create: `web/src/api/auth.ts`
- Create: `web/src/api/dramas.ts`
- Create: `web/src/api/episodes.ts`
- Create: `web/src/api/watchRecords.ts`

**Interfaces:**
- Consumes: Vite proxy → `http://localhost:8000`
- Produces: 各模块导出的 async 函数，供 stores 调用。拦截器在 Task 3 完善（此 task 先建实例，不含 401 重试逻辑）

- [ ] **Step 1: 写 client.ts（无拦截器版本）**

```typescript
// web/src/api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Request 拦截器：注入 Token（Token 从 storage 读取）
client.interceptors.request.use((config) => {
  const token =
    localStorage.getItem('access_token') ||
    sessionStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response 拦截器占位（Task 3 完善 401 重试逻辑）
client.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
)

export default client
```

- [ ] **Step 2: 写 auth.ts**

```typescript
// web/src/api/auth.ts
import client from './client'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { nickname: string; email: string; password: string }
export interface RefreshPayload { refresh_token: string }

export interface UserResponse { id: number; nickname: string; email: string }
export interface TokenResponse {
  access_token: string
  refresh_token: string
  user: UserResponse
}

export const authApi = {
  login: (data: LoginPayload) =>
    client.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterPayload) =>
    client.post<UserResponse>('/auth/register', data),
  logout: () => client.post('/auth/logout'),
  refresh: (data: RefreshPayload) =>
    client.post<TokenResponse>('/auth/refresh', data),
}
```

- [ ] **Step 3: 写 dramas.ts**

```typescript
// web/src/api/dramas.ts
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

export const dramaApi = {
  list: (params?: { category?: string; page?: number; size?: number }) =>
    client.get<PaginatedDramas>('/dramas', { params }),
  detail: (id: number) => client.get<DramaDetail>(`/dramas/${id}`),
  categories: () => client.get<{ id: number; name: string; slug: string }[]>('/categories'),
}
```

- [ ] **Step 4: 写 episodes.ts**

```typescript
// web/src/api/episodes.ts
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

- [ ] **Step 5: 写 watchRecords.ts**

```typescript
// web/src/api/watchRecords.ts
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

export const watchRecordApi = {
  upsert: (episodeId: number, data: WatchRecordPayload) =>
    client.put<WatchRecord>(`/watch-records/${episodeId}`, data),
  get: (episodeId: number) =>
    client.get<WatchRecord>(`/watch-records/${episodeId}`),
  list: (params?: { page?: number; size?: number }) =>
    client.get<{ items: WatchRecord[]; total: number; page: number; size: number }>(
      '/watch-records', { params }
    ),
  continueWatching: () =>
    client.get<ContinueWatchingItem[]>('/watch-records/continue-watching'),
}
```

- [ ] **Step 6: 验证 API 可访问**

在浏览器控制台（`http://localhost:5174`）或临时在 `main.ts` 中加一行测试（测完删掉）：
```typescript
import axios from 'axios'
axios.get('/api/dramas').then(r => console.log(r.data))
```
预期：控制台打印剧集列表 JSON，无 CORS 或 404 错误。

---

### Task 3: Auth Store + 401 拦截器

**Files:**
- Create: `web/src/stores/auth.ts`
- Modify: `web/src/api/client.ts`（完善 response 拦截器）

**Interfaces:**
- Produces:
  - `useAuthStore()` — `{ user, isLoggedIn, login, logout, initFromStorage }`
  - `login(email, password, rememberMe)` → `Promise<void>`，成功后写 storage
  - `logout()` → 清 storage，跳 `/login`
  - `initFromStorage()` → 尝试用 refreshToken 恢复 session，供 `main.ts` 启动时调用

- [ ] **Step 1: 写 auth store**

```typescript
// web/src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserResponse } from '@/api/auth'

function getStorage(key: string): string | null {
  return localStorage.getItem(key) ?? sessionStorage.getItem(key)
}

function setStorage(key: string, value: string, persistent: boolean) {
  if (persistent) localStorage.setItem(key, value)
  else sessionStorage.setItem(key, value)
}

function clearStorage() {
  ;['access_token', 'refresh_token', 'remember_me'].forEach((k) => {
    localStorage.removeItem(k)
    sessionStorage.removeItem(k)
  })
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserResponse | null>(null)
  const isLoggedIn = ref(false)

  async function login(email: string, password: string, rememberMe: boolean) {
    const { data } = await authApi.login({ email, password })
    const persistent = rememberMe
    setStorage('access_token', data.access_token, persistent)
    setStorage('refresh_token', data.refresh_token, persistent)
    if (persistent) localStorage.setItem('remember_me', '1')
    user.value = data.user
    isLoggedIn.value = true
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    clearStorage()
    user.value = null
    isLoggedIn.value = false
  }

  async function refreshAccessToken(): Promise<string | null> {
    const refreshToken = getStorage('refresh_token')
    if (!refreshToken) return null
    try {
      const persistent = !!localStorage.getItem('remember_me')
      const { data } = await authApi.refresh({ refresh_token: refreshToken })
      setStorage('access_token', data.access_token, persistent)
      setStorage('refresh_token', data.refresh_token, persistent)
      user.value = data.user
      isLoggedIn.value = true
      return data.access_token
    } catch {
      clearStorage()
      user.value = null
      isLoggedIn.value = false
      return null
    }
  }

  async function initFromStorage() {
    const accessToken = getStorage('access_token')
    if (!accessToken) return
    // 尝试刷新以验证 token 有效性并获取最新用户信息
    await refreshAccessToken()
  }

  return { user, isLoggedIn, login, logout, refreshAccessToken, initFromStorage }
})
```

- [ ] **Step 2: 完善 client.ts 的 401 拦截器**

替换 `client.ts` 中的 response 拦截器部分（`interceptors.response.use` 那一块）：
```typescript
// 在文件顶部加（避免循环依赖，动态 import store）
let isRefreshing = false
let waitQueue: Array<(token: string) => void> = []

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }
    original._retry = true

    if (isRefreshing) {
      return new Promise((resolve) => {
        waitQueue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(client(original))
        })
      })
    }

    isRefreshing = true
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    const newToken = await authStore.refreshAccessToken()
    isRefreshing = false

    if (newToken) {
      waitQueue.forEach((cb) => cb(newToken))
      waitQueue = []
      original.headers.Authorization = `Bearer ${newToken}`
      return client(original)
    } else {
      waitQueue = []
      const { useRouter } = await import('vue-router')
      useRouter().push('/login')
      return Promise.reject(err)
    }
  }
)
```

- [ ] **Step 3: 在 main.ts 启动时恢复 session**

在 `web/src/main.ts` 的 `app.mount('#app')` 之前加：
```typescript
const authStore = useAuthStore(pinia)
await authStore.initFromStorage()
```

完整 `main.ts`：
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import '@design/tokens/tokens.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const authStore = useAuthStore(pinia)
await authStore.initFromStorage()

app.mount('#app')
```

- [ ] **Step 4: 验证**

后端运行的情况下，访问 `http://localhost:5174`，在浏览器控制台执行：
```javascript
// 模拟 token 过期后刷新
localStorage.setItem('access_token', 'expired_token')
localStorage.setItem('refresh_token', '真实的refresh_token')
// 然后刷新页面，观察 network 面板
// 预期：先看到 401 → 随即看到 POST /api/auth/refresh → 原请求用新 token 重试
```

---

### Task 4: Router + 导航守卫

**Files:**
- Create: `web/src/router/index.ts`

**Interfaces:**
- Consumes: `useAuthStore().isLoggedIn`
- Produces: router 实例，含 6 条路由和 `beforeEach` 守卫

- [ ] **Step 1: 写 router/index.ts**

```typescript
// web/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/pages/Login.vue'), meta: { public: true } },
  { path: '/register', component: () => import('@/pages/Register.vue'), meta: { public: true } },
  { path: '/', component: () => import('@/pages/Home.vue') },
  { path: '/drama/:id', component: () => import('@/pages/Detail.vue') },
  { path: '/drama/:id/episode/:ep', component: () => import('@/pages/Player.vue') },
  { path: '/history', component: () => import('@/pages/History.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && auth.isLoggedIn) {
    return { path: '/' }
  }
})

export default router
```

- [ ] **Step 2: 验证路由守卫**

浏览器访问 `http://localhost:5174/history`（未登录状态），预期：自动跳转到 `http://localhost:5174/login?redirect=%2Fhistory`。

---

### Task 5: Login 页 + Register 页

**Files:**
- Create: `web/src/pages/Login.vue`
- Create: `web/src/pages/Register.vue`

**Interfaces:**
- Consumes: `useAuthStore().login(email, password, rememberMe)`
- Produces: 登录成功 → 跳 `redirect` query 指定路径或 `/`；注册成功 → 跳 `/login`

- [ ] **Step 1: 写 Login.vue**

```vue
<!-- web/src/pages/Login.vue -->
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
        <div class="field-row">
          <label><input v-model="rememberMe" type="checkbox" /> 记住我</label>
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
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value, rememberMe.value)
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
}
.auth-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--color-text-secondary); }
.field input[type="email"],
.field input[type="password"] {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-primary);
  font-size: 1rem;
}
.field-row { display: flex; align-items: center; gap: var(--space-2); }
.error { color: var(--color-error); font-size: 0.875rem; }
.btn-primary {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 1rem;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--color-text-secondary); }
.link a { color: var(--color-primary); }
</style>
```

- [ ] **Step 2: 写 Register.vue**

```vue
<!-- web/src/pages/Register.vue -->
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
import { authApi } from '@/api/auth'

const router = useRouter()
const nickname = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  // 前端密码校验
  if (password.value.length < 8 || !/[A-Za-z]/.test(password.value) || !/\d/.test(password.value)) {
    error.value = '密码至少 8 位，需包含字母和数字'
    return
  }
  loading.value = true
  try {
    await authApi.register({ nickname: nickname.value, email: email.value, password: password.value })
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
/* 与 Login.vue 相同结构，复用 auth-page / auth-card / field / btn-primary 样式 */
.auth-page {
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center; background: var(--bg-page);
}
.auth-card {
  background: var(--bg-card); border-radius: var(--radius-lg);
  padding: var(--space-8); width: 360px; display: flex;
  flex-direction: column; gap: var(--space-4);
}
h1 { color: var(--color-primary); text-align: center; font-size: 1.5rem; }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field label { font-size: 0.875rem; color: var(--color-text-secondary); }
.field input {
  padding: var(--space-2) var(--space-3); background: var(--bg-input);
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  color: var(--color-text-primary); font-size: 1rem;
}
.error { color: var(--color-error); font-size: 0.875rem; }
.btn-primary {
  width: 100%; padding: var(--space-3); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-size: 1rem; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.link { text-align: center; font-size: 0.875rem; color: var(--color-text-secondary); }
.link a { color: var(--color-primary); }
</style>
```

- [ ] **Step 3: 验证登录注册流程**

1. 访问 `http://localhost:5174/login`，页面渲染登录表单
2. 输入已有账号（可从 test.db 查询或先注册），点击登录
3. 预期：跳转到 `http://localhost:5174/`（Home 页，现在显示空白或 router-view）
4. 再访问 `http://localhost:5174/register`，注册新账号，预期跳回 `/login`
5. 输入错误密码，预期显示"邮箱或密码错误"而非技术报错

---

### Task 6: 剧集列表（Home + DramaCard + drama store）

**Files:**
- Create: `web/src/stores/drama.ts`
- Create: `web/src/components/DramaCard.vue`
- Create: `web/src/pages/Home.vue`

**Interfaces:**
- Consumes: `dramaApi.list()` → `PaginatedDramas`
- Produces:
  - `useDramaStore()` — `{ dramas, loading, loadMore() }`
  - `<DramaCard :drama="item" />` — 点击 emit `click`，父组件处理跳转

- [ ] **Step 1: 写 drama store**

```typescript
// web/src/stores/drama.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dramaApi, type DramaListItem, type DramaDetail } from '@/api/dramas'

export const useDramaStore = defineStore('drama', () => {
  const dramas = ref<DramaListItem[]>([])
  const currentDrama = ref<DramaDetail | null>(null)
  const loading = ref(false)
  const page = ref(1)
  const hasMore = ref(true)

  async function loadDramas(reset = false) {
    if (loading.value || (!hasMore.value && !reset)) return
    if (reset) { dramas.value = []; page.value = 1; hasMore.value = true }
    loading.value = true
    try {
      const { data } = await dramaApi.list({ page: page.value, size: 20 })
      dramas.value.push(...data.items)
      hasMore.value = dramas.value.length < data.total
      page.value++
    } finally {
      loading.value = false
    }
  }

  async function loadDrama(id: number) {
    const { data } = await dramaApi.detail(id)
    currentDrama.value = data
    return data
  }

  return { dramas, currentDrama, loading, hasMore, loadDramas, loadDrama }
})
```

- [ ] **Step 2: 写 DramaCard.vue**

```vue
<!-- web/src/components/DramaCard.vue -->
<template>
  <div class="drama-card" @click="$emit('click')">
    <img :src="drama.cover_url" :alt="drama.title" class="cover" />
    <div class="info">
      <p class="title">{{ drama.title }}</p>
      <p class="meta">{{ drama.rating.toFixed(1) }} · {{ drama.episode_count }}集</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DramaListItem } from '@/api/dramas'
defineProps<{ drama: DramaListItem }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.drama-card {
  cursor: pointer; border-radius: var(--radius-md);
  overflow: hidden; background: var(--bg-card);
  transition: transform 0.15s;
}
.drama-card:hover { transform: translateY(-2px); }
.cover { width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block; }
.info { padding: var(--space-2); }
.title { font-size: 0.875rem; font-weight: 600; color: var(--color-text-primary); line-height: 1.3; }
.meta { font-size: 0.75rem; color: var(--color-text-secondary); margin-top: var(--space-1); }
</style>
```

- [ ] **Step 3: 写 Home.vue**

```vue
<!-- web/src/pages/Home.vue -->
<template>
  <div class="page">
    <NavBar />
    <main class="container">
      <div class="grid">
        <DramaCard
          v-for="drama in dramaStore.dramas"
          :key="drama.id"
          :drama="drama"
          @click="router.push(`/drama/${drama.id}`)"
        />
      </div>
      <div v-if="dramaStore.loading" class="loading">加载中...</div>
      <div v-if="!dramaStore.hasMore && dramaStore.dramas.length" class="end">已加载全部</div>
      <button
        v-if="dramaStore.hasMore && !dramaStore.loading"
        class="load-more"
        @click="dramaStore.loadDramas()"
      >加载更多</button>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import DramaCard from '@/components/DramaCard.vue'
import NavBar from '@/components/NavBar.vue'

const router = useRouter()
const dramaStore = useDramaStore()
onMounted(() => dramaStore.loadDramas(true))
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-page); }
.container { max-width: 1200px; margin: 0 auto; padding: var(--space-4); }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-4);
}
.loading, .end { text-align: center; color: var(--color-text-secondary); padding: var(--space-4); }
.load-more {
  display: block; margin: var(--space-4) auto; padding: var(--space-2) var(--space-6);
  background: var(--color-primary); color: #fff; border: none;
  border-radius: var(--radius-sm); cursor: pointer;
}
</style>
```

- [ ] **Step 4: 写 NavBar.vue**（被 Home.vue 引用，先在这里实现）

```vue
<!-- web/src/components/NavBar.vue -->
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
  border-bottom: 1px solid var(--color-border);
}
.brand { font-size: 1.25rem; font-weight: 700; color: var(--color-primary); text-decoration: none; }
.links { display: flex; align-items: center; gap: var(--space-4); }
.links a { color: var(--color-text-secondary); text-decoration: none; }
.links a.router-link-active { color: var(--color-primary); }
.logout {
  background: none; border: 1px solid var(--color-border);
  color: var(--color-text-secondary); padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm); cursor: pointer;
}
</style>
```

- [ ] **Step 5: 验证**

登录后访问 `http://localhost:5174/`，预期：显示剧集卡片网格，点击"加载更多"加载下一页，点击卡片跳转 `/drama/:id`（Detail 页暂时空白）。

---

### Task 7: 剧集详情（Detail + EpisodeList + watchRecord store）

**Files:**
- Create: `web/src/stores/watchRecord.ts`
- Create: `web/src/components/EpisodeList.vue`
- Create: `web/src/pages/Detail.vue`

**Interfaces:**
- Consumes:
  - `useDramaStore().loadDrama(id)` → `DramaDetail`
  - `episodeApi.list(dramaId)` → `Episode[]`
  - `useWatchRecordStore().fetchForDrama(episodeIds)` → 批量拉取进度
- Produces:
  - `useWatchRecordStore()` — `{ records, fetchRecord, fetchForDrama, cachedRecord(episodeId) }`
  - `<EpisodeList :episodes="list" :records="records" @select="onSelect" />`

- [ ] **Step 1: 写 watchRecord store**

```typescript
// web/src/stores/watchRecord.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { watchRecordApi, type WatchRecord, type ContinueWatchingItem } from '@/api/watchRecords'

export const useWatchRecordStore = defineStore('watchRecord', () => {
  // key: episode_id
  const records = ref<Record<number, WatchRecord>>({})
  const history = ref<ContinueWatchingItem[]>([])

  async function fetchRecord(episodeId: number): Promise<WatchRecord> {
    const { data } = await watchRecordApi.get(episodeId)
    records.value[episodeId] = data
    return data
  }

  async function fetchForEpisodes(episodeIds: number[]) {
    await Promise.all(episodeIds.map(fetchRecord))
  }

  function cachedRecord(episodeId: number): WatchRecord | undefined {
    return records.value[episodeId]
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

  return { records, history, fetchRecord, fetchForEpisodes, cachedRecord, saveProgress, fetchHistory }
})
```

- [ ] **Step 2: 写 EpisodeList.vue**

```vue
<!-- web/src/components/EpisodeList.vue -->
<template>
  <div class="episode-list">
    <div
      v-for="ep in episodes"
      :key="ep.id"
      class="episode-item"
      @click="$emit('select', ep)"
    >
      <div class="ep-info">
        <span class="ep-num">第 {{ ep.episode_number }} 集</span>
        <span class="ep-title">{{ ep.title }}</span>
        <span class="ep-duration">{{ ep.duration }}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressOf(ep.id) + '%' }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Episode } from '@/api/episodes'
import type { WatchRecord } from '@/api/watchRecords'

const props = defineProps<{
  episodes: Episode[]
  records: Record<number, WatchRecord>
}>()
defineEmits<{ select: [ep: Episode] }>()

function progressOf(episodeId: number): number {
  return props.records[episodeId]?.progress ?? 0
}
</script>

<style scoped>
.episode-list { display: flex; flex-direction: column; gap: var(--space-2); }
.episode-item {
  padding: var(--space-3); background: var(--bg-card);
  border-radius: var(--radius-sm); cursor: pointer;
  border: 1px solid var(--color-border);
}
.episode-item:hover { border-color: var(--color-primary); }
.ep-info { display: flex; gap: var(--space-3); align-items: center; margin-bottom: var(--space-2); }
.ep-num { color: var(--color-primary); font-weight: 600; font-size: 0.875rem; min-width: 60px; }
.ep-title { flex: 1; color: var(--color-text-primary); font-size: 0.875rem; }
.ep-duration { color: var(--color-text-secondary); font-size: 0.75rem; }
.progress-bar { height: 3px; background: var(--color-border); border-radius: 2px; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; transition: width 0.3s; }
</style>
```

- [ ] **Step 3: 写 Detail.vue**

```vue
<!-- web/src/pages/Detail.vue -->
<template>
  <div class="page">
    <NavBar />
    <div v-if="loading" class="loading">加载中...</div>
    <main v-else-if="drama" class="container">
      <div class="hero">
        <img :src="drama.cover_url" :alt="drama.title" class="cover" />
        <div class="meta">
          <h1>{{ drama.title }}</h1>
          <p class="sub">{{ drama.category_name }} · {{ drama.year }} · {{ drama.episode_count }}集</p>
          <p class="rating">评分：{{ drama.rating.toFixed(1) }}</p>
          <p class="desc">{{ drama.description }}</p>
          <button v-if="continueEp" class="btn-primary" @click="goEpisode(continueEp)">
            继续观看第 {{ continueEp.episode_number }} 集
          </button>
        </div>
      </div>
      <h2>剧集列表</h2>
      <EpisodeList
        :episodes="episodes"
        :records="wrStore.records"
        @select="goEpisode"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDramaStore } from '@/stores/drama'
import { useWatchRecordStore } from '@/stores/watchRecord'
import { episodeApi, type Episode } from '@/api/episodes'
import NavBar from '@/components/NavBar.vue'
import EpisodeList from '@/components/EpisodeList.vue'

const route = useRoute()
const router = useRouter()
const dramaStore = useDramaStore()
const wrStore = useWatchRecordStore()

const loading = ref(true)
const episodes = ref<Episode[]>([])
const dramaId = Number(route.params.id)

const drama = computed(() => dramaStore.currentDrama)

// 找到最近未看完的集数
const continueEp = computed(() => {
  return episodes.value.find((ep) => {
    const rec = wrStore.cachedRecord(ep.id)
    return rec && rec.progress > 0 && !rec.completed
  }) ?? null
})

function goEpisode(ep: Episode) {
  router.push(`/drama/${dramaId}/episode/${ep.id}`)
}

onMounted(async () => {
  await dramaStore.loadDrama(dramaId)
  const { data } = await episodeApi.list(dramaId)
  episodes.value = data
  await wrStore.fetchForEpisodes(data.map((ep) => ep.id))
  loading.value = false
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-page); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
.loading { text-align: center; padding: var(--space-8); color: var(--color-text-secondary); }
.hero { display: flex; gap: var(--space-6); margin-bottom: var(--space-6); }
.cover { width: 200px; border-radius: var(--radius-md); object-fit: cover; flex-shrink: 0; }
.meta { flex: 1; display: flex; flex-direction: column; gap: var(--space-2); }
h1 { font-size: 1.5rem; color: var(--color-text-primary); }
.sub, .rating { font-size: 0.875rem; color: var(--color-text-secondary); }
.desc { color: var(--color-text-primary); line-height: 1.6; }
h2 { font-size: 1.125rem; margin-bottom: var(--space-3); color: var(--color-text-primary); }
.btn-primary {
  padding: var(--space-2) var(--space-4); background: var(--color-primary);
  color: #fff; border: none; border-radius: var(--radius-sm); cursor: pointer;
  font-size: 0.875rem; align-self: flex-start;
}
</style>
```

- [ ] **Step 4: 验证**

访问 `http://localhost:5174/drama/1`（假设 id=1 存在），预期：显示剧集封面、简介、分集列表，已有观看进度的集数显示进度条。点击某集跳转到 `/drama/1/episode/:ep`（Player 页暂时空白）。

---

### Task 8: 视频播放器（VideoPlayer + Player 页）

**Files:**
- Create: `web/src/components/VideoPlayer.vue`
- Create: `web/src/pages/Player.vue`

**Interfaces:**
- Consumes:
  - `episodeApi.videoUrl(episodeId)` → `{ url, expires_at }`
  - `useWatchRecordStore().fetchRecord(episodeId)` → `WatchRecord.last_position`
  - `useWatchRecordStore().saveProgress(episodeId, currentTime, duration, completed)`
- Produces:
  - `<VideoPlayer :src :startPosition @progress @ended />` 组件

- [ ] **Step 1: 写 VideoPlayer.vue**

```vue
<!-- web/src/components/VideoPlayer.vue -->
<template>
  <div class="video-wrapper">
    <video
      ref="videoEl"
      controls
      class="video"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @pause="onPause"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{
  src: string
  startPosition: number  // seconds
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
  emitProgress() // 离开前保存一次
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

function onTimeUpdate() {
  // 由定时器控制保存，这里不做处理
}

function onPause() {
  emitProgress()
}

function onEnded() {
  emit('ended')
}
</script>

<style scoped>
.video-wrapper { width: 100%; background: #000; }
.video { width: 100%; max-height: 70vh; display: block; }
</style>
```

- [ ] **Step 2: 写 Player.vue**

```vue
<!-- web/src/pages/Player.vue -->
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
  // 并行获取：视频 URL + 进度 + 分集列表（找下一集）
  const [urlResp, recordResp, episodesResp] = await Promise.all([
    episodeApi.videoUrl(episodeId),
    wrStore.fetchRecord(episodeId),
    episodeApi.list(dramaId),
  ])

  videoUrl.value = urlResp.data.url
  startPosition.value = recordResp.last_position ?? 0

  const episodes = episodesResp.data
  episode.value = episodes.find((ep) => ep.id === episodeId) ?? null
  const idx = episodes.findIndex((ep) => ep.id === episodeId)
  nextEpisode.value = idx >= 0 && idx < episodes.length - 1 ? episodes[idx + 1] : null

  loading.value = false
})
</script>

<style scoped>
.player-page { min-height: 100vh; background: var(--bg-page); }
.loading { text-align: center; padding: var(--space-8); color: var(--color-text-secondary); }
.player-container { max-width: 1000px; margin: 0 auto; padding: var(--space-4); }
.info { padding: var(--space-4) 0; }
.info h2 { color: var(--color-text-primary); }
.next-hint { margin-top: var(--space-2); color: var(--color-text-secondary); font-size: 0.875rem; }
</style>
```

- [ ] **Step 3: 验证**

访问 `/drama/1/episode/1`（假设有效 id），预期：
- 视频播放器出现，视频加载并自动定位到上次进度
- 播放约 10 秒后，network 面板出现 `PUT /api/watch-records/1`
- 播放结束后，自动跳转到下一集（若有）

---

### Task 9: 观看历史（History 页）

**Files:**
- Create: `web/src/pages/History.vue`

**Interfaces:**
- Consumes: `useWatchRecordStore().fetchHistory()` → `ContinueWatchingItem[]`

- [ ] **Step 1: 写 History.vue**

```vue
<!-- web/src/pages/History.vue -->
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
import { type ContinueWatchingItem } from '@/api/watchRecords'
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
  await wrStore.fetchHistory()
  loading.value = false
})
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-page); }
.container { max-width: 900px; margin: 0 auto; padding: var(--space-6); }
h1 { font-size: 1.5rem; color: var(--color-text-primary); margin-bottom: var(--space-4); }
.loading, .empty { color: var(--color-text-secondary); text-align: center; padding: var(--space-8); }
.history-list { display: flex; flex-direction: column; gap: var(--space-3); }
.history-item {
  display: flex; gap: var(--space-4); padding: var(--space-3);
  background: var(--bg-card); border-radius: var(--radius-md);
  cursor: pointer; border: 1px solid var(--color-border);
}
.history-item:hover { border-color: var(--color-primary); }
.cover { width: 80px; height: 110px; object-fit: cover; border-radius: var(--radius-sm); flex-shrink: 0; }
.info { flex: 1; display: flex; flex-direction: column; gap: var(--space-1); }
.title { font-weight: 600; color: var(--color-text-primary); }
.sub { font-size: 0.875rem; color: var(--color-text-secondary); }
.progress-bar { height: 3px; background: var(--color-border); border-radius: 2px; margin: var(--space-1) 0; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; }
.time { font-size: 0.75rem; color: var(--color-text-secondary); }
</style>
```

- [ ] **Step 2: 验证**

访问 `http://localhost:5174/history`，预期：显示观看历史列表，每条记录有剧名、集数、进度条，点击跳转到对应 Player 页并从上次进度续播。

---

## Self-Review

**Spec 覆盖检查：**
- ✅ 登录 / 注册（Task 5）
- ✅ 剧集列表（Task 6）
- ✅ 剧集详情 + 分集列表 + 进度条（Task 7）
- ✅ 视频播放 + 进度恢复 + 10 秒自动保存（Task 8）
- ✅ 观看历史（Task 9）
- ✅ "记住我"：localStorage vs sessionStorage（Task 3）
- ✅ Token 过期 → 静默刷新 → 失败才跳登录（Task 3）
- ✅ 路由守卫（Task 4）
- ✅ 设计 token 引用（Task 1）
- ✅ 播放完毕跳下一集（Task 8）
- ✅ "继续观看"按钮（Task 7）

**类型一致性：**
- `saveProgress(episodeId, currentTime, duration, completed)` — Task 7 store 定义，Task 8 Player 使用，签名一致
- `fetchForEpisodes(episodeIds: number[])` — Task 7 store 定义，Detail.vue 使用，一致
- `ContinueWatchingItem` — watchRecords.ts 定义，History.vue 使用，一致

**无 TBD / 占位符**：所有步骤含完整代码。

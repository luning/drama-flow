# Web 客户端设计文档

**日期：** 2026-06-25  
**范围：** 新建 `web/` 独立 Web 应用，复刻 Android 客户端完整功能，通过浏览器本地访问

---

## 背景与目标

项目已有 Android 原生客户端（auth/home/detail/player/history 五个模块）和嵌入 WebView 的 H5（Home + Detail 两个页面）。现需新增一个可在本地浏览器直接访问的 Web 客户端，覆盖与 Android 一致的完整功能。

**核心约束：**
- Android + H5（WebView）与 Web 客户端并行发展，共用同一套后端 API
- Android 的 native/H5 分工边界不受影响
- H5 保持现状（仅 Home + Detail，服务于 WebView）
- Web 客户端完全独立，位于新建的 `web/` 目录

---

## 架构决策

### 为什么新建 `web/` 而非扩展 H5

H5 通过 JSBridge（`window.DramaFlowBridge`）依赖 Android 处理认证和视频播放。若将 H5 扩展为完整 Web App，则 Android 的 WebView 必须同步调整（要么 native 页面减少，要么 H5 内维护双套逻辑），破坏现有分工边界。

新建独立 `web/` 保持三端边界清晰：Android native、H5 WebView、Web 浏览器各自独立演进，只共享后端这一层。

---

## 技术栈

| 模块 | 技术选型 |
|------|---------|
| 框架 | Vue3 + Vite + TypeScript |
| 状态管理 | Pinia |
| 路由 | Vue Router（history 模式） |
| HTTP | Axios（含拦截器） |
| 视频播放 | HTML5 原生 `<video>` |
| 样式 | design-system/tokens/tokens.css（复用设计 token） |

---

## 项目结构

```
web/
├── src/
│   ├── api/
│   │   ├── client.ts         # axios 实例 + 拦截器
│   │   ├── auth.ts           # 登录、注册、登出、刷新
│   │   ├── dramas.ts         # 剧集列表、详情
│   │   ├── episodes.ts       # 分集列表、签名 URL
│   │   └── watchRecords.ts   # 观看记录 CRUD
│   ├── stores/
│   │   ├── auth.ts           # 登录态、token 管理
│   │   ├── drama.ts          # 剧集数据
│   │   └── watchRecord.ts    # 观看进度
│   ├── pages/
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── Home.vue
│   │   ├── Detail.vue
│   │   ├── Player.vue
│   │   └── History.vue
│   ├── components/
│   │   ├── DramaCard.vue
│   │   ├── EpisodeList.vue
│   │   └── VideoPlayer.vue
│   ├── router/
│   │   └── index.ts          # 路由表 + 守卫
│   └── main.ts
├── index.html
├── vite.config.ts
└── package.json
```

---

## 路由设计

| 路径 | 页面 | 需要登录 |
|------|------|---------|
| `/login` | Login.vue | 否 |
| `/register` | Register.vue | 否 |
| `/` | Home.vue（剧集列表） | 是 |
| `/drama/:id` | Detail.vue（详情 + 分集） | 是 |
| `/drama/:id/episode/:ep` | Player.vue（视频播放） | 是 |
| `/history` | History.vue（观看历史） | 是 |

**路由守卫：** 未登录访问需认证页面自动跳转 `/login`，登录成功后重定向回原目标路径。

---

## 认证与状态管理

### Auth Store

```
authStore
├── state: { user, accessToken, refreshToken }
├── login(email, password, rememberMe)
│   ├── rememberMe=true  → localStorage 持久化（关闭浏览器后保留）
│   └── rememberMe=false → sessionStorage（关闭标签页后清除）
├── logout()             → 清除对应存储 + 跳转 /login
├── refreshAccessToken() → 用 refreshToken 换新 accessToken
└── initFromStorage()    → 应用启动时从 storage 恢复登录态
```

### Axios 拦截器

- **Request 拦截：** 自动注入 `Authorization: Bearer <accessToken>`
- **Response 拦截：** 检测 401 → 调用 `refreshAccessToken()` → 成功则重试原请求 → 失败则 `logout()`

行为与 Android 一致：Token 过期静默刷新，刷新失败才跳登录页。

---

## 视频播放器

### 进度恢复流程

```
进入 Player 页面
├── GET /api/episodes/:id/signed-url   → 获取播放 URL
├── GET /api/watch-records（缓存）      → 获取上次进度 position（秒）
├── video.src = signedUrl
└── video.addEventListener('loadedmetadata', () => {
       video.currentTime = position
    })

播放中
└── 每 10 秒 PATCH /api/watch-records 更新进度

页面离开 / 暂停超过 3 秒
└── 立即保存当前 currentTime

播放完毕
├── 标记该集 completed = true
└── 自动跳转下一集（若有）
```

### VideoPlayer 组件接口

```vue
<VideoPlayer
  :src="signedUrl"
  :startPosition="lastPosition"
  @progress="onProgress"
  @ended="onEnded"
/>
```

VideoPlayer 只管播放控制，Player.vue 只管数据获取与进度同步，职责分离。

---

## 各页面职责

### Home.vue — 剧集列表
- 加载 `GET /api/dramas`，展示 DramaCard 列表
- 支持分页（下拉加载更多）
- 点击跳转 `/drama/:id`

### Detail.vue — 剧集详情
- 展示剧集简介 + EpisodeList
- 每集显示观看进度条（从 watchRecord store 读取）
- "继续观看"按钮定位到上次未看完的集数
- 点击某集跳转 `/drama/:id/episode/:ep`

### History.vue — 观看历史
- `GET /api/watch-records`，按最近观看时间倒序
- 每条记录：剧名、当前集数、进度百分比
- 点击直接跳转对应 Player 并恢复进度

### Login.vue / Register.vue — 认证
- 表单校验与 Android 一致（邮箱格式、密码 8 位含字母+数字）
- Login 页含"记住我"复选框
- 错误信息用用户语言展示，不暴露技术细节（如 401 → "邮箱或密码错误"）

---

## 与现有系统的关系

| 资产 | 关系 |
|------|------|
| 后端 API | 完全复用，Web 直接调用同一套接口 |
| design-system/tokens/ | 复用 tokens.css，通过 `@import` 引入 |
| H5（h5/） | 无依赖，独立演进 |
| Android | 无依赖，共享后端 |

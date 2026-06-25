# h5/ 统一前端设计文档

**日期：** 2026-06-25  
**目标：** 删除 `web/`，以 `h5/` 为唯一前端代码库，同时服务 Android WebView 和浏览器两个入口。

---

## 背景

项目目前存在两套前端：
- `web/`：功能更完整（6 个页面），面向浏览器，使用 `createWebHistory`，有认证守卫
- `h5/`：面向 Android WebView，使用 hash 路由，有 JSBridge 集成，但只有 Home 和 Detail 两个页面

Android 原生没有用到任何 native 独有功能，WebView 和浏览器加载相同 H5 完全可行。维护两套代码带来额外成本，统一后改一处即可。

---

## 架构决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| 权威代码库 | `h5/` | JSBridge 集成已就位，迁移成本低 |
| 路由模式 | hash（`createWebHashHistory`） | WebView 加载本地文件天然支持；该项目不需要 SEO |
| 认证方式 | 双轨：浏览器走 Login 页、WebView 走 JSBridge token 注入 | `h5/src/stores/auth.ts` 的 `syncTokenFromNative()` 已实现 |
| 播放器 | 运行时检测：WebView 调 JSBridge、浏览器用 H5 VideoPlayer | 零配置，同一页面适配两端 |

---

## 需要做的改动

### 1. 保存并合并 `web/` 未提交改动

`web/` 有三处未提交改动，必须先合并进 `h5/`，再删除 `web/`：

- **`web/src/api/dramas.ts`** → 合并进 `h5/src/api/dramas.ts`
  - 新增 TypeScript interface：`DramaListItem`、`DramaDetail`、`PaginatedDramas`、`Banner`
  - 新增对象风格 `dramaApi`（可与现有函数风格并存，或替换）
- **`web/src/pages/Home.vue`** → diff 后合并进 `h5/src/pages/Home.vue`
- **`web/src/components/BannerCarousel.vue`**（新文件）→ 复制进 `h5/src/components/`

### 2. 补入缺失组件

从 `web/src/components/` 复制，适配 design-system token：
- `NavBar.vue`
- `VideoPlayer.vue`

### 3. 补入缺失页面

从 `web/src/pages/` 移植，适配 h5/ 的函数式 API 风格：
- `Login.vue`
- `Register.vue`
- `History.vue`
- `Player.vue`（见下方播放器逻辑）

### 4. Player 页面——环境检测逻辑

`Player.vue` 在 `onMounted` 时做一次检测：

```
if (window.DramaFlowBridge) {
  // WebView 环境：委托原生播放器，H5 不渲染 VideoPlayer
  window.DramaFlowBridge.openPlayer(dramaId, episodeId)
  router.back()  // 或展示"正在原生播放"提示
} else {
  // 浏览器环境：正常加载签名 URL，渲染 VideoPlayer
  loadVideoUrl()
}
```

Android 侧行为不变（JSBridge 收到 `openPlayer` 后打开 ExoPlayer）。观看记录在两端分别由各自逻辑写入，不依赖 H5 Player 页面。

### 5. 路由补全 + auth guard

在 `h5/src/router/index.ts` 中：

新增路由：
```
/login          → Login.vue     (public: true)
/register       → Register.vue  (public: true)
/drama/:id/episode/:ep → Player.vue
/history        → History.vue
```

新增 `beforeEach` 守卫：
```
- 未登录 + 非 public 路由 → 跳 /login
- 例外：WebView 环境（window.DramaFlowBridge 存在）→ 跳过守卫，由 syncTokenFromNative() 在 App.vue 初始化时注入 token
```

### 6. App.vue 初始化

在 `App.vue` 的 `onMounted` 中调用 `authStore.syncTokenFromNative()`，确保 WebView 环境下 token 在路由守卫执行前已就位。`h5/src/stores/auth.ts` 已实现该方法，无需修改。

### 7. 删除 `web/`

全部改动验证无误后删除 `web/` 目录。

---

## 不需要改动的部分

- `h5/src/stores/auth.ts`：已有完整的 login/logout/syncTokenFromNative/tryRestoreSession
- `h5/src/api/auth.ts`：接口完整
- `h5/src/api/client.ts`：token 注入逻辑已就位
- `h5/src/components/` 现有组件：Banner、CategoryTabs、ContinueWatching、DramaCard、EpisodeList
- hash 路由模式：保持不变

---

## 文件变更汇总

| 操作 | 文件 |
|---|---|
| 修改 | `h5/src/api/dramas.ts` |
| 修改 | `h5/src/pages/Home.vue` |
| 修改 | `h5/src/router/index.ts` |
| 修改 | `h5/src/App.vue` |
| 新增 | `h5/src/components/NavBar.vue` |
| 新增 | `h5/src/components/VideoPlayer.vue` |
| 新增 | `h5/src/components/BannerCarousel.vue` |
| 新增 | `h5/src/pages/Login.vue` |
| 新增 | `h5/src/pages/Register.vue` |
| 新增 | `h5/src/pages/Player.vue` |
| 新增 | `h5/src/pages/History.vue` |
| 删除 | `web/`（整个目录） |

---

## 验收标准

- [ ] 浏览器访问 `http://localhost:5173/#/`，未登录时跳转到 `/#/login`
- [ ] 浏览器登录后可正常浏览首页、剧集详情、历史记录
- [ ] 浏览器 Player 页面能播放视频（H5 VideoPlayer）
- [ ] Android WebView 加载 H5，token 由 JSBridge 注入，无需经过登录页
- [ ] Android WebView 进入 Player 页面时调用 `DramaFlowBridge.openPlayer()`，不渲染 H5 VideoPlayer
- [ ] `web/` 目录已删除，项目根目录只有 `h5/` 一套前端

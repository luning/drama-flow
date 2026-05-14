# DramaFlow 可执行规格说明 (SPEC.md)

> 覆盖范围：迭代 1 + 迭代 2 核心领域模型，迭代 3 增量更新（标注 [Changed] 的项目为迭代 3 变更）

---

## 一、User 用户领域

### 领域名词

| 术语 | 定义 |
|------|------|
| User | 注册用户，拥有邮箱和密码凭证 |
| JWT Token | JSON Web Token，服务端签发的认证令牌 |
| Access Token | 短期令牌（默认 2h），用于 API 请求鉴权 |
| Refresh Token | 长期令牌（默认 7d），用于静默续期 Access Token |

### 前置条件

- 系统已初始化 SQLite 数据库和 User 表
- FastAPI 服务已配置 JWT 密钥和过期时间
- Android 端已集成网络请求库（Retrofit/OkHttp）

### 主流程

1. **注册**
   - 用户填写昵称、邮箱、密码
   - 客户端提交 POST `/api/auth/register` 请求
   - 服务端校验邮箱格式和密码强度
   - 邮箱未被注册 → 创建用户记录，bcrypt 加密密码
   - 返回 `201 Created` + 用户基本信息（不含密码）
   - 客户端跳转到登录页

2. **登录** [Changed - 迭代3 增强记住我逻辑]
   - 用户输入邮箱 + 密码
   - 客户端提交 POST `/api/auth/login`
   - 服务端校验邮箱是否存在、密码是否匹配
   - 校验通过 → 签发 JWT Access Token + Refresh Token
   - 返回 `200 OK` + `{ access_token, refresh_token, user }`
   - 如果勾选"记住我"：Token 持久化存入 EncryptedSharedPreferences，下次启动 App 时自动加载并验证有效性
   - 未勾选"记住我"：Token 仅存内存（ViewModel），App 退出后需重新登录

3. **登出**
   - 客户端调用 POST `/api/auth/logout`（携带 Access Token）
   - 服务端将 Token 加入黑名单（可选：Redis / 内存 Set）
   - 返回 `200 OK`
   - Android 端清除本地 Token 缓存，跳转登录页
   - 主页提供退出登录入口（`popUpToInclusive=true` 清除回退栈）

4. **Token 刷新** [Changed - 迭代3 完整实现]
   - 客户端检测 Access Token 过期
   - 使用 Refresh Token 调用 POST `/api/auth/refresh`
   - 服务端验证 Refresh Token 有效性
   - 签发新的 Access Token 返回

### 异常处理

| 异常场景 | 错误响应 | 处理方式 |
|---------|---------|---------|
| 邮箱已注册 | 409 Conflict + "邮箱已被注册" | 显示错误提示 |
| 邮箱格式无效 | 422 Validation Error | 前端表单校验提示 |
| 密码强度不足 | 422 密码至少 8 位含字母+数字 | 表单实时校验 |
| 登录凭证错误 | 401 Unauthorized | 清空密码框，显示"邮箱或密码错误" |
| Token 过期 | 401 Token expired | 尝试 Refresh Token 自动续期 |
| Refresh Token 失效 | 401 重新登录 | 跳转登录页 |

### 验收标准 (AC)

| AC-ID | 描述 | 关联 |
|-------|------|------|
| AC-USER-01 | 用户可以使用邮箱+密码成功注册新账号 | 注册流程 |
| AC-USER-02 | 注册时重复邮箱返回 409 错误 | 异常处理 |
| AC-USER-03 | 注册成功后用户可以立即登录 | 登录流程 |
| AC-USER-04 | 用户可以使用正确的邮箱+密码登录 | 登录流程 |
| AC-USER-05 | 登录成功后返回有效的 JWT Token（包含用户 ID 和过期时间） | 登录流程 |
| AC-USER-06 | 登录错误密码返回 401 且不泄露用户是否存在 | 异常处理 |
| AC-USER-07 | 用户可以成功登出，登出后 Token 不可再用 | 登出流程 |
| AC-USER-08 | 所有认证接口返回符合 OpenAPI 规范的错误格式 | 通用 |
| AC-USER-09 | Token 中包含用户 ID 和角色信息，可解码验证 | JWT |
| AC-USER-10 | 登录勾选"记住我"后，Token 持久化存入 EncryptedSharedPreferences，重启 App 后自动加载并保持登录状态 | 迭代3 新增 |
| AC-USER-11 | Access Token 过期时自动使用 Refresh Token 续期，用户无感知 | 迭代3 新增 |
| AC-USER-12 | Refresh Token 失效后静默跳转登录页，不产生白屏或崩溃 | 迭代3 新增 |

---

## 二、Drama 剧集领域

### 领域名词

| 术语 | 定义 |
|------|------|
| Drama | 一部短剧，包含标题、描述、封面、分类等信息 |
| Category | 分类标签（甜宠/悬疑/搞笑/奇幻/霸总等） |
| Banner | 首页顶部轮播推荐位，关联 Drama |
| Rating | 评分，1-5 星，带小数点（如 4.8） |

### 前置条件

- SQLite 数据库已初始化 Drama 表
- `seed-data` Skill 已导入测试数据（至少 12 部剧集）
- FastAPI `/api/dramas` 路由已注册

### 主流程

1. **获取剧集列表** [Changed - 迭代3 新增个性化推荐]
   - 客户端 GET `/api/dramas?category={cat}&page={n}&size={m}`
   - 未登录用户或无分类参数时：按分类筛选（不传分类返回全量），按更新时间降序排列
   - 已登录用户且未指定分类时：基于用户观看历史（WatchRecord）进行个性化排序，优先级：同类未看（最高）→ 进行中 → 其他未看 → 已全部看完（最低），同层按评分降序。"已看完"指某剧的所有集都已完成（completed=true）
   - 支持分页：`page` 从 1 开始，`size` 默认 20
   - 返回 `200 OK` + `{ items: [...], total, page, size }`

2. **获取 Banner 列表**
   - 客户端 GET `/api/banners`
   - 服务端返回热门推荐的 Drama 列表（3-5 部）
   - 每项包含 `{ drama_id, title, image_url, sort_order }`

3. **获取剧集详情**
   - 客户端 GET `/api/dramas/{drama_id}`
   - 服务端返回完整剧集信息：标题、描述、封面、分类、评分、总集数、年份、状态（连载/完结）
   - 返回 `200 OK` + Drama 详情

4. **获取分类列表**
   - 客户端 GET `/api/categories`
   - 服务端返回可用分类列表
   - 返回 `200 OK` + `[{ id, name, icon }]`

### 异常处理

| 异常场景 | 错误响应 | 处理方式 |
|---------|---------|---------|
| 分类参数无效 | 400 无效分类 | 默认返回"全部"分类 |
| 页码超出范围 | 200 空数组 | 返回空列表 |
| 剧集不存在 | 404 Drama not found | 显示"剧集不存在" |

### 验收标准 (AC)

| AC-ID | 描述 | 关联 |
|-------|------|------|
| AC-DRAMA-01 | 首页按分类展示剧集列表，支持分页；已登录用户未指定分类时返回个性化推荐 | 列表接口 [Changed] |
| AC-DRAMA-02 | 不传分类参数时：未登录用户返回全量剧集，已登录用户返回个性化推荐 | 列表接口 [Changed] |
| AC-DRAMA-03 | Banner 返回 3-5 部推荐剧集 | Banner |
| AC-DRAMA-04 | 剧集详情接口返回完整信息（标题/描述/封面/分类/评分/集数） | 详情接口 |
| AC-DRAMA-05 | 请求不存在的剧集返回 404 | 异常处理 |
| AC-DRAMA-06 | 剧集按照更新时间降序排列 | 排序 |
| AC-DRAMA-07 | 已登录用户访问首页时，剧集列表基于观看历史进行个性化排序：同类未看 → 进行中 → 其他未看 → 已看完降权；同层内按评分降序 | 迭代3 新增 [Changed] |
| AC-DRAMA-08 | 用户已全部看完的剧集（所有集 completed=true）在推荐列表中权重最低（priority 3），避免重复推荐。进行中的剧集排在已看完之前 | 迭代3 新增 [Changed] |
| AC-DRAMA-09 | 未登录用户不受个性化推荐影响，按默认排序展示全量剧集 | 迭代3 新增 |

---

## 三、Episode 剧集领域

### 领域名词

| 术语 | 定义 |
|------|------|
| Episode | 剧集的单集，包含标题、序号、时长、视频 URL |
| Video URL | 七牛云 CDN 签名 URL，有时效性 |
| Episode Number | 集号，从 1 开始递增 |

### 前置条件

- SQLite 数据库已初始化 Episode 表，与 Drama 表通过 `drama_id` 外键关联
- `seed-data` Skill 已导入测试数据（每部剧集至少 10 集）
- 七牛云 Bucket 已配置，AccessKey + SecretKey 可用

### 主流程

1. **获取剧集的集数列表**
   - 客户端 GET `/api/dramas/{drama_id}/episodes`
   - 服务端按 `episode_number` 升序返回该剧集的所有集
   - 返回 `200 OK` + `[{ id, episode_number, title, duration, video_url, created_at }]`

2. **获取单集详情**
   - 客户端 GET `/api/episodes/{episode_id}`
   - 返回单集完整信息
   - 返回 `200 OK` + Episode 详情

3. **获取视频签名 URL**
   - 客户端 GET `/api/episodes/{episode_id}/video-url`
   - 服务端生成七牛云 CDN 签名 URL（有效期 1h）
   - 返回 `200 OK` + `{ url, expires_at }`

### 异常处理

| 异常场景 | 错误响应 | 处理方式 |
|---------|---------|---------|
| 剧集 ID 无效 | 404 Episode not found | 提示剧集不存在 |
| Drama ID 无效 | 404 Drama not found | 提示剧集不存在 |
| 视频 URL 无法生成 | 502 CDN service error | 显示"视频加载失败" |
| 视频 URL 过期 | 401/403 | 客户端重新请求签名 URL |

### 验收标准 (AC)

| AC-ID | 描述 | 关联 |
|-------|------|------|
| AC-EP-01 | 返回的集数列表按序号升序排列 | 列表接口 |
| AC-EP-02 | 每集包含标题、时长、序号、视频 URL | 列表接口 |
| AC-EP-03 | 视频签名 URL 有效期内可正常播放 | 签名接口 |
| AC-EP-04 | URL 过期后重新请求可获取新签名 | 签名接口 |
| AC-EP-05 | 请求不存在的单集返回 404 | 异常处理 |

---

## 四、WatchRecord 观看记录领域

### 领域名词

| 术语 | 定义 |
|------|------|
| WatchRecord | 用户对某一集的观看记录 |
| Progress | 播放进度百分比（0-100%） |
| LastPosition | 上次播放位置（秒） |
| Completed | 是否观看完成（进度 > 90% 视为完成） |

### 前置条件

- SQLite 数据库已初始化 WatchRecord 表，关联 User 和 Episode
- 用户已登录（有效的 JWT Token）
- 播放器已集成 ExoPlayer，可获取当前播放位置

### 主流程

1. **记录播放进度**
   - Android 端每隔 15s 调用 PUT `/api/watch-records/{episode_id}`
   - 或在暂停/退出播放器时立即上报
   - 请求体：`{ progress, last_position, completed }`
   - 服务端 upsert 逻辑：同一用户 + 同一集存在则更新，不存在则创建
   - 返回 `200 OK` + 更新后的记录

2. **获取用户的观看记录**
   - 客户端 GET `/api/watch-records?page={n}&size={m}`
   - 服务端返回当前用户的所有观看记录，按更新时间降序
   - 关联返回 Drama 基本信息（标题、封面）
   - 返回 `200 OK` + `{ items: [...], total, page, size }`

3. **获取单集续播位置**
   - 客户端 GET `/api/watch-records/{episode_id}`
   - 服务端返回该用户对该集的观看进度
   - 返回 `200 OK` + `{ progress, last_position, completed, updated_at }`

4. **获取继续观看列表**
   - 客户端 GET `/api/watch-records/continue-watching`
   - 服务端返回未看完的最近 5 条记录
   - 按更新时间降序，剔除已完成（completed=true）的记录
   - 返回 `200 OK` + `[{ drama_info, episode_info, progress, last_position }]`

5. **播放完成连播**
   - 当前集播放结束（ExoPlayer STATE_ENDED），自动上报 `completed = true`
   - Player 检测 `episode_number < total_episodes`：
     - 条件满足 → 加载下一集的 `video_url` 并开始播放
     - 条件不满足 → 显示"全部剧集已播放完毕"提示，延迟后返回剧集详情页
   - 自动连播期间短暂显示切换提示（如"正在播放第 X 集"）
   - 跨集切换时确保旧的协程任务被取消，避免竞态

### 异常处理

| 异常场景 | 错误响应 | 处理方式 |
|---------|---------|---------|
| 未登录请求记录 | 401 Unauthorized | 跳转登录 |
| Episode ID 无效 | 404 Episode not found | 忽略该记录 |
| Progress 超出范围 | 422 Progress应在0-100 | 客户端 clamp |
| 无观看记录 | 200 空数组 | 继续观看区域隐藏 |

### 验收标准 (AC)

| AC-ID | 描述 | 关联 |
|-------|------|------|
| AC-WR-01 | 用户播放某集后，服务端正确记录进度 | 记录接口 |
| AC-WR-02 | 再次播放同一集时返回上次播放位置 | 续播接口 |
| AC-WR-03 | 观看记录按更新时间降序排列 | 列表接口 |
| AC-WR-04 | 继续观看列表不包含已完成的剧集 | 继续观看接口 |
| AC-WR-05 | 未登录用户无法访问观看记录 | 鉴权 |
| AC-WR-06 | 同一用户重复上报同一集只保留最新记录（upsert） | 幂等性 |
| AC-WR-07 | 非最后一集播放结束后自动加载并播放下一集 | 自动连播 |
| AC-WR-08 | 最后一集播放结束后回到剧集详情页（H5 Detail 页面） | 全部播放完成 |
| AC-WR-09 | 自动连播时显示切换提示（如 Toast "正在播放第 X 集"） | 用户体验 |
| AC-WR-10 | PlayerActivity 关闭后自然返回前一页，不回到系统桌面 | 导航栈 |

---

## 五、视觉验收规范

### 领域名词

| 术语 | 定义 |
|------|------|
| 设计 Token | `design_system.md` 中定义的颜色/字体/间距/圆角变量 |
| 关键页面 | 首页、详情页、播放器、登录/注册 — 视觉验收在这 4 个页面上执行 |

### 前置条件

- `design_system.md` 已定义完整的设计 Token
- 交互原型（`prototype/index.html`）可在浏览器中正常运行

### 验收标准 (AC)

| AC-ID | 描述 | 验证方法 | 关联 |
|-------|------|---------|------|
| AC-VIS-01 | 颜色通过 CSS 变量引用 `design_system.md` 中的 Token，源文件中无硬编码色值 | `grep` 扫描 `#` 色值 | 色彩系统 |
| AC-VIS-02 | 4 个关键页面均为深色主题，无白底透出 | 逐页视觉检查 | 暗色主题 |
| AC-VIS-03 | 首页：Banner 宽高比约 16:7，剧集卡片 2 列等宽网格，间距 12px，左右 padding 16px | 首页截图目视检查 | 首页布局 |
| AC-VIS-04 | 播放器：控制条为半透明渐变层叠在视频之上，点击画面可切换显示/隐藏 | 播放页截图目视检查 | 播放器 |
| AC-VIS-05 | 登录/注册：表单居中，输入框高度 ≥ 44px（满足触控热区），圆角 12px | 表单页截图目视检查 | 表单规范 |

---

## 六、Player 播放器领域

### 领域名词

| 术语 | 定义 |
|------|------|
| PlayerActivity | Android 原生播放器 Activity，使用 ExoPlayer (Media3) 播放视频 |
| 控制条 | 播放器控制栏，包含播放/暂停、进度条、时间显示、倍速、全屏、上/下一集、返回按钮 |
| PlayerViewModel | 播放器状态管理，维护播放状态机（IDLE/BUFFERING/READY/PLAYING/PAUSED/ERROR/ENDED）|
| 签名 URL | 火山引擎 TOS 预签名 URL，有时效性（默认 6h）|
| 全屏模式 | 播放器横屏全屏显示，隐藏状态栏和控制条（3s 无操作后自动隐藏）|
| 剧集模式 | drama_id > 0 时，播放器显示上/下一集按钮并支持自动连播 |

### 前置条件

- Android ExoPlayer (Media3) 依赖已集成
- 后端 `/api/episodes/{id}/video-url` 接口可用
- 火山引擎 TOS 密钥已配置（否则返回 503 降级提示）
- 播放器 Activity 已在 AndroidManifest 中注册，含 `configChanges` 配置防止横屏重启

### 主流程

1. **进入播放器**
   - H5 详情页通过 JSBridge `window.DramaFlowBridge.openPlayer(episodeId, dramaId, episodeNumber)` 调用
   - 或通过 `window.DramaFlowBridge.playVideo(episodeId, videoUrl, title, dramaId, episodeNumber)` 直接传入 URL
   - PlayerActivity 通过 Intent 接收参数并初始化 ExoPlayer
   - 播放器启动后自动缓冲并播放视频

2. **播放控制**
   - 用户点击播放/暂停按钮切换播放状态，图标同步切换
   - 用户拖动 SeekBar 跳转到指定位置，拖动时实时显示时间
   - SeekBar 和当前时间/总时长每 250ms 更新一次

3. **倍速切换** [Changed - 迭代3 状态机集成]
   - 用户点击倍速按钮展开速度选择浮层（0.5x / 0.75x / 1.0x / 1.25x / 1.5x / 2.0x）
   - 选择后播放器调整播放速度，按钮文案同步更新
   - 倍速切换不改变播放状态机当前状态（PLAYING 仍为 PLAYING，PAUSED 仍为 PAUSED）
   - 倍速值由 PlayerViewModel 管理，作为状态机的一个独立属性

4. **全屏切换**
   - 用户点击全屏按钮进入全屏模式（隐藏状态栏，横屏显示）
   - 3 秒无操作后控制条自动隐藏
   - 用户点击视频画面切换控制条显示/隐藏
   - 再次点击退出全屏按钮恢复竖屏模式，控制条保持可见

5. **剧集导航（剧集模式下）**
   - 用户点击上一集/下一集按钮切换到对应剧集
   - 首集时上一集按钮置灰，末集时下一集按钮置灰
   - 当前集播放结束后自动加载并播放下一集
   - 全部剧集播放完毕后提示并返回

6. **签名 URL 过期处理**
   - 播放器监听 ExoPlayer 错误事件
   - 检测到 401/403 错误时自动请求 `GET /api/episodes/{episode_id}/video-url` 刷新签名
   - 获取新签名后更新 MediaItem 继续播放

7. **状态机同步** [Changed - 迭代3 新增倍速属性]
   - ExoPlayer 回调 `onPlaybackStateChanged` 驱动 PlayerViewModel 状态机
   - IDLE → BUFFERING → READY (PLAYING/PAUSED) → ENDED
   - 播放出错时切换到 ERROR 状态
   - 倍速（speed）作为 PlayerViewModel 的独立属性，默认 1.0x，切换倍速不影响主状态机流转

### 异常处理

| 异常场景 | 错误响应 | 处理方式 |
|---------|---------|---------|
| 视频 URL 过期 | ExoPlayer 401/403 错误 | 自动刷新签名 URL 后重试 |
| TOS 服务不可用 | 后端 503 | 显示"视频服务暂不可用" |
| 剧集 ID 无效 | 后端 404 | 提示"单集不存在" |
| 网络异常 | ExoPlayer 连接错误 | 显示 Toast 错误提示 |
| 视频地址为空 | 播放器初始化失败 | 提示"该集视频地址无效" |

### 验收标准 (AC)

| AC-ID | 描述 | 关联 |
|-------|------|------|
| AC-PLAYER-01 | 从 H5 详情页点击播放可跳转到 PlayerActivity 并开始播放 | 进入播放 |
| AC-PLAYER-02 | 播放/暂停按钮可切换播放状态，图标同步变化 | 播放控制 |
| AC-PLAYER-03 | SeekBar 实时反映播放进度，拖动可跳转 | 进度控制 |
| AC-PLAYER-04 | 控制条显示当前播放时间和视频总时长（mm:ss 格式） | 时间显示 |
| AC-PLAYER-05 | 倍速切换浮层含 0.5x~2.0x 选项，选择后正常生效 | 倍速控制 |
| AC-PLAYER-06 | 全屏模式隐藏状态栏，控制条 3 秒后自动隐藏，点击画面切换 | 全屏 |
| AC-PLAYER-07 | 剧集模式下显示上/下一集按钮，首末集置灰提示 | 剧集导航 |
| AC-PLAYER-08 | 当前集播放结束后自动加载下一集并提示 | 自动连播 |
| AC-PLAYER-09 | 签名 URL 过期时自动刷新并恢复播放 | URL 过期处理 |
| AC-PLAYER-10 | 播放器状态机覆盖7个状态（IDLE/BUFFERING/READY/PLAYING/PAUSED/ENDED/ERROR）及合法转换，状态仅由 onPlaybackStateChanged 驱动 | 状态机 |
| AC-PLAYER-11 | 横屏旋转不重启 Activity，播放状态不丢失 | 配置变更 |
| AC-PLAYER-12 | 初始状态为 IDLE，prepare 后进入 BUFFERING，缓冲完成后进入 READY | 状态机初始化 |
| AC-PLAYER-13 | READY 时根据 playWhenReady 决定进入 PLAYING 或 PAUSED | 状态机播放控制 |
| AC-PLAYER-14 | seek 拖动时状态从 PLAYING/PAUSED 进入 BUFFERING，缓冲完成后恢复到原状态 | 状态机 seek |
| AC-PLAYER-15 | 播放完成后状态切换到 ENDED | 状态机结束 |
| AC-PLAYER-16 | 播放出错时状态切换到 ERROR，控制条自动显示 | 状态机出错 |
| AC-PLAYER-17 | ERROR 状态下 recover() 方法将状态从 ERROR 切换回 BUFFERING 并重新播放 | 状态机恢复 |
| AC-PLAYER-18 | player release 后状态回到 IDLE | 状态机释放 |
| AC-PLAYER-19 | 倍速切换不改变播放状态机当前状态（PLAYING 仍为 PLAYING，PAUSED 仍为 PAUSED） | 迭代3 新增 |
| AC-PLAYER-20 | PlayerViewModel 维护当前倍速属性，支持 0.5x~2.0x 共 6 档枚举值，默认 1.0x | 迭代3 新增 |
| AC-PLAYER-21 | 倍速切换后播放速度即时生效，SeekBar 时间显示不受倍速影响（按实际播放时间） | 迭代3 新增 |

---

## 附录：API 接口总览

| 方法 | 路径 | 模块 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | User | 否 |
| POST | `/api/auth/login` | User | 否 |
| POST | `/api/auth/logout` | User | 是 |
| POST | `/api/auth/refresh` | User | 是 (Refresh) |
| GET | `/api/dramas` | Drama | 否 |
| GET | `/api/dramas/{id}` | Drama | 否 |
| GET | `/api/banners` | Drama | 否 |
| GET | `/api/categories` | Drama | 否 |
| GET | `/api/dramas/{id}/episodes` | Episode | 否 |
| GET | `/api/episodes/{id}` | Episode | 否 |
| GET | `/api/episodes/{id}/video-url` | Episode | 否 |
| PUT | `/api/watch-records/{episode_id}` | WatchRecord | 是 |
| GET | `/api/watch-records` | WatchRecord | 是 |
| GET | `/api/watch-records/{episode_id}` | WatchRecord | 是 |
| GET | `/api/watch-records/continue-watching` | WatchRecord | 是 |

---

*本文档覆盖迭代 1 + 迭代 2 + 迭代 3 增量更新。标注 `[Changed]` 的项为迭代 3 变更内容，完整历史记录在 git 中。*

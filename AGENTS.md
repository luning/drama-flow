# DramaFlow Agent 约束与规范

## 技术栈

| 模块 | 技术栈 |
|------|--------|
| 移动端 | Kotlin + Android Studio, ViewModel + LiveData, Navigation Component, ExoPlayer (Media3) |
| H5（WebView 内嵌）| Vue3 + Vite + TypeScript, Pinia 状态管理, Vue Router hash 模式 |
| 后端 API | Python 3.10+ + FastAPI, SQLAlchemy 2.0 ORM, SQLite, Pydantic v2 |
| 视频 CDN | 七牛云签名 URL |
| 安全存储 | EncryptedSharedPreferences（禁止明文存储 Token）|
| 测试 | pytest（后端行为级测试）, Espresso（Android UI 测试）, Cypress（H5 E2E）|

## 项目结构

```
/
├── design-system/     # 可执行设计系统（唯一源）
│   ├── tokens/       # Design Token（CSS/TS）
│   ├── specs/        # 约束 + 屏幕规格
│   ├── components/   # 组件规格 → CSS/Android
│   └── exports/      # 平台导出
├── android/          # Kotlin Android 原生
│   └── app/src/main/java/com/dramaflow/
│       ├── auth/     # 认证模块
│       ├── home/     # 首页模块（WebView 容器）
│       ├── detail/   # 详情模块
│       ├── player/   # 播放器模块（ExoPlayer）
│       ├── data/     # 数据层（API/Repository/Preferences）
│       └── common/   # JSBridge 等共享工具
├── h5/               # Vue3 H5（WebView 内嵌）
│   ├── src/pages/    # Home.vue, Detail.vue
│   ├── src/stores/   # Pinia stores
│   └── src/api/      # API 封装
├── scripts/
│   ├── design-system/ # Figma同步 + 代码生成
│   └── check/         # 合规检查
├── PRD.md            # 产品需求文档
└── SPEC.md           # 可执行规格 + 验收标准
```

## 架构约束（重要）

1. **跨模块调用禁止**：后端 API 路由 → Service → ORM，禁止跳过层直接操作数据库。Android 模块之间通过 Navigation/Intent 通信，禁止跨模块 import 内部实现。

2. **WebView 通信**：H5 与 Android 原生通过 JSBridge (`window.DramaFlowBridge`) 通信，禁止 H5 直接调用 Android 内部 API。

3. **关注点分离**：
   - Android: Fragment 只做 UI 绑定，ViewModel 管理状态和业务逻辑，Repository 封装数据源
   - H5: 页面组件只负责布局，Store 管理状态，API 层封装网络请求
   - 后端: API 路由层不直接操作数据库，通过 Service 层调用

## SDD 最小约束

在接收任务和生成代码时，必须遵循以下规则：

1. **接受任务前**：先阅读对应模块的 SPEC.md 中的规格定义和验收标准（AC），确认理解需求范围
2. **生成代码后**：逐条自检 AC，确保所有验收标准被覆盖
3. **测试**: 修改 API 后运行 `pytest`，确保不破坏已有行为级测试
4. **Spec 变更**: 修改已有 AC 时标注 `[Changed]` 保留历史意图，而非直接覆盖

## 命名规范

| 语言 | 规范 | 示例 |
|------|------|------|
| Python | snake_case 变量/函数, PascalCase 类 | `get_drama_detail()`, `DramaService` |
| Kotlin | camelCase 变量/函数, PascalCase 类/文件 | `loadDramas()`, `AuthViewModel` |
| TypeScript | camelCase 变量/函数, PascalCase 类/组件 | `fetchDramas()`, `LoginFragment` |
| SQL | UPPER_SNAKE_CASE 关键字, snake_case 表/字段 | `SELECT * FROM watch_records` |
| 路由 | kebab-case 路径 | `/api/watch-records/continue-watching` |

## 设计 Token 引用

颜色、字体、间距必须引用 `design_system.md` 中定义的设计 Token，禁止硬编码色值：

- Primary: `#6C5CE7`（主色/按钮/选中态）
- Primary Light: `#A29BFE`（辅助色/链接）
- Accent: `#FD79A8`（强调/收藏）
- Rating: `#FFC048`（评分星级）
- BG Primary: `#0F0F23`（页面背景）
- BG Card: `#16163A`（卡片背景）
- Border: `rgba(255,255,255,0.06~0.08)`

## 用户交互原则

- 所有异步操作需提供加载状态反馈（loading indicator）
- 错误信息用用户能理解的语言呈现，不暴露技术细节
- 播放器状态机必须覆盖：IDLE → BUFFERING → READY → PLAYING ↔ PAUSED → ERROR/ENDED
- Token 过期后自动尝试刷新，刷新失败再跳转登录页，不能直接闪退或白屏

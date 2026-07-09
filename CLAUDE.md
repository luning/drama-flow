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
├── backend/          # Python FastAPI 后端
│   ├── app/api/      # API 路由层
│   ├── app/models/   # SQLAlchemy ORM 模型
│   ├── app/schemas/  # Pydantic 请求/响应模型
│   ├── app/services/ # 业务逻辑层
│   └── app/db/       # 数据库引擎 + seed 脚本
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
├── design-system/     # 可执行设计系统（Single Source of Truth）
│   ├── tokens/       # Design Token（tokens.css, tokens.ts, schema）
│   ├── specs/        # 约束 & 屏幕规格（constraints, design-rules, screens/）
│   ├── components/   # 平台无关组件规格（components.yaml → CSS/Android）
│   └── exports/      # 平台导出（H5 CSS, Android colors.xml/styles.xml）
├── scripts/
│   ├── design-system/ # Figma 同步 + 代码生成脚本
│   └── check/         # Token/约束/组件合规检查脚本
├── docs/             # 设计截图与文档
├── prototype/        # 可交互 HTML 原型（引用 design-system）
│   └── generated/    # 从 screen spec 自动生成的原型
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

## OpenSpec 使用规范

项目使用自定义 schema `dramaflow`（fork 自 `spec-driven`），已有 spec：
`user-auth`, `drama-catalog`, `watch-record`, `jsbridge-protocol`, `player-state-machine`, `video-player`, `video-sign-url`

```bash
# 创建新 change（务必指定 --schema dramaflow）
openspec new change <name> --schema dramaflow

# 查看所有 spec
openspec list --specs

# 查看当前 change 状态
openspec status --change <name>
```

Spec 格式约定（dramaflow schema）：
- 每个 Requirement 用 `**Scope**: Backend | Android | H5 | JSBridge` 标注所属端
- Backend/JSBridge Requirement 包含 `**Endpoint**` / `**Request**` / `**Response**` 描述
- Scenario 必须用 4 个 `#`（`####`），不用 3 个或 bullet

## SDD 最小约束

在接收任务和生成代码时，必须遵循以下规则：

1. **接受任务前**：先阅读 `openspec/specs/<module>/spec.md` 中的规格和 AC，确认理解需求范围
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

## 设计系统（Design System）引用

所有颜色、字体、间距、组件必须引用 `design-system/` 中的定义，禁止硬编码。

### Token 层（design-system/tokens/tokens.css）
所有颜色必须通过 CSS 变量引用，变量名以 tokens.css 为准：
```css
/* ✅ 正确 */
color: var(--color-primary);
background: var(--bg-card);
padding: var(--space-4);

/* ❌ 错误 — 硬编码色值 */
color: #6c5ce7;
background: #0f0f23;

/* ❌ 错误 — 旧版变量名（已废弃） */
color: var(--primary);
background: var(--bg);
```

### 组件层（design-system/components/components.yaml）
H5 组件应使用 components.css 中预定义的 class（如 `.btn-primary`, `.drama-card`），不要重写组件样式。只有页面特有的布局逻辑放在 scoped style 中。

### 检查脚本
```
python scripts/check/check_tokens.py      # Token 合规
python scripts/check/check_constraints.py  # 业务约束
python scripts/check/check_components.py   # 组件使用
```

## 用户交互原则

- 所有异步操作需提供加载状态反馈（loading indicator）
- 错误信息用用户能理解的语言呈现，不暴露技术细节
- 播放器状态机必须覆盖：IDLE → BUFFERING → READY → PLAYING ↔ PAUSED → ERROR/ENDED
- Token 过期后自动尝试刷新，刷新失败再跳转登录页，不能直接闪退或白屏

## 培训大纲文档规范

`training_doc/` 下的课程大纲类文档（如"XXX必修课.md"）禁止使用表格，一律用列表/加粗小标题表达对比和分类内容。

## Python 环境

- 虚拟环境位于 `backend/drama-flow/`
- 激活：`source backend/drama-flow/bin/activate`
- 所有 Python 命令（运行、测试、pip install）均需在 venv 中执行

# DramaFlow 设计约束（Business Constraints）

> 写给 AI 和团队成员共同参考的 UX 规则。任何人（包括 AI）生成或修改 UI 代码时，必须遵守本文件中的约束。
>
> 本文件变更须经设计负责人 Review，可通过 GitLab 网页直接编辑后提交 MR。

---

## 一、布局约束

- **主操作按钮（Primary CTA）**：同一页面只能出现一个 `btn-primary`，用于最核心的转化动作（如"立即观看"、"登录"、"注册"）
- **卡片标题**：最多两行，超出截断加省略号（`text-overflow: ellipsis`）
- **页面水平内边距**：统一 `var(--space-4)` (16px)，不得使用不同值破坏视觉节奏
- **底部安全区**：底部导航高度 `var(--bottom-nav-height)` (56px)，内容不得被遮挡

## 二、状态约束

- **所有异步操作**必须有加载反馈（loading indicator 或 skeleton），禁止裸露骨架屏（skeleton 需有 shimmer 动效）
- **播放器状态机**必须完整覆盖：`IDLE → BUFFERING → READY → PLAYING ↔ PAUSED → ERROR / ENDED`
- **禁用态**不得使用品牌主色 `var(--color-primary)`，一律使用 `var(--text-muted)` + `var(--border)`
- **错误信息**用用户可理解的语言呈现，不暴露技术细节（不显示 HTTP 状态码、堆栈信息）

## 三、颜色约束

- **禁止硬编码色值**：所有颜色必须引用 `tokens.css` 中的 CSS 变量（如 `var(--color-primary)`），不得写 `#6c5ce7` 等裸值
- **文字对比度**：主文字 `var(--text-primary)` 在暗色背景上对比度需 ≥ 4.5:1（WCAG AA）
- **渐变方向**：品牌渐变统一使用 `linear-gradient(135deg, var(--color-primary), var(--color-primary-light))`

## 四、交互约束

- **点击响应**：所有可交互元素必须有 `transition` 反馈，按钮 hover 需有明确视觉变化
- **Token 过期**：自动尝试刷新，刷新失败再跳转登录页，禁止直接闪退或白屏
- **空状态**：列表为空时必须展示空状态提示，不得显示空白页面
- **最小触摸目标**：移动端可交互元素最小尺寸 44×44px（iOS HIG 规范）

## 五、文字约束

- **剧名**：最多显示两行，超出省略
- **评分**：保留一位小数，始终使用 `var(--color-rating)` 颜色
- **集数标签**：格式为"第 N 集"，总集数格式为"共 N 集"
- **时长标签**：格式为"MM:SS"

## 六、组件使用规范

| 场景 | 必用组件 | 禁止 |
|------|----------|------|
| 页面级加载 | Skeleton Grid | 空白等待 |
| 操作反馈 | Toast（底部浮现，1.8s 消失）| Alert / 原生 dialog |
| 剧集封面 | 3:4 比例卡片 | 任意比例图片 |
| 播放入口 | `btn-primary` "立即观看" | 多个并列 CTA |
| 继续观看 | 进度条 + 上次时间戳 | 仅显示集数 |

## 七、尺寸规范

| 元素 | 关键尺寸 |
|------|---------|
| 底部导航栏 | 高度 56px，图标 22px，标签 10px |
| 剧集卡片封面 | 宽高比 3:4，圆角 `var(--radius-card)` |
| 顶部 App Bar | 高度 44px |
| 主按钮 | 高度 48px，小按钮 32px |
| 表单输入框 | 高度 48px |
| 个人中心头像 | 72px 圆形 |

**页面关键比例：**

| 页面 | 关键参数 |
|------|---------|
| 首页 | Banner 16:7 比例，卡片两列网格，间距 `var(--space-3)` |
| 详情页 | Header 图片 16:9，内容区 Padding `var(--space-4)` |
| 搜索页 | 搜索栏圆角 24px，热门标签 wrap 布局 |
| 播放器 | 视频区 16:9，控制栏渐变 `linear-gradient(transparent 60%, rgba(0,0,0,0.8))` |

---

> 最后更新：2026-05-10 | 负责人：产品 & 设计团队

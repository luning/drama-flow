# DramaFlow 设计系统规范

> 从交互原型中提取的设计 Token，作为视觉验收基准。

---

## 一、色彩系统

### 1.1 品牌色

| Token | 用途 | 色值 | 预览 |
|-------|------|------|------|
| `--primary` | 主色/按钮/选中态/高亮 | `#6C5CE7` | <span style="background:#6C5CE7;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |
| `--primary-light` | 渐变/辅助色 | `#A29BFE` | <span style="background:#A29BFE;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |
| `--accent` | 强调色/收藏/推荐标记 | `#FD79A8` | <span style="background:#FD79A8;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |

### 1.2 语义色

| Token | 用途 | 色值 | 预览 |
|-------|------|------|------|
| `--rating` | 评分星级 | `#FFC048` | <span style="background:#FFC048;color:#000;padding:2px 8px;border-radius:4px;">████</span> |
| `--success` | 成功/完成状态 | `#00B894` | <span style="background:#00B894;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |
| `--danger` | 错误/退出/警告 | `#E17055` | <span style="background:#E17055;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |
| `--info` | 信息/悬疑分类 | `#0984E3` | <span style="background:#0984E3;color:#fff;padding:2px 8px;border-radius:4px;">████</span> |

### 1.3 暗色主题

| Token | 用途 | 色值 | 预览 |
|-------|------|------|------|
| `--bg-primary` | 页面背景 | `#0F0F23` | <span style="background:#0F0F23;color:#fff;padding:2px 8px;border-radius:4px;border:1px solid #333;">████</span> |
| `--bg-card` | 卡片/列表项背景 | `#16163A` | <span style="background:#16163A;color:#fff;padding:2px 8px;border-radius:4px;border:1px solid #333;">████</span> |
| `--bg-hover` | 悬停/按压态 | `#1C1C44` | <span style="background:#1C1C44;color:#fff;padding:2px 8px;border-radius:4px;border:1px solid #333;">████</span> |
| `--bg-elevated` | 弹窗/菜单背景 | `rgba(20,20,50,0.95)` | 半透明毛玻璃 |
| `--border` | 分割线/边框 | `rgba(255,255,255,0.06~0.08)` | 极淡白线 |

### 1.4 文字色阶

| Token | 用途 | 色值 |
|-------|------|------|
| `--text-primary` | 标题/正文 | `#FFFFFF` |
| `--text-secondary` | 次要信息 | `#CCCCCC` ~ `#DDDDDD` |
| `--text-tertiary` | 辅助文字 | `#888888` |
| `--text-muted` | 禁用态/占位符 | `#555555` |
| `--text-link` | 链接/操作文字 | `#A29BFE` |

---

## 二、字体系统

### 2.1 字族

| 层级 | 字族 |
|------|------|
| 英文数字 | `-apple-system, Roboto, sans-serif` |
| 中文 | `"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif` |

### 2.2 字号

| Token | 大小 | 行高 | 用途 |
|-------|------|------|------|
| `--text-xs` | 10px | 1.4 | 角标、时长标签 |
| `--text-sm` | 11-12px | 1.4 | 辅助信息、元数据 |
| `--text-base` | 13-14px | 1.5 | 正文、描述文字 |
| `--text-md` | 15-16px | 1.4 | 剧集标题、列表项 |
| `--text-lg` | 17-18px | 1.3 | Banner 标题、页面标题 |
| `--text-xl` | 20-24px | 1.3 | 详情页标题、大标题 |
| `--text-2xl` | 28px | 1.2 | 品牌名称 |

### 2.3 字重

| Token | 字重 | 用途 |
|-------|------|------|
| `--weight-normal` | 400 | 正文 |
| `--weight-medium` | 500 | 分类 Tab、辅助标题 |
| `--weight-semibold` | 600 | 卡片标题、按钮 |
| `--weight-bold` | 700 | 页面标题、品牌名 |
| `--weight-extrabold` | 800 | 品牌 Logo |

---

## 三、间距系统

基于 4px 基准的间距体系：

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-1` | 4px | 小间隔 |
| `--space-2` | 8px | 内边距/元素间距 |
| `--space-3` | 12px | 网格间距/卡片间距 |
| `--space-4` | 16px | 页面 Padding/卡片内边距 |
| `--space-5` | 20px | 分段间距 |
| `--space-6` | 24px | 表单间距/Section 间距 |
| `--space-8` | 32px | 页面顶部间距 |

---

## 四、圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 4-6px | 标签、Episode 数字 |
| `--radius-md` | 8-10px | 小按钮、小缩略图 |
| `--radius-lg` | 12-14px | 卡片、大按钮、输入框 |
| `--radius-xl` | 16-20px | Banner、Header 大图 |
| `--radius-full` | 50% | 头像、圆形按钮 |

---

## 五、阴影与层级

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `0 2px 8px rgba(0,0,0,0.2)` | 卡片默认 |
| `--shadow-md` | `0 4px 20px rgba(108,92,231,0.3)` | 按钮 hover |
| `--shadow-lg` | `0 8px 25px rgba(0,0,0,0.3)` | 卡片 hover |
| `--shadow-glow` | `0 0 6px rgba(108,92,231,0.5)` | 进度条拖拽圆点 |
| `--z-nav` | 100 | 底部导航 |
| `--z-overlay` | 10 | 播放器控制层 |
| `--z-toast` | 1000 | Toast 提示 |
| `--z-menu` | 10 | 下拉菜单 |

---

## 六、动画

| Token | 时长 | 缓动 | 用途 |
|-------|------|------|------|
| `--ease-default` | 0.2s | ease | hover/点击反馈 |
| `--ease-page` | 0.35s | cubic-bezier(0.4,0,0.2,1) | 页面切换 |
| `--ease-banner` | 0.5s | ease | Banner 滑动 |
| `--ease-skeleton` | 1.5s | infinite | 骨架屏 shimmer |

---

## 七、组件规范

### 7.1 底部导航栏

- 高度：56px（含安全区）
- 图标大小：22px
- 标签字号：10px
- 选中色：`#6C5CE7`
- 未选中色：`#666666`
- 背景：`#16163A`
- 顶部边框：1px `rgba(255,255,255,0.06)`

### 7.2 剧集卡片

- 宽高比：3:4（封面图）
- 圆角：14px
- 卡片背景：`#16163A`
- 标题：14px `#FFFFFF` 600w
- 元数据：11px `#777777`
- 评分：11px `#FFC048`
- 角标：8px 圆角，`rgba(108,92,231,0.9)` 背景

### 7.3 按钮

| 类型 | 背景 | 文字 | 圆角 | 高度 |
|------|------|------|------|------|
| Primary | `linear-gradient(135deg, #6c5ce7, #a29bfe)` | 15px 600w #fff | 12px | 48px |
| Secondary | `rgba(255,255,255,0.08)` | 15px 600w #fff | 12px | 48px |
| Outline | transparent + 1.5px #6c5ce7 border | 15px 600w #6c5ce7 | 12px | 48px |
| Small | same ratio | 13px | 8px | 32px |

### 7.4 表单输入

- 高度：48px
- 内边距：14px 16px
- 圆角：12px
- 默认边框：1.5px `rgba(255,255,255,0.08)`
- 聚焦边框：1.5px `#6C5CE7`
- 背景：`rgba(255,255,255,0.06)`
- 文字：15px #fff
- 占位符：14px #555

### 7.5 播放器控制条

- 控制栏渐变：`linear-gradient(transparent 60%, rgba(0,0,0,0.8))`
- 进度条高度：4px（悬浮时显示 14px 拖拽圆点）
- 已播：`#6C5CE7`
- 未播：`rgba(255,255,255,0.2)`
- 按钮大小：18px
- 时间文字：11px

### 7.6 顶部状态栏

- 高度：44px
- 背景：`#0F0F23`
- 时间：14px 700w #fff
- 图标：12px

---

## 八、页面布局规范

| 页面 | 关键布局参数 |
|------|-------------|
| 登录/注册 | Padding: 24px 左右, 40px 顶部 |
| 首页 | Banner 16:7 比例, 分类 Tab 水平滚动, 卡片 2 列网格 |
| 详情页 | Header 16:9, 内容 Padding 16px |
| 播放器 | 16:9 视频区, 下方信息 12px padding |
| 搜索页 | 搜索栏圆角 24px, 热门标签 wrap 布局 |
| Profile | 居中头像 72px, 列表项 14px padding |

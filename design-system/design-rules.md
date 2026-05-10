# DramaFlow AI 生成规则（AI Generation Rules）

> 本文件是 AI 生成 UI 代码时的上下文约束文件。
> 每次生成原型页面、组件或界面代码前，AI 必须先读取本文件及其引用的 tokens.css 和 constraints.md。
>
> **如果使用 Claude Code Skill 触发原型生成，本文件会自动注入 Prompt，无需手动提醒。**

---

## 可用 Token

所有设计变量定义在 `design-system/tokens.css`，对应的 TypeScript 版本在 `design-system/tokens.ts`。

**核心颜色 Token：**

```css
/* 品牌色 */
var(--color-primary)       /* #6C5CE7 — 主色、按钮、选中态 */
var(--color-primary-light) /* #A29BFE — 渐变辅助、链接文字 */
var(--color-accent)        /* #FD79A8 — 收藏、Logo、强调 */

/* 语义色 */
var(--color-rating)        /* #FFC048 — 评分星级 */
var(--color-success)       /* #00B894 — 成功状态 */
var(--color-danger)        /* #E17055 — 错误、退出 */
var(--color-info)          /* #0984E3 — 信息、悬疑分类 */

/* 背景色 */
var(--bg-primary)          /* #0F0F23 — 页面背景 */
var(--bg-card)             /* #16163A — 卡片背景 */
var(--bg-hover)            /* #1C1C44 — 悬停态 */
var(--bg-elevated)         /* 毛玻璃弹窗背景 */

/* 边框 / 表面 */
var(--border-subtle)       /* rgba(255,255,255,0.06) — 分割线 */
var(--border)              /* rgba(255,255,255,0.08) — 默认边框 */
var(--surface-hover)       /* rgba(255,255,255,0.14) — 按钮 hover */

/* 文字 */
var(--text-primary)        /* #FFF — 主文字 */
var(--text-tertiary)       /* #888 — 辅助文字 */
var(--text-muted)          /* #555 — 禁用/占位 */
```

**动画 Token：**

```css
var(--transition-fast)     /* 0.15s ease */
var(--transition-default)  /* 0.2s ease */
var(--transition-page)     /* 0.35s cubic-bezier(0.4,0,0.2,1) */
```

**阴影 Token：**

```css
var(--shadow-md)           /* 按钮 hover 发光 */
var(--shadow-lg)           /* 卡片 hover 阴影 */
var(--shadow-glow)         /* 进度条拖拽圆点光晕 */
```

---

## Token 引用规范

```
✅ 正确：color: var(--color-primary);
✅ 正确：background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
✅ 正确：transition: background var(--transition-default);

❌ 错误：color: #6c5ce7;
❌ 错误：background: #0f0f23;
❌ 错误：transition: background 0.2s ease;
```

---

## 页面生成规范

### 列表页（如首页推荐、搜索结果）

```html
<!-- 使用 drama-grid 网格，间距 var(--space-3) -->
<div class="drama-grid">
  <!-- 每个卡片：drama-card 组件，点击进详情 -->
  <div class="drama-card" onclick="openDetail(id)">
    <div class="thumb" style="background:linear-gradient(135deg,{genre-color},var(--bg-card-deep))">
      <span class="badge">{tag}</span>
    </div>
    <div class="info">
      <h4>{title}</h4>
      <div class="rating">★ {rating}</div>
    </div>
  </div>
</div>
```

### 页面标题栏

```html
<!-- app-bar：返回按钮 + 标题 + 可选操作 -->
<div class="app-bar">
  <button class="back" onclick="navigateTo('page-xxx')">‹</button>
  <h1>页面标题</h1>
  <button class="action">⋯</button>
</div>
```

### 主操作按钮（每页只能有一个）

```html
<!-- btn-primary：每页只出现一次 -->
<button class="btn btn-primary btn-full">立即观看</button>

<!-- btn-secondary：次要操作 -->
<button class="btn btn-secondary">收藏</button>

<!-- btn-outline：轮廓按钮 -->
<button class="btn btn-outline">♡ 收藏</button>
```

### 表单输入

```html
<div class="form-group">
  <label>字段名称</label>
  <input class="form-input" type="text" placeholder="提示文字">
</div>
```

### Toast 反馈

```javascript
// 所有操作反馈使用 showToast()，不使用原生 alert()
showToast('操作成功提示');
```

---

## 业务约束

详见 `design-system/constraints.md`，核心要点：

1. 同一页面**只能有一个** `btn-primary`
2. 所有异步操作需有 **loading 反馈**（skeleton 或 spinner）
3. 颜色必须通过 **CSS 变量**引用
4. 错误提示使用**用户语言**，不暴露技术细节
5. 最小触摸目标 **44×44px**

---

## 参考原型

`prototype/index.html` 是基于本设计系统构建的可交互参考原型，包含以下已实现页面：

| 页面 ID | 内容 |
|---------|------|
| `page-splash` | 启动页 |
| `page-login` | 登录页 |
| `page-register` | 注册页 |
| `page-home` | 首页（Banner + 分类 + 推荐） |
| `page-detail` | 剧集详情页 |
| `page-player` | 播放器页 |
| `page-search` | 搜索页 |
| `page-profile` | 个人中心 |
| `page-history` | 观看历史 |

生成新页面时，应与以上已有页面在视觉风格和交互模式上保持一致。

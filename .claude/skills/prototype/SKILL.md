---
name: prototype
description: 生成设计系统合规的原型页面——自动注入 Token、约束和生成规则，确保输出不含 hardcoded 色值。触发："生成原型"、"prototype --page"、"新增原型页面"、"原型设计"、"生成页面"。
---

# prototype

生成符合 DramaFlow 可执行设计系统约束的原型 HTML 页面或组件。

## 核心原则

**每次生成前必须注入设计系统上下文，禁止凭记忆生成色值。**

## 工作流

### 1. 注入设计系统上下文

读取以下文件，作为本次生成的约束基础：

| 文件 | 作用 |
|------|------|
| `design-system/tokens.css` | 所有可用 CSS 变量（颜色、间距、动画等）|
| `design-system/constraints.md` | 业务约束（每页只能有一个 Primary CTA 等）|
| `design-system/design-rules.md` | 页面结构模板和禁止项 |
| `prototype/index.html` | 现有原型（参考已有页面的代码风格和组件用法）|

### 2. 理解需求

- 如果用户明确描述了页面/组件，直接进入生成
- 如果描述模糊，追问以下信息后再生成：
  - 页面的核心功能是什么？
  - 展示哪些数据？
  - 关键交互（点击后跳转到哪里？）

### 3. 生成代码

**颜色约束（硬性）**：
```css
/* ✅ 必须这样写 */
color: var(--color-primary);
background: var(--bg-card);

/* ❌ 禁止这样写 */
color: #6c5ce7;
background: #16163a;
```

**布局约束**：
- 每页只能有一个 `.btn-primary`（主操作）
- 页面水平内边距统一 `var(--space-4)`
- 文字色通过 `var(--text-*)` 引用

**动画约束**：
```css
transition: background var(--transition-default);    /* 0.2s hover */
transition: transform var(--transition-page);        /* 0.35s 页面切换 */
```

**组件复用**：
- 列表页：`.drama-grid` 两列网格
- 标题栏：`.app-bar` 结构（back + h1 + action）
- 操作反馈：`showToast('...')` 不用原生 alert
- 标签：`.tags span`（自动继承 primary-tint 背景）

**输出格式**：
- 新完整页面：输出 `<div class="page" id="page-xxx">...</div>` 结构
- 组件片段：输出 HTML 片段 + 必要的 CSS 类说明

### 4. 自检清单（生成后逐项检查，发现问题立即修正再输出）

- [ ] 无 hardcoded 色值：全部使用 `var(--*)` 引用 Token
- [ ] 每个页面只有一个 `.btn-primary`
- [ ] 所有文字颜色使用 `var(--text-*)` 系列
- [ ] 所有 hover 效果有 `transition` 反馈
- [ ] 异步操作有 loading 或 skeleton 反馈（或 showToast 占位）
- [ ] 最小触摸目标 44×44px（所有可点击元素）

### 5. 输出集成指引

告知用户如何将生成代码集成到 `prototype/index.html`：

```
集成步骤：
1. 将 <div class="page" id="page-xxx"> 插入到 <!-- /app-content --> 注释前
2. 如需导航：在 navigateTo() 的 navMap 中添加页面映射
3. 如需底部 Tab：在 .bottom-nav 中添加 nav-item
4. 运行 design-check 验证无 Token 违规
```

### 6. 运行合规检查

```bash
python scripts/check_design_tokens.py --path prototype
```

如果脚本存在，运行并报告结果。

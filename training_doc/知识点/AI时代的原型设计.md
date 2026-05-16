# AI 时代的原型设计

---

## 演进全景：不只是工具在变

过去二十多年，软件行业的原型经历了四个时代的演进，最终指向第五个阶段。这些阶段并非依次替换，而是**叠加积累**——每一层都建立在上一层之上，工具和方法论同时并存：

| 时代 | 代表工具 | 原型的本质 |
|------|---------|-----------|
| 文档时代 | Axure、PRD | 沟通说明书 |
| 视觉设计时代 | Figma、Design System | 可复用设计组件 |
| 代码化时代 | React、Storybook、shadcn | 可运行的组件 |
| AI 生成时代（进行中）| Bolt.new、v0、Lovable | 可执行的产品 |
| 可执行设计系统（终态）| tokens.css + components.yaml + 代码生成器 | 人机共用的唯一真相源 |

很多人以为这只是"工具在变"。

**实际上，背后是"设计权力中心"的迁移**——即：

- 谁来定义 UI
- 谁来控制一致性
- 谁来掌握系统结构
- 谁能让产品持续演化

正在发生根本性的转移。

---

## 文档时代：原型 = 沟通说明书

这个时代的核心认知是：**原型 ≠ 产品，原型只是"说明书"**。

典型流程：

```
PRD → Axure 原型 → UI 设计稿 → 前端开发
```

代表工具：Axure、Visio、墨刀、OmniGraffle

原型的核心价值集中在：页面流程、业务逻辑、页面跳转、信息结构。

"产品经理"是这个时代的主导者——软件开发成本高，需求沟通成本更高，原型本质上是降低沟通成本的工具。

---

## 视觉设计时代：原型 = 可复用设计组件

随着 Web App、移动互联网、SaaS 的崛起，软件复杂度迅速提升，行业进入 **Design-first** 阶段。Axure 并未消失，但设计的中心开始向可视化组件系统转移。

### Figma 为什么能崛起？

Figma 解决了三个核心问题：

**1. 组件化**

过去每个页面都要重新画按钮；Figma 引入了 Button Component、Variant、Auto Layout，第一次让 UI "像代码一样复用"。

**2. 多人协作**

过去 PSD 文件来回传；Figma 实现了在线协同、评论、标注与实时同步，让设计开始像 Google Docs 一样协作。

**3. Design System**

大型产品第一次开始系统化建立颜色体系、间距体系、字体体系、组件体系与动效规范。

这个时代最关键的变化：页面从"一张图"变成"一组可组合组件"，思维方式已经非常接近现代前端。

---

## 代码化时代：原型 = 可运行的组件

随着 React、Vue、Tailwind、Component UI 的普及，行业出现一个重要变化：**"原型"与"前端"开始融合**。Figma 并未消失，但组件的权威来源开始向代码偏移。

现代前端本身已经是组件化、状态化、Token 化的：

```jsx
<Button variant="primary" />
```

这和 Figma 中的 Component 几乎一致。行业开始反思：为什么还需要"设计稿 → 前端重写"这个过程？

### 代表工具

- **Storybook**：组件文档与测试
- **shadcn/ui**：代码即组件库
- **Framer**：可交互的代码原型

这个时代正式确立了 **"代码即原型"** 的范式，设计系统的权威来源从 Figma 文件向代码仓库迁移。

---

## AI 生成时代：原型 = 可执行的产品（进行中）

代表工具：**Bolt.new、Lovable、v0 by Vercel**。前三个时代的能力依然存在，但 AI 在其上新增了一层：

```
Prompt → UI → React → 可运行 App
```

自然语言描述可以直接生成可运行应用，**原型与 MVP 的边界正在模糊**。

### 最大的误解

很多人以为：AI 能生成页面 = 不再需要设计系统。

**恰恰相反。**

正因为 AI 太能生成，以下问题会比以前更严重：

- 风格漂移（每次生成风格不一致）
- 组件重复（相似功能出现多套实现）
- UX 崩坏（界面可用，但体验混乱）
- 状态不一致（组件行为不统一）

AI 越强，**设计系统的约束越重要**。这正是"可执行设计系统"成为核心基础设施的原因。

---

## 终态：可执行设计系统（Executable Design System）

四个时代叠加积累的最终指向，是一个让人和 AI 都能直接使用的设计系统。

### 过去 vs 未来

| 维度 | 过去的设计系统 | 未来的设计系统 |
|------|--------------|--------------|
| 形式 | 文档 + 规范 + Figma 组件 | Token + 组件 + 约束 + Runtime + AI 规则 |
| 受众 | 人类设计师 | 人类 + AI 均可直接使用 |
| 可执行性 | 描述性，需要人来实现 | 运行时可直接驱动 UI 生成 |

### 未来设计体系的核心结构

五个层次从上到下依次定义约束，AI 在中间消费，Figma 在末端可视化：

```
Specification（业务约束）
    ↓ 定义规则
Design Token（品牌 / 主题）
    ↓ 驱动样式
Component Runtime（组件库）
    ↓ 提供构建块
AI Generation（页面生成）
    ↓ 输出结果
Visual Collaboration Layer（Figma 协作）
```

**第一层：Specification — 业务约束**

不是设计稿，而是写给 AI 和团队成员共同参考的规则文档。例如：

```markdown
<!-- constraints.md -->
- 主操作按钮同一页面只能出现一个
- 卡片标题最多两行，超出截断加省略号
- 所有异步操作必须有 loading 状态，禁止裸露骨架屏
- 禁用态不得使用品牌主色，一律使用 --color-disabled
```

**第二层：Design Token — 品牌变量**

用代码定义所有视觉常量。CSS 自定义属性为主要载体，同时提供 TypeScript 版和 JSON Schema 校验：

```css
/* design-system/tokens/tokens.css */
:root {
  --color-primary:       #6C5CE7;   /* 主色 / 按钮 */
  --color-primary-light: #A29BFE;   /* 渐变辅助 / 链接 */
  --color-accent:        #FD79A8;   /* 强调 / 收藏 */
  --color-rating:        #FFC048;   /* 评分 */
  --bg-primary:  #0F0F23;  --bg-card: #16163A;
  --text-primary: #FFF;    --text-muted: #555;
  --space-4: 16px;  --radius-card: 12px;
  --transition-default: 0.2s ease;
}
```

三种格式关系：`tokens.css` 是权威源 → `tokens.ts` 和 `tokens.schema.json` 从它派生。Figma 通过 Tokens Studio 导出 DTCG JSON，再由脚本同步到 `tokens.css`。

**第三层：Component Runtime — 组件库**

组件消费 Token，通过平台无关的规格文件定义，再自动生成各平台代码。以 `components.yaml` 为唯一源：

```yaml
# components.yaml — 用 {token.path} 语法引用 Token
components:
  btn-primary:
    base:
      padding: "{spacing.md} {spacing.xl}"
      border-radius: "{radius.btn}"
      background:
        type: gradient-linear
        angle: 135deg
        stops: ["{color.primary} 0%", "{color.primaryLight} 100%"]
    states:
      hover: { transform: translateY(-1px), box-shadow: "{shadow.md}" }
      disabled: { background: "{text.muted}", cursor: not-allowed }
```

从 components.yaml 自动生成各平台代码：
```
components.yaml → generate_css.py → components.css       (H5 用 class="btn-primary")
components.yaml → generate_android.py → styles.xml       (Android 用 style="DramaFlow.Button.Primary")
```

生成的代码全部由 Token 变量驱动，不含硬编码值。

**第四层：AI Generation — 从 Screen Spec 多路生成**

前三层提供了 Token、约束和组件。第四层用平台无关的 **Screen Spec（YAML）** 描述页面结构，然后多路生成：

```yaml
# specs/screens/home.yaml — 描述 "页面上有什么、从哪取数据"
screen: home
sections:
  - component: app-bar
    title: "DramaFlow"
  - component: continue-watching
    data: /api/watch-records/continue-watching
  - component: banner-carousel
    data: /api/dramas?recommend=1
  - component: drama-grid
    data: /api/dramas?category={selected}
    layout: { columns: 2, gap: "{spacing.md}" }
```

同一个 screen spec 三路生成，改一处同步更新：

```
specs/screens/home.yaml
    ├── generate_prototype.py     → prototype HTML     (给 PM 看)
    ├── generate_h5_template.py   → Vue 页面骨架       (给前端开发)
    └── generate_android_layout.py → Android layout XML (给 Android 开发)
```

生成的代码引用 tokens.css 和 components.css，样式自动合规。

**第五层：Figma — 可视化协作**

通过 **Tokens Studio** 插件将 Token 导出为 DTCG JSON，再由同步脚本写入 `tokens.css`。设计师在 Figma 中操作的是和代码同源的 Token，而非手动维护的色板：

- 产品经理在 Figma 中做 UX 走查、标注修改意见
- 设计师用 Figma 探索视觉节奏，AI 难以替代的微调在这里完成
- 评审、讨论、演示依然发生在 Figma，不需要所有人看代码

---

### AI 原型 Skill：让生成自动合规

仅靠文档还不够，更好的做法是让生成工具在设计系统约束下自动工作。DramaFlow 中做了两件事：

1. **脚本化生成**：已定义好的页面从 screen spec 直接生成 HTML，自动引用 tokens.css + components.css，无需 AI 参与
2. **AI 对话生成**：对于新页面，将 tokens.css、constraints.md、design-rules.md 自动注入 Claude Code Skill 上下文，确保 AI 生成的代码只用 var(--xxx) 和预定义 class

核心价值：**设计系统的遵守从"靠人记忆"变成"系统默认"**。

### 设计角色如何参与代码仓库

`tokens.css` 和 `constraints.md` 在代码仓库里，但设计师和 PM 可以不使用 Git 参与：

| 角色 | 方式 | 门槛 |
|------|------|------|
| PM / 设计师 | GitLab 网页编辑 `constraints.md`、`design-rules.md` → 提交 MR | 零 |
| 设计师 | Figma Tokens Studio 导出 DTCG JSON → 脚本更新 `tokens.css` | 低 |
| 设计负责人 | 成为 `design-system/` CODEOWNERS，所有变更需其 Approve | 中 |

改了之后看效果：`prototype/generated/` 本地刷新即时预览；Component Gallery（`components/index.html`）查看所有组件状态；MR 触发 CI 预览环境做正式验收。

过去规范写在 Figma 标注里，开发可以选择性遵守；未来规范写在仓库里，每次修改有 diff、有 review、有历史记录，执行结果肉眼可见。

---

## 设计权力中心的迁移

回到第一章提出的核心问题：谁来定义 UI、谁来控制一致性、谁能让产品持续演化？走完四个时代，答案已经清晰：

**过去：**

```
Figma 是源头 → 前端实现
```

**未来：**

```
Component Runtime 是源头
Design Token → 平台无关组件规格 → AI 生成页面（HTML / Vue / Android XML）
Figma 转型为可视化协作层
```

Figma 的定位正在从"设计源文件"（类似 PSD/Sketch），演变为"设计 IDE"——它的价值不再是手工画页面，而是作为可视化协作、UX 探索与 AI 上下文编辑的平台。

---

## Figma 未来最核心的四个价值

即使设计系统高度代码化，Figma 仍有难以替代的四个价值：

| # | 价值 | 说明 |
|---|------|------|
| 1 | 人类可视化理解层 | 老板、产品、运营不看代码，Figma 让非工程角色理解系统 |
| 2 | UX 微调层 | 视觉节奏、阅读层次、情绪感、微交互，AI 难以处理，需要可视化探索 |
| 3 | AI Prompt 编辑层 | Figma 可能演化为可视化 Prompt IDE（"这个页面太拥挤，强化 CTA"→ AI 自动调整）|
| 4 | 跨角色协作层 | 评论、审阅、讨论、演示，Figma 仍然是多角色协作界面 |

---

## 团队能力转变：执行层 → 系统定义层

AI 真正替代的是**"低结构化设计劳动"**——手工画按钮、重复搭列表、人肉同步规范。这些低决策含量的工作会逐步被 AI 接管。

团队能力随之迁移：

| 过去 | 未来 |
|------|------|
| 画页面 | 定义系统 |
| 标注规范 | 维护 Token + Component |
| 手工对稿 | 制定 AI Generation Rule |
| 重复适配 | 建立 UX Constraint |

真正需要人的部分——系统定义、UX 判断、品牌决策、跨角色协作——**价值反而更高**。

> 过去，原型是"产品说明书"；
> 后来，原型变成"视觉设计稿"；
> 现在，原型正在变成"可执行系统"。
>
> 而 Figma，也正在从"画图工具"演化为"AI 时代的设计协作 IDE"。

---

## 实践：DramaFlow 的可执行设计系统

以下是 DramaFlow 项目中完整落地的可执行设计系统架构，包含目录结构、流水线、脚本和检查体系。

### 完整目录结构

```
design-system/                     # 唯一视觉真相源
├── tokens/                        # Layer 1: Design Token
│   ├── tokens.css                 # CSS 自定义属性（:root 上定义 60+ 变量）
│   ├── tokens.ts                  # TypeScript 等价版（组件动态样式引用）
│   └── tokens.schema.json         # JSON Schema — 验证 token 文件完整性
│
├── specs/                         # Layer 2: 约束 + 屏幕规格
│   ├── constraints.md             # 业务约束（可自动检查：单 btn-primary、loading 态…）
│   ├── design-rules.md            # AI 生成规则（Skill 触发时自动注入 Prompt）
│   └── screens/                   # 屏幕规格（平台无关的页面描述）
│       ├── home.yaml              # 首页：有哪些区块、什么顺序、从哪个 API 取数据
│       └── detail.yaml            # 详情页：同上
│
├── components/                    # Layer 3: 组件规格
│   ├── components.yaml            # 平台无关组件定义（所有属性的唯一源）
│   ├── components.css             # 生成：CSS 组件样式（H5 & prototype 直接引用）
│   ├── index.html                 # 组件 Gallery（可视化验证所有组件渲染效果）
│   └── android/                   # 生成：Android 组件样式
│       └── styles.xml
│
└── exports/                       # Layer 4: 平台导出
    ├── h5/
    │   └── designsystem.css       # 一键导入：tokens.css + components.css
    └── android/
        ├── colors.xml             # Android 颜色资源（从 tokens.css 生成）
        └── styles.xml             # Android 组件样式（从 components.yaml 生成）

scripts/
├── design-system/                 # Figma → design-system → 多平台代码
│   ├── figma_sync_tokens.py       # Figma Tokens Studio (DTCG JSON) → tokens.css + tokens.ts
│   ├── figma_sync_components.py   # Figma REST API → components.yaml
│   ├── figma_sync_screens.py      # Figma auto-layout pages → specs/screens/*.yaml
│   ├── generate_css.py            # components.yaml → components.css
│   ├── generate_android.py        # components.yaml + tokens.css → Android XML
│   ├── generate_prototype.py      # screen specs → HTML 原型
│   └── generate_h5_template.py    # screen specs → Vue 页面模板骨架
│
└── check/                         # 合规检查（CI/pre-commit 自动运行）
    ├── check_tokens.py            # Layer 1：检查硬编码色值 + 变量名是否正确
    ├── check_constraints.py       # Layer 2：检查业务约束是否满足
    └── check_components.py        # Layer 3：检查组件使用是否符合 components.yaml

prototype/
├── index.html                     # 原始手写原型（保留）
├── generated/                     # 从 screen spec 自动生成
│   ├── home.html                  # 引用 tokens.css + components.css
│   └── detail.html                # 包含 @component 标记，可提取为 Vue 组件
└── README.md
```

### 核心流水线

```
                    ┌─ Figma ──────────────────────────────┐
                    │                                        │
                    │  Variables ──Tokens Studio──> DTCG JSON│
                    │  Components ──REST API──> Node Tree    │
                    │  Pages ──REST API──> Auto-layout Tree  │
                    └──┬────────────┬────────────┬───────────┘
                       │            │            │
          ┌────────────┘            │            └──────────────┐
          ▼                         ▼                           ▼
   figma_sync_tokens.py   figma_sync_components.py   figma_sync_screens.py
          │                         │                           │
          ▼                         ▼                           ▼
   tokens/                  components/                 specs/screens/
   tokens.css               components.yaml             *.yaml
   tokens.ts                      │
          │                       │
          └───────────┬───────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   generate_css.py  generate_android.py  generate_prototype.py
          │           │                  │
          ▼           ▼                  ▼
   components.css  exports/android/   prototype/generated/
   (H5引用)        colors.xml          *.html
                   styles.xml
                   (Android引用)
```

### 三层规格比较

| 层 | 格式 | 定义什么 | 例 |
|----|------|---------|-----|
| Token | DTCG JSON → CSS/TS | 原子值 | `--color-primary: #6C5CE7` |
| Component | components.yaml → CSS/Android | 完整组件 | `.btn-primary { 渐变+padding+圆角+hover }` |
| Screen | screen.yaml → HTML/Vue/XML | 页面布局 | "首页 = AppBar + Banner + CategoryTabs + DramaGrid" |

### H5 中的使用方式

```typescript
// main.ts — 一次导入，全站可用
import '@design/exports/h5/designsystem.css'
```

```vue
<!-- 页面中只用 class，样式来自 design-system -->
<template>
  <button class="btn-primary" @click="play">▶ 立即观看</button>
  <div class="drama-card">
    <div class="thumb"><span class="badge">热播</span></div>
    <div class="info"><h4>{{ title }}</h4></div>
  </div>
</template>

<style scoped>
/* 只写页面特有布局，不重写组件样式 */
</style>
```

### Android 中的使用方式

```xml
<!-- 引用 design-system 导出的样式 -->
<Button
    style="@style/DramaFlow.Button.Primary"
    android:layout_width="match_parent"
    android:text="立即观看" />

<!-- 引用 design-system 导出的颜色 -->
<TextView
    android:textColor="@color/text_primary"
    android:background="@color/bg_primary" />
```

### 合规检查三层

```bash
# Layer 1: 没有硬编码色值，CSS 变量名都在 tokens.css 中有定义
python scripts/check/check_tokens.py --path h5/src
python scripts/check/check_tokens.py --path android/app/src/main/res/layout

# Layer 2: 业务约束满足
#   - 每页只有一个 btn-primary
#   - 异步操作有 loading 态
#   - 最小触摸目标 44px
#   - 卡片 3:4 比例
python scripts/check/check_constraints.py

# Layer 3: 组件使用正确
#   - class 名与 components.yaml 一致
#   - 组件嵌套结构符合 parts 定义
python scripts/check/check_components.py
```

### 设计 ←→ 开发的完整闭环

```
设计师在 Figma 中调整主题色
    → Tokens Studio 同步 DTCG JSON
    → figma_sync_tokens.py 更新 tokens.css
    → generate_css.py 重新生成 components.css
    → generate_android.py 重新生成 colors.xml + styles.xml
    → generate_prototype.py 重新生成原型 HTML
    → CI 运行 check_*.py，全部通过
    → PR 合并，H5/Android/原型同步更新
```

**改一处，全平台生效。Figma 是创作入口，design-system/ 是唯一真相源。**

---

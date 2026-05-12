# AI 时代的原型设计

## 目录

1. [演进全景：不只是工具在变](#演进全景不只是工具在变)
2. [文档时代：原型 = 沟通说明书](#文档时代原型-沟通说明书)
3. [视觉设计时代：原型 = 可复用设计组件](#视觉设计时代原型-可复用设计组件)
   - [Figma 为什么能崛起？](#figma-为什么能崛起)
4. [代码化时代：原型 = 可运行的组件](#代码化时代原型-可运行的组件)
   - [代表工具](#代表工具)
5. [AI 生成时代：原型 = 可执行的产品（进行中）](#ai-生成时代原型-可执行的产品进行中)
   - [最大的误解](#最大的误解)
6. [终态：可执行设计系统（Executable Design System）](#终态可执行设计系统executable-design-system)
   - [过去 vs 未来](#过去-vs-未来)
   - [未来设计体系的核心结构](#未来设计体系的核心结构)
   - [推荐目录结构](#推荐目录结构)
   - [AI 原型 Skill：让生成自动合规](#ai-原型-skill让生成自动合规)
   - [设计角色如何参与代码仓库](#设计角色如何参与代码仓库)
7. [设计权力中心的迁移](#设计权力中心的迁移)
8. [Figma 未来最核心的四个价值](#figma-未来最核心的四个价值)
9. [团队能力转变：执行层 → 系统定义层](#团队能力转变执行层-系统定义层)

---

## 演进全景：不只是工具在变

过去二十多年，软件行业的原型经历了四个时代的演进。这四个时代并非依次替换，而是**叠加积累**——每一层都建立在上一层之上，工具和方法论同时并存：

| 时代 | 代表工具 | 原型的本质 |
|------|---------|-----------|
| 文档时代 | Axure、PRD | 沟通说明书 |
| 视觉设计时代 | Figma、Design System | 可复用设计组件 |
| 代码化时代 | React、Storybook、shadcn | 可运行的组件 |
| AI 生成时代（进行中）| Bolt.new、v0、Lovable | 可执行的产品 |

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

用代码定义所有视觉常量，是整个系统的"单一真相源"：

```ts
// design-system/tokens.ts
export const tokens = {
  color: {
    primary:      '#6C5CE7',
    primaryLight: '#A29BFE',
    accent:       '#FD79A8',
    bgPrimary:    '#0F0F23',
    bgCard:       '#16163A',
    disabled:     '#4A4A6A',
  },
  spacing: { xs: '4px', sm: '8px', md: '16px', lg: '24px' },
  radius:  { sm: '8px', md: '12px', lg: '20px' },
  font:    { body: '14px', title: '18px', hero: '24px' },
}
```

**第三层：Component Runtime — 组件库**

组件消费 Token，暴露语义化 API，人和 AI 都能调用：

```tsx
// design-system/components/Button.tsx
<Button variant="primary" size="md" loading={isSubmitting}>
  立即购买
</Button>

// design-system/components/Card.tsx
<Card title="都市爱情" badge="热播" onFavorite={handleFav} />

// design-system/components/Modal.tsx
<Modal title="确认购买" onConfirm={handleBuy} onCancel={close} />
```

**第四层：AI Generation — AI 如何使用前三层**

给 AI 提供一个上下文文件，让它生成页面时遵循约束：

```markdown
<!-- ai-context/design-rules.md -->
## 可用组件
从 @/design-system/components 引入：Button、Card、Modal、Input、Toast

## Token 引用规范
所有颜色、间距、字体必须引用 tokens.ts，禁止写 #xxx 或 px 裸值

## 页面约束
- 遵守 constraints.md 中的业务规则
- 列表页使用 <Card /> 网格布局，间距 tokens.spacing.md
- 主 CTA 使用 <Button variant="primary" />，每页只能出现一个
```

AI 生成页面时，直接调用这些组件，输出的代码天然符合规范：

```tsx
// AI 生成的 pages/Home.tsx（调用已有组件，符合设计系统约束）
import { Card, Button } from '@/design-system/components'

export function HomePage() {
  return (
    <div style={{ background: tokens.color.bgPrimary }}>
      {dramas.map(d => <Card key={d.id} title={d.title} badge={d.tag} />)}
      <Button variant="primary">开始观看</Button>
    </div>
  )
}
```

**第五层：Figma — 可视化协作**

通过 **Tokens Studio** 插件将 `tokens.ts` 同步到 Figma，设计师在 Figma 中操作的是和代码同源的 Token，而非手动维护的色板：

- 产品经理在 Figma 中做 UX 走查、标注修改意见
- 设计师用 Figma 探索视觉节奏，AI 难以替代的微调在这里完成
- 评审、讨论、演示依然发生在 Figma，不需要所有人看代码

---

### 推荐目录结构

可执行设计系统作为代码的一部分，建议放在 `design-system/` 目录下统一维护：

```
design-system/
├── tokens.css             # CSS 变量（HTML 原型直接引用）
├── tokens.ts              # TypeScript 版本（Vue/React 组件引用）
├── constraints.md         # 业务约束与尺寸规范（给 AI 和团队看）
├── design-rules.md        # AI 生成规则（引用 tokens + constraints）
└── components/            # Component Runtime
    └── index.html         # 组件 Gallery（可视化验证所有组件渲染效果）

prototype/                 # HTML 可交互原型（直接引用 tokens.css）
scripts/                   # 工具脚本（check_design_tokens.py 等）
```

`tokens.ts` 是整个系统的起点：Figma 用它渲染，组件用它驱动样式，AI 用它约束生成。改一个 Token，整个系统同步更新。

### AI 原型 Skill：让生成自动合规

仅靠 `design-rules.md` 文件还不够——每次让 AI 生成原型时，仍需要手动提醒它"去读设计规范"。更好的做法是把这件事做成一个 **Claude Code Skill**，在触发原型生成任务时自动注入上下文。

Skill 的工作流大致如下：

```
用户："帮我生成剧集详情页"
    ↓ Skill 自动执行
1. 读取 design-system/tokens.css          ← 获取可用 Token
2. 读取 design-system/constraints.md      ← 获取业务约束
3. 读取 design-system/design-rules.md     ← 获取 AI 生成规则
4. 将三份文件作为上下文注入 Prompt
    ↓
AI 生成的页面代码：
- 只使用 tokens.* 引用颜色和间距
- 只从 @/design-system/components 引入组件
- 自动遵守约束（单页只有一个主 CTA 等）
```

这个 Skill 的价值在于：**设计系统的遵守从"靠人记忆"变成"系统默认"**。团队成员无需每次手动提醒 AI，生成结果天然合规。

### 设计角色如何参与代码仓库

可执行设计系统有一个现实问题：`tokens.ts` 和 `constraints.md` 住在代码仓库里，但设计师和产品经理通常不使用 Git。实践中有几种方式可以低门槛地参与。

**参与分两个维度：写入规范 和 查看效果。**

---

#### 写入规范：三种门槛递增的方式

**方式一：GitLab 网页直接编辑（零门槛）**

`constraints.md` 和 `design-rules.md` 是纯文字文件。设计师和 PM 直接在 GitLab 网页上打开、编辑、提交 MR——体验和编辑 Notion 文档接近，无需安装任何本地工具：

```
GitLab 网页
→ 找到 design-system/constraints.md
→ 点击网页编辑按钮
→ 修改规则，填写变更说明
→ 提交 MR，等待开发 Review 合并
```

**方式二：Tokens Studio 同步 Token（Figma 原生）**

`tokens.ts` 的修改不需要设计师手动写代码。Figma 的 **Tokens Studio** 插件支持连接内部 Git 平台并双向同步：

```
设计师在 Figma 中调整色值或间距
    ↓ Tokens Studio 插件
自动生成 MR 更新 tokens.ts
    ↓ 开发 Review 合并
全系统 Token 同步更新
```

**方式三：成为 CODEOWNERS（深度参与）**

对于希望深度把关的设计负责人，在仓库配置中将其设为 `design-system/` 目录的 Owner：

```
# .gitlab/CODEOWNERS 或 .github/CODEOWNERS
design-system/tokens.ts       @design-lead
design-system/constraints.md  @product-lead @design-lead
```

效果：任何人修改这两个文件，**必须经过设计负责人 Approve 才能合并**。设计规范的守门人从"发 Figma 评论"变成了"MR Approve"。

---

#### 查看效果：改了之后怎么看结果？

只能编辑文件、看不到效果，是设计角色参与代码仓库最大的摩擦点。有三种途径解决：

**途径一：prototype/ 目录即时预览**

`prototype/` 目录的 HTML 原型直接引用 `tokens.ts` 导出的 CSS 变量，Token 修改后浏览器刷新即见效果，适合本地快速验证。

**途径二：Storybook 组件预览**

MR 合并后 CI 自动重新构建并部署 Storybook，设计师在内网访问即可看到所有组件在最新 Token 下的渲染效果，以及各种 props 状态。

**途径三：MR 触发预览环境**

MR 提交时 CI 自动构建独立预览环境，MR 页面出现 Preview 链接，设计师点击直接在完整真实页面中验收效果。

---

**三种预览方式对比：**

| 途径 | 反馈速度 | 覆盖范围 | 适用场景 |
|------|---------|---------|---------|
| prototype/ 本地刷新 | 即时 | 原型页面 | 本地快速探索 |
| Storybook 组件库 | 合并后分钟级 | 所有组件状态 | 团队日常参考 |
| PR 预览环境 | MR 提交后分钟级 | 完整真实页面 | 正式变更验收 |

---

**这个变化最根本的意义是：**

过去，规范写在 Figma 标注里，开发可以选择性遵守，设计师改了色值也不知道有没有生效。

未来，规范写在仓库里，每次修改有 diff、有 review、有历史记录，效果可以立即在原型或预览环境中看到——**规范的变更和代码的变更一样可追溯，执行结果也肉眼可见**。

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
Design Token → React Component → AI 生成页面
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

# 《AI Native 项目实战训练营》

## 课程简介

本课程以**海外短剧 APP（DramaFlow）**为核心载体，带领学员完整经历从产品设计、视觉设计、架构搭建到三轮迭代开发、集成测试、代码审阅与重构的全流程，同时还包括已有功能的改版升级。课程通过实战过程将 AI-Native 研发的核心方法论——Spec 驱动开发（SDD）、Agent 友好型架构、Skills 设计、CR与重构等 —— 全部落实在真实项目步骤中，让学员"做中学、学中做"。

五条知识体系贯穿两天实战，每条线在项目的不同阶段分层触发，形成"引入→深化→掌握"的学习螺旋。两天各设一次分享总结，集中讨论发现的问题与解决方案，确保学员离场前完成认知内化。

课程时长 **2 天**，教学形式以项目实战为主，辅以理论讲解和主题研讨。

---

## 适合人群

| 梯队 | 适合对象 |
|------|----------|
| 核心受益 | 有一定工程经验、希望将 AI 深度融入日常研发的软件工程师、全栈或移动端开发 |
| 同样适合 | 产品负责人、技术 TL，希望理解 Spec 驱动开发并推动团队 AI 工具链落地 |
| 管理视角 | 研发效能负责人，希望建立企业级 AI 研发规范与 SDD 工作流 |

---

## 课程收益

- 亲手完成三端独立架构（Python FastAPI 后端 + Kotlin 原生 Android + Vue3 H5）短剧 APP 的三轮迭代，获得从产品设计到上线的完整 AI Native 开发经验
- 掌握轻量 SDD 工作流（SPEC.md + CLAUDE.md + Skills），可直接带回团队落地
- 建立 AI 编程的人机边界认知：什么能做好、什么做不好、哪些卡点必须人工决策
- 掌握 AI 辅助 CR + 重构的方法论：如何寻找重构线索，如何在不破坏测试的前提下安全改造
- 理解 Agent 友好型架构：学会用文档约束 Agent 行为，可迁移至企业存量系统改造

---

## 课程特色

**真实项目驱动**

**三轮迭代，递进难度**

**五条知识体系贯穿练习之中**

---

## 技术栈（可调）

### 技术选型

| 层次 | 技术选型 | 备注 |
|------|---------|------|
| 移动端 | Kotlin + Android Studio | 原生 Android，Google 官方首选语言，AI 生成质量优于 Java |
| H5（WebView 内嵌）| Vue3 + Vite | 内嵌于 Android WebView，负责内容类页面，改动无需 APP 发版 |
| 后端 API（主）| Python 3.10+ + FastAPI | AI 友好：语法简洁，自动生成 Swagger 文档，SDD 演示主线 |
| 后端 API（辅）| Java Spring Boot + IDEA | 关键 API 片段演示，覆盖企业 Java 技术栈，不维护完整项目 |
| 版本管理 | Git（GitHub / Gitee）| 教学保障：预设分支，学员掉队时可一键同步代码进度 |
| 视频分发（CDN）| 七牛云（Qiniu）| 流畅体验：利用测试域名绕过备案，实现短视频流的"秒开"效果 |
| 数据库 | SQLite | 零维护成本 |
| 数据模型（后端）| Pydantic（Python 类型系统）| 逻辑核心：统一后端数据结构，配合 AI 自动生成前端模型 |
| 状态管理（Android）| ViewModel + LiveData | 标准 Android 架构组件，简单可靠 |
| 状态管理（Vue3）| Pinia | 轻量，AI 生成代码质量高 |
| 设计工具 | HTML/CSS 原型（浏览器预览）| 由 Claude Code 从 PRD 直接生成，作为视觉验收基准；WebView 页面可直接演进为 Vue3 组件 |
| IDE | Android Studio（移动端）/ VS Code（H5 + Python）/ IntelliJ（Java）| |
| AI 工具 | Claude Code + GLM / DeepSeek | 核心 Agent 及模型 |
| 后端测试 | Thunder Client（VS Code）/ pytest 集成测试 | |
| 前端测试 | Android Espresso（行为级）/ Vue3 Cypress（H5 E2E）| |

### 学员课前准备

- [ ] **Java 17** + **Android Studio** + API 34 SDK + **模拟器 AVD**（arm64-v8a 镜像，Pixel 6 Pro 推荐）
- [ ] **VS Code**（H5 + Python）或 **IntelliJ IDEA**（Android）安装 **Claude Code 插件**
- [ ] **Python 3.10+**，并提前创建好 venv
- [ ] **Node.js 20 LTS**
- [ ] **GLM / DeepSeek API Key**（二选一）
- [ ] **七牛云**：注册后创建 Bucket，记录 AccessKey + SecretKey（测试域名无需备案）
- [ ] **环境变量**：`JAVA_HOME`、`ANDROID_HOME`、adb/emulator 加入 PATH

---

## 项目介绍：DramaFlow 海外短剧 APP

### 三轮迭代功能范围参考

**迭代 1 — 用户认证 + 首页（Day 1 下午）**

| 模块 | 必做功能 | 实现端 | 可选进阶 |
|------|---------|--------|---------|
| Auth | FastAPI JWT 注册 / 登录 / 登出 | Python 后端 + Android 原生登录页 | 第三方 OAuth 登录 |
| Home | Banner 轮播 + 分类 Tab + 剧集列表 | Vue3 H5（WebView 内嵌）| 骨架屏加载效果 |
| 数据层 | Drama/Episode SQLite 模型 + 测试数据 | Python 后端 | 数据分页加载 |

**迭代 2 — 内容消费核心（Day 2 上午）**

| 模块 | 必做功能 | 实现端 | 可选进阶 |
|------|---------|--------|---------|
| Drama Detail | 剧集详情：简介 + 集数列表 + 评分 | Vue3 H5（WebView 内嵌）| 用户评论区 |
| Player | 视频播放器 + 进度控制条 | Android 原生（ExoPlayer）| 横屏全屏 + 手势快进 |
| Watch Progress | 播放进度持久化 | Python 后端 + Android 调用 | 断点续播提示 UI |

**迭代 3 — 需求演进与功能改造（Day 2 下午）**

> 核心挑战：模拟真实项目中"PM 改需求"的场景——在已交付代码上修改功能，而非添加全新模块。Agent 必须先理解已有设计意图，才能安全地修改。

| 改造场景 | 改造内容 | 实现端 |
|---------|---------|--------|
| 首页推荐改版 | 从"按分类展示"改为"基于观看历史的个性化推荐"→ 修改数据模型、API 逻辑和首页 UI | Python 后端 + Vue3 H5 推荐页 |
| 播放器功能增强 | 在已有播放器状态机上新增倍速控制 | Android 原生（ExoPlayer）|
| Auth 增强 | 添加"记住我"（持久化 Token），修改已有登录流程和安全逻辑 | Python 后端 + Android 原生 |

| 可选进阶 |
|---------|
| 播放器画质切换 |
| 首页 A/B 测试开关（验证改版推荐效果）|
| 播放进度跨设备同步（多端合并逻辑）|

---

## 知识体系

本课程将知识点组织为 **5 条知识体系**，每条线在项目的不同阶段在用到的时候分层讲解，而非一次性灌输。

| 主线 | 对应知识点 |
|------|-----------|
| **规格驱动** | PRD→Spec、增量 Spec、SDD、OpenSpec等工具 |
| **Agent友好架构** | CLAUDE.md、模块 README、Architecture as Code |
| **技能设计** | Skill实践、参数设计、管理、幂等性 |
| **测试自愈** | 行为级测试、Bug 注入、RCA |
| **HITL** | CR 触发时机、人工审阅节点、重构判断标准 |

---

## 课程大纲

### Day 1

#### 1. 认知重构与 AI 编程经验（1h）

> 目标：建立"AI Native"思维，以工程师实战经验为核心

**1.1 AI 能力演进的工程含义（20min）**

- 从补全到推理（CoT / o1 / o3）：能力跃迁对软件工程意味着什么
- S-P-A 架构速览：Agent 如何感知-规划-执行（规格驱动/Agent友好架构的理论基础）
- 三级记忆模型：为什么上下文管理是 Agent 的核心挑战
- 未来工作模式：全能个体 + 多 Agent 与 Harness + 上下文窗口与成本管理

**1.2 AI 编程核心经验（25min）**

十个关键认知，经验总结，配以演示：

1. 把需求写成结构化 Prompt，而不是口头描述
2. 设计先行，架构不能外包
3. 小步拆解，每步可验证
4. 用好 Git，随时掌握节奏
5. 必须看代码，很多微观工程决策需要人来定，Debug 要给足上下文
6. 哪些任务AI不擅长
7. 代码量增长后及时重构
8. 用 CLAUDE.md 固化约束，而不是每次在 Prompt 里重复
9. 管理好 Session 和上下文窗口
10. 分清执行类和架构类任务，善用对比提问
11. 保持人类最终裁决权（HITL）

**1.3 工具链说明（15min）**

- 工具与模型选择：Agent介绍，GLM / DeepSeek选择
- Claude Code实用技巧：上下文超 50% 时主动 /compact 并指明保留方向；走偏了 Esc Esc 回滚，不硬扛；复杂任务先 Shift+Tab 进入 Plan Mode 规划再执行；小任务一句话完成，别上全套流程。

---

#### 2. 产品设计（2h）

> 目标：完成产品定义和可执行 Spec

**2.1 [实践步骤] 竞品分析 + PRD 生成（20min）**

- 任务：分析 Viki / WeTV / DramaBox 核心功能，生成 DramaFlow PRD
- 产出：`PRD.md`（All-in-One 单文件，包含以下内容）
  1. **产品定位与目标用户**：一句话定位、用户画像分层
  2. **功能范围**：按迭代划分，标注 P0/P1/P2 优先级，关联实现端
  3. **非功能需求**：性能、安全、兼容性等约束
  4. **技术架构概要**：前后端选型与通信方式

**2.2 [实践步骤] 撰写可执行 Spec（30min）**

- **为什么 PRD 不够用**：PRD 描述"做什么"，但开发需要"怎么做才算完成"。可执行 Spec 的每项验收标准（AC）都可供开发者或 AI Agent 逐条自检，减少理解偏差和返工。
- **五段式格式**：领域名词 → 前置条件 → 主流程 → 异常处理 → 验收标准（AC）。
- 范围：仅覆盖迭代 1+2（Drama / Episode / User / WatchRecord），迭代 3 的 Spec 在 Day 2 下午以增量方式补写
- 产出：`SPEC.md` 初版；培训场景以主体功能可用为验收标准，无需追求完备性
- 提效演示：让 Claude 从 PRD 草稿自动提取五段式 Spec 骨架，人工确认 AC
- **HITL 检查点**：AC 的最终确认必须由人完成

**2.3 [实践步骤] HTML 原型生成（25min）**

- 任务：Claude Code / Codex 直接基于 PRD 生成可交互 HTML 原型，浏览器打开确认视觉方向，满意后截图存入 `docs/designs/`
- **原型 + 可执行 Spec 模式**：原型负责“看得见的流程”，Spec负责“看不见但必须正确的逻辑”。

**2.4 [实践步骤] 视觉验收（15min）**

- **用工具提取设计 Token**：让 Claude Code 直接从原型 HTML/CSS 中提取颜色、字体、间距，生成 `design_system.md`，无需手动翻阅
- **利用工具从多个维度提升验收效率**：分层验证逻辑，主流工具，自研工具方案，利用验收自动化串联流程
- **写入视觉 AC**：将关键验收标准（如"首页 Banner 使用 Primary #6C5CE7"）写入 SPEC.md，后续开发可逐条自检
- **产出**：`design_system.md` + `docs/designs/` 参考截图 + SPEC.md 视觉验收 AC

**2.5 [Agent友好架构][HITL] PM 利用 Agent 直接改代码快速试错（15min）**

> PM 用自然语言描述产品优化意图，Agent 直接改代码（H5 + 后端），PM 在预览环境验收改动效果，满意后开发接手并参考改动。

- **预览部署**：每次提交可自动构建并部署到 SaaS 预览环境（含后端 + H5），PM 获得可分享的预览链接。
- **改对地方**：Agent 友好架构是前提——模块 README 清晰、CLAUDE.md 描述全栈结构，Agent 能准确理解改动涉及哪些层，减少误改和漏改。
- **可观测性**：错误和变更影响以产品语言呈现，PM 无需读日志即可判断改动是否符合预期。
- **PM 专用 Skill**：`preview-change`（描述本次改动对用户的影响）、`safe-check`（提交前验证，结果以非技术语言呈现）
- **开发接手**：开发可直接参考，形成协作闭环

*午休 12:00–14:00*

---

#### 3. 项目工程化（40min）

> 目标：搭建 Agent 友好型项目骨架，写入最小约束

**3.1 [Agent友好架构] CLAUDE.md 是 Agent 的”宪法”，Repo 即 Agent 的”操作系统”**

**3.2 [实践步骤] 项目初始化 + 架构骨架（15min）**

- 指令示例：`基于 SPEC.md 的模块划分，生成 Kotlin Android 项目骨架 + Vue3 H5 项目骨架 + Python FastAPI 后端骨架 + SQLite 初始化脚本`
- 产出：可编译的项目目录结构（android/ + h5/ + backend/）+ 每个模块的 README 模板

**3.3 [实践步骤][规格驱动] 撰写 CLAUDE.md + Prompt SDD 初体验（15min）**

- 写入技术栈说明、架构约束（禁止跨模块直接调用）、命名规范、构建方式、测试命令，只放不可推断的信息，能从代码推断的不写。
- 写入 SDD 最小约束：接受任务前必须阅读对应 Spec、生成代码后自检 AC
- **演示**："无 Spec" vs "有 Spec"的 AI 响应差异；CLAUDE.md 中 SDD 约束如何影响 Agent 行为。
- Prompt SDD 的本质：在 CLAUDE.md 中固化约束 → Agent 读取后自动遵循

---

#### 4. 迭代 1：用户认证 + 首页（约 3h15min）

> 功能：FastAPI JWT 认证 + 首页（Banner + 分类 + 剧集列表）

**4.1 [实践步骤] Auth 模块开发（40min）**

- 任务：Python FastAPI 认证接口（注册 / 登录 / JWT）+ Kotlin Android 登录页（ViewModel + LiveData 表单）
- **演示重点**：Claude Code 读取 CLAUDE.md + auth/README.md + SPEC.md → 生成代码（Agent 如何利用上下文）
- 开发策略：先生成 Pydantic 数据模型和 API 路由（后端），再补充 Android UI 逻辑（多轮约束生成）
- **Java 辅助演示**：同一登录接口用 Java Spring Boot 实现一遍，对比 AI 在两种语言下的代码生成差异

**4.2 [实践步骤] 数据层（15min）**

- 任务：Drama / Episode / Category Pydantic 模型 + SQLAlchemy ORM Repository 层（SQLite 后端，Category 模型直接服务于 4.3 Home 页分类 Tab）
- **自我尝试**：第一轮不读 SPEC.md，直接让 AI 生成数据模型 → 第二轮加入 SPEC.md 约束重新生成 → 对比两次输出差异，体会 SDD 如何约束 AI 输出质量

**4.3 [实践步骤] Home 首页开发（55min）**

- 任务：Python 后端 `/api/dramas` 接口 + Vue3 H5 首页（Banner 轮播 + 分类 Tab + 剧集列表 + Pinia 状态管理）+ Android WebView 加载

**4.4 [实践步骤] 实现第一个 Skill（30min）**

- **Skill 设计理念与适用场景**：什么场景应该封装成 Skill？颗粒度如何把握？Skill目录结构，参数设计原则（最小化、自包含）
- **最佳实践**：幂等性（可重复调用不产生副作用）、结构化反馈（成功/失败/变更明细）、可重复调用的设计模式、无需推理的固定逻辑考量用代码实现。
- **实现 `rebuild-deploy` Skill**：编译 H5 → 启动后端 → 启动模拟器 → 安装 App 全流程，一键部署到模拟器
- 参考最佳实践，尝试重构和简化skill，讨论“用代码实现无需推理的固定逻辑”的必要性

**4.5 [测试自愈] 怎么做测试（25min）**

- 选择API级测试：单元测试绑定实现，AI 加速后技术债积累更快，维护成本高于价值。后端用 pytest 测 API 行为，不测实现。
- 选择行为级测试：Android 用 Espresso / ADB / UI Automator 测用户操作流程，Vue3 H5 用 Cypress 测端到端，可以设计为利用 Claude Code 等 Agent 调度测试流程
- 用 AI 生成测试场景矩阵（正常 / 异常 / 边界），人工筛选关键场景
- **实现 `spec-validate` Skill**：以 Spec 为唯一来源，AC 覆盖检查，补充 API 测试，作为 SDD 的验收门

**4.6 [实践步骤] CR + 重构（25min）**

- **实现 `cr-refactor` Skill**：输出 CR 清单 + 重构建议，参数最小化设计（只接受路径，自动定位问题）
- 寻找重构线索的提问框架及AI高频错误模式（重复逻辑 / 状态泄漏 / 命名混乱 / 不遵循设计 / 啰嗦的注释或实现）
- 学员按优先级执行 2–3 条重构，人工确认不破坏已通过的集成测试。

---

#### 5. Day 1 分享总结（30min）

> 目标：让学员将一天的实战体验转化为可表达的认知，暴露问题，共同探讨解决方案

- 今天最大的一个发现 / 踩过的一个坑
- 探讨高频问题
- 提出明天迭代 2 的关注点（带着问题进入第二天）

---

### Day 2

#### 6. 迭代 2：剧集详情 + 播放器（2h40min）

> 功能：Drama Detail 页（Vue3 H5）+ ExoPlayer 视频播放器（Android）+ 播放进度持久化

**6.1 [规格驱动] OpenSpec：从 Prompt SDD 到工具化 SDD（15min）**

- 问题暴露：项目复杂度上升后纯 Prompt 约束的局限（约束易遗漏、AC 无法自动化验证、Traceability 缺失）
- OpenSpec 核心能力演示：Change Proposal → Spec → Task → 实现
- 工具原理说明：Claude Code，OpenSpec 及 Spec 的互动关系
- 与 Prompt SDD 的对比跃迁：从"读 Spec → 编码 → 手动检查"到"Spec 即代码 → 自动化验证"，什么样的团队/项目值得引入工具化 SDD。

**6.2 [实践步骤] Drama Detail 页（25min）**

- 任务：Python 后端 `/api/dramas/{id}` 接口 + **Vue3 H5** 详情页（简介 / 集数列表 / 评分）+ Android WebView 加载
- **演示重点**：Agent 如何通过 Project Context 自动发现关联的 Pydantic 模型（跨文件定位）；Android WebView 与 H5 的通信机制（JSBridge）

**6.3 [实践步骤] 视频播放器集成（35min）**

- 任务：Python 后端七牛云（Qiniu）签名 URL 接口 + Android **ExoPlayer** 集成 + 自定义控制条（Kotlin）

**6.4 [实践步骤] 播放器状态机（20min）**

- 任务：实现最基础的状态记忆
- 留意状态机缺陷（缓冲/错误状态遗漏），识别"必须人工接手"的信号

**6.5 [实践步骤] 播放进度持久化（20min）**

- SQLite WatchRecord 模型 + 播放记录读写接口 + Android 写入调用

**6.6 [实践步骤] 迭代 2 集成测试 + CR + 重构（25min）**

- Bug 注入演练——让 Agent 读取 Python / Android 错误日志自动修复；如何写出"不脆弱"的集成测试
- 两轮代码积累后的系统性重构——跨模块重复模式识别；重构 vs 重写的判断标准；保持行为不变的重构提示词
- Architecture as Code——演示将架构规则嵌入 ruff / pylint（Python）/ Android Lint 自定义规则，阻止 AI 生成违规代码；ADR 写法示例

**6.7 [实践步骤] Agent自动化验收/探索性测试实践（30min）**

- **解读测试框架**：了解 test-agent（基于ADB）的 CLI 命令、核心模块及原理
- **设计验收场景**：编写 mission YAML，定义从登录到播放的核心验收路径，明确预期屏幕和通过条件
- **编写验收测试 Skill**：理解 Skill 如何编排"截图→观察→定位→操作→记录→检查"的执行循环，基于 test-agent CLI 实现验收测试 Skill，设计参数（指定 mission 路径）、执行逻辑和结果反馈格式
- **执行和完善验收测试**：运行测试 → 修复遇到的框架缺陷、环境适配、步骤不合理等问题 → 利用屏幕知识 `screen_knowledge/`提高执行效率和稳定性

---

#### 7. Day 2 上午分享总结（20min）

> 目标：趁着进入最复杂迭代（需求改造）之前，沉淀前两个迭代的认知

- 迭代 2 中遇到的最棘手问题（播放器状态 / AI 上下文断裂 / 测试不稳定）
- 重点讨论："AI 在哪里失效了？你是怎么接手的？"
- 迭代 3 的挑战：在已有代码上改需求，如何兼顾设计与实现

*午休 12:00–14:00*

---

#### 8. 迭代 3：需求演进与功能改造（2h40min）

> 改造场景：首页推荐改版 + 播放器功能增强 + Auth 增强

**8.1 [规格驱动] 增量更新可执行 Spec（10min）**

- 迭代 3 是需求演进，而非全新开发——原有 SPEC.md 中的 AC 需要增量更新
- 变更 Spec 的原则：直接覆盖为最新意图，历史由 git 记录。
- 演示：在首页推荐改版场景中，在原 Spec 基础上追加新 AC，标注哪些变更了

**8.2 [规格驱动] 引入 GSD——上下文工程 + 阶段化执行（10min）**

- 存量改造最大的挑战不是"改哪里"，而是"让 Agent 理解上下文不丢失"（context rot）
- GSD 核心理念：把复杂改造任务拆成原子计划，按阶段执行，每阶段可验证
- **演示**：修改首页推荐前，先用 GSD 思路输出"当前行为分析"→ 按阶段分解 → 逐阶段执行
- `cr-refactor` vs GSD：前者是快速扫描影响范围，适合"先看看再改"；后者是系统化的阶段化执行框架，适合"知道要改什么但步骤复杂"。二者是替代选择，按场景选用
- 适用场景：长任务、跨模块改造、重构

**8.3 [实践步骤] 首页推荐改版（40min）**

- 任务：修改后端推荐 API（从按分类查询改为基于 WatchRecord 的个性化排序）+ 更新 Vue3 H5 首页数据绑定
- **演示**：用 `cr-refactor` Skill 先理解现有首页逻辑 → 再生成改造方案，对比"直接改"的 AI 响应
- 在变更的 AC 旁用注释标注变更版本以便追溯（可选），或直接依赖 git 记录。

**8.4 [实践步骤] 播放器增强 + Auth 增强（55min）**

- 播放器：在已有 ExoPlayer 状态机中新增倍速枚举和状态转换（Kotlin）→ 演示 AI 对有限状态机的理解局限
- Auth：Android SharedPreferences / EncryptedSharedPreferences 持久化 Token + FastAPI JWT 自动刷新逻辑 → 安全逻辑须人工逐行审阅，不能依赖 AI 判断

**8.5 [实践步骤] 迭代 3 集成测试 + CR + 重构（45min）**

- 运行 `spec-validate`（重点：现有 AC 覆盖率是否仍然通过）
- 需求变更引入的技术债 vs 新增功能的技术债——区分"接受"和"立即修复"
- RCA 框架走一遍（现象 → 证据 → 假设 → 验证 → 根因）——以播放器回归失败为案例
- SDD 闭环回顾——Spec 变更 → 代码变更 → 测试验收的完整链条

---

#### 9. 要点深入讲解（1h）

> 目标：系统总结两天实战经验，深入讲解案例未能充分展示的内容

**9.1 AI 编程最佳实践（15min）**

- 从三轮迭代实战中现场提炼 Top 10 实践
- 人机协作的"黄金分割线"：哪些交给 AI，哪些必须人工
- **重构是 AI 时代的必修课**：AI 生成速度越快，技术债积累越快；如何建立团队重构节奏
- Vibe Coding vs SDD：两天的对比结论
- 效率提升的正确度量：不是"代码生成速度"，而是"交付质量 × 速度"

**9.2 Skills 深度设计（10min）**

- CLI Skill vs MCP Server 选型：确定性要求高 → Skill；生态集成需求强 → MCP
- 复杂 Skill 设计模式：**参数最小化**（减少模型出错）/ **结构化反馈**（stdout 让 Agent 自修复）/ **幂等性**（重复调用安全）/ **错误恢复**（降级逻辑）
- 本课程 3 个 Skills 的设计复盘：哪里设计好了？哪里还可以改进？
- 企业级 Skill 库：分层（个人 / 项目 / 团队）、版本管理、共享机制

**9.3 SDD 生态全景与选型指南（25min）**

- 回顾三层 SDD 递进：Prompt SDD（迭代1）→ OpenSpec（迭代2）→ GSD（迭代3）
- SDD 生态一览：
  - **Superpowers**（方法论与技能层）：把 TDD、调试、Review 等工程习惯变成默认动作
  - **OMC / Oh My ClaudeCode**（多代理编排层）：围绕 Claude Code 做 team-first orchestration
  - **ECC / Everything Claude Code**（增强层）：用 Skills、Instincts、Memory 补全 Harness 能力
  - **Trellis**（结构层）：用 Specs / Tasks / Workspace 组织跨平台工作流和项目记忆
- 构建团队自己的 SDD：基于已有框架裁剪或组合，根据项目特点和步骤要求形成团队的开箱即用模板

**9.4 存量系统 Agent 友好改造（10min）**

改造路径（优先级排序）：

1. **模块化 MD 优先级**：从变动最频繁的模块开始，先写 README 再改代码
2. **DDD 划分限界上下文**：将 Agent 任务限制在局部，压缩单次推理负担
3. **接口契约标准化**：OpenAPI / Protobuf 描述所有接口，减少 Agent 通讯幻觉
4. **典型任务的实现路径**：通过提炼典型任务帮助模型快速理解如何在设计约束下实现复杂任务
5. **ADR 历史决策记录**：让 Agent 不重蹈覆辙；从 Git History 提炼实现模式

Architecture as Code 工具链：ruff / pylint（Python）/ Android Lint（Kotlin）/ ESLint（Vue3）将架构规则嵌入 CI，由机器代替人工审查。
# 知识点扩展

## 1. Skill 真正不可替代的场景

### 背景：Agent 也能推理执行，为何还需要 Skill？

对于开发者来说，`/seed-data` 和直接对 Agent 说"添加测试数据"最终效果相似——Agent 都能找到 seed.py 并执行。如果非技术人员需要改业务逻辑或 UI，本来就需要下载全部代码、需要 Agent 理解全貌，一个孤立的 Skill 解决不了这个问题。

### Skill 的核心价值

Skill 的价值不在"替 Agent 找脚本"，而在以下四个更窄、更确定的场景：

#### 1. 权限隔离

Skill 可以精确限定它能做什么。例如 `/seed-data` 只申请操作数据库的权限，而不需要 "Run Arbitrary Python" 的全局权限。在权限敏感的环境中，这是安全层面的关键差异。

#### 2. 结构化输出

Agent 的自然语言回复不稳定——有时说"导入完成"，有时说"数据已存在"。Skill 可以输出 JSON，让 CI pipeline、测试框架或其他自动化工具程序化消费结果。

#### 3. 跨会话的确定性

在一个新会话里说"加测试数据"，Agent 的行为有方差：
- 正确找到 seed.py ✅
- 自己写一段 INSERT 语句 ❌
- 尝试用 SQLite CLI 直接操作 ❌
- 问你要什么数据格式 ❌

Skill 消除这种方差——每次结果一致，不管当前上下文是什么。

#### 4. 低频操作者的记忆成本

区分用户的不应是"非技术人员 vs 技术人员"，而是"天天用的人 vs 两周用一次的人"。Skill 为后者消除了每次重新摸索的成本。

### 何时值得将操作为 Skill

| 场景 | 价值 | 说明 |
|------|------|------|
| CI 自动化中需要程序化调用 | 高 | 结构化输出可被 pipeline 消费 |
| 操作涉及多个步骤且顺序固定 | 高 | 消除 Agent 推理偏差 |
| 需要精确权限控制 | 高 | 最小权限原则 |
| 低频但重要的操作 | 中 | 减少记忆成本 |
| Agent 本身能稳定搞定的简单操作 | 低 | 边际效益不高 |

---

## 2. SPEC.md 与 PRD.md 的分工

| 维度 | PRD.md | SPEC.md |
|------|--------|---------|
| 读者 | PM、设计师、管理者 | 开发者、Agent |
| 粒度 | 功能列表、用户故事 | 领域名词、前置条件、主流程、异常处理、AC |
| 结构 | Kano 优先级 | 五段式格式 |
| 是否可执行 | 否（意图层） | 是（验收层） |

核心原则：**PRD 定义"做什么"，SPEC 定义"怎么做才对"**。Agent 的 SDD 约束要求生成代码后逐条自检 AC，所以 AC 必须是可测试的。

---

## 3. 自研视觉验收的路线与取舍

### 背景：为什么不能直接全屏像素 diff

用设计稿截图直接和 App 运行截图做全屏像素对比，会面临严重的噪音问题：动态内容（用户名、剧名、时间戳）、CDN 图片（封面图每次不同）、渲染差异（抗锯齿、字体 fallback）产生的差异远大于真正的回归信号。全屏像素 diff 在实际项目中几乎不可用。

### 三层验证体系

```
高信号/低噪音  ┌─────────────────┐
               │ 布局树语义对比    │  原生页面首选
               ├─────────────────┤
               │ 区域 ROI 像素检查│  关键位置颜色/图标验证
               ├─────────────────┤
               │ AI 视觉评估      │  兜底，处理渲染差异化
               └─────────────────┘
 低信号/高噪音
```

#### 第一层：布局树语义对比

不碰像素，直接比较 UI Automator XML 的结构化特征。核心思路是不比"树的形状"，比"用户可感知的语义特征"：

| 对比规则 | 说明 |
|---------|------|
| 容器类型互认 | LinearLayout / FrameLayout / ConstraintLayout 视为等价 |
| 子节点排序归一 | 按 y→x 排序后对比，不按 XML 原始顺序 |
| 渲染舍入容忍 | bounds 差异 ≤ 2px 忽略 |
| 中间层展平 | 新增/移除纯容器层不报差异 |
| 真正报警的 diff | resource-id 增删、交互元素 bounds 偏移 > 8px、静态文本变化、可点击区域数量变化、visibility 变化 |

能覆盖的错误：元素缺失/偏移、文案错误、按钮消失。**抓不到的**：颜色/样式异常、裂图、字体替换、CSS 渲染异常。

#### 第二层：区域 ROI 像素检查

布局树覆盖不到的颜色、图标、背景渐变，按页面区域分别定义检查策略。关键问题：**不关心的区域怎么自动识别？**

**推荐方案：多 baseline 消噪。** 同一个页面跑 3 次，自动 diff 各次截图，反复出现差异的区域自动标记为动态区域（IGNORE），稳定区域出 diff 才报警。零人工配置，3 次运行后自动收敛。

| 组件类型 | 检查策略 | 理由 |
|---------|---------|------|
| ImageView | 只检查 bounds + visibility | 内容是 CDN 图片 |
| 动态 TextView（无 android:text） | 忽略 text，检查 bounds | 用户名、剧名等 |
| 静态 TextView（有 android:text） | text + bounds 都查 | 固定文案 |
| Button | text + bounds + 可点击态 | 交互元素 |
| 分隔线/背景 | 只查颜色和尺寸 | — |

#### 第三层：AI 视觉兜底

布局树和 ROI 都验证通过，但渲染效果仍然可能异常——这是纯自动化方案的天花板。让 AI（Claude）看图评估，覆盖剩余 30% 的场景：字体替换、H5 CSS 渲染异常、裂图、颜色编译错误。配合前两层过滤掉"布局没问题"的信息，AI 可以聚焦于真正的渲染问题，判断质量和成本都更好。

### 一测一补策略

```
布局树对比 ──pass──→ ROI diff ──pass──→ AI 看图评估 ──pass──→ ✅ 通过
   │ fail                 │ fail                 │ fail
   ↓                     ↓                     ↓
报具体错误            标记可疑区域                输出差异描述
（哪个元素偏移/缺失）  （截图 + 热力图）          （自然语言报告）
```

### 进阶路线

| 阶段 | 能力 | 投入 | 覆盖范围 |
|------|------|------|---------|
| P0 基线 | 多 baseline 消噪 + 布局树语义对比 | ~2 天 | 原生页面 70% 视觉回归 |
| P1 增强 | ROI 像素 diff + H5 CDP DOM 对比 | +2 天 | 关键区域颜色/图标 + H5 布局 |
| P2 AI 兜底 | Claude 看图评估接入 | +1 天 | 剩下 30% 渲染/样式异常 |
| P3 设计稿校验 | 设计稿 → baseline 的一次性 AI 评估 | +1 天 | 新功能首次上线前的设计还原度检查 |

### 关键决策点

1. **Golden image 不应是设计稿，而是真机 baseline。** 首次在稳定版本上跑用例，截图+存 XML 标为 baseline。设计稿只在新功能上线前做一次性 AI 评估，之后就转为自动化对比。

2. **纯自动化方案有上限。** 布局树 + ROI diff 只能覆盖约 70% 的视觉回归，剩余 30%（样式、渲染、H5 兼容性）需要 AI 看图来兜底。承认这一点比追求 100% 纯自动化更务实。

3. **H5 页面是自然难点。** WebView 内的渲染 UI Automator 拿不到内部结构，只能靠截图 diff 和 Chrome DevTools Protocol DOM 对比，精度低于原生页面。

---

## 4. 探索性验收测试的技术方案

### 架构：AI 决策 + 原子操作执行

```
┌─────────────────────┐       HTTP (localhost)        ┌──────────────────────┐
│  Claude Agent       │  ─── POST /tap /type /swipe ─▶│  Android Device      │
│  (大脑: 看截图、     │  ◀── screenshot / hierarchy ──│  UI Automator 服务   │
│   决策下一步)        │                               │  (稳定执行层)        │
└─────────────────────┘                               └──────────────────────┘
         │                                                       │
         │  adb forward tcp:8711 tcp:8711                        │
         │  (端口转发，电脑→手机)                                  │
```

### 两层分工

| 层 | 职责 | 技术 | 特点 |
|----|------|------|------|
| 决策层 | 看截图判断状态、规划操作、验证结果 | Claude 视觉识别 | 灵活，能处理意外弹窗和布局变化 |
| 执行层 | 找元素、点击、输入、截屏、获取 UI 树 | UI Automator HTTP Server | 稳定，元素级定位不依赖像素坐标 |

### 当前实现（test-agent）

Python CLI 工具集 + Claude 驱动的探索性测试循环：

- **核心模块**：adb_client / device / element_finder / crash_monitor / verifier / reporter
- **设备交互**：通过 ADB 命令（`input tap`、`screencap`、`uiautomator dump`、`logcat`）
- **测试任务**：YAML 定义的 mission 文件（smoke_test / login_flow / browse_content / playback_test）
- **执行流程**：Observe → Plan → Locate → Act → Record

### 从纯 ADB 到 UI Automator 的演进

| | 纯 ADB（当前） | UI Automator Server（推荐） |
|---|---|---|
| 找元素 | `uiautomator dump` + 硬解析 XML | `By.res()`、`By.text()` 官方 API |
| 点击 | `input tap x y`（像素坐标） | `.click()` 元素级点击，自适应位置 |
| 输入 | `input text`（不支持中文） | `.text = "..."` 原生输入 |
| 等待 | 轮询 Activity 名 | `device.wait(Until.findObject(...), 5000)` |
| 延迟 | 每次启动新进程 | 内存常驻服务，毫秒级响应 |

### 与 Espresso 的定位差异

| | Espresso | test-agent (AI 驱动) |
|---|---|---|
| 决策者 | 开发者写死脚本 | Claude 运行时决策 |
| 确定性 | 高，适合 CI 回归防线 | 低，适合探索找 bug |
| 验证粒度 | 精确到 View 内部状态 | 视觉级验证（布局/渲染/颜色） |
| 代码耦合 | 需要 View ID、编译测试 APK | 纯黑盒，零耦合 |

核心原则：**两者互补而非替代**。Espresso 做回归守门，AI 驱动方案做验收和探索测试。推荐的改进方向是将执行层从原始 ADB 替换为 UI Automator HTTP Server，以最小的架构变动获得最大的执行稳定性。

---

## 5. Espresso / UI Automator 的传统做法简记

### 定位

| | Espresso | UI Automator |
|---|---|---|
| 范围 | **单 App 内**，白盒，需源码 | **跨 App**，黑盒，无需源码 |
| 执行 | 注入 App 进程运行 | 独立进程，通过 Accessibility 服务 |
| 典型场景 | 组件/集成测试，回归 | 跨 App 流程、系统级测试 |
| 编译产物 | 单独的测试 APK | 测试 APK 或 standalone jar |

### 核心 API 模式

**Espresso**——声明式匹配 + 操作 + 断言：
```kotlin
onView(withId(R.id.login_button))         // 找控件（声明式 Matcher）
    .perform(click())                       // 执行操作
    .check(matches(isDisplayed()))          // 验证结果

// 常用匹配器：withId / withText / withTag / hasDescendant / allOf
// 常用操作：click / typeText / scrollTo / swipeLeft / closeSoftKeyboard
// 常用断言：isDisplayed / withText / isEnabled / isSelected / doesNotExist
// 异步等待：IdlingResource（自动等，不用 sleep）
```

**UI Automator**——命令式查找 + 操作：
```kotlin
val device = UiDevice.getInstance(instrumentation)
device.findObject(By.text("登录")).click()     // 按文本找
device.findObject(By.res("com.dramaflow:id/btn")).click()  // 按 ID 找
device.findObject(By.desc("菜单")).click()      // 按 content-desc 找
// 常用 By：text / res / desc / clazz / pkg
// 支持跨 App：device.pressHome() / pressRecentApps() / openQuickSettings()
// 等待：device.wait(Until.findObject(...), timeout)
```

### 测试写法对比

**直接录制**（两种工具都支持）：
```bash
# 操作手机录制
adb shell am instrument -e class com.dramaflow.TestRecorder ...
# 或使用 Android Studio: Run > Record Espresso Test
# 点击手机操作 → 自动生成 onView().perform().check() 代码
```

**手动编写**：
```kotlin
@RunWith(AndroidJUnit4::class)
class LoginTest {
    @Test
    fun login_success() {
        onView(withId(R.id.username)).perform(typeText("test@test.com"))
        onView(withId(R.id.password)).perform(typeText("123456"))
        onView(withId(R.id.login_btn)).perform(click())
        onView(withId(R.id.home_title)).check(matches(isDisplayed()))
    }
}
```

### 运行命令

```bash
# Espresso / UI Automator 统一用 adb instrument 运行
adb shell am instrument -w com.dramaflow.test/androidx.test.runner.AndroidJUnitRunner

# 指定单个测试类
adb shell am instrument -w -e class com.dramaflow.LoginTest com.dramaflow.test/...
```

---


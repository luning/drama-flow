# Web Test Agent 设计

## 目标

在 `test-agent/` 目录下新增 Web 测试能力，与现有 Android test agent 共享纯工具层（reporter、recorder、config），其余完全分离——各自拥有 controller、missions、screen_knowledge、config.yaml、README.md。Agent 加载自己目录的内容，不看另一个 target 的东西。

## 架构

```
test-agent/
├── shared/                   # 纯工具，不含任何 target 数据
│   ├── reporter.py           # HTML 报告生成
│   ├── recorder.py           # 会话管理 & 步骤记录
│   └── config.py             # YAML 加载函数（不是配置内容）
├── android/                  # Android Agent（自包含）
│   ├── controller/           # ADB 能力集
│   │   ├── adb_client.py
│   │   ├── device.py
│   │   ├── crash_monitor.py
│   │   ├── element_finder.py
│   │   └── verifier.py
│   ├── missions/             # Android 专属任务
│   ├── screen_knowledge/     # Activity 陷阱知识
│   ├── config.yaml           # Android 配置
│   └── README.md             # Android 用法
├── web/                      # Web Agent（自包含）
│   ├── controller/           # Playwright 能力集
│   │   ├── browser.py
│   │   ├── page.py
│   │   ├── element_finder.py
│   │   └── error_monitor.py
│   ├── missions/             # Web 专属任务
│   ├── screen_knowledge/     # 页面/路由陷阱知识
│   ├── config.yaml           # Web 配置
│   └── README.md             # Web 用法
```

**关键原则**：任何文件都不混入两个 target 的内容。Agent 启动时已知自己的 target（android 或 web），只加载对应目录。

## 运行流程

Agent 是唯一的入口和编排者，无 CLI 入口文件。

```
Agent（已知自己是 web agent）
  → 加载 web/config.yaml
  → 加载 web/missions/{name}.yaml
  → 启动 browser controller，进入 base_url + start_path
  → 循环：
      → controller.screenshot() 观察页面
      → 查阅 web/screen_knowledge/{screen}.md 获取陷阱提示
      → 推理，决定下一步操作
      → 调用 controller 执行
      → 调用 shared/recorder.record_step(...) 记录
  → mission 完成
  → 调用 shared/reporter.generate(session) 输出 HTML 报告
```

## 目录重构

### shared/ — 从现有 core/ 迁移纯工具

| 现有路径 | 新路径 | 说明 |
|---------|--------|------|
| `core/reporter.py` | `shared/reporter.py` | HTML 报告生成 |
| `core/recorder.py` | `shared/recorder.py` | 步骤记录、会话管理 |
| — | `shared/config.py` | YAML 配置加载工具函数（新建） |

### android/ — 现有 Android 能力集集中

| 现有路径 | 新路径 | 说明 |
|---------|--------|------|
| `core/adb_client.py` | `android/controller/adb_client.py` | ADB 封装 |
| `core/device.py` | `android/controller/device.py` | 设备控制 |
| `core/crash_monitor.py` | `android/controller/crash_monitor.py` | 崩溃监控 |
| `core/element_finder.py` | `android/controller/element_finder.py` | UI 元素定位 |
| `core/verifier.py` | `android/controller/verifier.py` | 操作验证 |
| `missions/*.yaml` | `android/missions/*.yaml` | Android 专属任务 |
| `screen_knowledge/*.md` | `android/screen_knowledge/*.md` | Android 专属知识 |
| `config.yaml` | `android/config.yaml` | Android 专属配置 |
| `run.py` | 删除 | Agent 直接调用 controller |

### web/ — 新增 Web Agent

```
web/
├── controller/
│   ├── __init__.py
│   ├── browser.py          # 启动/关闭 Chromium，管理页面上下文
│   ├── page.py             # screenshot, click, type, scroll, navigate
│   ├── element_finder.py   # 基于 text/selector/role 查找 DOM 元素
│   └── error_monitor.py    # 监听 console.error、网络请求失败、页面崩溃
├── missions/               # Web 专属测试任务
│   └── *.yaml
├── screen_knowledge/       # Web 专属陷阱知识
│   └── *.md
├── config.yaml             # Web 专属配置
└── README.md               # Web Agent 用法
```

## Web Controller 能力集

对标 Android controller 的能力，提供 Playwright 驱动的等价操作：

| Android (ADB) | Web (Playwright) | 说明 |
|---------------|-------------------|------|
| `screenshot()` | `screenshot()` | 截取当前视口 PNG |
| `tap(x, y)` | `click(x, y)` | 按坐标点击 |
| `text("str")` | `type("str")` | 输入文本 |
| `swipe(x1,y1,x2,y2)` | `scroll(dx, dy)` | 滚动 |
| `back()` | `go_back()` | 浏览器后退 |
| `find("text")` | `find_by_text("text")` | 按文本查找元素 |
| `find_id("res")` | `find_by_selector("css")` | 按选择器查找元素 |
| `find_inputs()` | `find_inputs()` | 查找所有输入框 |
| `info()` | `get_current_url()` / `title()` | 获取当前状态 |
| `check()` (logcat) | `check_errors()` | 检查 console 错误/网络异常 |
| `wait --activity` | `wait_for_url(url)` | 等待页面跳转 |
| `dump_ui()` | `get_dom()` | 获取页面 DOM 结构 |
| — | `navigate(url)` | 导航到指定 URL（Web 新增） |

## config.web.yaml

```yaml
base_url: "http://localhost:5173"
start_path: "/"
headless: false
viewport_width: 390
viewport_height: 844
post_action_delay: 0.5
recording:
  output_dir: "test-agent/assets/reports"
  screenshot_dir: "test-agent/assets/screenshots"
```

## Mission 文件格式

Web 和 Android 的 mission YAML 格式相同，各放各的目录，不含对方字段：

```yaml
name: "冒烟测试"
description: "覆盖 App 核心路径：登录 → 浏览 → 播放"
max_steps: 40
max_idle_cycles: 6
goals:
  - "打开首页，确认显示内容列表"
  - "点击第一个内容，进入详情页"
  - "点击播放，确认播放器正常启动"
credentials:
  email: "test@test.com"
  password: "123456ab"
```

- `goals` 为自然语言，不绑定平台术语
- 平台特定配置（base_url、app_package 等）在各自 `config.yaml` 中
- `expected_screens` 也在各自 config 中，因为屏幕名称两平台不同

## Screen Knowledge 格式

两个 target 格式一致，按各自平台编写：

```markdown
# {PageName}

## 已知陷阱
- 登录按钮可能被键盘遮挡，需先按 Back 关闭键盘

## 预期元素
- 标题文本: "首页"
- 内容列表 visible

## 交互提示
- 卡片点击后跳转到 /detail/{id}
```

## README.md（web/ 目录下）

内容要点：
- Web Agent 测试 DramaFlow H5 页面，基于 Playwright
- 前置条件：Node.js、`npm install playwright`
- 启动 Vite dev server（可手动，也可在 config 中配 `dev_server_command`）
- mission 文件说明
- screen_knowledge 编写指南
- 与 shared/ 的 reporter/recorder 关系

## 验收标准 (AC)

1. `shared/` 包含 reporter.py、recorder.py、config.py，从现有 `core/` 迁移而来，无 Android 特定逻辑
2. `android/` 包含 controller、missions、screen_knowledge、config.yaml、README.md，所有原有文件均在 android/ 目录内，功能不变
3. `web/controller/` 提供与 Android controller 对等的 Playwright 操作能力集（screenshot、click、type、scroll、find_by_text、find_by_selector、find_inputs、navigate、get_current_url、get_dom、check_errors、wait_for_url、go_back）
4. Web Agent 加载 `web/config.yaml` 和 `web/missions/*.yaml` 后，能按 goals 逐步执行测试
5. `web/controller/error_monitor.py` 能捕获 console.error 和网络请求失败（4xx/5xx）
6. `web/screen_knowledge/` 支持按页面路由命名的 .md 陷阱文件
7. `web/README.md` 说明 Web Agent 用法，Agent 可直接参考执行
8. Android 探索性测试能力不退化（路径从 `core/` 变到 `android/controller/` 后功能等价）
9. 任何文件不含另一个 target 的内容（agent 不会加载到无关数据）

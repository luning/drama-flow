---
name: exploratory-test
description: Agent 驱动的 Android App 探索性测试——指定大致操作路径，Claude Code 自己看截图、决定操作、发现崩溃。当用户说"探索性测试"、"跑探索测试"、"自动探索"、"exploratory test"、"跑 smoke test"时触发。
---

# exploratory-test

Claude Code 自己作为"大脑"，通过看屏幕截图来探索 DramaFlow Android App，发现崩溃和异常。

## 原理

```
Claude Code (看截图 → 决定操作) → Bash CLI (执行 ADB 操作) → 检查 logcat → 记录步骤 → 循环
```

不需要 `ANTHROPIC_API_KEY`，不需要额外配置模型——直接用当前的 Claude Code 会话。

## 参数

| 参数 | 说明 |
|------|------|
| `--list` | 列出可用的 Mission 文件 |
| `<mission>` | 运行指定的 Mission（如 `smoke_test`）|

## 前置条件

- Android 模拟器已启动（或设备已连接）
- App 已安装（可先执行 `/rebuild-deploy`）
- 终端在项目根目录

## 执行步骤

### 模式一：交互式探索（默认，推荐）

Claude Code 逐步骤驱动测试循环，每一步都"看"截图再决定。

> **步骤 1（初始化）`**：运行 `python test-agent/run.py setup`。如果设备未连接，先告知用户确认模拟器在运行。如果 setup 成功，继续。

> **步骤 2（初始化 mission）`**：
> ```bash
> python test-agent/run.py init test-agent/missions/{mission_name}.yaml
> ```

> **步骤 3（开始循环）`**：对每一步执行以下子步骤：

> **3a. 截图**：`python test-agent/run.py screenshot` → 记住截图路径。

> **3b. 看截图**：用 Read 工具打开 `test-agent/assets/screenshots/current.png`，观察当前屏幕内容。

> **3c. 决定操作**：根据 Mission 目标和当前屏幕，选择下一步操作：
>   - **点击**：估计按钮/控件的坐标 → `python test-agent/run.py tap <x> <y>`
>   - **输入**：先确保输入框已焦点（先点一次），再 `python test-agent/run.py text "内容"`
>   - **滑动**：`python test-agent/run.py swipe x1 y1 x2 y2`
>   - **返回**：`python test-agent/run.py back`
>   - **查看状态**：`python test-agent/run.py info`

> **3d. 检查崩溃**：`python test-agent/run.py check`。如果有崩溃，注意记录。

> **3e. 记录步骤**：`python test-agent/run.py record "操作说明（中文描述为什么做这个操作）"`

> **3f. 判断是否继续**：
>   - 如果 Mission 目标已完成，跳到步骤 4
>   - 如果连续 5 步屏幕无变化，说明卡住了，跳到步骤 4
>   - 否则回到步骤 3a 继续

> **步骤 4（生成报告）`**：`python test-agent/run.py report` → 打印报告路径，告知用户用浏览器打开。

## 操作坐标参考

Pixel 6 API 34 模拟器（1080×1920）常用区域：
- 顶部状态栏：y < 100
- 输入框区域：y ≈ 400-600
- 中间内容：y ≈ 600-1400
- 底部导航：y ≈ 1750-1920
- 居中按钮：x ≈ 540

## 注意

- 每次 tap 后需要等待界面渲染（CLI 已内置 1.5s 延迟）
- 多步文本输入：先 tap 输入框聚焦，再 text 输入
- 如果遇到弹窗（如 Toast），等它消失再操作
- 记录崩溃时用 `python test-agent/run.py check` 查看详情

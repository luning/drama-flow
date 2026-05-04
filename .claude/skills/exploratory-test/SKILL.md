---
name: exploratory-test
description: Agent 驱动的 Android App 探索性测试——指定测试任务，Claude Code 看截图决定操作、发现崩溃。当用户说"探索性测试"、"跑探索测试"、"自动探索"、"exploratory test"、"跑 smoke test"时触发。
---

# exploratory-test

逐步骤探索 App：看截图 → 用 `find` 定位元素 → `tap` 执行（自动验证屏幕变化）→ `record` 记录（自动缓存）→ 循环。

## 前置条件

- 模拟器已启动或设备已连接，App 已安装（可先执行 `/rebuild-deploy`）
- 终端在项目根目录

## 执行流程

> **1. 初始化**
> ```bash
> python test-agent/run.py setup                          # 检测设备、启动 App、开启崩溃监控
> python test-agent/run.py init test-agent/missions/smoke_test.yaml  # 加载测试任务（同时显示缓存的 Recipe）
> ```

> **2. 截图 + 观察**
> ```bash
> python test-agent/run.py screenshot                     # 截图，用 Read 工具打开 current.png
> python test-agent/run.py info                           # 查看当前 Activity
> ```
> 拿到 Activity/Fragment 名称后，检查 `test-agent/assets/screen_knowledge/` 下是否有对应的 `.md` 文件。
> 如果有，**先读文件再继续操作**，避免重复踩坑。

> **3. 定位元素 + 执行操作**
> ```bash
> python test-agent/run.py find "登录"                    # 按文字搜索元素，返回精确坐标
> python test-agent/run.py tap 720 1802                   # 点击（自动验证屏幕是否变化）
> python test-agent/run.py text "test@test.com"           # 输入文本（先 tap 聚焦输入框）
> python test-agent/run.py swipe 500 1500 500 500         # 滑动
> python test-agent/run.py back                           # 返回
> python test-agent/run.py wait --activity "PlayerActivity"  # 等待目标界面出现
> python test-agent/run.py info                           # 查看当前 Activity
> ```

> **4. 记录步骤 + 检查崩溃**
> ```bash
> python test-agent/run.py record "登录成功，进入首页"     # 记录步骤（自动缓存到 Recipe）
> python test-agent/run.py check                          # 检查 logcat 是否有崩溃
> ```

> **5. 生成报告**
> ```bash
> python test-agent/run.py report                         # 输出 HTML 报告路径
> ```

重复步骤 2-4 直到 Mission 目标完成。

## 注意事项

### `tap` 返回 "Screen unchanged" 怎么办

Navigation Component 单 Activity 架构下，Fragment 切换不会触发 Activity 变化，此时 "Screen unchanged" 是**正常信号**。此时应该：

1. 用 `info` 查看当前 Activity（可能没变）
2. 用 `uiautomator dump` 对比操作前后的 UI 层次结构，确认内容是否变化
3. 对于 WebView 内的 H5 页面，通过 Chrome DevTools Protocol 检查 URL 或页面内容

### 截图不可见时的替代方案

如果 Read 工具无法渲染截图（显示 "Unsupported Image"），改用以下方式判断屏幕状态：

1. `info` — 查看当前 Activity
2. `uiautomator dump` — 获取完整 UI 层次，检查关键节点
3. `find "文字"` — 搜索页面上的文字确认当前页面
4. `find-id "resource_id"` — 搜索关键控件

## 命令速查

| 命令 | 作用 | 说明 |
|------|------|------|
| `setup` | 初始化设备 + App + 监控 | 只需执行一次 |
| `init <mission>` | 加载测试任务 | 自动显示已缓存的 Recipe |
| `screenshot` | 截图 | 保存到 `assets/screenshots/` |
| `find "文字"` | 按文字搜 UI 元素 | 返回坐标、resource-id、class |
| `find-id "xxx"` | 按 resource-id 搜 | |
| `find-inputs` | 找所有输入框 | |
| `tap x y` | 点击 | 自动验证屏幕是否变化 |
| `text "内容"` | 输入文本 | 需先 tap 聚焦 |
| `swipe x1 y1 x2 y2` | 滑动 | |
| `back` | 返回键 | |
| `wait --activity "xxx"` | 等待 Activity | 默认超时 5s |
| `info` | 查看当前 Activity | |
| `record "说明"` | 记录步骤 | 自动缓存到 Recipe |
| `check` | 检查崩溃 | |
| `report` | 生成 HTML 报告 | |
| `cache-status` | 查看已缓存的 Recipe | |

缓存文件：`test-agent/assets/screen_cache.json` — 自动累积，无需手动管理。

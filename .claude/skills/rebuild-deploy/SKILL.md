---
name: rebuild-deploy
description: 重新编译 H5 和 Android App 并部署到模拟器——编译 H5、确保后端运行、打包安装 App。当用户说"重新编译"、"编译前端"、"重新安装app"、"部署测试"、"rebuild"、"重新构建并启动"、"跑一下完整流程"时触发。
---

# rebuild-deploy

编译 H5 前端、确保后端服务在运行、编译并安装 Android App 到模拟器。

> 后端 Python 使用 `--reload` 模式，代码修改后自动热重启，无需手动重新部署。

## 参数

| 参数 | 说明 |
|------|------|
| `--restart` 或 `-r` | 强制重启后端（杀端口 + 重新启动）。默认行为是只启动、不强行重启。 |

使用示例：`/rebuild-deploy --restart`

## 前置条件

- Android SDK 位于 `~/Library/Android/sdk`
- 模拟器 AVD 名称为 `Pixel_6_API_34`
- 虚拟环境位于 `backend/drama-flow/`
- H5 依赖已安装（`h5/node_modules` 存在）

## 执行步骤

> **开始前**：检查 args 是否包含 `--restart` 或 `-r`，如果是则设 `RESTART=true` 变量，后续步骤 2 据此决定是否强制重启后端。

### 1. 编译 H5 前端

```bash
cd h5 && npm run build
```

### 2. 确保后端服务运行

检查端口 8000 是否有进程在监听，如果没有则启动后端。**默认不强行重启**——`--reload` 模式自动热重启。

如果传入 `--restart` 参数，则先杀端口再启动（适合改动了 uvicorn 配置、依赖版本或需要清理状态时使用）。

```bash
source backend/drama-flow/bin/activate

# 如果指定了重启标志，先杀进程
if [ "$RESTART" = "true" ]; then
  echo "Force restarting backend..."
  lsof -ti:8000 | xargs kill -9 2>/dev/null
  sleep 1
fi

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
  echo "Backend already running"
else
  echo "Starting backend server..."
  cd backend && \
  nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/dramaflow-backend.log 2>&1 &
  sleep 2
  curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "Backend started" || echo "Backend may not be ready yet"
fi
```

### 3. 检查并启动 Android 模拟器

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# 检查是否有已连接的设备（模拟器或真机）
DEVICES=$($ANDROID_HOME/platform-tools/adb devices | grep -v "List" | grep -v "^$" | wc -l)
if [ "$DEVICES" -eq 0 ]; then
  echo "No device connected. Launching emulator Pixel_6_API_34..."
  $ANDROID_HOME/emulator/emulator -avd Pixel_6_API_34 -no-snapshot-load > /tmp/dramaflow-emulator.log 2>&1 &
  echo "Waiting for emulator to boot (may take 30-60 seconds)..."
  $ANDROID_HOME/platform-tools/adb wait-for-device
  # 额外等待系统就绪
  for i in $(seq 1 30); do
    BOOT_COMPLETE=$($ANDROID_HOME/platform-tools/adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
    if [ "$BOOT_COMPLETE" = "1" ]; then
      echo "Emulator boot complete!"
      break
    fi
    sleep 2
  done
else
  echo "Device(s) already connected:"
  $ANDROID_HOME/platform-tools/adb devices
fi
```

### 4. 编译并安装 Android App

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
cd android
./gradlew installDebug
```

### 5. 输出部署报告

逐项输出各步骤结果：

```
- H5 Build: ok | failed
- Backend: running | started | failed
- Emulator: running | started | not_found
- App Install: ok | failed
- Status: ok | partial | failed

Backend log: /tmp/dramaflow-backend.log
API base URL: http://localhost:8000

Tips:
- App 已安装，在模拟器中打开 DramaFlow 即可查看
- 后端 API 文档: http://localhost:8000/docs
- 修改 Python 代码后 --reload 会自动热重启，无需重新运行此 skill
```

## 注意事项

- 如果某个步骤失败，后续步骤继续执行（不会中断），最终报告中会标明失败状态
- 模拟器启动较慢（通常 30-60 秒），脚本会等待启动完成后再安装 App
- 如果 H5 编译报 TypeScript 类型错误，检查 `h5/src` 下的类型定义
- 如需重置数据库后再部署，先调用 `db-reset`
- 仅修改 Python 代码时无需运行此 skill，`--reload` 已覆盖

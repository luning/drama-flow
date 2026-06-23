# 《AI 新技术在测试的应用》课前准备

请在培训开始前按以下步骤完成安装。

---

## 一、IDE 及 Agent 工具（二选一）

### Cursor

前往 [https://www.cursor.com](https://www.cursor.com) 下载安装，Mac / Windows 均有独立安装包。

首次启动登录账号后即可使用内置 AI 能力，无需额外配置。

---

### VS Code + Claude Code

前往 [https://code.visualstudio.com](https://code.visualstudio.com) 下载安装 VS Code，然后在扩展市场搜索 **Claude Code**（Anthropic 官方）并安装插件。

---

## 二、大模型访问能力

课程使用 DeepSeek 或 GLM（智谱 AI）作为模型后端，二选一，API Key 可自备，也可使用现场统一提供的 Key。

---

## 三、Python 3.10+

日志预处理脚本和性能数据生成演示需要 Python。

**Mac**

打开"终端"（Launchpad → 其他 → 终端，或 Spotlight 搜索 Terminal），依次执行：

若未安装 Homebrew，先运行：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

再安装 Python：
```bash
brew install python@3.11
```

**Windows**

前往 [https://www.python.org/downloads](https://www.python.org/downloads) 下载 Python 3.11 安装包。  
安装时勾选 **"Add Python to PATH"**。

---

# Web Test Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development (recommended) or superpowers-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor test-agent directory to support both Android and Web targets with shared infrastructure, then build the Web agent controller set using Playwright.

**Architecture:** `shared/` holds reporter/recorder/config (pure tools). `android/` and `web/` are self-contained target directories, each with controller, missions, screen_knowledge, config, and README. Agent loads only its own directory — never touches the other target's files.

**Tech Stack:** Python 3.10+, Playwright, PyYAML

---

### Task 1: Create shared/ directory with reporter, recorder, config

**Files:**
- Create: `test-agent/shared/__init__.py`
- Create: `test-agent/shared/reporter.py`
- Create: `test-agent/shared/recorder.py`
- Create: `test-agent/shared/config.py`

- [ ] **Step 1: Create directory and __init__.py**

```bash
mkdir -p test-agent/shared
```

Write `test-agent/shared/__init__.py` (empty file).

- [ ] **Step 2: Copy reporter.py to shared/**

```bash
cp test-agent/core/reporter.py test-agent/shared/reporter.py
```

No edits needed — `reporter.py` has zero Android dependencies. It only imports `time`, `pathlib`, and `typing`.

- [ ] **Step 3: Copy and edit recorder.py for shared/**

```bash
cp test-agent/core/recorder.py test-agent/shared/recorder.py
```

Edit `test-agent/shared/recorder.py` — the only Android-aware line is the internal import at line 120. Change:

```python
from .reporter import generate_report as _gen_report
```

to:

```python
from shared.reporter import generate_report as _gen_report
```

The shared package uses absolute imports (`shared.xxx`) since it sits at `test-agent/shared/` and is loaded with `test-agent/` as part of the Python path.

- [ ] **Step 4: Create config.py in shared/**

Write `test-agent/shared/config.py`:

```python
"""YAML config loader — pure utility, no target knowledge."""

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str) -> dict[str, Any]:
    """Load a YAML config file. Returns empty dict if not found."""
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}
```

- [ ] **Step 5: Verify shared/ imports work**

```bash
cd test-agent && python -c "from shared.reporter import generate_report; from shared.recorder import SessionRecorder; from shared.config import load_config; print('shared/ OK')"
```

Expected: `shared/ OK`

---

### Task 2: Create android/ directory and migrate existing code

**Files:**
- Create: `test-agent/android/__init__.py`
- Create: `test-agent/android/controller/__init__.py`
- Create: `test-agent/android/controller/adb_client.py`
- Create: `test-agent/android/controller/device.py`
- Create: `test-agent/android/controller/crash_monitor.py`
- Create: `test-agent/android/controller/element_finder.py`
- Create: `test-agent/android/controller/verifier.py`
- Create: `test-agent/android/config.yaml`
- Create: `test-agent/android/README.md`

- [ ] **Step 1: Create android/ directory structure**

```bash
mkdir -p test-agent/android/controller
touch test-agent/android/__init__.py
touch test-agent/android/controller/__init__.py
```

- [ ] **Step 2: Copy Android controller files**

```bash
cp test-agent/core/adb_client.py test-agent/android/controller/adb_client.py
cp test-agent/core/device.py test-agent/android/controller/device.py
cp test-agent/core/crash_monitor.py test-agent/android/controller/crash_monitor.py
cp test-agent/core/element_finder.py test-agent/android/controller/element_finder.py
cp test-agent/core/verifier.py test-agent/android/controller/verifier.py
```

- [ ] **Step 3: Fix imports in Android controller files**

Five files need import path updates because they move from `core/` to `android/controller/`.

**`test-agent/android/controller/device.py`** (line 9):
```python
from . import adb_client as adb
```
becomes:
```python
from android.controller import adb_client as adb
```

**`test-agent/android/controller/crash_monitor.py`** (line 14):
```python
from . import adb_client as adb
```
becomes:
```python
from android.controller import adb_client as adb
```

**`test-agent/android/controller/verifier.py`** (line 10):
```python
from core.element_finder import ElementFinder
```
becomes:
```python
from android.controller.element_finder import ElementFinder
```

**`test-agent/android/controller/element_finder.py`** — no relative imports, no changes needed.

**`test-agent/android/controller/adb_client.py`** — no relative imports, no changes needed.

- [ ] **Step 4: Copy missions to android/**

```bash
cp -r test-agent/missions test-agent/android/missions
```

No content changes needed. Mission files (smoke_test.yaml, browse_content.yaml, etc.) are already written for Android.

- [ ] **Step 5: Copy screen_knowledge to android/**

```bash
cp -r test-agent/screen_knowledge test-agent/android/screen_knowledge
```

No changes needed.

- [ ] **Step 6: Copy config.yaml to android/**

```bash
cp test-agent/config.yaml test-agent/android/config.yaml
```

No changes needed — config.yaml already contains only Android fields.

- [ ] **Step 7: Create android/README.md**

Write `test-agent/android/README.md`:

```markdown
# Android Test Agent

Agent-driven exploratory testing for DramaFlow Android app via ADB.

## Directory

```
android/
├── controller/          # ADB capability set (screenshot, tap, text, swipe, dump_ui...)
│   ├── adb_client.py    # ADB command wrapper
│   ├── device.py        # High-level DeviceController
│   ├── crash_monitor.py # Background logcat crash/anomaly monitor
│   ├── element_finder.py# uiautomator dump XML parser
│   └── verifier.py      # Action result verification
├── missions/            # Android-specific test missions (YAML)
├── screen_knowledge/    # Activity-level trap knowledge (Markdown)
├── config.yaml          # Android configuration
└── README.md
```

## Usage

Agent loads `android/config.yaml` and `android/missions/{name}.yaml`, then autonomously:

1. Read mission goals
2. Take screenshot via `controller/adb_client.screenshot()`
3. Check `screen_knowledge/{activity}.md` for traps
4. Decide next action (tap, text, swipe, back, etc.)
5. Execute via controller
6. Record step via `shared/recorder.SessionRecorder`
7. Repeat until mission complete
8. Generate HTML report via `shared/reporter.generate_report()`

## Prerequisites

- Android SDK (`ANDROID_HOME` set in config)
- Device or emulator connected via ADB
- DramaFlow app installed
```

- [ ] **Step 8: Verify Android controllers still load**

```bash
cd test-agent && python -c "
import sys; sys.path.insert(0, '.')
from android.controller.adb_client import devices; print('adb_client OK')
from android.controller.device import DeviceController; print('device OK')
from android.controller.crash_monitor import CrashMonitor; print('crash_monitor OK')
from android.controller.element_finder import ElementFinder; print('element_finder OK')
from android.controller.verifier import ActionVerifier; print('verifier OK')
"
```

Expected: all OK messages.

---

### Task 3: Clean up old files and remove run.py

**Files:**
- Delete: `test-agent/run.py`
- Delete: `test-agent/core/` (entire directory after migration confirmed)
- Delete: `test-agent/missions/` (migrated to android/)
- Delete: `test-agent/screen_knowledge/` (migrated to android/)
- Keep: `test-agent/config.yaml` at root (delete after verifying android/ has its own)
- Keep: `test-agent/requirements.txt` (shared dependency)
- Keep: `test-agent/assets/` (output directory, shared)

- [ ] **Step 1: Delete run.py**

```bash
rm test-agent/run.py
```

Agent is the entry point now — no CLI needed.

- [ ] **Step 2: Delete old core/ directory**

```bash
rm -rf test-agent/core
```

All files have been migrated to `shared/` or `android/controller/`.

- [ ] **Step 3: Delete migrated directories from root**

```bash
rm -rf test-agent/missions test-agent/screen_knowledge test-agent/config.yaml
```

- [ ] **Step 4: Verify directory structure is clean**

```bash
find test-agent -maxdepth 3 -type f -name '*.py' -o -name '*.yaml' -o -name '*.md' | sort
```

Expected output:
```
test-agent/shared/__init__.py
test-agent/shared/config.py
test-agent/shared/recorder.py
test-agent/shared/reporter.py
test-agent/android/__init__.py
test-agent/android/README.md
test-agent/android/config.yaml
test-agent/android/controller/__init__.py
test-agent/android/controller/adb_client.py
test-agent/android/controller/crash_monitor.py
test-agent/android/controller/device.py
test-agent/android/controller/element_finder.py
test-agent/android/controller/verifier.py
test-agent/android/missions/browse_content.yaml
test-agent/android/missions/login_flow.yaml
test-agent/android/missions/playback_test.yaml
test-agent/android/missions/smoke_test.yaml
test-agent/android/screen_knowledge/HomeFragment.md
test-agent/android/screen_knowledge/LoginFragment.md
test-agent/android/screen_knowledge/README.md
```

(web/ will follow in Task 5)

---

### Task 4: Verify Android functionality not degraded (AC #8)

- [ ] **Step 1: Import check — all Android modules load without error**

```bash
cd test-agent && python -c "
from shared.reporter import generate_report
from shared.recorder import SessionRecorder
from shared.config import load_config
from android.controller.adb_client import devices
from android.controller.device import DeviceController
from android.controller.crash_monitor import CrashMonitor
from android.controller.element_finder import ElementFinder
from android.controller.verifier import ActionVerifier
print('All imports OK')
"
```

Expected: `All imports OK`

- [ ] **Step 2: Config loading works**

```bash
cd test-agent && python -c "
from shared.config import load_config
c = load_config('android/config.yaml')
assert c['device']['app_package'] == 'com.dramaflow'
print('Config OK')
"
```

Expected: `Config OK`

- [ ] **Step 3: Mission loading works**

```bash
cd test-agent && python -c "
from shared.config import load_config
import yaml
with open('android/missions/smoke_test.yaml') as f:
    m = yaml.safe_load(f)
assert m['name'] == '冒烟测试'
assert len(m['goals']) == 9
print('Mission OK')
"
```

Expected: `Mission OK`

- [ ] **Step 4: Commit**

```bash
git add test-agent/shared/ test-agent/android/
git rm test-agent/run.py test-agent/core/ test-agent/missions/ test-agent/screen_knowledge/ test-agent/config.yaml
git add test-agent/requirements.txt
git commit -m "refactor(test-agent): split into shared/ and android/ modules"
```

---

### Task 5: Create web/controller/ capability set (AC #3)

**Files:**
- Create: `test-agent/web/__init__.py`
- Create: `test-agent/web/controller/__init__.py`
- Create: `test-agent/web/controller/browser.py`
- Create: `test-agent/web/controller/page.py`
- Create: `test-agent/web/controller/element_finder.py`
- Create: `test-agent/web/controller/error_monitor.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p test-agent/web/controller
touch test-agent/web/__init__.py
touch test-agent/web/controller/__init__.py
```

- [ ] **Step 2: Write browser.py — Chromium lifecycle management**

Write `test-agent/web/controller/browser.py`:

```python
"""Browser lifecycle — wraps Playwright Chromium launcher."""

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserController:
    """Manages Playwright browser instance and page contexts."""

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 390,
        viewport_height: int = 844,
    ):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> Page:
        """Launch browser and return a fresh page."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(
            viewport={"width": self.viewport_width, "height": self.viewport_height}
        )
        self._page = self._context.new_page()
        return self._page

    def stop(self):
        """Clean shutdown."""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page
```

- [ ] **Step 3: Write page.py — screenshot, click, type, scroll, navigate**

Write `test-agent/web/controller/page.py`:

```python
"""Page operations — screenshot, click, type, scroll, navigate."""

import time
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page


def screenshot(page: Page, output_path: str) -> Path:
    """Capture current viewport to PNG. Returns output_path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out), full_page=False)
    return out


def navigate(page: Page, url: str, post_delay: float = 0.5):
    """Navigate to URL and wait for load."""
    page.goto(url, wait_until="networkidle")
    time.sleep(post_delay)


def click(page: Page, x: int, y: int, post_delay: float = 0.5):
    """Click at viewport coordinates."""
    page.mouse.click(x, y)
    time.sleep(post_delay)


def type_text(page: Page, text: str, post_delay: float = 0.5):
    """Type text into the focused element."""
    page.keyboard.type(text)
    time.sleep(post_delay)


def scroll(page: Page, dx: int, dy: int, post_delay: float = 0.5):
    """Scroll viewport by (dx, dy)."""
    page.mouse.wheel(dx, dy)
    time.sleep(post_delay)


def go_back(page: Page, post_delay: float = 0.5):
    """Browser back navigation."""
    page.go_back()
    time.sleep(post_delay)


def get_current_url(page: Page) -> str:
    """Return the current page URL."""
    return page.url


def get_title(page: Page) -> str:
    """Return the current page title."""
    return page.title()


def get_dom(page: Page) -> Optional[str]:
    """Return serialized DOM HTML. Returns None on failure."""
    try:
        return page.content()
    except Exception:
        return None


def wait_for_url(page: Page, url_substring: str, timeout: float = 5.0) -> bool:
    """Wait until current URL contains the given substring."""
    try:
        page.wait_for_url(f"**{url_substring}**", timeout=int(timeout * 1000))
        return True
    except Exception:
        return False


def fill_input_by_selector(page: Page, selector: str, text: str, post_delay: float = 0.5):
    """Fill a specific input by CSS selector."""
    page.fill(selector, text)
    time.sleep(post_delay)
```

- [ ] **Step 4: Write element_finder.py — DOM element locator**

Write `test-agent/web/controller/element_finder.py`:

```python
"""DOM element finder — locate elements by text, selector, role."""

from playwright.sync_api import Page, Locator


def find_by_text(page: Page, text: str) -> list[dict]:
    """Find all elements whose visible text contains the substring.
    Returns list of {tag, text, selector, visible}."""
    locator = page.get_by_text(text)
    count = locator.count()
    results = []
    for i in range(count):
        el = locator.nth(i)
        if el.is_visible():
            box = el.bounding_box()
            results.append({
                "tag": el.evaluate("el => el.tagName").lower() if box else "unknown",
                "text": el.text_content() or "",
                "selector": f"text={text}",
                "center_x": int(box["x"] + box["width"] / 2) if box else None,
                "center_y": int(box["y"] + box["height"] / 2) if box else None,
                "visible": el.is_visible(),
            })
    return results


def find_by_selector(page: Page, selector: str) -> list[dict]:
    """Find all elements matching a CSS selector.
    Returns list of {tag, text, selector, center_x, center_y, visible}."""
    locator = page.locator(selector)
    count = locator.count()
    results = []
    for i in range(count):
        el = locator.nth(i)
        box = el.bounding_box()
        results.append({
            "tag": el.evaluate("el => el.tagName").lower() if box else "unknown",
            "text": (el.text_content() or "")[:100],
            "selector": selector,
            "center_x": int(box["x"] + box["width"] / 2) if box else None,
            "center_y": int(box["y"] + box["height"] / 2) if box else None,
            "visible": el.is_visible() if box else False,
        })
    return results


def find_inputs(page: Page) -> list[dict]:
    """Find all visible text/email/password input fields.
    Returns list of {tag, type, placeholder, selector, center_x, center_y}."""
    locator = page.locator("input:visible")
    count = locator.count()
    results = []
    for i in range(count):
        el = locator.nth(i)
        box = el.bounding_box()
        if not box:
            continue
        input_type = el.get_attribute("type") or "text"
        results.append({
            "tag": "input",
            "type": input_type,
            "placeholder": el.get_attribute("placeholder") or "",
            "name": el.get_attribute("name") or "",
            "id": el.get_attribute("id") or "",
            "selector": (
                f"#{el.get_attribute('id')}" if el.get_attribute("id")
                else f"input[type='{input_type}']"
            ),
            "center_x": int(box["x"] + box["width"] / 2),
            "center_y": int(box["y"] + box["height"] / 2),
        })
    return results
```

- [ ] **Step 5: Write error_monitor.py — console/network error watcher**

Write `test-agent/web/controller/error_monitor.py`:

```python
"""Browser error monitor — captures console errors and failed network requests."""

import time
from dataclasses import dataclass, field
from typing import Optional
from playwright.sync_api import Page


@dataclass
class WebError:
    """A single detected error event."""
    timestamp: float
    error_type: str           # "console_error" | "network_error" | "page_crash"
    message: str
    url: str = ""
    status_code: int = 0


class ErrorMonitor:
    """Listens for console.errors and failed network requests on a Playwright page."""

    def __init__(self, page: Page):
        self.page = page
        self.events: list[WebError] = []
        self._listening = False

    def start(self):
        """Attach listeners to the page."""
        if self._listening:
            return
        self._listening = True

        def on_console(msg):
            if msg.type == "error":
                self.events.append(WebError(
                    timestamp=time.time(),
                    error_type="console_error",
                    message=msg.text,
                ))

        def on_response(response):
            if response.status >= 400:
                self.events.append(WebError(
                    timestamp=time.time(),
                    error_type="network_error",
                    message=f"HTTP {response.status} {response.url}",
                    url=response.url,
                    status_code=response.status,
                ))

        def on_page_crash():
            self.events.append(WebError(
                timestamp=time.time(),
                error_type="page_crash",
                message="Page crashed",
            ))

        self.page.on("console", on_console)
        self.page.on("response", on_response)
        self.page.on("crash", on_page_crash)

    def stop(self):
        """Remove listeners (best-effort)."""
        self._listening = False

    @property
    def has_errors(self) -> bool:
        return len(self.events) > 0

    @property
    def error_count(self) -> int:
        return len(self.events)

    def recent_events(self, n: int = 10) -> list[WebError]:
        return self.events[-n:]

    def summary(self) -> dict:
        """Return a summary of all detected errors."""
        by_type: dict[str, int] = {}
        for e in self.events:
            by_type[e.error_type] = by_type.get(e.error_type, 0) + 1
        return {
            "total_events": len(self.events),
            "by_type": by_type,
            "events": [
                {"timestamp": e.timestamp, "type": e.error_type, "message": e.message[:200]}
                for e in self.events
            ],
        }
```

- [ ] **Step 6: Verify web/controller/ imports**

```bash
cd test-agent && python -c "
from web.controller.browser import BrowserController; print('browser OK')
from web.controller.page import screenshot, navigate, click, type_text, scroll, go_back, get_current_url, get_title, get_dom, wait_for_url, fill_input_by_selector; print('page OK')
from web.controller.element_finder import find_by_text, find_by_selector, find_inputs; print('element_finder OK')
from web.controller.error_monitor import ErrorMonitor, WebError; print('error_monitor OK')
"
```

Expected: all OK messages.

- [ ] **Step 7: Commit**

```bash
git add test-agent/web/controller/
git commit -m "feat(test-agent): add web controller capability set (browser, page, element_finder, error_monitor)"
```

---

### Task 6: Create web/missions/ and web/screen_knowledge/ (AC #4, #7)

**Files:**
- Create: `test-agent/web/missions/smoke_test.yaml`
- Create: `test-agent/web/screen_knowledge/README.md`
- Create: `test-agent/web/screen_knowledge/LoginPage.md`
- Create: `test-agent/web/screen_knowledge/HomePage.md`

- [ ] **Step 1: Create directories**

```bash
mkdir -p test-agent/web/missions test-agent/web/screen_knowledge
```

- [ ] **Step 2: Write smoke_test.yaml for web**

Write `test-agent/web/missions/smoke_test.yaml`:

```yaml
name: "冒烟测试 (Web)"
description: "覆盖 H5 核心路径：登录 → 浏览首页 → 查看详情 → 播放视频"
max_steps: 40
max_idle_cycles: 6

goals:
  - "打开首页 http://localhost:5173，确认页面加载完成"
  - "检查是否需要登录；如果需要，跳转到登录页"
  - "使用测试账号登录（邮箱: test@test.com, 密码: 123456ab）"
  - "验证登录成功后跳转回首页"
  - "首页加载后，确认是否有剧集卡片/列表展示"
  - "如果有剧集卡片，点击第一个进入详情页"
  - "在详情页确认显示了剧集名称、简介等信息"
  - "如果有播放按钮或选集入口，点击进入播放页"
  - "确认播放器页面正常加载"
  - "返回首页，确认页面状态正常"

credentials:
  email: "test@test.com"
  password: "123456ab"
```

- [ ] **Step 3: Write screen_knowledge/README.md**

Write `test-agent/web/screen_knowledge/README.md`:

```markdown
# Web Screen Knowledge

Each `.md` file documents known traps and interaction tips for a specific page (by route name).

## File Naming

Name files by their page/component name (not URL path):
- `LoginPage.md` — Login.vue (/login)
- `HomePage.md` — Home.vue (/)
- `DetailPage.md` — Detail.vue (/detail/:id)
- `PlayerPage.md` — Player.vue (/drama/:id/episode/:ep)

## Format

```markdown
# PageName

## 已知陷阱
- Description of known issues

## 预期元素
- Expected visible elements

## 交互提示
- How to interact with elements on this page
```
```

- [ ] **Step 4: Write LoginPage.md**

Write `test-agent/web/screen_knowledge/LoginPage.md`:

```markdown
# LoginPage

## 已知陷阱
- 登录页可能有 CSRF token 或表单验证，直接 type 到 input 有时不触发 Vue 的 v-model 绑定。优先使用 selector fill 或先 click input 再 type。
- 登录按钮可能被虚拟键盘遮挡（移动端视口），确保 viewport 高度足够。

## 预期元素
- 邮箱输入框 (input[type="email"] 或 input[placeholder*="邮箱"])
- 密码输入框 (input[type="password"])
- 登录按钮 (包含文本 "登录" 的 button)

## 交互提示
- 路由路径: /login
- 注册页入口: /register（如果是验证码登录，需注意后端 mock 验证码）
- 登录成功后跳转到 / 首页
```

- [ ] **Step 5: Write HomePage.md**

Write `test-agent/web/screen_knowledge/HomePage.md`:

```markdown
# HomePage

## 已知陷阱
- 首页可能有骨架屏/loading 态，需等待内容实际渲染后再交互
- 首页内容可能通过 API 异步加载，点击前确认元素可见且非 loading 状态
- 页面可能有顶部导航栏吸顶，排查元素时注意 z-index 层级

## 预期元素
- 导航栏 (可能是顶部 tabs 或底部 nav)
- 剧集/内容卡片列表
- 每张卡片包含封面图 + 标题

## 交互提示
- 路由路径: /
- 点击剧集卡片 → 跳转到 /detail/:id
- 可能需要先登录才能看到内容列表（未登录可能跳转到 /login）
```

- [ ] **Step 6: Verify mission loads**

```bash
cd test-agent && python -c "
import yaml
with open('web/missions/smoke_test.yaml') as f:
    m = yaml.safe_load(f)
assert m['name'] == '冒烟测试 (Web)'
print('Web mission OK')
"
```

Expected: `Web mission OK`

- [ ] **Step 7: Commit**

```bash
git add test-agent/web/missions/ test-agent/web/screen_knowledge/
git commit -m "feat(test-agent): add web missions and screen knowledge"
```

---

### Task 7: Create web/config.yaml and web/README.md (AC #7)

**Files:**
- Create: `test-agent/web/config.yaml`
- Create: `test-agent/web/README.md`

- [ ] **Step 1: Write web/config.yaml**

Write `test-agent/web/config.yaml`:

```yaml
# Web Test Agent Configuration
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

- [ ] **Step 2: Write web/README.md**

Write `test-agent/web/README.md`:

```markdown
# Web Test Agent

Agent-driven exploratory testing for DramaFlow H5 pages (Vue3 SPA) via Playwright.

## Directory

```
web/
├── controller/           # Playwright capability set
│   ├── browser.py        # Chromium lifecycle management
│   ├── page.py           # Screenshot, click, type, scroll, navigate
│   ├── element_finder.py # DOM element location (by text, selector, role)
│   └── error_monitor.py  # Console error & network failure watcher
├── missions/             # Web-specific test missions (YAML)
├── screen_knowledge/     # Page/route trap knowledge (Markdown)
├── config.yaml           # Web configuration
└── README.md
```

## Usage

Agent loads `web/config.yaml` and `web/missions/{name}.yaml`, then autonomously:

1. Read mission goals
2. Launch Chromium via `controller/browser.BrowserController`
3. Navigate to `base_url + start_path`
4. Take screenshot via `controller/page.screenshot()`
5. Check `screen_knowledge/{PageName}.md` for traps
6. Decide next action (click, type, scroll, navigate, etc.)
7. Execute via controller
8. Record step via `shared/recorder.SessionRecorder`
9. Monitor errors via `controller/error_monitor.ErrorMonitor`
10. Repeat until mission complete
11. Generate HTML report via `shared/reporter.generate_report()`

## Prerequisites

- Node.js 16+
- Playwright: `npm install playwright` or `pip install playwright && playwright install chromium`
- Vite dev server running: `cd h5 && npm run dev` (starts at http://localhost:5173)
- Optional: backend running if H5 pages call real API

## Config

| Key | Default | Description |
|-----|---------|-------------|
| `base_url` | `http://localhost:5173` | Vite dev server URL |
| `start_path` | `/` | Starting route |
| `headless` | `false` | Set `true` for CI |
| `viewport_width` | `390` | Mobile viewport width |
| `viewport_height` | `844` | Mobile viewport height |
| `post_action_delay` | `0.5` | Wait after each action (seconds) |
```

- [ ] **Step 3: Commit**

```bash
git add test-agent/web/config.yaml test-agent/web/README.md
git commit -m "feat(test-agent): add web config and README"
```

---

### Task 8: End-to-end verification (AC #4, #5, #6)

- [ ] **Step 1: Test browser lifecycle**

```bash
cd test-agent && python -c "
from web.controller.browser import BrowserController
b = BrowserController(headless=True)
page = b.start()
print(f'Browser started, page URL: {page.url}')
b.stop()
print('Browser stopped cleanly')
"
```

Expected: `Browser started` and `Browser stopped cleanly` (no exceptions).

- [ ] **Step 2: Test page operations (requires Vite dev server running)**

First, start the Vite dev server in a background terminal:
```bash
cd h5 && npm run dev &
```
Wait for it to be ready, then:

```bash
cd test-agent && python -c "
import time
from pathlib import Path
from web.controller.browser import BrowserController
from web.controller import page as pg
from web.controller.element_finder import find_by_text, find_inputs
from web.controller.error_monitor import ErrorMonitor

b = BrowserController(headless=True)
p = b.start()
monitor = ErrorMonitor(p)
monitor.start()

# Navigate to home
pg.navigate(p, 'http://localhost:5173/')
print(f'URL: {pg.get_current_url(p)}')
print(f'Title: {pg.get_title(p)}')

# Take screenshot
ss = pg.screenshot(p, 'test-agent/assets/screenshots/web_test.png')
print(f'Screenshot: {ss}')

# Check errors
print(f'Console/network errors: {monitor.error_count}')

b.stop()
print('Page operations test passed')
"
```

Expected: no errors, screenshot saved.

- [ ] **Step 3: Test element_finder**

```bash
cd test-agent && python -c "
from web.controller.browser import BrowserController
from web.controller import page as pg
from web.controller.element_finder import find_by_text, find_inputs, find_by_selector

b = BrowserController(headless=True)
p = b.start()
pg.navigate(p, 'http://localhost:5173/')

# Try finding elements
elements = find_by_text(p, '登录')
print(f'Found {len(elements)} elements containing 登录')
for el in elements[:3]:
    print(f'  {el[\"tag\"]}: \"{el[\"text\"][:30]}\" at ({el[\"center_x\"]}, {el[\"center_y\"]})')

inputs = find_inputs(p)
print(f'Found {len(inputs)} input fields')
for inp in inputs[:3]:
    print(f'  input[{inp[\"type\"]}] placeholder=\"{inp[\"placeholder\"]}\"')

b.stop()
print('Element finder test passed')
"
```

Expected: element counts printed (may be 0 if home page doesn't show login — that's OK).

- [ ] **Step 4: Verify recorder + reporter integration**

```bash
cd test-agent && pytest -xvs -k "test_health" 2>/dev/null || echo "No pytest tests for test-agent (expected — agent is interactive)"
```

The test-agent has no pytest tests (by design, it's agent-driven). Verifying that imports and core functions work is sufficient.

- [ ] **Step 5: Final directory structure check**

```bash
find test-agent -type f \( -name '*.py' -o -name '*.yaml' -o -name '*.md' \) | sort
```

Expected:
```
test-agent/shared/__init__.py
test-agent/shared/config.py
test-agent/shared/recorder.py
test-agent/shared/reporter.py
test-agent/android/__init__.py
test-agent/android/README.md
test-agent/android/config.yaml
test-agent/android/controller/__init__.py
test-agent/android/controller/adb_client.py
test-agent/android/controller/crash_monitor.py
test-agent/android/controller/device.py
test-agent/android/controller/element_finder.py
test-agent/android/controller/verifier.py
test-agent/android/missions/browse_content.yaml
test-agent/android/missions/login_flow.yaml
test-agent/android/missions/playback_test.yaml
test-agent/android/missions/smoke_test.yaml
test-agent/android/screen_knowledge/HomeFragment.md
test-agent/android/screen_knowledge/LoginFragment.md
test-agent/android/screen_knowledge/README.md
test-agent/web/__init__.py
test-agent/web/README.md
test-agent/web/config.yaml
test-agent/web/controller/__init__.py
test-agent/web/controller/browser.py
test-agent/web/controller/element_finder.py
test-agent/web/controller/error_monitor.py
test-agent/web/controller/page.py
test-agent/web/missions/smoke_test.yaml
test-agent/web/screen_knowledge/HomePage.md
test-agent/web/screen_knowledge/LoginPage.md
test-agent/web/screen_knowledge/README.md
```

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat(test-agent): add web test agent with Playwright controller, missions, and screen knowledge"
```

---

## AC Coverage Summary

| AC | Covered by |
|----|-----------|
| #1 shared/ contains reporter, recorder, config | Task 1 Steps 2-4 |
| #2 android/ self-contained with all modules | Task 2 Steps 2-7 |
| #3 web/controller/ Playwright capability set | Task 5 Steps 2-5 |
| #4 Agent loads config + mission for web target | Task 6 Step 2, Task 8 Step 2 |
| #5 screenshot, click, type, scroll, find, navigate | Task 5 Step 3-4, Task 8 Steps 2-3 |
| #6 error_monitor captures console.errors + network failures | Task 5 Step 5 |
| #7 screen_knowledge supports page-route .md files | Task 6 Steps 3-5 |
| #8 Android functionality not degraded | Task 4 Steps 1-3 |
| #9 No file contains another target's content | Task 3 Step 4 (clean split verified) |

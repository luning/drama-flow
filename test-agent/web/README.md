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

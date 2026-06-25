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

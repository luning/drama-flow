#!/usr/bin/env python3
"""
DramaFlow Android Exploratory Test Agent — CLI tool for device control + recording.

Claude Code drives the testing loop interactively:
  1. Take screenshot → read with Read tool → decide next action
  2. Execute via CLI (tap/swipe/text/back)
  3. Record step → check for crashes
  4. Repeat

Usage:
  # Setup (one-time)
  python run.py setup                   Check device, launch app, start monitoring

  # Device interaction
  python run.py screenshot              Take screenshot → assets/screenshots/current.png
  python run.py tap <x> <y>             Tap at pixel coordinates
  python run.py text "hello"            Type text (when input field is focused)
  python run.py swipe x1 y1 x2 y2       Swipe gesture
  python run.py back                    Back key
  python run.py info                    Show current activity / screen info

  # Test recording
  python run.py init <mission.yaml>     Start a new mission recording
  python run.py record "reason text"    Record current step (screenshot + action reason)
  python run.py check                   Check logcat for new crashes
  python run.py note "text"             Save a note to the session
  python run.py report                  Generate HTML report

  # Listing
  python run.py --list                  List available missions
  python run.py --analyze               Quick screen analysis (take screenshot + describe)
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

from agent.device import DeviceController
from agent.crash_monitor import CrashMonitor
from agent.recorder import SessionRecorder


# --- helpers ----------------------------------------------------------------

def _load_config(path: str = "config.yaml") -> dict:
    config_path = Path(__file__).parent / path
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def _load_mission(path: str) -> dict:
    mission_path = Path(path)
    if not mission_path.exists():
        print(f"❌ Mission file not found: {mission_path}")
        sys.exit(1)
    with open(mission_path) as f:
        return yaml.safe_load(f) or {}


def _list_missions(missions_dir: str = "missions"):
    missions_path = Path(__file__).parent / missions_dir
    if not missions_path.exists():
        print(f"No missions directory at {missions_path}")
        return
    yaml_files = sorted(missions_path.glob("*.yaml")) + sorted(missions_path.glob("*.yml"))
    if not yaml_files:
        print(f"No mission files in {missions_path}")
        return
    print("\nAvailable Missions:")
    print("─" * 60)
    for mf in yaml_files:
        try:
            with open(mf) as f:
                data = yaml.safe_load(f)
            name = data.get("name", mf.stem)
            desc = data.get("description", "")
            steps = data.get("max_steps", "?")
            print(f"  📋 {name}")
            print(f"     File: {mf.relative_to(Path(__file__).parent)}")
            print(f"     Desc: {desc}")
            print(f"     Max steps: {steps}\n")
        except Exception as e:
            print(f"  ⚠ {mf.name}: {e}")


def _make_device(config: dict, serial: str = "") -> DeviceController:
    dc = config.get("device", {})
    return DeviceController(
        serial=serial or dc.get("serial", ""),
        app_package=dc.get("app_package", "com.dramaflow"),
        app_activity=dc.get("app_activity", ".MainActivity"),
        post_action_delay=dc.get("post_action_delay", 1.5),
        launch_delay=dc.get("launch_delay", 3.0),
        screenshot_dir=config.get("recording", {}).get("screenshot_dir", "assets/screenshots"),
    )


def _make_monitor(config: dict, serial: str = "") -> CrashMonitor:
    dc = config.get("device", {})
    cm = config.get("crash_monitor", {})
    return CrashMonitor(
        serial=serial or dc.get("serial", ""),
        buffer_size=cm.get("buffer_size", 1000),
        poll_interval=cm.get("poll_interval", 0.5),
        app_package=dc.get("app_package", "com.dramaflow"),
    )


# --- subcommands -------------------------------------------------------------

def cmd_setup(config: dict, serial: str):
    """Check device, launch app, start crash monitor."""
    print("🔌 Checking device...")
    device = _make_device(config, serial)
    device.ensure_device()
    print(f"   Device ready: {device.serial}")

    print("🚀 Launching app...")
    device.restart_app()
    print(f"   App launched: {device.app_package}")

    print("📡 Starting crash monitor...")
    monitor = _make_monitor(config, serial)
    monitor.start()
    print("   Crash monitor active")

    return device, monitor


def cmd_screenshot(config: dict, serial: str):
    """Take a screenshot and save to a well-known path."""
    device = _make_device(config, serial)
    device.ensure_device()
    path = device.take_screenshot("current")
    # Also save a copy as current.png for easy reference
    current_path = Path(config.get("recording", {}).get("screenshot_dir", "assets/screenshots")) / "current.png"
    import shutil
    shutil.copy(path, current_path)
    print(f"📸 Screenshot saved: {path}")
    print(f"   Current: {current_path}")
    return path


def cmd_tap(config: dict, serial: str, x: int, y: int):
    """Tap at screen coordinates."""
    device = _make_device(config, serial)
    device.ensure_device()
    device.tap(x, y)
    print(f"👆 Tapped ({x}, {y})")


def cmd_text(config: dict, serial: str, text_to_type: str):
    """Type text."""
    device = _make_device(config, serial)
    device.ensure_device()
    device.text(text_to_type)
    print(f"⌨ Typed: {text_to_type}")


def cmd_swipe(config: dict, serial: str, x1: int, y1: int, x2: int, y2: int):
    """Swipe gesture."""
    device = _make_device(config, serial)
    device.ensure_device()
    device.swipe(x1, y1, x2, y2)
    print(f"👇 Swiped ({x1},{y1}) → ({x2},{y2})")


def cmd_back(config: dict, serial: str):
    """Send BACK key."""
    device = _make_device(config, serial)
    device.ensure_device()
    device.back()
    print("◀ Back")


def cmd_info(config: dict, serial: str):
    """Show device and app info."""
    device = _make_device(config, serial)
    device.ensure_device()
    act = device.current_activity()
    w, h = device.screen_size
    print(f"📱 Device: {device.serial}")
    print(f"   Screen: {w}x{h}")
    print(f"   Activity: {act or 'unknown'}")
    print(f"   App foreground: {device.is_app_foreground()}")


def cmd_check(monitor: CrashMonitor):
    """Check for new crashes."""
    events = monitor.recent_events()
    if not events:
        print("✅ No crashes detected")
        return
    print(f"⚠ {len(events)} crash event(s):")
    for ev in events[-5:]:
        print(f"   [{ev.crash_type}] {ev.log_line[:150]}")
    return events


def cmd_init(config: dict, serial: str, mission_path: str):
    """Initialize a new mission recording."""
    mission = _load_mission(mission_path)
    recorder = SessionRecorder(
        screenshot_dir=config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
    )
    recorder.start_mission(
        name=mission.get("name", mission_path),
        description=mission.get("description", ""),
    )
    # Also start monitor
    monitor = _make_monitor(config, serial)
    monitor.start()
    return recorder, monitor, mission


def cmd_record(recorder: SessionRecorder, device: DeviceController, reason: str):
    """Record a step: take screenshot + note action reason."""
    ss = device.take_screenshot(f"step_{recorder._step_counter + 1:03d}")
    screen = device.current_activity() or ""
    step = recorder.record_step(
        action={"type": "manual", "reason": reason},
        screenshot_path=str(ss),
        screen_info=screen,
    )
    print(f"📝 Step {step['step']} recorded: {reason}")
    print(f"   Screen: {screen}")
    print(f"   Screenshot: {ss}")


def cmd_note(recorder: SessionRecorder, text: str):
    """Save a note."""
    recorder.save_note(text)
    print(f"📌 Note saved: {text}")


def cmd_report(recorder: SessionRecorder, config: dict):
    """Generate HTML report."""
    report_dir = config.get("recording", {}).get("output_dir", "assets/reports")
    path = recorder.generate_report(report_dir)
    print(f"📄 Report: file://{path.resolve()}")


# --- main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DramaFlow Android Exploratory Test Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--serial", default="", help="Device serial number")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--list", action="store_true", help="List available missions")
    parser.add_argument("--analyze", action="store_true", help="Quick screen analysis")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Setup
    sub.add_parser("setup", help="Check device, launch app, start monitor")

    # Device control
    sub.add_parser("screenshot", help="Take a screenshot")
    p_tap = sub.add_parser("tap", help="Tap at coordinates")
    p_tap.add_argument("x", type=int)
    p_tap.add_argument("y", type=int)
    p_text = sub.add_parser("text", help="Type text")
    p_text.add_argument("text", type=str)
    p_swipe = sub.add_parser("swipe", help="Swipe gesture")
    p_swipe.add_argument("x1", type=int)
    p_swipe.add_argument("y1", type=int)
    p_swipe.add_argument("x2", type=int)
    p_swipe.add_argument("y2", type=int)
    sub.add_parser("back", help="Back key")
    sub.add_parser("info", help="Device/app info")
    sub.add_parser("check", help="Check logcat for crashes")

    # Recording
    p_init = sub.add_parser("init", help="Start a new mission recording")
    p_init.add_argument("mission", help="Path to mission YAML")
    p_record = sub.add_parser("record", help="Record current step")
    p_record.add_argument("reason", type=str, nargs="?", default="")
    p_note = sub.add_parser("note", help="Save a note")
    p_note.add_argument("text", type=str)
    sub.add_parser("report", help="Generate HTML report")

    args = parser.parse_args()

    config = _load_config(args.config)

    # Handle flags
    if args.list:
        _list_missions()
        return

    if args.analyze:
        cmd_screenshot(config, args.serial)
        print("💡 Use the Read tool to open the screenshot and analyze it.")
        return

    if not args.command:
        parser.print_help()
        print("\n💡 Tip: Use one of the commands above. See '--list' for available missions.")
        return

    # Route commands
    if args.command == "setup":
        cmd_setup(config, args.serial)

    elif args.command == "screenshot":
        cmd_screenshot(config, args.serial)

    elif args.command == "tap":
        cmd_tap(config, args.serial, args.x, args.y)

    elif args.command == "text":
        cmd_text(config, args.serial, args.text)

    elif args.command == "swipe":
        cmd_swipe(config, args.serial, args.x1, args.y1, args.x2, args.y2)

    elif args.command == "back":
        cmd_back(config, args.serial)

    elif args.command == "info":
        cmd_info(config, args.serial)

    elif args.command == "check":
        monitor = _make_monitor(config, args.serial)
        monitor.start()
        time.sleep(2)
        cmd_check(monitor)
        monitor.stop()

    elif args.command == "init":
        recorder, monitor, mission = cmd_init(config, args.serial, args.mission)

    elif args.command == "record":
        device = _make_device(config, args.serial)
        device.ensure_device()
        recorder = SessionRecorder(
            screenshot_dir=config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
        )
        # Try loading active session
        sess_path = Path(recorder.screenshot_dir) / "_session.json"
        if sess_path.exists():
            recorder.load_session(sess_path)
        cmd_record(recorder, device, args.reason or "manual step")

    elif args.command == "note":
        recorder = SessionRecorder(
            screenshot_dir=config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
        )
        sess_path = Path(recorder.screenshot_dir) / "_session.json"
        if sess_path.exists():
            recorder.load_session(sess_path)
        cmd_note(recorder, args.text)

    elif args.command == "report":
        recorder = SessionRecorder(
            screenshot_dir=config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
        )
        sess_path = Path(recorder.screenshot_dir) / "_session.json"
        if sess_path.exists():
            recorder.load_session(sess_path)
        cmd_report(recorder, config)

    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Web Test Agent CLI — persistent browser session via OpenCLI.

Agent reasons step-by-step, executing one command at a time:
  python -m web.agent start
  python -m web.agent screenshot
  python -m web.agent state
  python -m web.agent find --text "登录"
  python -m web.agent click 12
  python -m web.agent click-text "登录"
  python -m web.agent fill "#username" "admin"
  python -m web.agent type "some text"
  python -m web.agent scroll down
  python -m web.agent back
  python -m web.agent navigate http://localhost:5173/login
  python -m web.agent check
  python -m web.agent record "clicked login"
  python -m web.agent report
  python -m web.agent stop
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# Ensure test-agent/ is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from web.controller import opencli_client as cli
from web.controller import page as pg
from web.controller.element_finder import find_by_text, find_by_selector, find_inputs
from web.controller.error_monitor import ErrorMonitor
from shared.recorder import SessionRecorder
from shared.config import load_config

SESSION_FILE = Path(__file__).resolve().parent / ".session.json"
DEFAULT_SESSION = "dramaflow-web"


def _get_config():
    return load_config(str(Path(__file__).resolve().parent / "config.yaml"))


def _get_session() -> dict:
    if not SESSION_FILE.exists():
        print("No active session. Run 'start' first.")
        sys.exit(1)
    return json.loads(SESSION_FILE.read_text())


def _save_session(data: dict):
    SESSION_FILE.write_text(json.dumps(data, indent=2))


def _session_name() -> str:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text()).get("session", DEFAULT_SESSION)
    return DEFAULT_SESSION


# ---- commands ----

def cmd_start(config: dict):
    if SESSION_FILE.exists():
        print("Session already active. Run 'stop' first.")
        return

    session = DEFAULT_SESSION
    base_url = config.get("base_url", "http://localhost:5173")
    start_path = config.get("start_path", "/")
    url = f"{base_url}{start_path}"

    # Open the URL in OpenCLI (requires Chrome with the OpenCLI extension running)
    try:
        cli.open_url(session, url, post_delay=1.0)
    except cli.OpenCLIError as e:
        print(f"Failed to open browser session: {e}")
        print("Make sure Chrome is running with the OpenCLI extension installed.")
        sys.exit(1)

    # Init recorder
    ss_dir = config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
    recorder = SessionRecorder(ss_dir)
    recorder.start_mission("Web Test", "")

    _save_session({
        "session": session,
        "base_url": base_url,
        "start_path": start_path,
    })

    print(f"Session '{session}' started")
    print(f"Page: {url}")


def cmd_stop():
    session_data = _get_session()
    session = session_data.get("session", DEFAULT_SESSION)
    cli.close_session(session)
    SESSION_FILE.unlink(missing_ok=True)
    print(f"Session '{session}' stopped.")


def cmd_screenshot(config: dict):
    session = _session_name()
    ss_dir = config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
    path = pg.screenshot(session, f"{ss_dir}/current.png")
    print(str(path))


def cmd_state():
    session = _session_name()
    print(pg.get_state(session))


def cmd_url():
    session = _session_name()
    print(pg.get_current_url(session))


def cmd_title():
    session = _session_name()
    print(pg.get_title(session))


def cmd_click(target: str, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    result = pg.click(session, target, post_delay=delay)
    print(json.dumps(result, ensure_ascii=False))
    print(f"URL: {pg.get_current_url(session)}")


def cmd_click_text(text: str, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    result = pg.click_by_text(session, text, post_delay=delay)
    print(json.dumps(result, ensure_ascii=False))
    print(f"URL: {pg.get_current_url(session)}")


def cmd_type_text(text: str, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    pg.type_text(session, text, post_delay=delay)
    print(f"Typed: {text}")


def cmd_fill(target: str, text: str, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    pg.fill_input(session, target, text, post_delay=delay)
    print(f"Filled {target!r} = {text!r}")


def cmd_navigate(url: str, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    pg.navigate(session, url, post_delay=delay)
    print(f"URL: {pg.get_current_url(session)}")


def cmd_scroll(direction: str, amount: int, config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    pg.scroll(session, direction, amount=amount, post_delay=delay)
    print(f"Scrolled {direction} {amount}px")


def cmd_back(config: dict):
    session = _session_name()
    delay = config.get("post_action_delay", 0.5)
    pg.go_back(session, post_delay=delay)
    print(f"URL: {pg.get_current_url(session)}")


def cmd_find(query: str):
    session = _session_name()
    results = find_by_text(session, query)
    if not results:
        print("No matches")
    else:
        for i, el in enumerate(results):
            ref = el.get("ref", "?")
            print(f"[{i}] ref={ref} {el['tag']} \"{el['text'][:60]}\"")


def cmd_find_inputs():
    session = _session_name()
    results = find_inputs(session)
    if not results:
        print("No inputs")
    else:
        for i, inp in enumerate(results):
            ref = inp.get("ref", "?")
            print(f"[{i}] ref={ref} [{inp.get('type','text')}] "
                  f"placeholder=\"{inp.get('placeholder','')}\" "
                  f"selector=\"{inp.get('selector','')}\"")


def cmd_check(config: dict):
    """Check for console errors and failed network requests."""
    session = _session_name()
    monitor = ErrorMonitor(session)
    monitor.check(since="10m")
    if not monitor.has_errors:
        print("No errors detected")
    else:
        print(f"{monitor.error_count} error(s):")
        for ev in monitor.recent_events(20):
            print(f"  [{ev.error_type}] {ev.message[:150]}")


def cmd_record(reason: str, config: dict):
    session = _session_name()
    ss_dir = config.get("recording", {}).get("screenshot_dir", "assets/screenshots")

    recorder = SessionRecorder(ss_dir)
    sess_path = Path(ss_dir) / "_session.json"
    if sess_path.exists():
        recorder.load_session(sess_path)

    ss = pg.screenshot(session, f"{ss_dir}/step_{recorder._step_counter + 1:03d}.png")
    step = recorder.record_step(
        action={"type": "action", "reason": reason},
        screenshot_path=str(ss),
        screen_info=pg.get_current_url(session),
    )
    print(f"Step {step['step']} recorded: {reason}")
    print(f"URL: {pg.get_current_url(session)}")


def cmd_report(config: dict):
    ss_dir = config.get("recording", {}).get("screenshot_dir", "assets/screenshots")
    out_dir = config.get("recording", {}).get("output_dir", "assets/reports")

    recorder = SessionRecorder(ss_dir)
    sess_path = Path(ss_dir) / "_session.json"
    if sess_path.exists():
        recorder.load_session(sess_path)
    else:
        print("No session data to report")
        return

    path = recorder.generate_report(out_dir)
    print(str(path))


def cmd_wait_text(text: str):
    session = _session_name()
    ok = pg.wait_for_text(session, text, timeout=8.0)
    print(f"Text check: {'OK' if ok else 'TIMEOUT'}")
    print(f"URL: {pg.get_current_url(session)}")


def cmd_dom():
    session = _session_name()
    html = pg.get_dom(session)
    if html:
        print(html[:5000])
    else:
        print("Failed to get DOM")


# ---- main ----

def main():
    parser = argparse.ArgumentParser(description="Web Test Agent CLI (OpenCLI)")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start", help="Open browser session via OpenCLI")
    sub.add_parser("stop", help="Close browser session")
    sub.add_parser("screenshot", help="Take screenshot → current.png")
    sub.add_parser("state", help="Print page state with interactive element refs")
    sub.add_parser("url", help="Print current URL")
    sub.add_parser("title", help="Print page title")

    p_click = sub.add_parser("click", help="Click element by ref number or CSS selector")
    p_click.add_argument("target", type=str, help="Numeric ref (from state) or CSS selector")

    p_click_text = sub.add_parser("click-text", help="Click element by visible text")
    p_click_text.add_argument("text", type=str)

    p_type = sub.add_parser("type", help="Type text into focused element")
    p_type.add_argument("text", type=str)

    p_fill = sub.add_parser("fill", help="Fill input by ref or CSS selector")
    p_fill.add_argument("target", type=str)
    p_fill.add_argument("text", type=str)

    p_nav = sub.add_parser("navigate", help="Navigate to URL")
    p_nav.add_argument("url", type=str)

    p_scroll = sub.add_parser("scroll", help="Scroll page up or down")
    p_scroll.add_argument("direction", choices=["up", "down"])
    p_scroll.add_argument("--amount", type=int, default=500, help="Pixels to scroll")

    sub.add_parser("back", help="Browser back")

    p_find = sub.add_parser("find", help="Find elements by text")
    p_find.add_argument("query", type=str)

    sub.add_parser("find-inputs", help="Find all input fields")

    sub.add_parser("check", help="Check for console errors and network failures")

    p_record = sub.add_parser("record", help="Record current step with screenshot")
    p_record.add_argument("reason", type=str)

    sub.add_parser("report", help="Generate HTML report")

    p_wait = sub.add_parser("wait-text", help="Wait for text to appear on page")
    p_wait.add_argument("text", type=str)

    sub.add_parser("dom", help="Print page DOM (first 5000 chars)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = _get_config()

    if args.command == "start":
        cmd_start(config)
    elif args.command == "stop":
        cmd_stop()
    elif args.command == "screenshot":
        cmd_screenshot(config)
    elif args.command == "state":
        cmd_state()
    elif args.command == "url":
        cmd_url()
    elif args.command == "title":
        cmd_title()
    elif args.command == "click":
        cmd_click(args.target, config)
    elif args.command == "click-text":
        cmd_click_text(args.text, config)
    elif args.command == "type":
        cmd_type_text(args.text, config)
    elif args.command == "fill":
        cmd_fill(args.target, args.text, config)
    elif args.command == "navigate":
        cmd_navigate(args.url, config)
    elif args.command == "scroll":
        cmd_scroll(args.direction, args.amount, config)
    elif args.command == "back":
        cmd_back(config)
    elif args.command == "find":
        cmd_find(args.query)
    elif args.command == "find-inputs":
        cmd_find_inputs()
    elif args.command == "check":
        cmd_check(config)
    elif args.command == "record":
        cmd_record(args.reason, config)
    elif args.command == "report":
        cmd_report(config)
    elif args.command == "wait-text":
        cmd_wait_text(args.text)
    elif args.command == "dom":
        cmd_dom()
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

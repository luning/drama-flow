"""
ADB command wrapper — pure subprocess-based, no device-side agents required.

All methods raise AdbError on non-zero exit; the caller handles retry/abort.
"""

import subprocess
import os
import re
import time
from pathlib import Path
from typing import Optional, Union


class AdbError(Exception):
    """Raised when an ADB command exits with non-zero status."""


def _adb(serial: str, args: list[str], timeout: int = 30) -> str:
    """Run `adb [-s serial] <args>` and return stdout as text."""
    cmd = _build_cmd(serial, args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        raise AdbError("adb not found — check ANDROID_HOME/platform-tools in PATH")
    except subprocess.TimeoutExpired:
        raise AdbError(f"adb command timed out after {timeout}s: {' '.join(cmd)}")
    if r.returncode != 0:
        err = r.stderr.strip() or r.stdout.strip() or f"exit code {r.returncode}"
        raise AdbError(f"adb {' '.join(args[:3])}… failed: {err}")
    return r.stdout


def _adb_binary(serial: str, args: list[str], timeout: int = 30) -> bytes:
    """Run `adb [-s serial] <args>` and return raw stdout bytes."""
    cmd = _build_cmd(serial, args)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise AdbError("adb not found — check ANDROID_HOME/platform-tools in PATH")
    except subprocess.TimeoutExpired:
        raise AdbError(f"adb command timed out after {timeout}s: {' '.join(cmd)}")
    if r.returncode != 0:
        err = r.stderr.strip().decode(errors="replace") or f"exit code {r.returncode}"
        raise AdbError(f"adb {' '.join(args[:3])}… failed: {err}")
    return r.stdout


def _build_cmd(serial: str, args: list[str]) -> list[str]:
    android_home = os.environ.get("ANDROID_HOME", os.path.expanduser("~/Library/Android/sdk"))
    adb_path = os.path.join(android_home, "platform-tools", "adb")
    if not os.path.isfile(adb_path):
        # fallback to PATH
        adb_path = "adb"
    cmd = [adb_path]
    if serial:
        cmd += ["-s", serial]
    return cmd + args


# --- public API ----------------------------------------------------------------


def devices(serial: str = "") -> list[dict]:
    """List connected devices."""
    raw = _adb(serial, ["devices"])
    result = []
    for line in raw.splitlines():
        m = re.match(r"(\S+)\s+(device|offline|unauthorized)", line)
        if m:
            result.append({"serial": m.group(1), "state": m.group(2)})
    return result


def shell(serial: str, command: str, timeout: int = 15) -> str:
    """Run a shell command on the device."""
    return _adb(serial, ["shell", command], timeout=timeout)


def tap(serial: str, x: int, y: int):
    """Tap at screen coordinates."""
    shell(serial, f"input tap {x} {y}")


def text(serial: str, text_to_type: str):
    """Type text (escapes special chars for ADB)."""
    # Escape: % for %, space for %s, etc.
    escaped = text_to_type.replace(" ", "%s").replace("'", "")
    escaped = escaped.replace("(", "").replace(")", "")
    escaped = escaped.replace("&", "").replace("|", "").replace("<", "").replace(">", "")
    shell(serial, f"input text '{escaped}'")


def swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
    """Swipe from (x1,y1) to (x2,y2)."""
    shell(serial, f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")


def keyevent(serial: str, keycode: int):
    """Send a key event (e.g. KEYCODE_BACK=4, KEYCODE_HOME=3)."""
    shell(serial, f"input keyevent {keycode}")


def back(serial: str):
    """Send BACK key."""
    keyevent(serial, 4)


def home(serial: str):
    """Send HOME key."""
    keyevent(serial, 3)


def enter(serial: str):
    """Send ENTER key."""
    keyevent(serial, 66)


def screenshot(serial: str, output_path: Union[str, Path]) -> Path:
    """Capture screen to PNG file. Returns output_path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Push the screenshot via exec-out to avoid leaving temp files on device
    raw = _adb_binary(serial, ["exec-out", "screencap", "-p"], timeout=15)
    out.write_bytes(raw)
    return out


def dump_ui(serial: str, output_path: Union[str, Path]) -> Optional[str]:
    """Dump UI hierarchy XML via uiautomator. Returns file path or None on failure."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        shell(serial, "uiautomator dump /sdcard/ui.xml 2>/dev/null", timeout=10)
        _adb(serial, ["pull", "/sdcard/ui.xml", str(out.resolve())], timeout=10)
        _adb(serial, ["shell", "rm", "/sdcard/ui.xml"], timeout=5)
        if out.exists() and out.stat().st_size > 0:
            return out.read_text(encoding="utf-8", errors="replace")
    except AdbError:
        pass
    return None


def start_app(serial: str, package: str, activity: str):
    """Launch an app activity."""
    shell(serial, f"am start -n {package}/{activity}", timeout=10)


def stop_app(serial: str, package: str):
    """Force-stop an app."""
    shell(serial, f"am force-stop {package}", timeout=10)


def current_activity(serial: str) -> Optional[str]:
    """Return the current foreground activity or None."""
    try:
        raw = shell(serial, "dumpsys window 2>/dev/null | grep mCurrentFocus", timeout=5)
        m = re.search(r"mCurrentFocus=.*?\s\S+\s(\S+?)}", raw)
        return m.group(1) if m else None
    except AdbError:
        return None


def is_app_running(serial: str, package: str) -> bool:
    """Check if the given package has any running processes."""
    try:
        raw = shell(serial, f"pidof {package}", timeout=5)
        return bool(raw.strip())
    except AdbError:
        return False


def clear_logcat(serial: str):
    """Clear the logcat buffer."""
    _adb(serial, ["logcat", "-c"], timeout=5)


def logcat(serial: str, filter_spec: str = "*:E", lines: int = 200) -> str:
    """Dump recent logcat output."""
    try:
        return _adb(serial, ["logcat", "-d", f"-t{lines}", "-v", "time", filter_spec], timeout=15)
    except AdbError:
        return ""


def get_screen_size(serial: str) -> tuple[int, int]:
    """Return (width, height) of the device display."""
    raw = shell(serial, "wm size", timeout=5)
    m = re.search(r"(\d+)x(\d+)", raw)
    if m:
        return int(m.group(1)), int(m.group(2))
    return (1080, 1920)  # safe default


def is_boot_complete(serial: str) -> bool:
    """Check whether the device has finished booting."""
    raw = shell(serial, "getprop sys.boot_completed", timeout=5)
    return raw.strip() == "1"


def wait_for_device(serial: str, timeout_sec: int = 60) -> bool:
    """Block until the device is online and boot is complete."""
    try:
        _adb(serial, ["wait-for-device"], timeout=timeout_sec)
    except AdbError:
        return False
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if is_boot_complete(serial):
            return True
        time.sleep(2)
    return False

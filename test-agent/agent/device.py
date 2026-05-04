"""
Device management — wraps adb_client with state tracking and convenience methods.
"""

import time
from pathlib import Path
from typing import Optional, Union

from . import adb_client as adb


class DeviceError(Exception):
    """Device is unreachable or in an unusable state."""


class DeviceController:
    """High-level controller for an Android device/emulator."""

    def __init__(
        self,
        serial: str = "",
        app_package: str = "com.dramaflow",
        app_activity: str = ".MainActivity",
        post_action_delay: float = 1.5,
        launch_delay: float = 3.0,
        screenshot_dir: Union[str, Path] = "assets/screenshots",
    ):
        self.serial = serial
        self.app_package = app_package
        self.app_activity = app_activity
        self.post_action_delay = post_action_delay
        self.launch_delay = launch_delay
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self._screen_size: Optional[tuple[int, int]] = None

    # --- connectivity ---------------------------------------------------------

    def ensure_device(self, timeout_sec: int = 60) -> None:
        """Wait until at least one device is visible and booted."""
        if self.serial:
            if not adb.wait_for_device(self.serial, timeout_sec):
                raise DeviceError(f"Device {self.serial} did not become ready")
        else:
            deadline = time.time() + timeout_sec
            while time.time() < deadline:
                devs = adb.devices()
                online = [d for d in devs if d["state"] == "device"]
                if online:
                    self.serial = online[0]["serial"]
                    if adb.is_boot_complete(self.serial):
                        return
                time.sleep(2)
            raise DeviceError("No booted device found")

    def is_online(self) -> bool:
        """Quick check if the device is still reachable."""
        try:
            devs = adb.devices(self.serial)
            return any(d["serial"] == self.serial and d["state"] == "device" for d in devs)
        except adb.AdbError:
            return False

    # --- app lifecycle --------------------------------------------------------

    def launch_app(self) -> None:
        """Start the target app and wait for it to render."""
        adb.stop_app(self.serial, self.app_package)
        time.sleep(0.5)
        adb.start_app(self.serial, self.app_package, self.app_activity)
        time.sleep(self.launch_delay)

    def stop_app(self) -> None:
        """Force-stop the target app."""
        adb.stop_app(self.serial, self.app_package)

    def restart_app(self) -> None:
        """Kill and re-launch the app."""
        self.stop_app()
        time.sleep(0.5)
        self.launch_app()

    def current_activity(self) -> Optional[str]:
        """Return the current foreground activity, if it exists."""
        return adb.current_activity(self.serial)

    def is_app_foreground(self) -> bool:
        """Return True if the target package is in the foreground."""
        act = self.current_activity()
        return act is not None and self.app_package in act

    # --- screen interaction --------------------------------------------------

    def tap(self, x: int, y: int, delay: Optional[float] = None) -> None:
        """Tap at (x, y) and wait for UI to settle."""
        adb.tap(self.serial, x, y)
        time.sleep(delay or self.post_action_delay)

    def text(self, text_to_type: str, delay: Optional[float] = None) -> None:
        """Type text and wait."""
        adb.text(self.serial, text_to_type)
        time.sleep(delay or self.post_action_delay)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, delay: Optional[float] = None) -> None:
        """Swipe and wait."""
        adb.swipe(self.serial, x1, y1, x2, y2, duration_ms)
        time.sleep(delay or self.post_action_delay)

    def back(self, delay: Optional[float] = None) -> None:
        """Send BACK key and wait."""
        adb.back(self.serial)
        time.sleep(delay or self.post_action_delay)

    def home(self, delay: Optional[float] = None) -> None:
        """Send HOME key and wait."""
        adb.home(self.serial)
        time.sleep(delay or self.post_action_delay)

    def enter(self, delay: Optional[float] = None) -> None:
        """Send ENTER key and wait."""
        adb.enter(self.serial)
        time.sleep(delay or self.post_action_delay)

    # --- screenshot & UI dump -------------------------------------------------

    def take_screenshot(self, name: str = "step") -> Path:
        """Capture a screenshot to a timestamped file. Returns the file path."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = self.screenshot_dir / f"{name}_{ts}.png"
        return adb.screenshot(self.serial, path)

    def dump_ui(self) -> Optional[str]:
        """Return the current UI hierarchy XML, or None."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = self.screenshot_dir / f"ui_{ts}.xml"
        return adb.dump_ui(self.serial, path)

    @property
    def screen_size(self) -> tuple[int, int]:
        if self._screen_size is None:
            self._screen_size = adb.get_screen_size(self.serial)
        return self._screen_size

    # --- convenience for coordinate targeting ---------------------------------

    def center_top(self, fraction_y: float = 0.1) -> tuple[int, int]:
        """Return (center_x, fraction_y * height) for tapping top-of-screen items."""
        w, h = self.screen_size
        return (w // 2, int(h * fraction_y))

    def center_bottom(self, fraction_y: float = 0.9) -> tuple[int, int]:
        """Return (center_x, fraction_y * height) for tapping bottom-of-screen items."""
        w, h = self.screen_size
        return (w // 2, int(h * fraction_y))

    def center(self) -> tuple[int, int]:
        """Return the center of the screen."""
        w, h = self.screen_size
        return (w // 2, h // 2)

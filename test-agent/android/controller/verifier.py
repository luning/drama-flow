"""
Action verifier — checks whether device actions produced expected results.

Generic: no app-specific knowledge, only monitors activity and screen state.
"""

import time
from typing import Optional, Tuple

from android.controller.element_finder import ElementFinder


class ActionVerifier:
    """Verifies that actions on a device produce expected changes."""

    def __init__(self, device):
        self.device = device

    # --- activity verification -------------------------------------------------

    def verify_activity_changed(
        self, before_activity: Optional[str] = None, timeout: float = 3.0
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Wait for the foreground activity to change from *before_activity*.

        Returns (changed, before, after).
        If *before_activity* is None, captures current activity as baseline.
        """
        if before_activity is None:
            before_activity = self.device.current_activity()

        deadline = time.time() + timeout
        while time.time() < deadline:
            after = self.device.current_activity()
            if after and after != before_activity:
                return True, before_activity, after
            time.sleep(0.3)

        # One last check
        after = self.device.current_activity()
        changed = after is not None and after != before_activity
        return changed, before_activity, after

    def wait_for_activity(
        self, expected_activity: str, timeout: float = 5.0
    ) -> Tuple[bool, float]:
        """Wait until *expected_activity* appears in the foreground.

        Returns (found, elapsed_seconds).
        """
        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            current = self.device.current_activity() or ""
            if expected_activity in current:
                return True, time.time() - start
            time.sleep(0.3)
        return False, time.time() - start

    # --- screen-content verification -------------------------------------------

    def wait_for_element(
        self, text_contains: str, timeout: float = 5.0
    ) -> Tuple[bool, float]:
        """Wait until an element with matching text appears on screen.

        Polls uiautomator dump. Returns (found, elapsed_seconds).
        """
        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            ui_xml = self.device.dump_ui()
            if ui_xml:
                finder = ElementFinder(ui_xml)
                if finder.find_by_text(text_contains):
                    return True, time.time() - start
            time.sleep(0.5)
        return False, time.time() - start

    def wait_for_idle(
        self, stable_period: float = 1.0, timeout: float = 5.0
    ) -> bool:
        """Wait until the activity stays constant for *stable_period*.

        Useful after a navigation action that passes through intermediate screens.
        """
        deadline = time.time() + timeout
        last_activity = self.device.current_activity()
        stable_since = time.time()

        while time.time() < deadline:
            current = self.device.current_activity()
            if current == last_activity:
                if time.time() - stable_since >= stable_period:
                    return True
            else:
                last_activity = current
                stable_since = time.time()
            time.sleep(0.3)

        return False

    # --- convenience wrapper ---------------------------------------------------

    def verify_tap(
        self,
        x: int,
        y: int,
        expect_activity: Optional[str] = None,
        timeout: float = 3.0,
    ) -> dict:
        """Tap at (x, y) and verify the screen changed.

        Returns a result dict with status, before/after activity, timing.
        """
        before = self.device.current_activity()
        self.device.tap(x, y)

        if expect_activity:
            found, elapsed = self.wait_for_activity(expect_activity, timeout)
            return {
                "success": found,
                "before": before,
                "after": expect_activity if found else before,
                "elapsed": round(elapsed, 1),
                "message": (
                    f"✓ Reached {expect_activity} after {elapsed:.1f}s"
                    if found
                    else f"✗ Timed out waiting for {expect_activity} ({timeout}s)"
                ),
            }
        else:
            changed, before_act, after_act = self.verify_activity_changed(before, timeout)
            return {
                "success": changed,
                "before": before_act,
                "after": after_act,
                "elapsed": round(timeout, 1),
                "message": (
                    f"✓ Screen changed: {before_act} → {after_act}"
                    if changed
                    else f"✗ Screen unchanged (still {before_act})"
                ),
            }

"""
Background logcat crash/anomaly monitor.

Runs a daemon thread that tails logcat and captures crash signatures.
"""

import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional

from android.controller import adb_client as adb


# Patterns that indicate a crash or serious error
CRASH_PATTERNS: list[tuple[str, str]] = [
    ("java_crash", r"FATAL EXCEPTION"),
    ("anr", r"ANR in"),
    ("android_runtime", r"E/AndroidRuntime:?.*FATAL"),
    ("uncaught", r"UncaughtException"),
    ("native_crash", r"E/DEBUG:.*signal"),
    ("oom", r"OutOfMemoryError"),
    ("stacktrace", r"^\s+at\s+[\w.]+\([\w.]+\.java:\d+\)"),
    ("null_pointer", r"NullPointerException"),
    ("illegal_state", r"IllegalStateException"),
    ("illegal_arg", r"IllegalArgumentException"),
    ("runtime_exception", r"RuntimeException"),
]

# App-specific log tags for DramaFlow
APP_TAGS = ["DramaFlow", "JSBridge", "PlayerViewModel", "AuthViewModel", "HomeViewModel"]


@dataclass
class CrashEvent:
    """A single detected crash or anomaly."""
    timestamp: float
    crash_type: str          # from CRASH_PATTERNS key
    log_line: str            # the matching log line
    context_lines: list[str] = field(default_factory=list)


class CrashMonitor:
    """Monitors logcat in a background thread for crash/anomaly signatures."""

    def __init__(
        self,
        serial: str,
        buffer_size: int = 1000,
        poll_interval: float = 0.5,
        on_crash: Optional[Callable[[CrashEvent], None]] = None,
        app_package: str = "com.dramaflow",
    ):
        self.serial = serial
        self.buffer_size = buffer_size
        self.poll_interval = poll_interval
        self.on_crash = on_crash
        self.app_package = app_package

        self.events: list[CrashEvent] = []
        self._buffer: deque[str] = deque(maxlen=buffer_size)
        self._last_position = 0
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # --- lifecycle -----------------------------------------------------------

    def start(self) -> None:
        """Start the background monitor thread."""
        if self._thread and self._thread.is_alive():
            return
        adb.clear_logcat(self.serial)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="crash-monitor")
        self._thread.start()

    def stop(self) -> None:
        """Signal the monitor to stop and wait for it."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # --- accessors -----------------------------------------------------------

    @property
    def has_crashes(self) -> bool:
        return len(self.events) > 0

    @property
    def crash_count(self) -> int:
        return len(self.events)

    def recent_events(self, n: int = 10) -> list[CrashEvent]:
        """Return the most recent N crash events."""
        return self.events[-n:]

    # --- internal ------------------------------------------------------------

    def _run(self) -> None:
        """Monitor loop — runs in daemon thread."""
        while not self._stop_event.is_set():
            try:
                self._poll()
            except Exception:
                pass  # keep running despite transient errors
            time.sleep(self.poll_interval)

    def _poll(self) -> None:
        """Fetch new logcat lines and scan for crash signatures."""
        raw = adb.logcat(self.serial, filter_spec="*:E", lines=500)
        if not raw:
            return

        lines = raw.splitlines()
        if len(lines) <= self._last_position:
            self._last_position = 0

        new_lines = lines[self._last_position:]
        self._last_position = len(lines)

        for log_line in new_lines:
            # Filter to relevant lines (app package or crash patterns)
            if self.app_package not in log_line and not any(
                re.search(pat, log_line) for _, pat in CRASH_PATTERNS
            ):
                continue

            self._buffer.append(log_line)

            # Check against known crash patterns
            for crash_type, pattern in CRASH_PATTERNS:
                if re.search(pattern, log_line, re.IGNORECASE):
                    event = CrashEvent(
                        timestamp=time.time(),
                        crash_type=crash_type,
                        log_line=log_line,
                        context_lines=list(self._buffer)[-10:],
                    )
                    self.events.append(event)
                    if self.on_crash:
                        try:
                            self.on_crash(event)
                        except Exception:
                            pass
                    break

    # --- summary -------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary of all detected anomalies."""
        by_type: dict[str, int] = {}
        for e in self.events:
            by_type[e.crash_type] = by_type.get(e.crash_type, 0) + 1
        return {
            "total_events": len(self.events),
            "by_type": by_type,
            "events": [
                {
                    "timestamp": e.timestamp,
                    "type": e.crash_type,
                    "log": e.log_line[:200],
                }
                for e in self.events
            ],
        }

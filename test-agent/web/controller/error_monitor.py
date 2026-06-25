"""Browser error monitor — reads console errors and failed network requests via opencli."""

import time
from dataclasses import dataclass, field
from typing import Optional

from web.controller import opencli_client as cli


@dataclass
class WebError:
    """A single detected error event."""
    timestamp: float
    error_type: str           # "console_error" | "network_error"
    message: str
    url: str = ""
    status_code: int = 0


class ErrorMonitor:
    """Polls opencli console/network commands for errors since last check."""

    def __init__(self, session: str):
        self.session = session
        self.events: list[WebError] = []
        self._start_time: float = 0.0

    def start(self):
        """Record start time; errors are queried relative to this."""
        self._start_time = time.time()

    def stop(self):
        pass

    def check(self, since: str = "5m"):
        """Query opencli for recent errors and append new ones to events."""
        self._collect_console_errors(since)
        self._collect_network_errors(since)

    def _collect_console_errors(self, since: str):
        try:
            raw = cli.get_console_errors(self.session, since=since)
            for line in raw.splitlines():
                line = line.strip()
                if line:
                    self.events.append(WebError(
                        timestamp=time.time(),
                        error_type="console_error",
                        message=line[:300],
                    ))
        except cli.OpenCLIError:
            pass

    def _collect_network_errors(self, since: str):
        try:
            raw = cli.get_network_errors(self.session, since=since)
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                status = 0
                url = ""
                # opencli network output lines look like: "GET 404 https://..."
                parts = line.split()
                if len(parts) >= 3 and parts[1].isdigit():
                    status = int(parts[1])
                    url = parts[2]
                self.events.append(WebError(
                    timestamp=time.time(),
                    error_type="network_error",
                    message=line[:300],
                    url=url,
                    status_code=status,
                ))
        except cli.OpenCLIError:
            pass

    @property
    def has_errors(self) -> bool:
        return len(self.events) > 0

    @property
    def error_count(self) -> int:
        return len(self.events)

    def recent_events(self, n: int = 10) -> list[WebError]:
        return self.events[-n:]

    def summary(self) -> dict:
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

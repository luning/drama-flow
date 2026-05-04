"""
Test session recorder — records steps, screenshots, actions, and crash events
into a JSON session file, then hands off to reporter.py for HTML generation.
"""

import json
import time
from pathlib import Path
from typing import Optional, Union


class SessionRecorder:
    """Records a test session step by step."""

    def __init__(self, screenshot_dir: Union[str, Path] = "assets/screenshots"):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.session = {
            "mission": "",
            "started_at": time.time(),
            "steps": [],
            "crashes": [],
        }
        self._crashes_collected: list[dict] = []
        self._step_counter = 0

    # --- session lifecycle ---------------------------------------------------

    def start_mission(self, name: str, description: str = "") -> None:
        """Begin a new mission recording."""
        self.session["mission"] = name
        self.session["description"] = description
        self.session["started_at"] = time.time()
        self._step_counter = 0
        print(f"📋 Mission started: {name}")

    def add_crash(self, crash_event: dict) -> None:
        """Record a crash/anomaly event."""
        self._crashes_collected.append(crash_event)
        self.session["crashes"] = self._crashes_collected

    # --- step recording ------------------------------------------------------

    def record_step(
        self,
        action: dict,
        screenshot_path: Optional[str] = None,
        screen_info: str = "",
        success: bool = True,
        error: Optional[str] = None,
    ) -> dict:
        """Record one test step. Returns the step record dict."""
        self._step_counter += 1
        step = {
            "step": self._step_counter,
            "timestamp": time.time(),
            "action": action,
            "screenshot": str(screenshot_path) if screenshot_path else "",
            "screen": screen_info,
            "success": success,
            "error": error,
            "crashes": list(self._crashes_collected),  # snapshot at this step
        }
        self.session["steps"].append(step)
        self._crashes_collected = []  # reset after attaching to step
        self.session["updated_at"] = time.time()
        self._save()
        return step

    def save_note(self, text: str) -> None:
        """Save a free-text note for the current context."""
        note = {
            "type": "note",
            "timestamp": time.time(),
            "text": text,
        }
        self.session.setdefault("notes", []).append(note)
        self._save()

    # --- reporting -----------------------------------------------------------

    def build_result(self) -> dict:
        """Build the final result dict for the reporter."""
        duration = time.time() - self.session["started_at"]

        # collect unique screens
        screens = set()
        for s in self.session["steps"]:
            if s.get("screen"):
                screens.add(s["screen"])

        # collect all crashes
        all_crashes = []
        for s in self.session["steps"]:
            for c in s.get("crashes", []):
                if c not in all_crashes:
                    all_crashes.append(c)

        by_type: dict[str, int] = {}
        for c in all_crashes:
            t = c.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1

        return {
            "mission": self.session.get("mission", "Unnamed"),
            "status": "completed",
            "duration_seconds": round(duration, 1),
            "steps": len(self.session["steps"]),
            "screens_visited": sorted(screens),
            "crashes": {
                "total_events": len(all_crashes),
                "by_type": by_type,
                "events": [{"type": c.get("type", "?"), "log": c.get("log", "")[:200]} for c in all_crashes],
            },
            "history": self.session["steps"],
        }

    def generate_report(self, output_dir: Union[str, Path] = "assets/reports") -> Path:
        """Generate the final HTML report and return the file path."""
        from .reporter import generate_report as _gen_report
        result = self.build_result()
        return _gen_report(result, output_dir)

    # --- persistence ----------------------------------------------------------

    def _save(self) -> None:
        """Persist session to JSON for crash recovery."""
        path = self.screenshot_dir / "_session.json"
        try:
            with open(path, "w") as f:
                json.dump(self.session, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # best-effort

    def load_session(self, path: Union[str, Path]) -> None:
        """Load a previously saved session."""
        with open(path) as f:
            self.session = json.load(f)
        self._step_counter = len(self.session.get("steps", []))
        self._crashes_collected = list(self.session.get("crashes", []))

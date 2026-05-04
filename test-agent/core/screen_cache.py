"""
Screen signature + recipe cache — remembers successful action sequences per screen.

Reuses past success to skip LLM reasoning on repeat visits.
"""

import hashlib
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ScreenCache:
    """Persistent cache of successful action sequences keyed by screen signature.

    The cache file is JSON, stored at *cache_path* (default test-agent/assets/screen_cache.json).
    """

    def __init__(self, cache_path: str = "test-agent/assets/screen_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache: Dict[str, dict] = self._load()

    # --- persistence ------------------------------------------------------------

    def _load(self) -> dict:
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return {}
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        return {}

    def _save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.cache, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    # --- signature computation --------------------------------------------------

    @staticmethod
    def compute_signature(ui_xml_or_activity: str) -> str:
        """Create a stable hash from the UI tree.

        Uses all visible text and resource-ids (sorted), ignoring coordinates,
        timestamps, and dynamic content. Falls back to the raw string if
        the input is not XML (e.g. just an activity name).
        """
        if not ui_xml_or_activity:
            return ""

        if "<" not in ui_xml_or_activity:
            # Plain activity name — use as-is
            return f"act:{ui_xml_or_activity}"

        texts: List[str] = []
        rids: List[str] = []
        classes: List[str] = []

        try:
            root = ET.fromstring(ui_xml_or_activity)
            for node in root.iter("node"):
                t = (node.get("text") or "").strip()
                if t:
                    texts.append(t)
                rid = (node.get("resource-id") or "").strip()
                if rid:
                    rids.append(rid)
                cls = (node.get("class") or "").strip()
                if cls:
                    classes.append(cls.rsplit(".", 1)[-1])
        except ET.ParseError:
            return f"raw:{ui_xml_or_activity[:100]}"

        raw = "|".join([
            ",".join(sorted(texts)),
            ",".join(sorted(rids)),
            ",".join(sorted(classes)),
        ])
        return hashlib.md5(raw.encode()).hexdigest()

    # --- lookup / save ----------------------------------------------------------

    def lookup(self, signature: str) -> Optional[dict]:
        """Find a cached recipe by screen signature. Returns None if not found."""
        return self.cache.get(signature)

    def lookup_by_activity(self, activity_name: str) -> List[dict]:
        """Find all recipes that match the given activity name."""
        return [
            r for r in self.cache.values()
            if r.get("activity", "") == activity_name
        ]

    def lookup_by_text(self, text_substring: str) -> List[dict]:
        """Find all recipes whose steps reference the given text."""
        results = []
        for r in self.cache.values():
            for step in r.get("steps", []):
                if text_substring in step.get("target_text", ""):
                    results.append(r)
                    break
        return results

    def save_recipe(
        self,
        signature: str,
        screen_name: str,
        activity: str,
        steps: list,
        merge: bool = True,
    ) -> dict:
        """Save or update a recipe.

        If *merge* is True and a recipe already exists for this signature,
        the new steps replace the old ones and the success counter increments.
        """
        existing = self.cache.get(signature)
        if existing and merge:
            existing["success_count"] = existing.get("success_count", 0) + 1
            existing["last_success"] = time.time()
            existing["steps"] = steps
            existing["activity"] = activity
            existing["screen_name"] = screen_name
            recipe = existing
        else:
            recipe = {
                "signature": signature,
                "screen_name": screen_name,
                "activity": activity,
                "success_count": 1,
                "first_seen": time.time(),
                "last_success": time.time(),
                "steps": steps,
            }
        self.cache[signature] = recipe
        self._save()
        return recipe

    def forget(self, signature: str) -> bool:
        """Remove a cached recipe. Returns True if it existed."""
        if signature in self.cache:
            del self.cache[signature]
            self._save()
            return True
        return False

    # --- summary ---------------------------------------------------------------

    @property
    def recipe_count(self) -> int:
        return len(self.cache)

    def list_recipes(self) -> List[dict]:
        """Return all recipes sorted by last_success (most recent first)."""
        recipes = list(self.cache.values())
        recipes.sort(key=lambda r: r.get("last_success", 0), reverse=True)
        return recipes

    def format_recipe(self, signature: str) -> Optional[str]:
        """Format a recipe as a human-readable string."""
        recipe = self.cache.get(signature)
        if not recipe:
            return None

        lines = [
            f"📋 Recipe: {recipe.get('screen_name', '?')}",
            f"   Activity: {recipe.get('activity', '?')}",
            f"   Used {recipe.get('success_count', 0)} times",
            f"   Last success: {time.ctime(recipe.get('last_success', 0))}",
            f"   Steps:",
        ]
        for i, step in enumerate(recipe.get("steps", []), 1):
            action_type = step.get("action_type", "?")
            target = step.get("target_text", "") or step.get("target_id", "")
            if action_type == "tap":
                lines.append(f"     {i}. tap  [{target}]  ({step.get('center_x', '?')}, {step.get('center_y', '?')})")
            elif action_type == "text":
                lines.append(f"     {i}. text '{step.get('text_value', '')}'")
            elif action_type == "swipe":
                sd = step.get("swipe_data", {})
                lines.append(f"     {i}. swipe ({sd.get('x1')},{sd.get('y1')})→({sd.get('x2')},{sd.get('y2')})")
            elif action_type == "back":
                lines.append(f"     {i}. back")
            else:
                lines.append(f"     {i}. {action_type}")
        return "\n".join(lines)

    def get_status(self) -> str:
        """One-line cache status summary."""
        return f"📦 Screen cache: {self.recipe_count} recipe(s) cached — {self.cache_path}"

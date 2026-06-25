"""DOM element finder — locate elements via opencli find/state commands."""

import json
from typing import Optional

from web.controller import opencli_client as cli


def find_by_text(session: str, text: str) -> list[dict]:
    """Find all elements whose visible text contains the substring."""
    result = cli.find_by_text(session, text)
    return _normalize_entries(result)


def find_by_selector(session: str, selector: str) -> list[dict]:
    """Find all elements matching a CSS selector."""
    result = cli.find_by_css(session, selector)
    return _normalize_entries(result)


def find_by_role(session: str, role: str, name: str = "") -> list[dict]:
    """Find elements by ARIA role and optional accessible name."""
    result = cli.find_by_role(session, role, name=name)
    return _normalize_entries(result)


def find_inputs(session: str) -> list[dict]:
    """Find all visible input/textarea fields (textbox role)."""
    result = cli.find_inputs(session)
    entries = _normalize_entries(result)
    # Supplement with password inputs which may have role="textbox" or not
    pw_result = cli.find_by_css(session, "input[type='password']")
    for e in _normalize_entries(pw_result):
        e.setdefault("type", "password")
        entries.append(e)
    return entries


def _normalize_entries(result: dict) -> list[dict]:
    """Convert opencli find JSON to a flat list compatible with agent expectations."""
    entries = result.get("entries", [])
    normalized = []
    for e in entries:
        normalized.append({
            "ref": e.get("ref", ""),          # numeric ref for click/fill
            "tag": e.get("tag", "unknown"),
            "text": (e.get("text") or e.get("name") or "")[:100],
            "type": e.get("type", ""),
            "placeholder": e.get("placeholder", ""),
            "name": e.get("name", ""),
            "id": e.get("id", ""),
            "selector": e.get("selector", ""),
        })
    return normalized

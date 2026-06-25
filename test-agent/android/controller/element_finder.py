"""
UI hierarchy element finder — parses uiautomator dump XML to locate on-screen elements.

Completely generic — no app-specific knowledge.
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple


class UIElement:
    """Parsed UI node with computed center and readable attributes."""

    def __init__(self, node: ET.Element):
        self.text = node.get("text", "") or ""
        self.resource_id = node.get("resource-id", "") or ""
        self.class_name = node.get("class", "") or ""
        self.content_desc = node.get("content-desc", "") or ""
        self.package = node.get("package", "") or ""
        self.clickable = node.get("clickable", "false") == "true"
        self.focusable = node.get("focusable", "false") == "true"
        self.checkable = node.get("checkable", "false") == "true"
        self.enabled = node.get("enabled", "true") == "true"
        self.selected = node.get("selected", "false") == "true"

        bounds_str = node.get("bounds", "[0,0][0,0]")
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
        if m:
            self.x1, self.y1, self.x2, self.y2 = map(int, m.groups())
        else:
            self.x1 = self.y1 = self.x2 = self.y2 = 0

    @property
    def center(self) -> Tuple[int, int]:
        """Center point of the element bounds — suitable for tap."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """(x1, y1, x2, y2) bounding box."""
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    def __repr__(self) -> str:
        click = "✓" if self.clickable else "✗"
        return (
            f"UIElement(text='{self.text[:40]}'"
            f" id='{self.resource_id}'"
            f" center={self.center}"
            f" clickable={click})"
        )

    def summary(self, index: int = 0) -> str:
        """Human-readable summary line."""
        click = "clickable ✓" if self.clickable else ""
        focus = "focusable ✓" if self.focusable and not self.clickable else ""
        tags = " ".join(filter(None, [click, focus]))
        text_snippet = self.text[:60] if self.text else "(no text)"
        return (
            f"  [{index}] {text_snippet}\n"
            f"       id={self.resource_id or '(none)'}\n"
            f"       class={self.class_name.rsplit('.')[-1]}\n"
            f"       center=({self.center[0]}, {self.center[1]})\n"
            f"       bounds={self.bounds}  {tags}"
        )


class ElementFinder:
    """Search a uiautomator dump XML for UI elements."""

    def __init__(self, ui_xml: Optional[str] = None):
        self.raw_xml = ui_xml
        self.root: Optional[ET.Element] = None
        if ui_xml:
            # Strip encoding declarations that confuse ET
            cleaned = re.sub(r'<\?xml[^>]*\?>', '', ui_xml).strip()
            try:
                self.root = ET.fromstring(cleaned)
            except ET.ParseError:
                pass

    @classmethod
    def from_dump(cls, file_path: str) -> "ElementFinder":
        """Load from a saved uiautomator dump XML file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return cls(f.read())
        except (FileNotFoundError, IOError):
            return cls()

    def find(self, **criteria) -> List[UIElement]:
        """Generic search by any combination of attributes.

        Special keys:
          text_contains (str) — substring match on text
          id_contains (str)   — substring match on resource-id
          class_name (str)    — exact match on class (full or simple name)

        Regular keys map directly to XML node attributes (exact match):
          text, resource-id, content-desc, package, class,
          clickable, focusable, enabled (all bool).
        """
        results: List[UIElement] = []
        if self.root is None:
            return results

        for node in self.root.iter("node"):
            if self._matches(node, criteria):
                results.append(UIElement(node))
        return results

    def find_by_text(self, text_substring: str, clickable_only: bool = False) -> List[UIElement]:
        """Find elements whose text contains the substring."""
        criteria = {"text_contains": text_substring}
        if clickable_only:
            criteria["clickable"] = True
        return self.find(**criteria)

    def find_by_id(self, resource_id: str) -> List[UIElement]:
        """Find elements whose resource-id matches exactly."""
        return self.find(**{"resource-id": resource_id})

    def find_by_id_contains(self, id_substring: str) -> List[UIElement]:
        """Find elements whose resource-id contains the substring."""
        return self.find(id_contains=id_substring)

    def find_clickable(self) -> List[UIElement]:
        """Return all clickable elements."""
        return self.find(clickable=True)

    def find_input_fields(self) -> List[UIElement]:
        """Find text input fields (EditText class or focusable)."""
        results = []
        if self.root is None:
            return results
        for node in self.root.iter("node"):
            cls = (node.get("class") or "")
            if "EditText" in cls or "TextField" in cls:
                results.append(UIElement(node))
            elif node.get("focusable") == "true" and node.get("clickable") == "false":
                results.append(UIElement(node))
        return results

    def _matches(self, node: ET.Element, criteria: dict) -> bool:
        for key, value in criteria.items():
            if key == "text_contains":
                if value not in (node.get("text") or ""):
                    return False
            elif key == "id_contains":
                if value not in (node.get("resource-id") or ""):
                    return False
            elif key == "content_desc_contains":
                if value not in (node.get("content-desc") or ""):
                    return False
            elif key == "class_name":
                cls = node.get("class", "")
                if cls != value and cls.split(".")[-1] != value:
                    return False
            elif key in ("clickable", "focusable", "checkable", "enabled", "selected"):
                if (node.get(key, "false") == "true") != bool(value):
                    return False
            else:
                if node.get(key) != str(value):
                    return False
        return True

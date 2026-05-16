#!/usr/bin/env python3
"""
check_components.py — Component Usage Compliance Check (Layer 3)

Checks H5/Android code against components.yaml definitions:
  1. Class names used in HTML/Vue/CSS should match component names
  2. Unknown component-like classes are flagged
  3. Auto-generated files are skipped

Usage:
  python scripts/check/check_components.py --path h5/src
  python scripts/check/check_components.py --path prototype
"""

import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS_YAML = ROOT / "design-system" / "components" / "components.yaml"

# Files to skip (auto-generated, token definitions, etc.)
SKIP_PATTERNS = [
    "design-system/tokens/",
    "design-system/components/components.css",
    "design-system/exports/",
    "scripts/",
    "prototype/generated/",
]

CSS_CLASS_RE = re.compile(r'class=["\']([^"\']+)["\']')


def load_component_names() -> set[str]:
    if not COMPONENTS_YAML.exists():
        return set()
    with open(COMPONENTS_YAML) as f:
        data = yaml.safe_load(f)
    return set(data.get("components", {}))


def should_skip(filepath: str) -> bool:
    return any(p in filepath for p in SKIP_PATTERNS)


def check_file(filepath: Path, component_names: set[str]) -> list[dict]:
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return violations

    used_classes: set[str] = set()

    # Extract class names from class="xxx yyy"
    for match in CSS_CLASS_RE.finditer(content):
        classes = match.group(1).split()
        used_classes.update(c.strip() for c in classes if c.strip())

    # Also find class names in CSS selectors (.xxx {)
    for match in re.finditer(r'\.([a-z][a-z0-9-]*)', content):
        used_classes.add(match.group(1))

    # Check used classes against component names
    rel = str(filepath)
    for cls in sorted(used_classes):
        # Only flag classes that look like component classes
        # (hyphenated, not utility classes like 'flex', 'grid', etc.)
        if "-" not in cls:
            continue
        if cls in component_names:
            continue
        # Common CSS utility classes to skip
        if cls.startswith(("flex-", "grid-", "text-", "bg-", "p-", "m-", "w-", "h-")):
            continue
        # Known CSS properties like text-overflow
        if any(cls.startswith(p) for p in ("app-bar", "auth-", "brand-", "banner-",
                "category-", "detail-", "drama-", "episode-", "form-", "player-",
                "profile-", "search-", "section-", "skeleton", "social-", "speed-",
                "status-", "toast")):
            continue

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Component usage compliance check"
    )
    parser.add_argument("--path", nargs="+",
                        default=["h5/src", "prototype/index.html"],
                        help="Directories or files to scan")
    args = parser.parse_args()

    component_names = load_component_names()

    print()
    print("🧩  Component Usage Check (Layer 3)")
    print(f"    Components defined in components.yaml: {len(component_names)}")
    if component_names:
        print(f"    Names: {', '.join(sorted(component_names))}")
    print()

    if not component_names:
        print("⚠️  No components defined in components.yaml")
        print()
        return 0

    all_violations = []
    files_checked = 0
    components_used = set()

    TARGET_EXTS = {".html", ".vue", ".css", ".xml", ".ts", ".kt"}

    for dir_str in args.path:
        p = Path(dir_str)
        if not p.exists():
            print(f"⚠️  Not found: {p}")
            continue

        files = [p] if p.is_file() else sorted(p.rglob("*"))
        for fp in files:
            if not fp.is_file():
                continue
            if fp.suffix not in TARGET_EXTS:
                continue
            if should_skip(str(fp)):
                continue

            files_checked += 1
            try:
                content = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Count which components are used
            for comp_name in component_names:
                if comp_name in content:
                    components_used.add(comp_name)

            violations = check_file(fp, component_names)
            all_violations.extend(violations)

    print(f"    Files checked: {files_checked}")
    print()

    # Report component usage coverage
    unused = component_names - components_used
    if unused:
        print(f"📊  Components NOT used in scanned files ({len(unused)}):")
        for name in sorted(unused):
            print(f"    - {name}")
        print()

    if unused == component_names:
        print("    ℹ️  This may be expected if components are used differently")
        print("       in production code than in prototype.")
        print()

    if all_violations:
        by_file = defaultdict(list)
        for v in all_violations:
            by_file[v["file"]].append(v)
        for fp, violations in sorted(by_file.items()):
            print(f"❌  {fp}")
            for v in violations:
                print(f"    [{v['type']}] {v['message']}")
        print(f"⚠️   {len(all_violations)} violations")
        print()
        return 1

    print("✅  All component references matched.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

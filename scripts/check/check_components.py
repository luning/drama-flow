#!/usr/bin/env python3
"""
check_components.py — Component Usage Check (Layer 3)

Checks which components.yaml components are used in the scanned files.
Reports unused components so you can spot stale component definitions.

Usage:
  python scripts/check/check_components.py --path h5/src
  python scripts/check/check_components.py --path prototype
"""

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS_YAML = ROOT / "design-system" / "components" / "components.yaml"

TARGET_EXTS = {".html", ".vue", ".css", ".xml", ".ts", ".kt"}

# Auto-generated files — never scan these
SKIP_PATHS = [
    "design-system/tokens/",
    "design-system/components/components.css",
    "design-system/exports/",
    "scripts/",
    "prototype/generated/",
]


def load_component_names() -> set[str]:
    if not COMPONENTS_YAML.exists():
        return set()
    with open(COMPONENTS_YAML) as f:
        data = yaml.safe_load(f)
    return set(data.get("components", {}))


def main() -> int:
    parser = argparse.ArgumentParser(description="Component usage check")
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

    components_used: set[str] = set()
    files_checked = 0

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
            if any(skip in str(fp) for skip in SKIP_PATHS):
                continue

            files_checked += 1
            try:
                content = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for comp_name in component_names:
                if comp_name in content:
                    components_used.add(comp_name)

    print(f"    Files checked: {files_checked}")
    print()

    unused = component_names - components_used
    if unused:
        print(f"📊  Components NOT used in scanned files ({len(unused)}):")
        for name in sorted(unused):
            print(f"    - {name}")
        print()
    else:
        print("✅  All components referenced in scanned files.")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

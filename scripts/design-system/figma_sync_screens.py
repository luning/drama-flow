#!/usr/bin/env python3
"""
figma_sync_screens.py — Figma Page Data → Screen Specs

Placeholder: In production, this would:
  1. Call Figma REST API for each page/frame
  2. Detect auto-layout frames as sections
  3. Match Figma component instances to design-system component names
     by comparing figma component keys
  4. Detect repeated children → grid/list
  5. Extract data-source hints from text layers
  6. Output specs/screens/*.yaml

Prerequisites:
  - FIGMA_TOKEN env var
  - FIGMA_FILE_KEY env var
  - Figma pages must use auto-layout + component instances (not free-form groups)

For now, this validates the existing screen specs.

Usage:
  python scripts/design-system/figma_sync_screens.py --check
"""

import argparse
import os
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
SCREENS_DIR = ROOT / "design-system" / "specs" / "screens"


def validate_screen_spec(path: Path) -> list[str]:
    """Validate a single screen spec YAML file."""
    issues = []
    with open(path) as f:
        data = yaml.safe_load(f)

    expected_top = ["screen", "title", "scroll", "sections"]
    for key in expected_top:
        if key not in data:
            issues.append(f"{path.name}: missing '{key}'")

    for i, section in enumerate(data.get("sections", [])):
        for required in ["id", "component", "data"]:
            if required not in section:
                issues.append(f"{path.name} section[{i}]: missing '{required}'")

        # Validate that component names look valid
        comp = section.get("component", "")
        if comp and " " in comp:
            issues.append(f"{path.name} section[{i}]: component name '{comp}' contains spaces (use kebab-case)")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Figma page data → screen specs (placeholder)"
    )
    parser.add_argument("--check", action="store_true", help="Validate existing screen specs")
    args = parser.parse_args()

    print("📱  Figma → Screen Specs")
    print(f"    Screens directory: {SCREENS_DIR}")
    print()

    if args.check and SCREENS_DIR.exists():
        all_ok = True
        for yaml_file in sorted(SCREENS_DIR.glob("*.yaml")):
            issues = validate_screen_spec(yaml_file)
            if issues:
                for i in issues:
                    print(f"❌ {i}")
                all_ok = False
            else:
                print(f"✅ {yaml_file.name}: valid screen spec")

        if all_ok:
            print("\n    All screen specs valid.")
            return 0
        return 1

    file_key = os.environ.get("FIGMA_FILE_KEY")
    if file_key:
        print(f"    (Placeholder) Would fetch page layout from Figma file: {file_key}")
        print(f"    Detects: auto-layout sections → component instances → screen spec")
    else:
        print("    Set FIGMA_FILE_KEY env var to specify Figma file.")
        print("    Running in validation-only mode.")

    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
figma_sync_components.py — Figma Component Data → components.yaml

Placeholder: In production, this would:
  1. Call Figma REST API (GET /v1/files/{file_key}/components)
  2. For each component, extract:
     - Auto-layout properties (padding, gap, direction)
     - Fills (solid color, gradient stops)
     - Strokes (border color, width)
     - Effects (shadows, blurs)
     - Text styles (fontSize, fontWeight, fills)
     - Corner radius
  3. Resolve raw color values → token references using tokens.css reverse map
  4. Detect variants → generate variants section
  5. Output components/components.yaml

Prerequisites:
  - FIGMA_TOKEN env var set (personal access token)
  - FIGMA_FILE_KEY env var or --file-key argument

For now, this validates the existing components.yaml structure.

Usage:
  python scripts/design-system/figma_sync_components.py --check       # Validate components.yaml
  python scripts/design-system/figma_sync_components.py --dry-run     # Show what would change
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
DESIGN_SYSTEM = ROOT / "design-system"
COMPONENTS_YAML = DESIGN_SYSTEM / "components" / "components.yaml"
TOKENS_CSS = DESIGN_SYSTEM / "tokens" / "tokens.css"


def load_token_reverse_map() -> dict[str, str]:
    """
    Parse tokens.css and build a reverse map: hex value → token name.

    Returns dict like: {'#6C5CE7': 'color.primary', '#0F0F23': 'background.primary', ...}
    """
    token_map = {}
    if not TOKENS_CSS.exists():
        return token_map

    css = TOKENS_CSS.read_text()
    # Match: --color-primary: #6C5CE7;
    token_def_re = re.compile(r'--([a-z][a-z0-9-]*):\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))')
    for match in token_def_re.finditer(css):
        var_name = match.group(1)
        value = match.group(2)

        # Convert kebab-case to camelCase for components.yaml reference
        # e.g. --color-primary → color.primary
        # e.g. --color-primary-light → color.primaryLight
        parts = var_name.split("-")
        category = parts[0]
        # Rest parts to camelCase
        rest = parts[1:]
        camel = rest[0] + "".join(p.capitalize() for p in rest[1:]) if rest else ""
        ref = f"{category}.{camel}" if camel else category

        token_map[value.lower()] = ref
        token_map[value.upper()] = ref

    return token_map


def validate_components_yaml() -> list[str]:
    """Validate components.yaml structure."""
    issues = []

    if not COMPONENTS_YAML.exists():
        issues.append(f"components.yaml not found at {COMPONENTS_YAML}")
        return issues

    with open(COMPONENTS_YAML) as f:
        data = yaml.safe_load(f)

    if "components" not in data:
        issues.append("Missing top-level 'components' key")
        return issues

    components = data["components"]
    required_sections = ["base"]
    recommended_sections = ["description", "states"]

    for name, comp in components.items():
        for section in required_sections:
            if section not in comp:
                issues.append(f"Component '{name}': missing required section '{section}'")

        if "description" not in comp:
            issues.append(f"Component '{name}': missing recommended 'description'")

        # Check that all {token.refs} reference actual tokens
        token_refs = re.findall(r'\{([^}]+)\}', str(comp))
        for ref in token_refs:
            # Basic format check: should be like 'color.primary' or 'spacing.md'
            if '.' not in ref:
                issues.append(f"Component '{name}': suspicious token ref '{{{ref}}}' (missing category?)")

    return issues


def extract_figma_components(file_key: str) -> dict:
    """
    PLACEHOLDER: Extract components from Figma REST API.

    In production, this would:
      1. GET https://api.figma.com/v1/files/{file_key}/components
      2. For each component_set, iterate its variants
      3. GET /v1/files/{file_key}/nodes?ids={component_id} for detailed node data
      4. Process fill/effect/text nodes into component spec properties
    """
    print(f"    (Placeholder) Would fetch components from Figma file: {file_key}")
    print(f"    Requires FIGMA_TOKEN env var for authentication.")
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="Sync Figma components → components.yaml"
    )
    parser.add_argument("--check", action="store_true", help="Validate components.yaml")
    parser.add_argument("--file-key", help="Figma file key (overrides FIGMA_FILE_KEY env var)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    args = parser.parse_args()

    print("🧩  Figma → Components Sync")
    print(f"    Components file: {COMPONENTS_YAML}")
    print()

    # Load token reverse map
    token_map = load_token_reverse_map()
    print(f"    Token map: {len(token_map)} entries loaded from tokens.css")
    print()

    # Validate
    if args.check:
        issues = validate_components_yaml()
        if issues:
            for i in issues:
                print(f"❌ {i}")
            return 1
        else:
            print("✅ components.yaml: valid structure")
            return 0

    # Placeholder: fetch from Figma
    file_key = args.file_key or os.environ.get("FIGMA_FILE_KEY")
    if file_key:
        extract_figma_components(file_key)
    else:
        print("    Set FIGMA_FILE_KEY env var or use --file-key to specify Figma file.")
        print("    Currently running in validation-only mode.")

    print()


if __name__ == "__main__":
    main()

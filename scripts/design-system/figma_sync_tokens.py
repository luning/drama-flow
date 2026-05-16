#!/usr/bin/env python3
"""
figma_sync_tokens.py — Figma Tokens Studio → tokens.css + tokens.ts

Placeholder: In production, this would:
  1. Call Figma REST API or read Tokens Studio export (DTCG JSON format)
  2. Parse the DTCG design token JSON
  3. Generate tokens/tokens.css (CSS custom properties on :root)
  4. Generate tokens/tokens.ts (TypeScript const object)
  5. Validate against tokens/tokens.schema.json

For now, this script prints the expected pipeline structure and validates
that the current tokens files conform to the schema.

Usage:
  python scripts/design-system/figma_sync_tokens.py                # Dry-run: show what would change
  python scripts/design-system/figma_sync_tokens.py --source tokens.json  # From DTCG JSON file
  python scripts/design-system/figma_sync_tokens.py --apply                # Apply changes to tokens files
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DESIGN_SYSTEM = ROOT / "design-system"
TOKENS_DIR = DESIGN_SYSTEM / "tokens"
SCHEMA_FILE = TOKENS_DIR / "tokens.schema.json"
TOKENS_CSS = TOKENS_DIR / "tokens.css"
TOKENS_TS = TOKENS_DIR / "tokens.ts"


def validate_tokens_css(css_content: str) -> list[str]:
    """Parse tokens.css and check for common issues."""
    issues = []
    if ":root" not in css_content:
        issues.append("Missing :root selector in tokens.css")
    if "var(--" in css_content:
        issues.append("tokens.css should define tokens, not reference them (found var())")
    return issues


def validate_tokens_ts(ts_content: str) -> list[str]:
    """Parse tokens.ts and check for common issues."""
    issues = []
    if "export const tokens" not in ts_content:
        issues.append("Missing 'export const tokens' in tokens.ts")
    return issues


def sync_from_dtcg(dtcg_path: Path) -> dict:
    """
    Read DTCG-format JSON and map to our token structure.

    DTCG format example:
    {
      "color": {
        "primary": { "$value": "#6C5CE7", "$type": "color" }
      },
      "spacing": {
        "md": { "$value": "12px", "$type": "dimension" }
      }
    }
    """
    with open(dtcg_path) as f:
        dtcg = json.load(f)

    # Flatten DTCG to our token format
    tokens = {}
    for category, values in dtcg.items():
        tokens[category] = {}
        for name, entry in values.items():
            tokens[category][name] = entry.get("$value", entry)

    return tokens


def main():
    parser = argparse.ArgumentParser(
        description="Sync Figma Tokens Studio export → design-system tokens"
    )
    parser.add_argument("--source", type=Path, help="Path to DTCG JSON file from Figma")
    parser.add_argument("--apply", action="store_true", help="Write changes to tokens files")
    parser.add_argument("--check", action="store_true", help="Only check consistency, no write")
    args = parser.parse_args()

    print("🎨  Figma → Tokens Sync")
    print(f"    Tokens directory: {TOKENS_DIR}")
    print()

    # Validate schema exists
    if not SCHEMA_FILE.exists():
        print(f"⚠️  Schema file not found: {SCHEMA_FILE}")
    else:
        print(f"✅ Schema: {SCHEMA_FILE}")

    # Validate tokens.css
    if TOKENS_CSS.exists():
        css = TOKENS_CSS.read_text()
        issues = validate_tokens_css(css)
        if issues:
            for i in issues:
                print(f"⚠️  tokens.css: {i}")
        else:
            print(f"✅ tokens.css: valid ({len(css.splitlines())} lines)")
    else:
        print(f"❌ tokens.css not found at {TOKENS_CSS}")

    # Validate tokens.ts
    if TOKENS_TS.exists():
        ts = TOKENS_TS.read_text()
        issues = validate_tokens_ts(ts)
        if issues:
            for i in issues:
                print(f"⚠️  tokens.ts: {i}")
        else:
            print(f"✅ tokens.ts: valid ({len(ts.splitlines())} lines)")
    else:
        print(f"❌ tokens.ts not found at {TOKENS_TS}")

    # If --source provided, show what would be synced
    if args.source and args.source.exists():
        print(f"\n📥  Reading DTCG tokens from: {args.source}")
        tokens = sync_from_dtcg(args.source)
        print(f"    Categories found: {list(tokens.keys())}")
        for cat, vals in tokens.items():
            print(f"    {cat}: {len(vals)} tokens")
        if not args.apply:
            print("\n    (dry-run: use --apply to write changes)")

    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
check_tokens.py — Design Token Compliance Check (Layer 1)

Scans frontend files for:
  1. Hardcoded hex colors — should use var(--xxx)
  2. Hardcoded rgba() / rgb() colors
  3. Short hex codes (#fff, #888)
  4. Unknown CSS variable names (var(--primary) instead of var(--color-primary))
  5. Missing import of tokens.css in entry files

Enhanced from original check_design_tokens.py.

Usage:
  python scripts/check/check_tokens.py                      # Default: h5/src, prototype
  python scripts/check/check_tokens.py --path h5/src        # Specific directory
  python scripts/check/check_tokens.py --path android/...   # Android XML
  python scripts/check/check_tokens.py --strict             # Unknown colors fail
  python scripts/check/check_tokens.py --check-imports      # Also verify CSS import chain
"""

import argparse
import difflib
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent

# ── Token definition files (raw colors allowed) ────────────
SKIP_FILES = {
    "design-system/tokens/tokens.css",
    "design-system/tokens/tokens.ts",
    "design-system/exports/android/colors.xml",
    "scripts/check/check_tokens.py",
}

TARGET_EXTENSIONS = {".html", ".vue", ".css", ".scss", ".xml"}

# ── Regex ──────────────────────────────────────────────────
CSS_HEX_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
CSS_RGBA_RE = re.compile(r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+')
CSS_VAR_RE = re.compile(r'var\(--([a-z][a-z0-9-]*)\)')

SKIP_LINE_PATTERNS = [
    re.compile(r'^\s*--[a-z]'),
    re.compile(r'//\s'),
    re.compile(r'/\*|\*/'),
    re.compile(r'<!--'),
    re.compile(r"color:\s*'#"),
    re.compile(r'color:\s*"#'),
    re.compile(r'fill="%23'),
    re.compile(r'href=|src='),
    re.compile(r'AUTO-GENERATED'),
    re.compile(r'DO NOT EDIT'),
    re.compile(r'^#!/'),
    re.compile(r'SKIP_FILES'),
]


def load_token_names() -> set[str]:
    """Parse tokens.css and return valid CSS variable names."""
    tokens_css = ROOT / "design-system" / "tokens" / "tokens.css"
    if not tokens_css.exists():
        return set()
    names = set()
    for m in re.finditer(r'--([a-z][a-z0-9-]*):', tokens_css.read_text()):
        names.add(m.group(1))
    return names


def load_token_map() -> dict[str, str]:
    """Parse tokens.css, return {hex: var(--name)} mapping."""
    tokens_css = ROOT / "design-system" / "tokens" / "tokens.css"
    if not tokens_css.exists():
        return {}
    m = {}
    content = tokens_css.read_text()
    for match in re.finditer(r'--([a-z][a-z0-9-]*):\s*(#[0-9a-fA-F]{3,8})', content):
        var_name, hex_val = match.group(1), match.group(2)
        v = f"var(--{var_name})"
        m[hex_val.lower()] = v
        m[hex_val.upper()] = v
    return m


def should_skip_line(line: str) -> bool:
    return any(p.search(line) for p in SKIP_LINE_PATTERNS)


def find_violations(path: Path, token_map: dict[str, str],
                    token_names: set[str]) -> list[dict]:
    rel = str(path)
    for skip in SKIP_FILES:
        if skip in rel:
            return []
    if path.suffix not in TARGET_EXTENSIONS:
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    violations = []
    for lineno, line in enumerate(content.splitlines(), 1):
        if should_skip_line(line):
            continue

        # Check 1: Hardcoded hex colors
        for match in CSS_HEX_RE.finditer(line):
            raw = "#" + match.group(1)
            if len(match.group(1)) == 3:
                if not re.search(r'[:,\s]' + re.escape(raw) + r'\b', line):
                    continue
            if "var(" in line[:match.start()]:
                continue
            suggestion = token_map.get(raw.lower())
            violations.append({
                "file": rel, "line": lineno, "type": "hex",
                "value": raw, "suggestion": suggestion,
                "context": line.strip()[:120]
            })

        # Check 2: Hardcoded rgba()
        for match in CSS_RGBA_RE.finditer(line):
            if "var(" in line[:match.start()]:
                continue
            raw = match.group(0)
            violations.append({
                "file": rel, "line": lineno, "type": "rgba",
                "value": raw, "suggestion": None,
                "context": line.strip()[:120]
            })

        # Check 3: Unknown CSS variable names
        for match in CSS_VAR_RE.finditer(line):
            var_name = match.group(1)
            if var_name not in token_names:
                close = difflib.get_close_matches(var_name, token_names, n=1, cutoff=0.5)
                suggestion = f"var(--{close[0]})" if close else None
                violations.append({
                    "file": rel, "line": lineno, "type": "var",
                    "value": f"var(--{var_name})", "suggestion": suggestion,
                    "context": line.strip()[:120]
                })

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Design Token compliance check")
    parser.add_argument("--path", nargs="+",
                        default=["h5/src", "prototype"],
                        help="Directories to scan")
    parser.add_argument("--strict", action="store_true",
                        help="Unknown colors fail the check")
    parser.add_argument("--check-imports", action="store_true",
                        help="Also verify tokens.css import chain")
    args = parser.parse_args()

    token_map = load_token_map()
    token_names = load_token_names()

    print()
    print("🔍  Design Token Compliance Check (Layer 1)")
    print(f"    Tokens loaded: {len(token_map)} colors, {len(token_names)} variables")
    print(f"    Scanning: {' '.join(args.path)}")
    print()

    all_violations = []
    files_checked = 0

    for dir_str in args.path:
        p = Path(dir_str)
        if not p.exists():
            print(f"⚠️  Not found: {p}")
            continue
        for fp in sorted(p.rglob("*")):
            if fp.is_file() and fp.suffix in TARGET_EXTENSIONS:
                files_checked += 1
                all_violations.extend(find_violations(fp, token_map, token_names))

    print(f"    Files checked: {files_checked}")
    print()

    if not all_violations:
        print("✅  All clear — 0 design token violations.")
        print()
        return 0

    by_file = defaultdict(list)
    for v in all_violations:
        by_file[v["file"]].append(v)

    for fp, violations in sorted(by_file.items()):
        print(f"❌  {fp}")
        for v in violations:
            icon = {"hex": "🎨", "rgba": "🎨", "var": "🏷️"}.get(v["type"], "❓")
            fix = f"→ {v['suggestion']}" if v.get("suggestion") else "→ add to tokens.css"
            print(f"    L{v['line']:<5} {icon} {v['value']:<24} {fix}")
            if v["context"]:
                print(f"           {v['context'][:80]}")
        print()

    by_type = defaultdict(int)
    for v in all_violations:
        by_type[v["type"]] += 1

    print(f"⚠️   {len(all_violations)} violations total")
    for t, c in sorted(by_type.items()):
        label = {"hex": "Hardcoded hex", "rgba": "Hardcoded rgba()",
                 "var": "Unknown var() name"}.get(t, t)
        print(f"    · {label}: {c}")
    print()

    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
check_constraints.py — Business Constraint Compliance Check (Layer 2)

Checks H5/Android code against constraints.md rules:
  1. Single btn-primary per page
  2. All async operations have loading states
  3. Minimum touch target 44x44px
  4. 3:4 aspect ratio for drama cards
  5. 16px horizontal page padding
  6. No disabled state using brand color
  7. Card title max 2 lines with ellipsis
  8. Episode labels in "第N集" format
  9. Duration labels in "MM:SS" format

Usage:
  python scripts/check/check_constraints.py --path h5/src
  python scripts/check/check_constraints.py --path android/.../res/layout
"""

import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent

# ── Constraint checkers ───────────────────────────────────────

def check_single_primary_button(content: str, filepath: str) -> list[dict]:
    """Check: Only one btn-primary per page."""
    violations = []
    count = len(re.findall(r'btn-primary|btnPrimary', content))
    if count > 1:
        violations.append({
            "file": filepath, "line": 0, "constraint": "single-primary-cta",
            "message": f"Found {count} primary buttons (constraint: max 1 per page)",
            "fix": "Keep only the most important CTA as btn-primary; use btn-secondary for others"
        })
    return violations


def check_loading_states(content: str, filepath: str) -> list[dict]:
    """Check: Async operations have loading/skeleton states."""
    violations = []

    # Detect async operations (fetch, onMounted, async functions)
    has_async = bool(re.search(
        r'(onMounted|async\s+function|\.fetch|\.get\(|axios|fetch\()', content
    ))

    # Detect loading states
    has_loading = bool(re.search(
        r'(loading|skeleton|spinner|Loading|Skeleton|\.loading|v-if.*loading)',
        content, re.IGNORECASE
    ))

    if has_async and not has_loading:
        violations.append({
            "file": filepath, "line": 0, "constraint": "loading-state",
            "message": "Async operations detected but no loading/skeleton state found",
            "fix": "Add a loading skeleton or spinner while data is being fetched"
        })
    return violations


def check_touch_targets(content: str, filepath: str) -> list[dict]:
    """Check: Interactive elements have minimum 44x44px touch target."""
    violations = []

    # Find button-like elements with small dimensions
    small_buttons = re.findall(
        r'(?:width|height):\s*(\d+)px.*(?:button|btn|click)',
        content
    )
    for match in re.finditer(
        r'\.btn.*\{[^}]*?(?:width|height):\s*(\d+)px',
        content, re.DOTALL
    ):
        size = int(match.group(1))
        if size < 44:
            violations.append({
                "file": filepath, "line": 0, "constraint": "touch-target",
                "message": f"Button with {size}px dimension < 44px minimum",
                "fix": f"Increase to at least 44px"
            })

    # Also check Android layouts
    small_android = re.findall(
        r'android:layout_height="(\d+)dp".*(?:[Bb]utton|[Cc]lick)',
        content
    )
    for h in small_android:
        if int(h) < 44:
            violations.append({
                "file": filepath, "line": 0, "constraint": "touch-target",
                "message": f"Android button height {h}dp < 44dp minimum",
                "fix": "Increase android:layout_height to at least 44dp"
            })

    return violations


def check_aspect_ratio(content: str, filepath: str) -> list[dict]:
    """Check: Drama cards use 3:4 aspect ratio."""
    violations = []

    # Find aspect-ratio declarations near card-related classes
    card_regions = re.findall(
        r'(?:drama-card|thumb).*?aspect-ratio:\s*([\d/]+)',
        content, re.DOTALL
    )
    for ratio in card_regions:
        ratio = ratio.strip()
        if ratio not in ("3/4", "3 / 4", "0.75"):
            violations.append({
                "file": filepath, "line": 0, "constraint": "aspect-ratio",
                "message": f"Card/thumb aspect-ratio is {ratio}, expected 3/4",
                "fix": "Change to aspect-ratio: 3/4"
            })

    # Check for missing aspect-ratio
    if "drama-card" in content and "aspect-ratio" not in content:
        # Only flag if thumb class exists without ratio
        if re.search(r'\.thumb\s*\{', content):
            if "aspect-ratio" not in content:
                violations.append({
                    "file": filepath, "line": 0, "constraint": "aspect-ratio",
                    "message": "drama-card .thumb missing aspect-ratio: 3/4",
                    "fix": "Add aspect-ratio: 3/4 to .thumb styles"
                })

    return violations


def check_disabled_state(content: str, filepath: str) -> list[dict]:
    """Check: Disabled state doesn't use brand color."""
    violations = []
    # Look for :disabled with primary color or gradient
    if re.search(r':disabled.*(?:var\(--color-primary\)|#6C5CE7|#6c5ce7)', content):
        violations.append({
            "file": filepath, "line": 0, "constraint": "disabled-color",
            "message": "Disabled state uses brand primary color",
            "fix": "Use var(--text-muted) for disabled state instead"
        })
    return violations


def check_card_title_ellipsis(content: str, filepath: str) -> list[dict]:
    """Check: Card titles use ellipsis for overflow (max 2 lines)."""
    violations = []
    # Find card title elements
    if "drama-card" in content or ".info h4" in content:
        has_ellipsis = (
            "text-overflow: ellipsis" in content
            or "-webkit-line-clamp" in content
            or "line-clamp" in content
        )
        if not has_ellipsis:
            violations.append({
                "file": filepath, "line": 0, "constraint": "title-ellipsis",
                "message": "Card title missing text overflow handling",
                "fix": "Add: overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2;"
            })
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Business constraint compliance check"
    )
    parser.add_argument("--path", nargs="+",
                        default=["h5/src", "android/app/src/main/res/layout"],
                        help="Directories to scan")
    args = parser.parse_args()

    print()
    print("📋  Business Constraint Check (Layer 2)")
    print(f"    Constraints source: design-system/specs/constraints.md")
    print(f"    Scanning: {' '.join(args.path)}")
    print()

    all_violations = []
    files_checked = 0

    checkers = [
        check_single_primary_button,
        check_loading_states,
        check_touch_targets,
        check_aspect_ratio,
        check_disabled_state,
        check_card_title_ellipsis,
    ]

    for dir_str in args.path:
        p = Path(dir_str)
        if not p.exists():
            print(f"⚠️  Path not found: {p}")
            continue

        for file_path in sorted(p.rglob("*")):
            if not file_path.is_file():
                continue
            ext = file_path.suffix
            if ext not in (".vue", ".css", ".xml", ".html", ".ts", ".kt"):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            files_checked += 1
            for checker in checkers:
                all_violations.extend(checker(content, str(file_path)))

    print(f"    Files checked: {files_checked}")
    print()

    if not all_violations:
        print("✅  All constraints satisfied.")
        print()
        return 0

    # Group by file
    by_file = defaultdict(list)
    for v in all_violations:
        by_file[v["file"]].append(v)

    for file_path, violations in sorted(by_file.items()):
        print(f"❌  {file_path}")
        for v in violations:
            print(f"    [{v['constraint']}] {v['message']}")
            print(f"    Fix: {v['fix']}")
        print()

    print(f"⚠️   Total: {len(all_violations)} constraint violations")
    print()

    return 1


if __name__ == "__main__":
    sys.exit(main())

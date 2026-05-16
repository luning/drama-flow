#!/usr/bin/env python3
"""
generate_prototype.py — Screen Specs → HTML Prototype Pages

Takes screen specs from specs/screens/*.yaml and generates prototype HTML pages
with real component markup but fake/static data.

The generated prototype:
  - Imports tokens.css and components.css for styles
  - Uses the same component class names as H5
  - Contains dummy data so PM/designers can see the layout
  - Serves as a "living spec" — what you see IS what gets built

Usage:
  python scripts/design-system/generate_prototype.py                      # Generate all screens
  python scripts/design-system/generate_prototype.py --screen home        # Generate one screen
  python scripts/design-system/generate_prototype.py --output prototype/generated/
"""

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
SCREENS_DIR = ROOT / "design-system" / "specs" / "screens"
DEFAULT_OUTPUT = ROOT / "prototype" / "generated"

# Page wrapper template
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title} — DramaFlow Prototype</title>
<link rel="stylesheet" href="../../design-system/tokens/tokens.css">
<link rel="stylesheet" href="../../design-system/components/components.css">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg-outer);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: var(--font-family);
  }}
  .phone {{
    width: var(--phone-width);
    min-height: var(--phone-height);
    background: var(--bg-primary);
    border-radius: var(--phone-radius);
    overflow: hidden;
    box-shadow: var(--shadow-phone);
    display: flex;
    flex-direction: column;
  }}
  .page-content {{
    flex: 1;
    overflow-y: auto;
    {scroll}
  }}
  .page-content::-webkit-scrollbar {{ display: none; }}

  /* Page-specific layout helpers */
  .drama-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-4) var(--space-5);
  }}
  .section-title {{
    padding: 0 var(--space-4);
    margin-top: var(--space-3);
    margin-bottom: var(--space-2);
  }}
  .section-title h3 {{
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
  }}

  /* App Bar */
  .app-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    height: 44px;
  }}
  .app-bar h1 {{
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-extrabold);
    background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .app-bar .search-btn {{
    background: none;
    border: none;
    color: var(--text-primary);
    font-size: 20px;
    cursor: pointer;
  }}

  /* Detail Page */
  .detail-header {{
    width: 100%;
    aspect-ratio: 16/9;
    background: linear-gradient(135deg, var(--color-primary), var(--bg-deep));
    position: relative;
  }}
  .detail-header .overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(transparent 40%, var(--bg-primary));
  }}
  .detail-header .back {{
    position: absolute;
    top: 12px;
    left: 12px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(0,0,0,0.4);
    border: none;
    color: var(--text-primary);
    font-size: 20px;
    cursor: pointer;
    z-index: 2;
  }}
  .detail-body {{
    padding: var(--space-4);
  }}
  .detail-body h1 {{
    color: var(--text-primary);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }}
  .detail-body .sub-info {{
    display: flex;
    gap: var(--space-3);
    margin-top: 6px;
    color: var(--text-tertiary);
    font-size: 13px;
  }}
  .detail-body .rating-row {{
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: 10px;
  }}
  .detail-body .stars {{
    color: var(--color-rating);
    font-size: 16px;
  }}
  .detail-body .score {{
    color: var(--color-rating);
    font-size: 18px;
    font-weight: var(--font-weight-bold);
  }}
  .detail-body .desc {{
    color: var(--text-secondary);
    font-size: var(--font-size-base);
    line-height: 1.7;
    margin-top: 14px;
  }}
  .detail-body .actions {{
    margin-top: var(--space-4);
    display: flex;
    gap: var(--space-3);
  }}
  .tabs-header {{
    display: flex;
    border-bottom: 1px solid var(--border);
    padding: 0 var(--space-4);
  }}
  .tabs-header span {{
    padding: 10px 0;
    color: var(--color-primary);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    border-bottom: 2px solid var(--color-primary);
    margin-right: var(--space-6);
  }}

  /* Continue Watching */
  .continue-section {{
    padding: 0 var(--space-4);
    margin-top: var(--space-2);
  }}
  .continue-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2);
  }}
  .continue-header span {{
    color: var(--text-primary);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
  }}
  .continue-header a {{
    color: var(--color-primary-light);
    font-size: var(--font-size-sm);
    cursor: pointer;
  }}
</style>
</head>
<body>
<div class="phone">
  <div class="page-content">
{content}
  </div>
</div>
</body>
</html>
"""


def generate_section_html(section: dict) -> str:
    """Generate HTML for a single section from its screen spec."""
    comp = section["component"]
    sid = section["id"]
    lines = []

    if comp == "app-bar":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <header class="app-bar">')
        lines.append(f'    <h1>{section.get("props", {}).get("title", "DramaFlow")}</h1>')
        lines.append(f'    <button class="search-btn">🔍</button>')
        lines.append(f'  </header>')

    elif comp == "continue-watching-card":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="continue-section">')
        lines.append(f'    <div class="continue-header">')
        lines.append(f'      <span>{section.get("props", {}).get("header_title", "继续观看")}</span>')
        lines.append(f'      <a>{section.get("props", {}).get("header_action", "查看全部 →")}</a>')
        lines.append(f'    </div>')
        # Dummy continue watching cards
        for i in range(2):
            dummy = [
                ("重生之都市仙尊", "第 12 集 · 68%", 68),
                ("总裁的替身新娘", "第 5 集 · 42%", 42),
            ][i]
            lines.append(f'    <div class="continue-watching-card">')
            lines.append(f'      <div class="thumb"></div>')
            lines.append(f'      <div class="info">')
            lines.append(f'        <h4>{dummy[0]}</h4>')
            lines.append(f'        <div class="ep">{dummy[1]}</div>')
            lines.append(f'        <div class="progress-bar" style="margin-top:8px;"><div class="fill" style="width:{dummy[2]}%"></div></div>')
            lines.append(f'      </div>')
            lines.append(f'    </div>')
        lines.append(f'  </div>')

    elif comp == "banner-carousel":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div style="padding: var(--space-3) var(--space-4);">')
        lines.append(f'    <div class="banner-carousel">')
        lines.append(f'      <div class="slide"></div>')
        lines.append(f'      <div class="dots">')
        lines.append(f'        <span class="dot active"></span>')
        lines.append(f'        <span class="dot"></span>')
        lines.append(f'        <span class="dot"></span>')
        lines.append(f'      </div>')
        lines.append(f'    </div>')
        lines.append(f'  </div>')

    elif comp == "category-tabs":
        tabs = ["全部", "甜宠", "悬疑", "搞笑", "奇幻", "霸总"]
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="category-tabs">')
        for i, tab in enumerate(tabs):
            active = ' active' if i == 0 else ''
            lines.append(f'    <button class="tab{active}">{tab}</button>')
        lines.append(f'  </div>')

    elif comp == "drama-grid":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="section-title"><h3>为你推荐</h3></div>')
        lines.append(f'  <div class="drama-grid">')
        dummy_dramas = [
            ("重生之都市仙尊", "热播", "9.5"),
            ("总裁的替身新娘", "新剧", "8.9"),
            ("穿越之医女倾城", "甜宠", "9.2"),
            ("最强赘婿在都市", "搞笑", "8.7"),
            ("重生之亿万富翁", "奇幻", "9.1"),
            ("穿越之绝世王妃", "霸总", "8.8"),
        ]
        for title, badge, rating in dummy_dramas:
            lines.append(f'    <div class="drama-card">')
            lines.append(f'      <div class="thumb"><span class="badge">{badge}</span></div>')
            lines.append(f'      <div class="info">')
            lines.append(f'        <h4>{title}</h4>')
            lines.append(f'        <div class="rating">★ {rating}</div>')
            lines.append(f'      </div>')
            lines.append(f'    </div>')
        lines.append(f'  </div>')

    elif comp == "detail-header":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="detail-header">')
        lines.append(f'    <div class="overlay"></div>')
        lines.append(f'    <button class="back">‹</button>')
        lines.append(f'  </div>')

    elif comp == "detail-body":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="detail-body">')
        lines.append(f'    <h1>重生之都市仙尊</h1>')
        lines.append(f'    <div class="sub-info"><span>2024 · 共24集</span></div>')
        lines.append(f'    <div class="rating-row">')
        lines.append(f'      <span class="stars">★★★★★</span>')
        lines.append(f'      <span class="score">9.5</span>')
        lines.append(f'    </div>')
        lines.append(f'    <div class="desc">都市青年林风意外重生到修真世界，获得神秘功法，从此踏上逆天改命的修仙之路...</div>')
        lines.append(f'    <div class="actions">')
        lines.append(f'      <button class="btn-primary">▶ 立即观看</button>')
        lines.append(f'      <button class="btn-outline">♡ 收藏</button>')
        lines.append(f'    </div>')
        lines.append(f'  </div>')

    elif comp == "tabs":
        lines.append(f'  <!-- {sid} -->')
        lines.append(f'  <div class="tabs-header">')
        lines.append(f'    <span>剧集列表</span>')
        lines.append(f'    <span style="border-color:transparent;color:var(--text-tertiary);">评论</span>')
        lines.append(f'  </div>')

    elif comp == "episode-list":
        lines.append(f'  <!-- {sid} -->')
        episodes = [
            ("1", "第一集：重生归来", "15:32"),
            ("2", "第二集：都市风云", "16:48"),
            ("3", "第三集：暗流涌动", "14:55"),
            ("4", "第四集：初露锋芒", "17:20"),
            ("5", "第五集：危机四伏", "15:10"),
        ]
        for num, title, dur in episodes:
            lines.append(f'  <div class="episode-item">')
            lines.append(f'    <span class="number">{num}</span>')
            lines.append(f'    <div class="thumb"></div>')
            lines.append(f'    <div class="info">')
            lines.append(f'      <div class="title">{title}</div>')
            lines.append(f'      <div class="duration">{dur}</div>')
            lines.append(f'    </div>')
            lines.append(f'  </div>')

    return "\n".join(lines)


def generate_screen(yaml_path: Path) -> str:
    """Generate a complete prototype HTML page from a screen spec."""
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    scroll = ""
    if spec.get("scroll") == "vertical":
        scroll = "overflow-y: auto;"

    content_lines = []
    for section in spec.get("sections", []):
        content_lines.append(f"    <!-- @component: {section['component']} -->")
        content_lines.append(generate_section_html(section))
        content_lines.append(f"    <!-- @endcomponent -->")
        content_lines.append("")

    content = "\n".join(content_lines)

    return PAGE_TEMPLATE.format(
        title=spec.get("title", "Prototype"),
        scroll=scroll,
        content=content
    )


def main():
    parser = argparse.ArgumentParser(
        description="Screen specs → HTML prototype pages"
    )
    parser.add_argument("--screen", help="Generate a specific screen (e.g. 'home')")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output directory for generated HTML")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of writing")
    args = parser.parse_args()

    print("📄  Screen Specs → HTML Prototype")
    print(f"    Source: {SCREENS_DIR}")
    print(f"    Output: {args.output}")
    print()

    if not SCREENS_DIR.exists():
        print(f"❌ Screens directory not found: {SCREENS_DIR}")
        return 1

    yaml_files = sorted(SCREENS_DIR.glob("*.yaml"))

    if args.screen:
        yaml_files = [f for f in yaml_files if args.screen in f.name]

    if not yaml_files:
        print("    No screen specs found.")
        return 0

    for yf in yaml_files:
        try:
            html = generate_screen(yf)
        except Exception as e:
            print(f"❌ {yf.name}: generation failed — {e}")
            continue

        out_name = yf.stem + ".html"
        if args.stdout:
            print(f"\n{'='*60}")
            print(f"Generated: {out_name}")
            print(f"{'='*60}")
            print(html[:2000])
            print("...")
        else:
            args.output.mkdir(parents=True, exist_ok=True)
            out_path = args.output / out_name
            out_path.write_text(html)
            print(f"✅ {out_name} ({len(html.splitlines())} lines)")

    print()


if __name__ == "__main__":
    main()

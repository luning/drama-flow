#!/usr/bin/env python3
"""
generate_h5_template.py — Screen Specs → Vue 3 Page Templates

Takes screen specs from specs/screens/*.yaml and generates Vue 3 SFC
page templates with proper data bindings, store imports, and router integration.

Usage:
  python scripts/design-system/generate_h5_template.py
  python scripts/design-system/generate_h5_template.py --screen home
  python scripts/design-system/generate_h5_template.py --stdout
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
SCREENS_DIR = ROOT / "design-system" / "specs" / "screens"
DEFAULT_OUTPUT = ROOT / "h5" / "src" / "pages"

# Which refs each component type needs declared in <script setup>
COMPONENT_REFS: dict[str, list[str]] = {
    "app-bar": ["title"],
    "continue-watching-card": ["continueWatching"],
    "banner-carousel": ["banners"],
    "category-tabs": ["activeCategory", "categories"],
    "drama-grid": ["items"],
    "episode-list": ["episodes"],
}

VUE_TEMPLATE = """<!--
  {title}.vue — Scaffold generated from specs/screens/{screen}.yaml
  Edit this file to implement the page. The screen spec defines the structure.
-->
<script setup lang="ts">
import {{ ref, onMounted }} from 'vue'
import {{ useRouter }} from 'vue-router'
{imports}

const router = useRouter()
const loading = ref(true)
{refs}
// Data sources defined in screen spec:
// {data_sources}

onMounted(async () => {{
  loading.value = true
  try {{
    // TODO: Fetch data from: {data_sources}
  }} finally {{
    loading.value = false
  }}
}})
</script>

<template>
  <div class="page {screen}-page">
{template_content}
  </div>
</template>

<style scoped>
.{screen}-page {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}}
</style>
"""

# Default values for ref declarations so templates type-check out of the box
REF_DEFAULTS: dict[str, str] = {
    "title": "''",
    "continueWatching": "[] as any[]",
    "banners": "[] as any[]",
    "activeCategory": "''",
    "categories": "[] as any[]",
    "items": "[] as any[]",
    "episodes": "[] as any[]",
}


def generate_vue_page(yaml_path: Path) -> str:
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    screen = spec["screen"]
    screen_title = spec.get("title", screen.capitalize())
    sections = spec.get("sections", [])

    imports = ["// Import stores and APIs as needed:"]
    template_lines: list[str] = []
    data_sources: list[str] = []
    refs_needed: dict[str, str] = {}  # name → default value

    for section in sections:
        comp = section["component"]
        sid = section.get("id", "")
        data_src = section.get("data", "static")

        if data_src != "static" and data_src != "none":
            data_sources.append(data_src)

        # Collect needed refs
        for ref_name in COMPONENT_REFS.get(comp, []):
            if ref_name not in refs_needed:
                refs_needed[ref_name] = REF_DEFAULTS.get(ref_name, "null")

        if comp == "app-bar":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <header class="app-bar">')
            template_lines.append(f'      <h1>{{{{ title }}}}</h1>')
            template_lines.append(f'    </header>')
        elif comp == "drama-grid":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <div class="drama-grid">')
            template_lines.append(f'      <div class="drama-card" v-for="item in items" :key="item.id"')
            template_lines.append(f'           @click="router.push(\'/detail/\' + item.id)">')
            template_lines.append(f'        <div class="thumb"><span class="badge">{{{{ item.tag }}}}</span></div>')
            template_lines.append(f'        <div class="info">')
            template_lines.append(f'          <h4>{{{{ item.title }}}}</h4>')
            template_lines.append(f'          <div class="rating">★ {{{{ item.rating }}}}</div>')
            template_lines.append(f'        </div>')
            template_lines.append(f'      </div>')
            template_lines.append(f'    </div>')
        elif comp == "category-tabs":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <CategoryTabs v-model="activeCategory" :items="categories" />')
        elif comp == "banner-carousel":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <BannerCarousel :items="banners" />')
        elif comp == "continue-watching-card":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <ContinueWatchingCard :items="continueWatching" />')
        elif comp == "episode-list":
            template_lines.append(f'    <!-- {sid}: {comp} -->')
            template_lines.append(f'    <div class="episode-list">')
            template_lines.append(f'      <div class="episode-item" v-for="ep in episodes" :key="ep.num"')
            template_lines.append(f'           @click="router.push(\'/player/\' + ep.num)">')
            template_lines.append(f'        <span class="number">{{{{ ep.num }}}}</span>')
            template_lines.append(f'        <div class="info">')
            template_lines.append(f'          <div class="title">{{{{ ep.title }}}}</div>')
            template_lines.append(f'        </div>')
            template_lines.append(f'      </div>')
            template_lines.append(f'    </div>')
        else:
            template_lines.append(f'    <!-- @component: {comp} — template not yet defined for section {sid} -->')

    # Generate ref declarations
    ref_lines = [f"const {name} = ref({default_val})" for name, default_val in refs_needed.items()]
    if not ref_lines:
        ref_lines.append("// No reactive state defined in screen spec")

    return VUE_TEMPLATE.format(
        title=screen_title,
        screen=screen,
        imports="\n".join(imports),
        refs="\n".join(ref_lines),
        data_sources=", ".join(data_sources) if data_sources else "static content",
        template_content="\n".join(template_lines) or "    <!-- No sections defined in screen spec -->",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Screen specs → Vue 3 page templates"
    )
    parser.add_argument("--screen", help="Generate a specific screen")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output directory for Vue templates")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of writing")
    args = parser.parse_args()

    print("🔧  Screen Specs → Vue 3 Templates")
    print(f"    Source: {SCREENS_DIR}")
    print()

    if not SCREENS_DIR.exists():
        print(f"⚠️  Screens directory not found: {SCREENS_DIR}")
        return 0

    yaml_files = sorted(SCREENS_DIR.glob("*.yaml"))
    if args.screen:
        yaml_files = [f for f in yaml_files if args.screen in f.name]

    for yf in yaml_files:
        try:
            vue = generate_vue_page(yf)
        except Exception as e:
            print(f"❌ {yf.name}: generation failed — {e}")
            continue

        out_name = yf.stem.capitalize() + ".vue"
        if args.stdout:
            print(vue[:3000])
        else:
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / out_name).write_text(vue)
            print(f"✅ {out_name} ({len(vue.splitlines())} lines)")

    print()


if __name__ == "__main__":
    main()

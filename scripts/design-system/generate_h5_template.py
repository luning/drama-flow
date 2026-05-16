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

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
SCREENS_DIR = ROOT / "design-system" / "specs" / "screens"
DEFAULT_OUTPUT = ROOT / "h5" / "src" / "pages"

COMPONENT_VUE_MAP = {
    "app-bar": "header",
    "continue-watching-card": "ContinueWatchingCard",
    "banner-carousel": "BannerCarousel",
    "category-tabs": "CategoryTabs",
    "drama-grid": "DramaCard",
    "detail-header": "DetailHeader",
    "detail-body": "DetailBody",
    "tabs": "EpisodeTabs",
    "episode-list": "EpisodeItem",
}

VUE_TEMPLATE = """<!--
  {title}.vue — Auto-generated from specs/screens/{screen}.yaml
  DO NOT EDIT MANUALLY. Modify the screen spec instead.
-->
<script setup lang="ts">
import {{ ref, onMounted }} from 'vue'
import {{ useRouter }} from 'vue-router'
import {{ use{store_name} }} from '@/stores/{store_file}'
{imports}

const router = useRouter()
const store = use{store_name}()
const loading = ref(true)
{reactive_state}

onMounted(async () => {{
  loading.value = true
  try {{
{fetches}
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


def generate_vue_page(yaml_path: Path) -> str:
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    screen = spec["screen"]
    screen_title = spec.get("title", screen.capitalize())
    sections = spec.get("sections", [])

    store_name = screen.capitalize()
    store_file = screen.lower()

    imports = []
    template_lines = []
    reactive_state = []
    fetches = []

    for section in sections:
        comp = section["component"]
        sid = section.get("id", "")
        data_src = section.get("data", "static")
        vue_comp = COMPONENT_VUE_MAP.get(comp)

        if not vue_comp:
            continue

        if data_src != "static" and data_src != "none":
            method = f"fetch{sid.replace('-', ' ').title().replace(' ', '')}"
            imports.append(f"import {{ fetch{method} }} from '@/api/{store_file}'")
            fetches.append(f"    await store.{method}()")
            reactive_state.append(f"const {sid.replace('-', '_')} = ref([])")

        if comp == "app-bar":
            template_lines.append(f'    <header class="app-bar">')
            template_lines.append(f'      <h1>{{{{ title }}}}</h1>')
            template_lines.append(f'    </header>')
        elif comp == "drama-grid":
            template_lines.append(f'    <div class="drama-grid">')
            template_lines.append(f'      <div class="drama-card" v-for="item in store.dramas" :key="item.id"')
            template_lines.append(f'           @click="router.push(\'/detail/\' + item.id)">')
            template_lines.append(f'        <div class="thumb"><span class="badge">{{{{ item.tag }}}}</span></div>')
            template_lines.append(f'        <div class="info">')
            template_lines.append(f'          <h4>{{{{ item.title }}}}</h4>')
            template_lines.append(f'          <div class="rating">★ {{{{ item.rating }}}}</div>')
            template_lines.append(f'        </div>')
            template_lines.append(f'      </div>')
            template_lines.append(f'    </div>')
        elif comp == "category-tabs":
            template_lines.append(f'    <CategoryTabs v-model="activeCategory" :items="store.categories" />')
        elif comp == "banner-carousel":
            template_lines.append(f'    <BannerCarousel :items="store.banners" />')
        elif comp == "continue-watching-card":
            template_lines.append(f'    <ContinueWatchingCard :items="store.continueWatching" />')
        elif comp == "episode-list":
            template_lines.append(f'    <div class="episode-list">')
            template_lines.append(f'      <div class="episode-item" v-for="ep in store.episodes" :key="ep.num"')
            template_lines.append(f'           @click="router.push(\'/player/\' + ep.num)">')
            template_lines.append(f'        <span class="number">{{{{ ep.num }}}}</span>')
            template_lines.append(f'        <div class="info">')
            template_lines.append(f'          <div class="title">{{{{ ep.title }}}}</div>')
            template_lines.append(f'        </div>')
            template_lines.append(f'      </div>')
            template_lines.append(f'    </div>')
        else:
            # Generic placeholder for undefined components
            template_lines.append(f'    <!-- @component: {comp} (template not yet defined) -->')

    return VUE_TEMPLATE.format(
        title=screen_title,
        screen=screen,
        store_name=store_name,
        store_file=store_file,
        imports="\n".join(imports) if imports else "// No API imports needed (static content)",
        reactive_state="\n".join(reactive_state) if reactive_state else "",
        fetches="\n".join(fetches) if fetches else "    // Static content — no data fetch",
        template_content="\n".join(template_lines) or "    <!-- No sections defined -->",
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

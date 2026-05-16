"""
Design System Scripts

Pipeline:
  Figma → (figma_sync_*.py) → design-system/*.yaml → (generate_*.py) → platform exports

Directory:
  figma_sync_tokens.py     — Figma Tokens Studio export → tokens/tokens.css + tokens/tokens.ts
  figma_sync_components.py — Figma REST API → components/components.yaml
  figma_sync_screens.py    — Figma REST API (auto-layout pages) → specs/screens/*.yaml
  generate_css.py          — components.yaml → components/components.css
  generate_android.py      — components.yaml → exports/android/
  generate_prototype.py    — screen specs → prototype HTML pages
  generate_h5_template.py  — screen specs → H5 Vue page templates
  validate.py              — Validate that all design-system files are internally consistent
"""

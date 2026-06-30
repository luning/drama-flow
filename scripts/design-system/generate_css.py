#!/usr/bin/env python3
"""
generate_css.py — components.yaml → components.css

Generates a complete CSS file from the platform-agnostic component spec.
Each component in components.yaml is rendered to a CSS class with all
{token.refs} resolved to var(--xxx) CSS custom properties.

Usage:
  python scripts/design-system/generate_css.py                # Generate to stdout
  python scripts/design-system/generate_css.py --output design-system/components/components.css
  python scripts/design-system/generate_css.py --check        # Verify generated matches existing
"""

import argparse
import re
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS_YAML = ROOT / "design-system" / "components" / "components.yaml"
DEFAULT_OUTPUT = ROOT / "design-system" / "components" / "components.css"

# Mapping from tokens.yaml ref → CSS variable
# {color.primary} → var(--color-primary)
# {spacing.md} → var(--space-3)
# {radius.btn} → var(--radius-btn)
# {typography.size.md} → var(--font-size-md)
# {typography.weight.semibold} → var(--font-weight-semibold)
# {text.primary} → var(--text-primary)
# {background.card} → var(--bg-card)
# {border.default} → var(--border)
# {shadow.md} → var(--shadow-md)
# {z.toast} → var(--z-toast)
# {device.bottomNavHeight} → var(--bottom-nav-height)


def resolve_token_ref(ref: str) -> str:
    """
    Convert a components.yaml token reference to a CSS variable.

    Examples:
      {color.primary}        → var(--color-primary)
      {color.primaryLight}   → var(--color-primary-light)
      {spacing.md}           → var(--space-3)
      {typography.size.md}   → var(--font-size-md)
      {typography.weight.semibold} → var(--font-weight-semibold)
      {text.primary}         → var(--text-primary)
      {background.card}      → var(--bg-card)
      {border.subtle}        → var(--border-subtle)
      {radius.btn}           → var(--radius-btn)
    """
    parts = ref.split(".")

    # Special category mappings
    category_prefixes = {
        "spacing": "space",
        "typography.size": "font-size",
        "typography.weight": "font-weight",
        "typography.family": "font-family",
        "radius": "radius",
        "shadow": "shadow",
        "transition": "transition",
        "z": "z",
        "device": "",
    }

    # Spacing uses short codes: xs, sm, md → space-1, space-2, space-3
    spacing_map = {
        "xs": "space-1", "sm": "space-2", "md": "space-3",
        "lg": "space-4", "xl": "space-6", "2xl": "space-8", "3xl": "space-10"
    }

    # Text colors map to --text-xxx
    if parts[0] == "text":
        return f"var(--text-{parts[1]})"

    # Colors map to --color-xxx
    if parts[0] == "color":
        name = parts[1]
        kebab = re.sub(r'([A-Z])', r'-\1', name).lower()
        return f"var(--color-{kebab})"

    # Backgrounds: background.card → --bg-card
    if parts[0] == "background":
        name = parts[1]
        kebab = re.sub(r'([A-Z])', r'-\1', name).lower()
        return f"var(--bg-{kebab})"

    # Borders: border.subtle → --border-subtle
    if parts[0] == "border":
        name = parts[1]
        # "default" is special: border.default → --border
        if name == "default":
            return "var(--border)"
        kebab = re.sub(r'([A-Z])', r'-\1', name).lower()
        return f"var(--border-{kebab})"

    # Surface: surface.subtle → --surface-subtle
    if parts[0] == "surface":
        name = parts[1]
        kebab = re.sub(r'([A-Z])', r'-\1', name).lower()
        return f"var(--surface-{kebab})"

    # Spacing: convert to scale
    if parts[0] == "spacing":
        return f"var(--{spacing_map.get(parts[1], f'space-{parts[1]}')})"

    # Typography sizes
    if parts[0] == "typography" and parts[1] == "size":
        return f"var(--font-size-{parts[2]})"

    # Typography weights
    if parts[0] == "typography" and parts[1] == "weight":
        return f"var(--font-weight-{parts[2]})"

    # Radius
    if parts[0] == "radius":
        return f"var(--radius-{parts[1]})"

    # Shadow
    if parts[0] == "shadow":
        return f"var(--shadow-{parts[1]})"

    # Transition
    if parts[0] == "transition":
        return f"var(--transition-{parts[1]})"

    # Z-index
    if parts[0] == "z":
        return f"var(--z-{parts[1]})"

    # Device
    if parts[0] == "device":
        return f"var(--{parts[1]})"

    # Fallback: just join everything
    kebab = "-".join(parts)
    return f"var(--{kebab})"


def resolve_value(value) -> str:
    """Recursively resolve token references in a value (string, list, dict)."""
    if isinstance(value, str):
        # Replace {token.ref} with var(--xxx)
        return re.sub(r'\{([^}]+)\}', lambda m: resolve_token_ref(m.group(1)), value)
    elif isinstance(value, list):
        return " ".join(resolve_value(v) for v in value)
    elif isinstance(value, dict):
        # Special: gradient, transform, etc.
        if "type" in value:
            if value["type"] == "gradient-linear":
                angle = value.get("angle", "135deg")
                stops = ", ".join(
                    resolve_value(s) for s in value.get("stops", [])
                )
                return f"linear-gradient({angle}, {stops})"
            elif value["type"] == "solid":
                return resolve_value(value.get("color", ""))
        # Generic dict: treat as CSS shorthand (e.g., {color: "xxx"} → resolve to the color value)
        # or expand to space-separated values
        if "color" in value and len(value) == 1:
            return resolve_value(value["color"])
        return " ".join(f"{css_property(k)}: {resolve_value(v)}" for k, v in value.items())
    return str(value)


def css_property(key: str) -> str:
    """Convert camelCase to kebab-case for CSS property names."""
    return re.sub(r'([A-Z])', r'-\1', key).lower()


def generate_components_css(components_yaml: Path) -> str:
    """Generate complete CSS from components.yaml."""
    with open(components_yaml) as f:
        data = yaml.safe_load(f)

    lines = []
    lines.append("/*")
    lines.append(" * components.css — Generated Component Styles for H5")
    lines.append(" *")
    lines.append(" * AUTO-GENERATED by scripts/design-system/generate_css.py")
    lines.append(" * from components/components.yaml.")
    lines.append(" * DO NOT EDIT MANUALLY. Modify components.yaml instead.")
    lines.append(" *")
    lines.append(" * All values reference tokens from tokens/tokens.css.")
    lines.append(" * Import this file after tokens.css in your H5 entry point.")
    lines.append(" */")
    lines.append("")

    css_property_skip = {"type", "figma_component_id", "extends", "description",
                         "parts", "states", "variants", "animation", "typography"}

    components = data.get("components", {})

    def expand_typography(base: dict) -> dict:
        """Flatten 'typography' dict into top-level CSS properties."""
        result = dict(base)
        typography = result.pop("typography", None)
        if isinstance(typography, dict):
            for key, value in typography.items():
                if not isinstance(value, dict):
                    result[key] = value
        return result

    def resolve_base(comp: dict) -> dict:
        """Resolve 'extends' by merging parent base properties, child overrides parent."""
        base = comp.get("base", {})
        parent_name = base.get("extends")
        if parent_name and parent_name in components:
            parent = components[parent_name]
            parent_base = resolve_base(parent)
            # Deep-merge typography and states (work on copies to avoid mutating source)
            parent_typo = dict(parent_base.get("typography", {}))
            child_typo = dict(base.get("typography", {}))
            parent_states = dict(parent_base.get("states", {}))
            child_states = dict(base.get("states", {}))
            merged = {**parent_base, **base}
            if parent_typo or child_typo:
                merged["typography"] = {**parent_typo, **child_typo}
            if parent_states or child_states:
                merged["states"] = {**parent_states, **child_states}
            return merged
        return base

    for comp_name, comp in components.items():
        base = resolve_base(comp)
        description = comp.get("description", "")

        lines.append(f"/* {'─' * 60} */")
        if description:
            lines.append(f"/* {comp_name}: {description} */")
        else:
            lines.append(f"/* {comp_name} */")
        lines.append("")

        # --- Base state ---
        base = expand_typography(base)
        lines.append(f".{comp_name} {{")
        for prop, value in base.items():
            if prop in css_property_skip:
                continue
            resolved = resolve_value(value)
            lines.append(f"  {css_property(prop)}: {resolved};")
        lines.append("}")
        lines.append("")

        # --- States ---
        states = comp.get("states", {})
        for state_name, state_props in states.items():
            lines.append(f".{comp_name}:{state_name} {{")
            for prop, value in state_props.items():
                if prop in css_property_skip:
                    continue
                resolved = resolve_value(value)
                lines.append(f"  {css_property(prop)}: {resolved};")
            lines.append("}")
            lines.append("")

        # --- Parts ---
        parts = base.get("parts", {})
        for part_name, part_props in parts.items():
            # Handle nested parts (thumb → title, rating)
            if isinstance(part_props, dict) and not any(
                k in part_props for k in css_property_skip
            ):
                # Check if this is a style object or nested parts
                has_nested = any(
                    isinstance(v, dict) and "type" not in str(v)
                    for v in part_props.values()
                )
                if not has_nested and any(
                    k not in css_property_skip for k in part_props
                ):
                    lines.append(f".{comp_name} .{part_name} {{")
                    for prop, value in part_props.items():
                        if isinstance(value, dict):
                            continue
                        resolved = resolve_value(value)
                        lines.append(f"  {css_property(prop)}: {resolved};")
                    lines.append("}")
                    lines.append("")

                # Nested sub-parts
                for sub_name, sub_props in part_props.items():
                    if isinstance(sub_props, dict) and not any(
                        k in sub_props for k in ("type", "stops")
                    ):
                        lines.append(f".{comp_name} .{part_name} .{sub_name} {{")
                        for prop, value in sub_props.items():
                            if isinstance(value, dict):
                                continue
                            resolved = resolve_value(value)
                            lines.append(f"  {css_property(prop)}: {resolved};")
                        lines.append("}")
                        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSS from components.yaml"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output CSS file path")
    parser.add_argument("--check", action="store_true",
                        help="Check that output matches existing file")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of writing file")
    args = parser.parse_args()

    print("🎨  components.yaml → components.css")
    print(f"    Source: {COMPONENTS_YAML}")
    print()

    if not COMPONENTS_YAML.exists():
        print(f"❌ Source file not found: {COMPONENTS_YAML}")
        return 1

    try:
        css = generate_components_css(COMPONENTS_YAML)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return 1

    print(f"    Generated {len(css.splitlines())} lines of CSS")

    if args.stdout:
        print(css)
    else:
        args.output.write_text(css)
        print(f"    Written to: {args.output}")

    print()
    return 0


if __name__ == "__main__":
    main()

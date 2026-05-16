"""
Compliance Check Scripts

Multi-layer automated checking for design-system compliance:
  check_tokens.py     — Layer 1: No hardcoded colors, correct CSS variable names
  check_constraints.py — Layer 2: Business rule compliance (one primary button, etc.)
  check_components.py  — Layer 3: Component usage patterns (right class names, proper nesting)

Run all checks:
  python scripts/check/check_tokens.py
  python scripts/check/check_constraints.py
  python scripts/check/check_components.py

Or use the unified entry point:
  python scripts/check/ --all
"""

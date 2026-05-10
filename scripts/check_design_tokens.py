#!/usr/bin/env python3
"""
check_design_tokens.py — DramaFlow Design Token 合规检查

扫描前端文件中的 hardcoded CSS 色值，确保代码引用 Design Token（CSS 变量）。
Token 映射从 design-system/tokens.css 动态解析，无需手工维护。

用法:
  python scripts/check_design_tokens.py               # 检查默认目录
  python scripts/check_design_tokens.py --path h5/src # 检查指定目录
  python scripts/check_design_tokens.py --strict       # 严格模式（警告也报错）
退出码:
  0  全部通过
  1  发现违规（CI 可用此判断是否拦截）
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# ── Token 定义文件（跳过，这里允许出现原始色值）────────────────────
SKIP_FILES = {
    'design-system/tokens.css',
    'design-system/tokens.ts',
}

# ── 扫描文件类型 ───────────────────────────────────────────────────
TARGET_EXTENSIONS = {'.html', '.vue', '.css', '.scss'}

# ── 正则：匹配 hex 色值 ─────────────────────────────────────────────
CSS_HEX_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
# 匹配 tokens.css 变量定义：--var-name: #hexval;
TOKEN_DEF_RE = re.compile(r'--([a-z][a-z0-9-]*):\s*(#[0-9a-fA-F]{3,8})\b')

# ── 跳过的行模式 ───────────────────────────────────────────────────
SKIP_LINE_PATTERNS = [
    re.compile(r'^\s*--[a-z]'),          # CSS 变量定义行（--color-primary: #6C5CE7）
    re.compile(r'//\s'),                  # JS 单行注释
    re.compile(r'/\*|\*/'),               # CSS/JS 多行注释
    re.compile(r'<!--'),                  # HTML 注释
    re.compile(r"color:\s*'#"),           # JS 对象中的色值数据（如 DRAMAS 数组）
    re.compile(r'color:\s*"#'),           # 同上，双引号
    re.compile(r'fill="%23'),             # SVG data URI 编码色
    re.compile(r'href=|src='),            # 资源路径（可能含 # anchor）
]


def load_token_map(tokens_css: Path = Path('design-system/tokens.css')) -> dict[str, str]:
    """解析 tokens.css，返回 hex → var(--name) 映射（大小写均注册）。"""
    token_map: dict[str, str] = {}
    if not tokens_css.exists():
        print(f'⚠️  未找到 {tokens_css}，无法提供修复建议（不影响检查）')
        return token_map
    content = tokens_css.read_text(encoding='utf-8')
    for match in TOKEN_DEF_RE.finditer(content):
        var_name, hex_val = match.group(1), match.group(2)
        css_var = f'var(--{var_name})'
        token_map[hex_val.lower()] = css_var
        token_map[hex_val.upper()] = css_var
        token_map[hex_val] = css_var
    return token_map


def should_skip_line(line: str) -> bool:
    return any(p.search(line) for p in SKIP_LINE_PATTERNS)


def find_violations(path: Path, token_map: dict[str, str]) -> list[dict]:
    """返回文件中的 hardcoded 色值违规列表"""
    rel_str = str(path)
    if any(skip in rel_str for skip in SKIP_FILES):
        return []
    if path.suffix not in TARGET_EXTENSIONS:
        return []
    try:
        content = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return []

    violations = []
    for lineno, line in enumerate(content.splitlines(), 1):
        if should_skip_line(line):
            continue
        for match in CSS_HEX_RE.finditer(line):
            raw_color = '#' + match.group(1)
            if 'var(' in line[:match.start()]:
                continue
            suggestion = token_map.get(raw_color) or token_map.get(raw_color.lower())
            violations.append({
                'file': rel_str,
                'line': lineno,
                'color': raw_color,
                'suggestion': suggestion,
                'context': line.strip()[:120],
            })
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description='扫描 hardcoded 色值，确保代码引用 Design Token'
    )
    parser.add_argument(
        '--path', nargs='+',
        default=['prototype', 'h5/src'],
        help='扫描目录（默认: prototype h5/src）'
    )
    parser.add_argument(
        '--strict', action='store_true',
        help='严格模式：未知色值（无对应 Token）也报错'
    )
    args = parser.parse_args()

    token_map = load_token_map()

    all_violations: list[dict] = []
    files_checked = 0

    for dir_str in args.path:
        p = Path(dir_str)
        if not p.exists():
            continue
        for file_path in sorted(p.rglob('*')):
            if file_path.is_file() and file_path.suffix in TARGET_EXTENSIONS:
                files_checked += 1
                all_violations.extend(find_violations(file_path, token_map))

    print()
    print('🔍  DramaFlow Design Token 合规检查')
    print(f'    扫描路径: {" ".join(args.path)}')
    print(f'    文件数量: {files_checked}  Token 数量: {len(set(token_map.values()))}')
    print()

    if not all_violations:
        print('✅  全部通过！0 个 hardcoded 色值')
        print()
        return 0

    by_file: dict[str, list[dict]] = defaultdict(list)
    for v in all_violations:
        by_file[v['file']].append(v)

    for file_path, violations in sorted(by_file.items()):
        print(f'❌  {file_path}')
        for v in violations:
            fix = f'→  {v["suggestion"]}' if v['suggestion'] else '→  （无对应 Token，请在 tokens.css 中新增）'
            print(f'    L{v["line"]:<5} {v["color"]:<12} {fix}')
            print(f'           {v["context"][:80]}')
        print()

    known = sum(1 for v in all_violations if v['suggestion'])
    unknown = len(all_violations) - known
    print(f'⚠️   共 {len(all_violations)} 处 hardcoded 色值')
    print(f'    · 有对应 Token（可自动替换）: {known} 处')
    print(f'    · 无对应 Token（需新增或审查）: {unknown} 处')
    print()
    print('    修复方式：将 #color 替换为对应 CSS 变量，参考 design-system/tokens.css')
    print()

    if args.strict:
        return 1
    return 1 if known > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

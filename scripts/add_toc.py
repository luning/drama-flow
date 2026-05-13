#!/usr/bin/env python3
"""为知识点目录中的 md 文件自动添加目录，已有目录则删除后重建"""

import re
import os

DIR = os.path.join(os.path.dirname(__file__), "..", "training_doc", "知识点")


def slugify(text: str) -> str:
    """生成锚点 ID：只保留 Unicode 文字字符，其余去除，空格换连字符"""
    text = text.strip()
    # 去掉 markdown 格式符号（只保留文字）
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 保留下划线（常见于变量名），其余非字母非空白字符移除
    # \w 在 re.UNICODE 下包括所有 Unicode 字母/数字/下划线 + 中文
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    text = text.strip()
    # 空白 → 连字符
    text = re.sub(r'\s+', '-', text)
    # 合并连续连字符
    text = re.sub(r'-{2,}', '-', text)
    return text.lower()


def count_fences(lines: list[str]) -> int:
    """统计代码围栏行数，用于配对检查"""
    return sum(1 for line in lines if line.strip().startswith("```"))


def extract_headings(lines: list[str]) -> list[tuple[int, str, str]]:
    """提取所有 h2 / h3 标题（跳过代码块内的）"""
    headings = []
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            headings.append((3, text, slugify(text)))
        elif stripped.startswith("## "):
            text = stripped[3:].strip()
            headings.append((2, text, slugify(text)))
    return headings


def generate_toc(headings: list[tuple[int, str, str]]) -> str:
    """生成目录：h2 用编号，h3 用破折号缩进"""
    result = ["## 目录", ""]
    h2_counter = 0
    for level, text, anchor in headings:
        if level == 2:
            h2_counter += 1
            result.append(f"{h2_counter}. [{text}](#{anchor})")
        else:
            result.append(f"   - [{text}](#{anchor})")
    result.append("")
    result.append("---")
    result.append("")
    return "\n".join(result)


def remove_existing_toc(lines: list[str]) -> list[str]:
    """如果已有目录块（## 目录 ... ---），整块删除"""
    toc_start = None
    toc_end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## 目录":
            toc_start = i
        if toc_start is not None and stripped == "---" and i > toc_start:
            toc_end = i
            break

    if toc_start is None:
        return lines  # 没有目录，原样返回

    # 删除目录块前后的空行
    while toc_start > 0 and lines[toc_start - 1].strip() == "":
        toc_start -= 1
    # 向后：删除 toc_end 后面的空行
    while toc_end + 1 < len(lines) and lines[toc_end + 1].strip() == "":
        toc_end += 1
    # 向后：如果后面紧跟原始文件的 ---（h1 下原有的水平线），一并删除
    if toc_end + 1 < len(lines) and lines[toc_end + 1].strip() == "---":
        toc_end += 1
        while toc_end + 1 < len(lines) and lines[toc_end + 1].strip() == "":
            toc_end += 1

    return lines[:toc_start] + lines[toc_end + 1:]


def insert_toc(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_lines = content.split("\n")

    # 检查代码围栏是否成对，奇数则报错跳过，等待人工修复
    if count_fences(original_lines) % 2 != 0:
        print(f"  [ERROR] {os.path.basename(filepath)} — 代码围栏（```）不成对，请先修复")
        return False

    # 先删除已有目录
    lines = remove_existing_toc(original_lines)

    headings = extract_headings(lines)
    if not headings:
        print(f"  [SKIP] {os.path.basename(filepath)} — 无标题")
        return False

    toc = generate_toc(headings)

    # 在第一个 h1 标题行之后插入目录
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and re.match(r'^# [^#]', line.strip()):
            # 确保 h1 后面有空行
            new_lines.append("")
            new_lines.append(toc)
            inserted = True

    if not inserted:
        print(f"  [SKIP] {os.path.basename(filepath)} — 未找到 h1 标题")
        return False

    new_content = "\n".join(new_lines)
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  [DONE] {os.path.basename(filepath)} — {len(headings)} 条目录项")
    else:
        print(f"  [SAME] {os.path.basename(filepath)} — 目录无变化")
    return True


def main():
    count = 0
    for fname in sorted(os.listdir(DIR)):
        if fname.endswith(".md"):
            fpath = os.path.join(DIR, fname)
            if insert_toc(fpath):
                count += 1
    print(f"\n完成：处理了 {count} 个文件")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""检查 Markdown 文件翻译覆盖率.

用法:
    python3 tests/e2e/check-markdown-translation-coverage.py
    python3 tests/e2e/check-markdown-translation-coverage.py --detailed
"""

import re
import sys
from pathlib import Path
import argparse
from dataclasses import dataclass
from typing import List


@dataclass
class FileCheckResult:
    """单个文件的检查结果."""
    path: Path
    total_lines: int
    chinese_lines: int
    english_lines: int
    is_translated: bool
    coverage: float


# 需要检查翻译的目录
CHECK_DIRECTORIES = [
    "templates/commands",
    "templates",
    "docs",
    "memory",
    "presets",
    "extensions",
]

# 排除的文件模式
EXCLUDE_PATTERNS = [
    r".*\.json$",
    r".*catalog\.json$",
    r".*catalog\.community\.json$",
    r".*\.yml$",
    r".*\.yaml$",
]

# 指示翻译质量的关键指标
# 如果文件包含这些中文短语，很可能已翻译
CHINESE_INDICATORS = [
    "用户输入",
    "概述",
    "执行步骤",
    "目标",
    "功能描述",
    "规范",
    "实现",
    "任务",
    "计划",
    "注意",
    "重要",
    "警告",
    "提示",
    "示例",
    "说明",
]

# 模板占位符标记 - 这些文件通常包含大量占位符
TEMPLATE_PLACEHOLDERS = [
    "[项目名称]",
    "[功能名称]",
    "[日期]",
    "[检查清单类型]",
    "[类别",
    "[摘要]",
    "[详情",
]


def should_exclude(filepath: Path) -> bool:
    """检查文件是否应该被排除."""
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, filepath.name):
            return True
    return False


def is_template_placeholder_file(content: str) -> bool:
    """判断是否为模板占位符文件."""
    # 如果包含大量方括号占位符，可能是模板文件
    placeholder_count = len(re.findall(r'\[.*?\]', content))
    return placeholder_count > 5


def analyze_file(filepath: Path) -> FileCheckResult:
    """分析单个文件的翻译情况."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return FileCheckResult(
            path=filepath,
            total_lines=0,
            chinese_lines=0,
            english_lines=0,
            is_translated=False,
            coverage=0.0
        )

    lines = content.split('\n')
    total_lines = len(lines)
    chinese_lines = 0
    english_lines = 0
    code_block_lines = 0

    in_code_block = False

    # 统计包含中文字符和英文字符的行
    for line in lines:
        # 检测代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            code_block_lines += 1
            continue

        if in_code_block:
            code_block_lines += 1
            continue

        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', line))
        has_english = bool(re.search(r'[a-zA-Z]{3,}', line))  # 至少3个字母

        if has_chinese:
            chinese_lines += 1
        elif has_english:
            english_lines += 1

    # 计算非代码行的覆盖率
    non_code_lines = total_lines - code_block_lines
    if non_code_lines > 0:
        coverage = chinese_lines / non_code_lines * 100
    else:
        coverage = 100.0 if chinese_lines > 0 else 0.0

    # 检查是否包含中文指示词
    has_chinese_indicators = any(
        indicator in content for indicator in CHINESE_INDICATORS
    )

    # 检查是否为模板占位符文件
    is_template = is_template_placeholder_file(content)

    # 检查是否标题已经是中文
    chinese_title = bool(re.search(r'^#+\s+[\u4e00-\u9fff]', content, re.MULTILINE))

    # 判断是否已翻译的逻辑：
    # 1. 如果有中文指示词且覆盖率 > 15%（降低阈值，排除代码块影响）
    # 2. 或者是模板占位符文件且包含中文
    # 3. 或者中文行数 > 3 且标题是中文
    is_translated = (
        (has_chinese_indicators and coverage > 15) or
        (is_template and chinese_lines > 3) or
        (chinese_lines > 3 and chinese_title)
    )

    return FileCheckResult(
        path=filepath,
        total_lines=total_lines,
        chinese_lines=chinese_lines,
        english_lines=english_lines,
        is_translated=is_translated,
        coverage=coverage
    )


def scan_directory(dir_path: Path) -> List[FileCheckResult]:
    """扫描目录中的所有 Markdown 文件."""
    results = []

    if not dir_path.exists():
        return results

    for md_file in dir_path.rglob("*.md"):
        if should_exclude(md_file):
            continue
        result = analyze_file(md_file)
        results.append(result)

    return results


def print_summary(results: List[FileCheckResult], detailed: bool = False):
    """打印检查摘要."""
    if not results:
        print("  未找到 Markdown 文件")
        return

    translated = [r for r in results if r.is_translated]
    untranslated = [r for r in results if not r.is_translated]

    print(f"  总文件数: {len(results)}")
    print(f"  已翻译: {len(translated)} ({len(translated)/len(results)*100:.1f}%)")
    print(f"  未翻译/需更新: {len(untranslated)} ({len(untranslated)/len(results)*100:.1f}%)")

    if detailed and untranslated:
        print()
        print("  未翻译文件列表:")
        for r in sorted(untranslated, key=lambda x: str(x.path)):
            print(f"    - {r.path} (覆盖率: {r.coverage:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="检查 Markdown 文件翻译覆盖率"
    )
    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="显示详细的未翻译文件列表"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=30.0,
        help="翻译覆盖率阈值 (默认: 30%%)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  Markdown 翻译覆盖率检查")
    print("=" * 70)
    print()

    all_results = []

    for dir_name in CHECK_DIRECTORIES:
        dir_path = Path(dir_name)
        results = scan_directory(dir_path)

        if results:
            print(f"📁 {dir_name}/")
            print_summary(results, args.detailed)
            print()
            all_results.extend(results)

    # 总体统计
    if all_results:
        print("=" * 70)
        print("  总体统计")
        print("=" * 70)
        print()

        total = len(all_results)
        translated = len([r for r in all_results if r.is_translated])
        untranslated = total - translated

        print(f"  总文件数: {total}")
        print(f"  已翻译: {translated} ({translated/total*100:.1f}%)")
        print(f"  需翻译: {untranslated} ({untranslated/total*100:.1f}%)")
        print()

        if untranslated > 0:
            print("=" * 70)
            print("  需翻译的文件:")
            print("=" * 70)
            print()
            for r in sorted(
                [r for r in all_results if not r.is_translated],
                key=lambda x: str(x.path)
            ):
                print(f"  - {r.path}")
            print()
            return 1
    else:
        print("  未找到需要检查的文件")

    print("✅ 所有 Markdown 文件已达到翻译覆盖率要求!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

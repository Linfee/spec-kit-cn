#!/usr/bin/env python3
"""检查 yaml.dump/yaml.safe_dump 调用是否包含 allow_unicode=True.

用法:
    python3 tests/e2e/check-yaml-unicode.py
    python3 tests/e2e/check-yaml-unicode.py --fix
"""

import re
import sys
from pathlib import Path
import argparse


def find_yaml_dump_calls(filepath):
    """查找文件中的 yaml.dump 调用."""
    content = filepath.read_text(encoding='utf-8')
    issues = []

    # 匹配 yaml.dump 或 yaml.safe_dump 调用
    pattern = r'yaml\.(safe_)?dump\(([^)]+)\)'

    for match in re.finditer(pattern, content):
        full_match = match.group(0)
        args = match.group(2)
        line_num = content[:match.start()].count('\n') + 1

        # 检查是否包含 allow_unicode
        if 'allow_unicode' not in args:
            issues.append({
                'line': line_num,
                'code': full_match,
                'args': args.strip()
            })

    return issues


def check_file(filepath):
    """检查单个文件."""
    issues = find_yaml_dump_calls(filepath)
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="检查 yaml.dump 调用是否包含 allow_unicode=True"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="尝试自动修复 (谨慎使用)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  YAML Unicode 检查")
    print("=" * 60)
    print()
    print("检查目标: src/specify_cli/ 目录下的所有 Python 文件")
    print("检查规则: yaml.dump() 和 yaml.safe_dump() 必须包含 allow_unicode=True")
    print()

    src_dir = Path("src/specify_cli")
    if not src_dir.exists():
        print(f"❌ 目录不存在: {src_dir}")
        return 1

    all_issues = []
    py_files = list(src_dir.rglob("*.py"))

    print(f"扫描文件数: {len(py_files)}")
    print()

    for pyfile in py_files:
        issues = check_file(pyfile)
        if issues:
            for issue in issues:
                all_issues.append({
                    'file': pyfile,
                    'line': issue['line'],
                    'code': issue['code'],
                    'args': issue['args']
                })

    if all_issues:
        print(f"发现 {len(all_issues)} 个问题:")
        print()

        for issue in all_issues:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     代码: {issue['code'][:60]}...")
            print()

        print("=" * 60)
        print("  修复方法:")
        print("=" * 60)
        print()
        print("  将以下代码:")
        print('    yaml.dump(data, f)')
        print("  修改为:")
        print('    yaml.dump(data, f, allow_unicode=True)')
        print()
        print("  或将:")
        print('    yaml.safe_dump(data, f)')
        print("  修改为:")
        print('    yaml.safe_dump(data, f, allow_unicode=True)')
        print()
        print("  为什么要这样做?")
        print("  - yaml 库默认会将非 ASCII 字符转义为 \\uXXXX 格式")
        print("  - allow_unicode=True 保证中文原样输出")
        print()

        return 1

    print("✅ 所有 yaml.dump 调用都包含 allow_unicode=True")
    print()
    print(f"扫描完成: {len(py_files)} 个文件通过检查")
    return 0


if __name__ == "__main__":
    sys.exit(main())

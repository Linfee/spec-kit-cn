#!/usr/bin/env python3
"""检查 CLI help 输出是否包含未翻译的英文内容.

用法:
    python3 tests/e2e/check-cli-help-localization.py
    python3 tests/e2e/check-cli-help-localization.py --verbose
"""

import subprocess
import sys
import argparse


# 必须翻译的框架标签
REQUIRED_LABELS = ["用法:", "参数", "选项", "命令", "显示此帮助信息并退出。"]

# 必须检查的命令
COMMANDS = [
    ["specify-cn", "--help"],
    ["specify-cn", "init", "--help"],
    ["specify-cn", "preset", "--help"],
    ["specify-cn", "preset", "add", "--help"],
    ["specify-cn", "preset", "remove", "--help"],
    ["specify-cn", "extension", "--help"],
    ["specify-cn", "extension", "add", "--help"],
    ["specify-cn", "extension", "remove", "--help"],
    ["specify-cn", "check", "--help"],
    ["specify-cn", "version", "--help"],
]

# 禁止出现的未翻译英文标签
FORBIDDEN_LABELS = [
    "Usage:",
    "Arguments",
    "Options",
    "Commands",
    "Show this message and exit.",
]


def run_help_command(cmd):
    """运行 help 命令并捕获输出."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout, None
    except subprocess.CalledProcessError as e:
        return None, f"命令执行失败: {' '.join(cmd)} - {e}"
    except FileNotFoundError:
        return None, f"命令未找到: {cmd[0]} (请确保已安装 specify-cn-cli)"


def check_help_output(output, cmd, verbose=False):
    """检查 help 输出是否包含未翻译内容."""
    issues = []
    lines = output.split('\n')

    # 检查禁止的英文标签
    for forbidden in FORBIDDEN_LABELS:
        if forbidden in output:
            # 找到出现位置
            for i, line in enumerate(lines):
                if forbidden in line:
                    issues.append(f"  行 {i+1}: 发现未翻译标签 '{forbidden}'")
                    break

    # 检查是否缺少必需的中文标签
    for required in REQUIRED_LABELS:
        if required not in output:
            issues.append(f"  缺少必需的中文标签: '{required}'")

    # 检查成段的英文说明 (长度超过50字符的英文段落)
    english_pattern = re.compile(r'[a-zA-Z]{3,}')
    for i, line in enumerate(lines):
        # 跳过代码块、命令示例
        if line.strip().startswith('`') or line.strip().startswith('specify-cn'):
            continue
        # 检查是否包含较长的英文段落
        if len(line) > 50 and english_pattern.search(line):
            # 排除混合中英文的情况（中文为主）
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', line))
            english_chars = len(re.findall(r'[a-zA-Z]', line))
            if english_chars > chinese_chars * 2:  # 英文显著多于中文
                issues.append(f"  行 {i+1}: 可能包含未翻译的英文段落")

    if verbose:
        print(f"  检查 {' '.join(cmd)}...")
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ 通过")

    return len(issues) == 0, issues


def main():
    parser = argparse.ArgumentParser(
        description="检查 specify-cn CLI help 输出是否完全中文化"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  CLI Help 本地化检查")
    print("=" * 60)
    print()

    all_passed = True
    total_checks = 0
    failed_checks = 0

    for cmd in COMMANDS:
        total_checks += 1
        output, error = run_help_command(cmd)

        if error:
            print(f"❌ {' '.join(cmd)}")
            print(f"   错误: {error}")
            all_passed = False
            failed_checks += 1
            continue

        passed, issues = check_help_output(output, cmd, args.verbose)

        if not passed:
            all_passed = False
            failed_checks += 1
            if not args.verbose:
                print(f"❌ {' '.join(cmd)}")
                for issue in issues:
                    print(f"   {issue}")

    print()
    print("=" * 60)
    print(f"  检查结果: {total_checks - failed_checks}/{total_checks} 通过")
    print("=" * 60)

    if not all_passed:
        print()
        print("修复建议:")
        print("  1. 检查 src/specify_cli/__init__.py 中的 HELP_TEXT_TRANSLATIONS 字典")
        print("  2. 检查 COMMAND_HELP_TRANSLATIONS 字典")
        print("  3. 检查 PARAM_HELP_TRANSLATIONS 字典")
        print("  4. 确保所有 typer.Option/Argument 的 help 参数已翻译")
        return 1

    print()
    print("✅ 所有 CLI help 输出已完全中文化!")
    return 0


if __name__ == "__main__":
    import re
    sys.exit(main())

#!/usr/bin/env python3
"""校验 Spec Kit CN Markdown 翻译覆盖范围与疑似未翻译内容。

规则:
- 仅检查需要本地化的范围, 避免把项目内部规则/脚本文档混入翻译审查
- 对照源固定为 ./spec-kit
- 忽略 .claude/, tests/, CLAUDE.md, AGENTS.md, TRANSLATION_STANDARDS.md, TERMINOLOGY.md, CHANGELOG.md
- memory/constitution.md 已在上游移除, 不再纳入检查

退出码:
- 0: 覆盖率通过(即无原版缺失文件)
- 1: 存在原版文件缺失或基础环境问题
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_ROOT = ROOT / "spec-kit"

ROOT_TRANSLATION_FILES = [
    "README.md",
    "SUPPORT.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "spec-driven.md",
]
TRANSLATION_DIRS = [
    "docs",
    "templates",
    "presets",
    "extensions",
]
SUSPICIOUS_SCAN_ROOT_FILES = [
    "README.md",
    "SUPPORT.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "spec-driven.md",
]
SUSPICIOUS_SCAN_DIRS = [
    "docs",
    "templates",
]

IGNORE_LINE_PATTERNS = [
    r"https?://",
    r"`[^`]+`",
    r"\b(specify-cn|specify-cli|specify-cn-cli)\b",
    r"\b(GitHub|CLI|API|JSON|YAML|TOML|Markdown|PowerShell|Python|JavaScript|TypeScript|Mermaid)\b",
    r"\b(TODO|TKTK|N/A|NEEDS CLARIFICATION)\b",
    r"\[(PROJECT|PRINCIPLE|NEEDS CLARIFICATION)[^\]]*\]",
    r"\{ARGS\}|\$ARGUMENTS",
    r"\b(Claude|Gemini|Codex|Cursor|Windsurf|Qwen|Copilot|Auggie|Tabnine|Kimi|Trae|Amp|SHAI|IBM Bob|Amazon Q|Agy|Auggie CLI|Kilo Code|OpenCode|CodeBuddy|Roo)\b",
    r"\b(vibe-coding|Greenfield|Brownfield|UX|UI|IDE|VS Code|Linux/macOS/Windows|Bash/Zsh|Mercurial|SVN|monorepo)\b",
    r"(^|\s)[./][^\s]+",
]
IGNORE_LINE_RE = re.compile("|".join(IGNORE_LINE_PATTERNS))
ENGLISH_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+./'-]*")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CODE_FENCE_RE = re.compile(r"^```")
SUSPICIOUS_LINE_LIMIT = 80


@dataclass(frozen=True)
class ScanResult:
    matched: list[str]
    local_only: list[str]
    upstream_missing: list[str]
    suspicious_lines: list[str]


def iter_translation_files(base: Path) -> list[str]:
    files: list[str] = []

    for rel in ROOT_TRANSLATION_FILES:
        path = base / rel
        if path.is_file():
            files.append(rel)

    for rel_dir in TRANSLATION_DIRS:
        dir_path = base / rel_dir
        if not dir_path.is_dir():
            continue
        for path in sorted(dir_path.rglob("*.md")):
            files.append(path.relative_to(base).as_posix())

    return sorted(set(files))


def is_suspicious_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if IGNORE_LINE_RE.search(stripped):
        return False

    english_tokens = ENGLISH_TOKEN_RE.findall(stripped)
    if len(english_tokens) < 4:
        return False

    if CJK_RE.search(stripped):
        ascii_letters = sum(ch.isascii() and ch.isalpha() for ch in stripped)
        cjk_chars = len(CJK_RE.findall(stripped))
        return ascii_letters > cjk_chars * 3

    return True


def iter_suspicious_scan_files(base: Path) -> list[str]:
    files: list[str] = []

    for rel in SUSPICIOUS_SCAN_ROOT_FILES:
        path = base / rel
        if path.is_file():
            files.append(rel)

    for rel_dir in SUSPICIOUS_SCAN_DIRS:
        dir_path = base / rel_dir
        if not dir_path.is_dir():
            continue
        for path in sorted(dir_path.rglob("*.md")):
            files.append(path.relative_to(base).as_posix())

    return sorted(set(files))


def scan_suspicious_lines(files: Iterable[str]) -> list[str]:
    suspicious: list[str] = []

    for rel in files:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        in_code_fence = False

        for index, line in enumerate(text.splitlines(), start=1):
            if CODE_FENCE_RE.match(line.strip()):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue
            if is_suspicious_line(line):
                suspicious.append(f"{rel}:{index}: {line.strip()}")
                if len(suspicious) >= SUSPICIOUS_LINE_LIMIT:
                    return suspicious

    return suspicious


def run() -> int:
    if not UPSTREAM_ROOT.is_dir():
        print("❌ 未找到原版目录: spec-kit")
        return 1

    current_files = iter_translation_files(ROOT)
    upstream_files = iter_translation_files(UPSTREAM_ROOT)

    current_set = set(current_files)
    upstream_set = set(upstream_files)

    suspicious_scan_files = iter_suspicious_scan_files(ROOT)

    result = ScanResult(
        matched=sorted(current_set & upstream_set),
        local_only=sorted(current_set - upstream_set),
        upstream_missing=sorted(upstream_set - current_set),
        suspicious_lines=scan_suspicious_lines(suspicious_scan_files),
    )

    print("=== Markdown 翻译覆盖校验 ===")
    print(f"项目根目录: {ROOT}")
    print(f"原版目录: {UPSTREAM_ROOT}")
    print()
    print("[范围]")
    print(f"- 根目录文件: {', '.join(ROOT_TRANSLATION_FILES)}")
    print(f"- 目录: {', '.join(TRANSLATION_DIRS)}")
    print("- 忽略: .claude/, tests/, CLAUDE.md, AGENTS.md, TRANSLATION_STANDARDS.md, TERMINOLOGY.md, CHANGELOG.md, memory/constitution.md")
    print(f"- 疑似英文扫描范围: {', '.join(SUSPICIOUS_SCAN_ROOT_FILES)} + {', '.join(SUSPICIOUS_SCAN_DIRS)}")
    print()
    print("[统计]")
    print(f"- 当前纳入校验: {len(current_set)}")
    print(f"- 原版纳入校验: {len(upstream_set)}")
    print(f"- 与原版同路径: {len(result.matched)}")
    print(f"- 当前独有: {len(result.local_only)}")
    print(f"- 原版缺失: {len(result.upstream_missing)}")
    print()

    if result.local_only:
        print("[当前独有文件]")
        for item in result.local_only:
            print(f"- {item}")
        print()

    if result.upstream_missing:
        print("[原版存在但当前缺失]")
        for item in result.upstream_missing:
            print(f"- {item}")
        print()

    if result.suspicious_lines:
        print(f"[疑似未翻译英文行] 最多显示 {SUSPICIOUS_LINE_LIMIT} 条")
        for item in result.suspicious_lines:
            print(f"- {item}")
        print()
    else:
        print("[疑似未翻译英文行]")
        print("- 未发现明显可疑项")
        print()

    if result.upstream_missing:
        print("❌ 校验失败: 存在原版文件未纳入当前翻译范围")
        return 1

    print("✅ 校验通过: 翻译范围覆盖原版对应 Markdown 文件")
    return 0


if __name__ == "__main__":
    sys.exit(run())

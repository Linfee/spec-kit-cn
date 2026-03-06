#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]


def load_cli_config() -> tuple[dict[str, dict[str, object]], dict[str, str], str]:
    source_path = ROOT_DIR / "src" / "specify_cli" / "__init__.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    agent_config: dict[str, dict[str, object]] | None = None
    overrides: dict[str, str] | None = None
    default_skills_dir: str | None = None

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == "AGENT_CONFIG":
                agent_config = ast.literal_eval(node.value)
            elif target.id == "AGENT_SKILLS_DIR_OVERRIDES":
                overrides = ast.literal_eval(node.value)
            elif target.id == "DEFAULT_SKILLS_DIR":
                default_skills_dir = ast.literal_eval(node.value)

    if agent_config is None or overrides is None or default_skills_dir is None:
        raise SystemExit("无法从 src/specify_cli/__init__.py 解析 agent 配置")

    return agent_config, overrides, default_skills_dir


AGENT_CONFIG, AGENT_SKILLS_DIR_OVERRIDES, DEFAULT_SKILLS_DIR = load_cli_config()


def get_skills_dir(project_path: Path, selected_ai: str) -> Path:
    if selected_ai in AGENT_SKILLS_DIR_OVERRIDES:
        return project_path / AGENT_SKILLS_DIR_OVERRIDES[selected_ai]

    agent_config = AGENT_CONFIG.get(selected_ai, {})
    agent_folder = str(agent_config.get("folder") or "")
    if agent_folder:
        return project_path / agent_folder.rstrip("/") / "skills"

    return project_path / DEFAULT_SKILLS_DIR


DEFAULT_PS_AGENTS = ["claude", "copilot", "q"]
CHINESE_MARKERS = ["规范驱动", "章程", "实施计划", "项目设置工具", "已就绪"]
SKILL_COMMANDS = sorted((ROOT_DIR / "templates" / "commands").glob("*.md"))
EXPECTED_TEMPLATE_FILES = sorted(
    path.relative_to(ROOT_DIR / "templates")
    for path in (ROOT_DIR / "templates").rglob("*")
    if path.is_file() and path.parent.name != "commands" and path.name != "vscode-settings.json"
)
EXPECTED_MEMORY_FILES = sorted(
    path.relative_to(ROOT_DIR / "memory")
    for path in (ROOT_DIR / "memory").rglob("*")
    if path.is_file()
)
EXPECTED_BASH_FILES = sorted(
    path.relative_to(ROOT_DIR / "scripts" / "bash")
    for path in (ROOT_DIR / "scripts" / "bash").rglob("*")
    if path.is_file()
)
EXPECTED_POWERSHELL_FILES = sorted(
    path.relative_to(ROOT_DIR / "scripts" / "powershell")
    for path in (ROOT_DIR / "scripts" / "powershell").rglob("*")
    if path.is_file()
)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CLI_VERSION_RE = re.compile(r"CLI Version\s+([^\s]+)")
TEMPLATE_VERSION_RE = re.compile(r"Template Version\s+([^\s]+)")


@dataclass
class PhaseResult:
    name: str
    ok: bool = True
    failures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.ok = False
        self.failures.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)

    def record(self, command: list[str]) -> None:
        self.commands.append(shell_join(redact_command(command)))


@dataclass
class AgentRun:
    agent: str
    normal: PhaseResult
    ai_skills: PhaseResult | None = None
    powershell: PhaseResult | None = None

    @property
    def ok(self) -> bool:
        parts = [self.normal, self.ai_skills, self.powershell]
        return all(part is None or part.ok for part in parts)


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex_quote(part) for part in parts)


def redact_command(parts: list[str]) -> list[str]:
    redacted: list[str] = []
    redact_next = False
    for part in parts:
        if redact_next:
            redacted.append("***REDACTED***")
            redact_next = False
            continue
        redacted.append(part)
        if part == "--github-token":
            redact_next = True
    return redacted


def shlex_quote(part: str) -> str:
    if not part:
        return "''"
    if re.fullmatch(r"[A-Za-z0-9_./:@=-]+", part):
        return part
    return "'" + part.replace("'", "'\"'\"'") + "'"


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def load_expected_version() -> str:
    with (ROOT_DIR / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    return str(data["project"]["version"])


def load_github_token() -> str | None:
    for env_name in ("GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(env_name)
        if value:
            return value

    if shutil.which("gh") is None:
        return None

    result = subprocess.run(["gh", "auth", "token"], text=True, capture_output=True)
    if result.returncode != 0:
        return None

    token = result.stdout.strip()
    return token or None


def load_latest_release_version() -> str | None:
    if shutil.which("gh") is None:
        return None

    result = subprocess.run(
        ["gh", "release", "list", "--repo", "Linfee/spec-kit-cn", "--limit", "1"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None

    first_line = result.stdout.strip().splitlines()
    if not first_line:
        return None

    match = re.search(r"\bv(\d+\.\d+\.\d+)\b", first_line[0])
    return match.group(1) if match else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="验证 specify-cn main 分支最新提交是否可正确初始化所有支持的 agent。")
    parser.add_argument("--repo-root", type=Path, default=ROOT_DIR, help="仓库根目录")
    parser.add_argument("--agents", nargs="*", help="仅验证指定 agent，支持空格或逗号分隔")
    parser.add_argument("--keep-temp", action="store_true", help="执行结束后保留临时目录")
    parser.add_argument("--skip-ai-skills", action="store_true", help="跳过 --ai-skills 模式验证")
    parser.add_argument("--skip-ps-sample", action="store_true", help="跳过 PowerShell 抽样验证")
    parser.add_argument("--json-output", type=Path, help="将结果额外写入指定 JSON 文件")
    return parser.parse_args()


def selected_agents(raw: list[str] | None) -> list[str]:
    all_agents = [agent for agent in AGENT_CONFIG if agent != "generic"]
    if not raw:
        return all_agents

    chosen: list[str] = []
    for item in raw:
        for part in item.split(","):
            part = part.strip()
            if part:
                chosen.append(part)

    unknown = sorted(set(chosen) - set(all_agents))
    if unknown:
        raise SystemExit(f"未知 agent: {', '.join(unknown)}")

    deduped: list[str] = []
    for agent in chosen:
        if agent not in deduped:
            deduped.append(agent)
    return deduped


def resolve_runner() -> list[str]:
    git_source = "git+https://github.com/linfee/spec-kit-cn@main"
    candidates = [
        ["uvx", "--isolated", "--from", git_source, "specify-cn"],
        ["uv", "tool", "run", "--isolated", "--from", git_source, "specify-cn"],
    ]
    last_error: str | None = None
    for base in candidates:
        if shutil.which(base[0]) is None:
            continue
        probe = run_command(base + ["version"], check=False)
        if probe.returncode == 0:
            return base
        last_error = probe.stderr or probe.stdout
    raise SystemExit(f"无法调用最新发布的 specify-cn。最后错误: {last_error or '未找到 uvx/uv'}")


def run_command(command: list[str], *, check: bool, cwd: Path | None = None, github_token: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        joined = shell_join(command)
        raise RuntimeError(f"命令失败: {joined}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def parse_version_output(text: str, label: str) -> str:
    clean = strip_ansi(text)
    pattern = CLI_VERSION_RE if label == "cli" else TEMPLATE_VERSION_RE
    match = pattern.search(clean)
    return match.group(1) if match else "unknown"


def contains_chinese_marker(text: str) -> bool:
    clean = strip_ansi(text)
    return any(marker in clean for marker in CHINESE_MARKERS)


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(strip_ansi(text)))


def command_extension(agent: str) -> str:
    if agent in {"gemini", "qwen"}:
        return ".toml"
    if agent == "copilot":
        return ".agent.md"
    return ".md"


def expected_command_files(agent: str) -> list[str]:
    ext = command_extension(agent)
    return [f"speckit.{path.stem}{ext}" for path in SKILL_COMMANDS]


def expected_skill_dirs(agent: str) -> list[str]:
    skill_dirs: list[str] = []
    for command_file in expected_command_files(agent):
        stem = Path(command_file).stem
        if stem.startswith("speckit."):
            stem = "speckit-" + stem[len("speckit."):]
        skill_dirs.append(stem)
    return skill_dirs


def validate_file_exists(base: Path, relative_paths: list[Path], phase: PhaseResult, *, label: str) -> None:
    for relative in relative_paths:
        target = base / relative
        if not target.exists():
            phase.fail(f"缺少{label}: {relative}")
            continue
        if target.is_file() and target.stat().st_size == 0:
            phase.fail(f"{label}为空文件: {relative}")


def validate_normal_project(target: Path, agent: str, script_type: str, phase: PhaseResult) -> None:
    validate_file_exists(target / ".specify" / "templates", EXPECTED_TEMPLATE_FILES, phase, label="模板")
    validate_file_exists(target / ".specify" / "memory", EXPECTED_MEMORY_FILES, phase, label="memory 文件")

    script_root = target / ".specify" / "scripts"
    if script_type == "sh":
        validate_file_exists(script_root / "bash", EXPECTED_BASH_FILES, phase, label="bash 脚本")
    else:
        validate_file_exists(script_root / "powershell", EXPECTED_POWERSHELL_FILES, phase, label="PowerShell 脚本")

    agent_cfg = AGENT_CONFIG[agent]
    commands_dir = target / agent_cfg["folder"].rstrip("/") / agent_cfg["commands_subdir"]
    if not commands_dir.exists():
        phase.fail(f"缺少 agent 目录: {commands_dir.relative_to(target)}")
    else:
        for file_name in expected_command_files(agent):
            file_path = commands_dir / file_name
            if not file_path.exists():
                phase.fail(f"缺少 agent 命令文件: {(commands_dir / file_name).relative_to(target)}")
            elif file_path.stat().st_size == 0:
                phase.fail(f"agent 命令文件为空: {(commands_dir / file_name).relative_to(target)}")

    if agent == "copilot":
        prompts_dir = target / ".github" / "prompts"
        if not prompts_dir.exists():
            phase.fail("缺少 copilot prompt 目录: .github/prompts")
        else:
            for command_file in expected_command_files(agent):
                prompt_name = command_file.replace(".agent.md", ".prompt.md")
                prompt_path = prompts_dir / prompt_name
                if not prompt_path.exists():
                    phase.fail(f"缺少 copilot prompt 文件: {prompt_path.relative_to(target)}")

        vscode_settings = target / ".vscode" / "settings.json"
        if not vscode_settings.exists():
            phase.fail("缺少 VS Code 设置文件: .vscode/settings.json")

    spec_template = target / ".specify" / "templates" / "spec-template.md"
    constitution = target / ".specify" / "memory" / "constitution.md"
    if spec_template.exists() and not contains_cjk(spec_template.read_text(encoding="utf-8")):
        phase.fail("spec-template.md 未检测到中文关键字")
    if constitution.exists() and not contains_cjk(constitution.read_text(encoding="utf-8")):
        phase.fail("constitution.md 未检测到中文内容")


def validate_ai_skills_project(target: Path, agent: str, phase: PhaseResult) -> None:
    validate_file_exists(target / ".specify" / "templates", EXPECTED_TEMPLATE_FILES, phase, label="模板")
    validate_file_exists(target / ".specify" / "memory", EXPECTED_MEMORY_FILES, phase, label="memory 文件")

    skills_dir = get_skills_dir(target, agent)
    if not skills_dir.exists():
        phase.fail(f"缺少 skills 目录: {skills_dir.relative_to(target)}")
        return

    for skill_name in expected_skill_dirs(agent):
        skill_file = skills_dir / skill_name / "SKILL.md"
        if not skill_file.exists():
            phase.fail(f"缺少 skill 文件: {skill_file.relative_to(target)}")
            continue
        content = skill_file.read_text(encoding="utf-8")
        if "name:" not in content or "description:" not in content:
            phase.fail(f"skill frontmatter 不完整: {skill_file.relative_to(target)}")


def execute_phase(base_command: list[str], phase_command: list[str], phase: PhaseResult, *, github_token: str | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str] | None:
    command = base_command + phase_command
    phase.record(command)
    result = run_command(command, check=False, cwd=cwd, github_token=github_token)
    if result.returncode != 0:
        phase.fail(f"命令失败: {shell_join(command)}")
        stderr = strip_ansi(result.stderr.strip())
        stdout = strip_ansi(result.stdout.strip())
        if stderr:
            phase.note(f"stderr: {stderr[-2000:]}")
        if stdout:
            phase.note(f"stdout: {stdout[-2000:]}")
        return None
    return result


def with_github_token(command: list[str], github_token: str | None) -> list[str]:
    if not github_token or command[0] != "init" or "--github-token" in command:
        return command
    return command + ["--github-token", github_token]


def run_agent_validation(base_command: list[str], workspace: Path, agent: str, *, include_ai_skills: bool, include_ps: bool, github_token: str | None) -> AgentRun:
    normal = PhaseResult(name="normal-init")
    normal_target = workspace / f"{agent}-sh"
    result = execute_phase(
        base_command,
        with_github_token(["init", str(normal_target), "--ai", agent, "--ignore-agent-tools", "--no-git", "--script", "sh"], github_token),
        normal,
        github_token=github_token,
    )
    if result is not None:
        if not contains_chinese_marker(result.stdout + result.stderr):
            normal.note("init 输出未命中中文关键字，继续检查文件产物")
        validate_normal_project(normal_target, agent, "sh", normal)

    ai_skills_phase: PhaseResult | None = None
    if include_ai_skills:
        ai_skills_phase = PhaseResult(name="ai-skills-init")
        ai_target = workspace / f"{agent}-ai-skills"
        result = execute_phase(
            base_command,
            with_github_token(["init", str(ai_target), "--ai", agent, "--ai-skills", "--ignore-agent-tools", "--no-git", "--script", "sh"], github_token),
            ai_skills_phase,
            github_token=github_token,
        )
        if result is not None:
            validate_ai_skills_project(ai_target, agent, ai_skills_phase)

    powershell_phase: PhaseResult | None = None
    if include_ps:
        powershell_phase = PhaseResult(name="powershell-sample")
        ps_target = workspace / f"{agent}-ps"
        result = execute_phase(
            base_command,
            with_github_token(["init", str(ps_target), "--ai", agent, "--ignore-agent-tools", "--no-git", "--script", "ps"], github_token),
            powershell_phase,
            github_token=github_token,
        )
        if result is not None:
            validate_normal_project(ps_target, agent, "ps", powershell_phase)

    return AgentRun(agent=agent, normal=normal, ai_skills=ai_skills_phase, powershell=powershell_phase)


def print_phase(prefix: str, phase: PhaseResult | None) -> None:
    if phase is None:
        return
    status = "PASS" if phase.ok else "FAIL"
    print(f"{prefix} {phase.name}: {status}")
    for failure in phase.failures:
        print(f"    - {failure}")
    for note in phase.notes:
        print(f"    - {note}")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if repo_root != ROOT_DIR:
        raise SystemExit(f"当前脚本仅支持在仓库根目录 {ROOT_DIR} 下运行，收到: {repo_root}")
    expected_version = load_expected_version()
    agents = selected_agents(args.agents)
    runner = resolve_runner()
    github_token = load_github_token()

    temp_root = Path(tempfile.mkdtemp(prefix="specify-cn-release-verify-"))
    report_path = temp_root / "report.json"
    keep_temp = args.keep_temp

    summary: dict[str, object] = {
        "repo_root": str(repo_root),
        "expected_version": expected_version,
        "temp_root": str(temp_root),
        "runner": shell_join(runner),
        "global_checks": {},
        "agents": [],
    }

    failed = False
    try:
        help_result = run_command(runner + ["--help"], check=True, github_token=github_token)
        check_result = run_command(runner + ["check"], check=True, github_token=github_token)
        version_result = run_command(runner + ["version"], check=True, github_token=github_token)

        cli_version = parse_version_output(version_result.stdout, "cli")
        template_version = parse_version_output(version_result.stdout, "template")
        if template_version == "unknown":
            latest_release_version = load_latest_release_version()
            if latest_release_version:
                template_version = latest_release_version
        global_failures: list[str] = []

        if cli_version != expected_version:
            global_failures.append(f"发布包版本不匹配: expected={expected_version}, actual={cli_version}")
        if template_version != expected_version:
            global_failures.append(f"模板版本不匹配: expected={expected_version}, actual={template_version}")
        if not contains_chinese_marker(help_result.stdout):
            global_failures.append("--help 输出未检测到中文关键字")
        if "已就绪" not in strip_ansi(check_result.stdout):
            global_failures.append("check 输出未检测到“已就绪”")

        summary["global_checks"] = {
            "cli_version": cli_version,
            "template_version": template_version,
            "help_has_chinese": contains_chinese_marker(help_result.stdout),
            "check_has_ready": "已就绪" in strip_ansi(check_result.stdout),
            "failures": global_failures,
        }

        if global_failures:
            failed = True

        ps_agents = set(DEFAULT_PS_AGENTS) & set(agents)
        for agent in agents:
            run = run_agent_validation(
                runner,
                temp_root,
                agent,
                include_ai_skills=not args.skip_ai_skills,
                include_ps=(agent in ps_agents and not args.skip_ps_sample),
                github_token=github_token,
            )
            if not run.ok:
                failed = True
            summary["agents"].append(
                {
                    "agent": run.agent,
                    "ok": run.ok,
                    "normal": asdict(run.normal),
                    "ai_skills": asdict(run.ai_skills) if run.ai_skills else None,
                    "powershell": asdict(run.powershell) if run.powershell else None,
                }
            )

        report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.json_output:
            args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"Runner: {shell_join(runner)}")
        print(f"Expected version: {expected_version}")
        print(f"Temp root: {temp_root}")
        print(f"Report: {report_path}")

        for failure in summary["global_checks"].get("failures", []):
            print(f"GLOBAL FAIL: {failure}")

        for agent_data in summary["agents"]:
            print(f"\n[{agent_data['agent']}] {'PASS' if agent_data['ok'] else 'FAIL'}")
            print_phase("  -", PhaseResult(**agent_data["normal"]))
            if agent_data["ai_skills"]:
                print_phase("  -", PhaseResult(**agent_data["ai_skills"]))
            if agent_data["powershell"]:
                print_phase("  -", PhaseResult(**agent_data["powershell"]))

        if failed:
            keep_temp = True
            print("\n发布后验证失败，已保留临时目录供排查。")
            return 1

        print("\n发布后验证通过。")
        return 0
    finally:
        if not keep_temp:
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

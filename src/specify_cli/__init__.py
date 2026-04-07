#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
#     "json5",
# ]
# ///
"""
Specify CN CLI - Spec Kit CN 项目初始化工具

Usage:
    uvx specify-cn init <project-name>
    uvx specify-cn init .
    uvx specify-cn init --here

Or install globally:
    uv tool install specify-cn-cli
    specify-cn init <project-name>
    specify-cn init .
    specify-cn init --here
"""

import os
import subprocess
import sys
import zipfile
import tempfile
import shutil
import json
import json5
import stat
import yaml
from pathlib import Path
from typing import Any, Optional, Tuple

import typer
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar
import ssl
import truststore
from datetime import datetime

ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)

# --- CLI help framework label localization ---
def _localize_help_labels():
    """Patch Click/Typer help framework labels with Chinese translations."""
    # 1. Typer Rich panel titles (computed at import time as module-level vars)
    try:
        import typer.rich_utils as _ru
        _ru.ARGUMENTS_PANEL_TITLE = "参数"
        _ru.OPTIONS_PANEL_TITLE = "选项"
        _ru.COMMANDS_PANEL_TITLE = "命令"
        # Update highlighter regex to also match Chinese usage prefix
        if hasattr(_ru, 'OptionHighlighter'):
            for i, pat in enumerate(_ru.OptionHighlighter.highlights):
                if '?P<usage>' in pat:
                    _ru.OptionHighlighter.highlights[i] = r"(?P<usage>用法: |Usage: )"
    except (ImportError, AttributeError):
        pass

    # 2. Patch Click's _() for runtime labels (both click.core and click.decorators)
    _help_labels = {
        "Show this message and exit.": "显示此帮助信息并退出.",
        "Options": "选项",
        "Commands": "命令",
        "Arguments": "参数",
        "Usage: ": "用法: ",
    }
    for _mod_name in ("click.core", "click.decorators"):
        try:
            _mod = __import__(_mod_name, fromlist=["_"])
            _orig_fn = _mod._
            def _make_cn(fn):
                def _cn(msg, _fn=fn):
                    return _help_labels.get(msg, _fn(msg))
                return _cn
            _mod._ = _make_cn(_orig_fn)
        except (ImportError, AttributeError):
            pass

    # 3. Patch Click's HelpFormatter.write_usage default prefix
    try:
        import click.formatting as _cf
        _orig_wu = _cf.HelpFormatter.write_usage
        def _cn_write_usage(self, prog, args='', prefix=None):
            if prefix is None:
                prefix = "用法: "
            return _orig_wu(self, prog, args, prefix)
        _cf.HelpFormatter.write_usage = _cn_write_usage
    except (ImportError, AttributeError):
        pass

_localize_help_labels()
# --- end localization ---

def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None."""
    return ((cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()) or None

def _github_auth_headers(cli_token: str | None = None) -> dict:
    """Return Authorization header dict only when a non-empty token exists."""
    token = _github_token(cli_token)
    return {"Authorization": f"Bearer {token}"} if token else {}

def _build_agent_config() -> dict[str, dict[str, Any]]:
    """Derive AGENT_CONFIG from INTEGRATION_REGISTRY."""
    from .integrations import INTEGRATION_REGISTRY
    config: dict[str, dict[str, Any]] = {}
    for key, integration in INTEGRATION_REGISTRY.items():
        if integration.config:
            config[key] = dict(integration.config)
    return config

AGENT_CONFIG = _build_agent_config()

AI_ASSISTANT_ALIASES = {
    "kiro": "kiro-cli",
}

# Agents that use TOML command format (others use Markdown)
_TOML_AGENTS = frozenset({"gemini", "tabnine"})

def _build_ai_assistant_help() -> str:
    """Build the --ai help text from AGENT_CONFIG so it stays in sync with runtime config."""

    non_generic_agents = sorted(agent for agent in AGENT_CONFIG if agent != "generic")
    base_help = (
        f"要使用的 AI 助手: {', '.join(non_generic_agents)}, "
        "或 generic (需要 --ai-commands-dir)."
    )

    if not AI_ASSISTANT_ALIASES:
        return base_help

    alias_phrases = []
    for alias, target in sorted(AI_ASSISTANT_ALIASES.items()):
        alias_phrases.append(f"'{alias}' 是 '{target}' 的别名")

    if len(alias_phrases) == 1:
        aliases_text = alias_phrases[0]
    else:
        aliases_text = ', '.join(alias_phrases[:-1]) + ' and ' + alias_phrases[-1]

    return base_help + " " + aliases_text + "."
AI_ASSISTANT_HELP = _build_ai_assistant_help()

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"
CLAUDE_NPM_LOCAL_PATH = Path.home() / ".claude" / "local" / "node_modules" / ".bin" / "claude"

BANNER = """
███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝  
███████║██║     ███████╗╚██████╗██║██║        ██║   
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝   
"""

TAGLINE = "Spec Kit CN - 规范驱动开发工具包"
class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """
    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {"pending": 0, "running": 1, "done": 2, "error": 3, "skipped": 4}
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label, "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append({"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree

def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return 'up'
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return 'down'

    if key == readchar.key.ENTER:
        return 'enter'

    if key == readchar.key.ESC:
        return 'escape'

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key

def select_with_arrows(options: dict, prompt_text: str = "选择一个选项", default_key: str = None) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with
        
    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row("", "[dim]使用 ↑/↓ 导航, Enter 选择, Esc 取消[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]已取消选择[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]已取消选择[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]选择失败.[/red]")
        raise typer.Exit(1)

    return selected_key

console = Console()

class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="specify-cn",
    help="Spec Kit CN 项目初始化工具 - 规范驱动开发",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)

def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()

@app.callback()
def callback(ctx: typer.Context):
    """未提供子命令时显示横幅."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]运行 'specify-cn --help' 查看用法[/dim]"))
        console.print()

def run_command(cmd: list[str], check_return: bool = True, capture: bool = False, shell: bool = False) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(cmd, check=check_return, capture_output=True, text=True, shell=shell)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]命令执行错误:[/red] {' '.join(cmd)}")
            console.print(f"[red]退出码:[/red] {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                console.print(f"[red]错误输出:[/red] {e.stderr}")
            raise
        return None

def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.
    
    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results
        
    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI local installs
    # See: https://github.com/github/spec-kit/issues/123
    # See: https://github.com/github/spec-kit/issues/550
    # Claude Code can be installed in two local paths:
    #   1. ~/.claude/local/claude          (after `claude migrate-installer`)
    #   2. ~/.claude/local/node_modules/.bin/claude  (npm-local install, e.g. via nvm)
    # Neither path may be on the system PATH, so we check them explicitly.
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.is_file() or CLAUDE_NPM_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True
    
    if tool == "kiro-cli":
        # Kiro currently supports both executable names. Prefer kiro-cli and
        # accept kiro as a compatibility fallback.
        found = shutil.which("kiro-cli") is not None or shutil.which("kiro") is not None
    else:
        found = shutil.which(tool) is not None
    
    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")
    
    return found

def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()
    
    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo(project_path: Path, quiet: bool = False) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.
    
    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]正在初始化 Git 仓库...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from Specify template"], check=True, capture_output=True, text=True)
        if not quiet:
            console.print("[green]✓[/green] Git 仓库已初始化")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"
        
        if not quiet:
            console.print(f"[red]Git 仓库初始化错误:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)

def handle_vscode_settings(sub_item, dest_file, rel_path, verbose=False, tracker=None) -> None:
    """Handle merging or copying of .vscode/settings.json files.

    Note: when merge produces changes, rewritten output is normalized JSON and
    existing JSONC comments/trailing commas are not preserved.
    """
    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    def atomic_write_json(target_file: Path, payload: dict[str, Any]) -> None:
        """Atomically write JSON while preserving existing mode bits when possible."""
        temp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=target_file.parent,
                prefix=f"{target_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as f:
                temp_path = Path(f.name)
                json.dump(payload, f, indent=4)
                f.write('\n')

            if target_file.exists():
                try:
                    existing_stat = target_file.stat()
                    os.chmod(temp_path, stat.S_IMODE(existing_stat.st_mode))
                    if hasattr(os, "chown"):
                        try:
                            os.chown(temp_path, existing_stat.st_uid, existing_stat.st_gid)
                        except PermissionError:
                            # Best-effort owner/group preservation without requiring elevated privileges.
                            pass
                except OSError:
                    # Best-effort metadata preservation; data safety is prioritized.
                    pass

            os.replace(temp_path, target_file)
        except Exception:
            if temp_path and temp_path.exists():
                temp_path.unlink()
            raise

    try:
        with open(sub_item, 'r', encoding='utf-8') as f:
            # json5 natively supports comments and trailing commas (JSONC)
            new_settings = json5.load(f)

        if dest_file.exists():
            merged = merge_json_files(dest_file, new_settings, verbose=verbose and not tracker)
            if merged is not None:
                atomic_write_json(dest_file, merged)
                log("Merged:", "green")
                log("Note: comments/trailing commas are normalized when rewritten", "yellow")
            else:
                log("Skipped merge (preserved existing settings)", "yellow")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge settings: {e}", "yellow")
        if not dest_file.exists():
            shutil.copy2(sub_item, dest_file)


def merge_json_files(existing_path: Path, new_content: Any, verbose: bool = False) -> Optional[dict[str, Any]]:
    """Merge new JSON content into existing JSON file.

    Performs a polite deep merge where:
    - New keys are added
    - Existing keys are preserved (not overwritten) unless both values are dictionaries
    - Nested dictionaries are merged recursively only when both sides are dictionaries
    - Lists and other values are preserved from base if they exist

    Args:
        existing_path: Path to existing JSON file
        new_content: New JSON content to merge in
        verbose: Whether to print merge details

    Returns:
        Merged JSON content as dict, or None if the existing file should be left untouched.
    """
    # Load existing content first to have a safe fallback
    existing_content = None
    exists = existing_path.exists()

    if exists:
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                # Handle comments (JSONC) natively with json5
                # Note: json5 handles BOM automatically
                existing_content = json5.load(f)
        except FileNotFoundError:
            # Handle race condition where file is deleted after exists() check
            exists = False
        except Exception as e:
            if verbose:
                console.print(f"[yellow]警告: 无法读取或解析 {existing_path.name} 中的现有 JSON ({e}).[/yellow]")
            # Skip merge to preserve existing file if unparseable or inaccessible (e.g. PermissionError)
            return None

    # Validate template content
    if not isinstance(new_content, dict):
        if verbose:
            console.print(f"[yellow]警告: {existing_path.name} 的模板内容不是字典, 已保留现有设置.[/yellow]")
        return None

    if not exists:
        return new_content

    # If existing content parsed but is not a dict, skip merge to avoid data loss
    if not isinstance(existing_content, dict):
        if verbose:
            console.print(f"[yellow]警告: {existing_path.name} 中的现有 JSON 不是对象, 跳过合并以避免数据丢失.[/yellow]")
        return None

    def deep_merge_polite(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge update dict into base dict, preserving base values."""
        result = base.copy()
        for key, value in update.items():
            if key not in result:
                # Add new key
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = deep_merge_polite(result[key], value)
            else:
                # Key already exists and values are not both dicts; preserve existing value.
                # This ensures user settings aren't overwritten by template defaults.
                pass
        return result

    merged = deep_merge_polite(existing_content, new_content)

    # Detect if anything actually changed. If not, return None so the caller
    # can skip rewriting the file (preserving user's comments/formatting).
    if merged == existing_content:
        return None

    if verbose:
        console.print(f"[cyan]已合并 JSON 文件:[/cyan] {existing_path.name}")

    return merged

def _locate_core_pack() -> Path | None:
    """Return the filesystem path to the bundled core_pack directory, or None.

    Only present in wheel installs: hatchling's force-include copies
    templates/, scripts/ etc. into specify_cli/core_pack/ at build time.

    Source-checkout and editable installs do NOT have this directory.
    Callers that need to work in both environments must check the repo-root
    trees (templates/, scripts/) as a fallback when this returns None.
    """
    # Wheel install: core_pack is a sibling directory of this file
    candidate = Path(__file__).parent / "core_pack"
    if candidate.is_dir():
        return candidate
    return None


def _install_shared_infra(
    project_path: Path,
    script_type: str,
    tracker: StepTracker | None = None,
) -> bool:
    """Install shared infrastructure files into *project_path*.

    Copies ``.specify/scripts/`` and ``.specify/templates/`` from the
    bundled core_pack or source checkout.  Tracks all installed files
    in ``speckit.manifest.json``.
    Returns ``True`` on success.
    """
    from .integrations.manifest import IntegrationManifest

    core = _locate_core_pack()
    manifest = IntegrationManifest("speckit", project_path, version=get_speckit_version())

    # Scripts
    if core and (core / "scripts").is_dir():
        scripts_src = core / "scripts"
    else:
        repo_root = Path(__file__).parent.parent.parent
        scripts_src = repo_root / "scripts"

    skipped_files: list[str] = []

    if scripts_src.is_dir():
        dest_scripts = project_path / ".specify" / "scripts"
        dest_scripts.mkdir(parents=True, exist_ok=True)
        variant_dir = "bash" if script_type == "sh" else "powershell"
        variant_src = scripts_src / variant_dir
        if variant_src.is_dir():
            dest_variant = dest_scripts / variant_dir
            dest_variant.mkdir(parents=True, exist_ok=True)
            # Merge without overwriting — only add files that don't exist yet
            for src_path in variant_src.rglob("*"):
                if src_path.is_file():
                    rel_path = src_path.relative_to(variant_src)
                    dst_path = dest_variant / rel_path
                    if dst_path.exists():
                        skipped_files.append(str(dst_path.relative_to(project_path)))
                    else:
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        rel = dst_path.relative_to(project_path).as_posix()
                        manifest.record_existing(rel)

    # Page templates (not command templates, not vscode-settings.json)
    if core and (core / "templates").is_dir():
        templates_src = core / "templates"
    else:
        repo_root = Path(__file__).parent.parent.parent
        templates_src = repo_root / "templates"

    if templates_src.is_dir():
        dest_templates = project_path / ".specify" / "templates"
        dest_templates.mkdir(parents=True, exist_ok=True)
        for f in templates_src.iterdir():
            if f.is_file() and f.name != "vscode-settings.json" and not f.name.startswith("."):
                dst = dest_templates / f.name
                if dst.exists():
                    skipped_files.append(str(dst.relative_to(project_path)))
                else:
                    shutil.copy2(f, dst)
                    rel = dst.relative_to(project_path).as_posix()
                    manifest.record_existing(rel)

    if skipped_files:
        import logging
        logging.getLogger(__name__).warning(
            "The following shared files already exist and were not overwritten:\n%s",
            "\n".join(f"  {f}" for f in skipped_files),
        )

    manifest.save()
    return True


def ensure_executable_scripts(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Ensure POSIX .sh scripts under .specify/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".specify" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat()
            mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400:
                new_mode |= 0o100
            if mode & 0o040:
                new_mode |= 0o010
            if mode & 0o004:
                new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (f", {len(failures)} failed" if failures else "")
        tracker.add("chmod", "递归设置脚本权限")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(f"[cyan]已递归更新 {updated} 个脚本的执行权限[/cyan]")
        if failures:
            console.print("[yellow]部分脚本无法更新:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")

def ensure_constitution_from_template(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Copy constitution template to memory if it doesn't exist (preserves existing constitution on reinitialization)."""
    memory_constitution = project_path / ".specify" / "memory" / "constitution.md"
    template_constitution = project_path / ".specify" / "templates" / "constitution-template.md"

    # If constitution already exists in memory, preserve it
    if memory_constitution.exists():
        if tracker:
            tracker.add("constitution", "章程设置")
            tracker.skip("constitution", "已保留现有文件")
        return

    # If template doesn't exist, something went wrong with extraction
    if not template_constitution.exists():
        if tracker:
            tracker.add("constitution", "章程设置")
            tracker.error("constitution", "未找到模板")
        return

    # Copy template to memory directory
    try:
        memory_constitution.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_constitution, memory_constitution)
        if tracker:
            tracker.add("constitution", "章程设置")
            tracker.complete("constitution", "已从模板复制")
        else:
            console.print("[cyan]已从模板初始化章程[/cyan]")
    except Exception as e:
        if tracker:
            tracker.add("constitution", "章程设置")
            tracker.error("constitution", str(e))
        else:
            console.print(f"[yellow]警告: 无法初始化章程: {e}[/yellow]")


INIT_OPTIONS_FILE = ".specify/init-options.json"


def save_init_options(project_path: Path, options: dict[str, Any]) -> None:
    """Persist the CLI options used during ``specify init``.

    Writes a small JSON file to ``.specify/init-options.json`` so that
    later operations (e.g. preset install) can adapt their behaviour
    without scanning the filesystem.
    """
    dest = project_path / INIT_OPTIONS_FILE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(options, indent=2, sort_keys=True))


def load_init_options(project_path: Path) -> dict[str, Any]:
    """Load the init options previously saved by ``specify init``.

    Returns an empty dict if the file does not exist or cannot be parsed.
    """
    path = project_path / INIT_OPTIONS_FILE
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _get_skills_dir(project_path: Path, selected_ai: str) -> Path:
    """Resolve the agent-specific skills directory.

    Returns ``project_path / <agent_folder> / "skills"``, falling back
    to ``project_path / ".agents/skills"`` for unknown agents.
    """
    agent_config = AGENT_CONFIG.get(selected_ai, {})
    agent_folder = agent_config.get("folder", "")
    if agent_folder:
        return project_path / agent_folder.rstrip("/") / "skills"
    return project_path / ".agents" / "skills"


# Constants kept for backward compatibility with presets and extensions.
DEFAULT_SKILLS_DIR = ".agents/skills"
NATIVE_SKILLS_AGENTS = {"codex", "kimi"}
SKILL_DESCRIPTIONS = {
    "specify": "从自然语言描述创建或更新功能规范.",
    "plan": "从功能规范生成技术实施计划.",
    "tasks": "将实施计划分解为可执行的任务列表.",
    "implement": "执行任务分解中的所有任务来构建功能.",
    "analyze": "对 spec.md, plan.md 和 tasks.md 进行跨制品一致性分析.",
    "clarify": "针对不明确需求的结构化澄清工作流.",
    "constitution": "创建或更新项目治理原则和开发指南.",
    "checklist": "生成自定义质量清单, 验证需求的完整性和清晰度.",
    "taskstoissues": "将 tasks.md 中的任务转换为 GitHub issues.",
}


@app.command()
def init(
    project_name: str = typer.Argument(None, help="新项目目录名称 (使用 --here 或 '.' 表示当前目录时可选)"),
    ai_assistant: str = typer.Option(None, "--ai", help=AI_ASSISTANT_HELP),
    ai_commands_dir: str = typer.Option(None, "--ai-commands-dir", help="代理命令文件目录 (使用 --ai generic 时必填, 例如 .myagent/commands/)"),
    script_type: str = typer.Option(None, "--script", help="脚本类型: sh 或 ps"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="跳过 Claude Code 等 AI 代理工具检查"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 Git 仓库初始化"),
    here: bool = typer.Option(False, "--here", help="在当前目录初始化项目, 而非创建新目录"),
    force: bool = typer.Option(False, "--force", help="使用 --here 时强制合并/覆盖 (跳过确认)"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Deprecated (no-op). Previously: skip SSL/TLS verification.", hidden=True),
    debug: bool = typer.Option(False, "--debug", help="Deprecated (no-op). Previously: show verbose diagnostic output.", hidden=True),
    github_token: str = typer.Option(None, "--github-token", help="Deprecated (no-op). Previously: GitHub token for API requests.", hidden=True),
    ai_skills: bool = typer.Option(False, "--ai-skills", help="将 Prompt.MD 模板安装为代理技能 (需要 --ai)"),
    offline: bool = typer.Option(False, "--offline", help="Deprecated (no-op). All scaffolding now uses bundled assets.", hidden=True),
    preset: str = typer.Option(None, "--preset", help="初始化时安装预设 (通过预设 ID)"),
    branch_numbering: str = typer.Option(None, "--branch-numbering", help="分支编号策略: 'sequential' (001, 002, ...) 或 'timestamp' (YYYYMMDD-HHMMSS)"),
    integration: str = typer.Option(None, "--integration", help="使用集成系统 (例如 --integration copilot). 与 --ai 互斥."),
    integration_options: str = typer.Option(None, "--integration-options", help='集成选项 (例如 --integration-options="--commands-dir .myagent/cmds")'),
):
    """
    初始化新的 Specify 项目.

    默认从最新的 GitHub Release 下载项目文件.
    使用 --offline 从 specify-cn-cli 包内置资源搭建 (无需网络, 适合离线或企业环境).

    注意: 从 v0.6.0 开始, 将默认使用内置资源并移除 --offline 标志.
    GitHub 下载路径将被弃用, 因为内置资源消除了网络需求, 避免代理/防火墙问题,
    并保证模板始终与已安装的 CLI 版本匹配.

    此命令将:
    1. 检查必需工具是否已安装 (Git 可选)
    2. 选择 AI 助手
    3. 从 GitHub 下载模板 (或使用 --offline 内置资源)
    4. 初始化 Git 仓库 (如果未指定 --no-git 且无现有仓库)
    5. 可选: 设置 AI 助手命令

    示例:
        specify-cn init my-project
        specify-cn init my-project --ai claude
        specify-cn init my-project --ai copilot --no-git
        specify-cn init --ignore-agent-tools my-project
        specify-cn init . --ai claude         # 在当前目录初始化
        specify-cn init .                     # 在当前目录初始化 (交互式选择 AI)
        specify-cn init --here --ai claude    # 当前目录初始化的替代语法
        specify-cn init --here --ai codex --ai-skills
        specify-cn init --here --ai codebuddy
        specify-cn init --here --ai vibe      # 使用 Mistral Vibe 支持初始化
        specify-cn init --here
        specify-cn init --here --force  # 跳过确认 (当前目录非空时)
        specify-cn init my-project --ai claude   # Claude 默认安装技能
        specify-cn init --here --ai gemini --ai-skills
        specify-cn init my-project --ai generic --ai-commands-dir .myagent/commands/  # 不支持的代理
        specify-cn init my-project --offline  # 使用内置资源 (无网络)
        specify-cn init my-project --ai claude --preset healthcare-compliance  # 使用预设
    """

    show_banner()

    # Detect when option values are likely misinterpreted flags (parameter ordering issue)
    if ai_assistant and ai_assistant.startswith("--"):
        console.print(f"[red]错误:[/red] --ai 的值无效: '{ai_assistant}'")
        console.print("[yellow]提示:[/yellow] 你是否忘记为 --ai 提供值?")
        console.print("[yellow]示例:[/yellow] specify-cn init --ai claude --here")
        console.print(f"[yellow]可用的代理:[/yellow] {', '.join(AGENT_CONFIG.keys())}")
        raise typer.Exit(1)
    
    if ai_commands_dir and ai_commands_dir.startswith("--"):
        console.print(f"[red]错误:[/red] --ai-commands-dir 的值无效: '{ai_commands_dir}'")
        console.print("[yellow]提示:[/yellow] 你是否忘记为 --ai-commands-dir 提供值?")
        console.print("[yellow]示例:[/yellow] specify-cn init --ai generic --ai-commands-dir .myagent/commands/")
        raise typer.Exit(1)

    if ai_assistant:
        ai_assistant = AI_ASSISTANT_ALIASES.get(ai_assistant, ai_assistant)

    # --integration and --ai are mutually exclusive
    if integration and ai_assistant:
        console.print("[red]错误:[/red] --integration 和 --ai 互斥")
        raise typer.Exit(1)

    # Resolve the integration — either from --integration or --ai
    from .integrations import INTEGRATION_REGISTRY, get_integration
    if integration:
        resolved_integration = get_integration(integration)
        if not resolved_integration:
            console.print(f"[red]错误:[/red] 未知的集成: '{integration}'")
            available = ", ".join(sorted(INTEGRATION_REGISTRY))
            console.print(f"[yellow]可用的集成:[/yellow] {available}")
            raise typer.Exit(1)
        ai_assistant = integration
    elif ai_assistant:
        resolved_integration = get_integration(ai_assistant)
        if not resolved_integration:
            console.print(f"[red]错误:[/red] 未知的代理 '{ai_assistant}'. 可选: {', '.join(sorted(INTEGRATION_REGISTRY))}")
            raise typer.Exit(1)

    # Deprecation warnings for --ai-skills and --ai-commands-dir (only when
    # an integration has been resolved from --ai or --integration)
    if ai_assistant or integration:
        if ai_skills:
            from .integrations.base import SkillsIntegration as _SkillsCheck
            if isinstance(resolved_integration, _SkillsCheck):
                console.print(
                    "[dim]注意: --ai-skills 不需要; "
                    "技能是此集成的默认模式.[/dim]"
                )
            else:
                console.print(
                    "[dim]注意: --ai-skills 对 "
                    f"{resolved_integration.key} 无效; 此集成使用命令而非技能.[/dim]"
                )
        if ai_commands_dir and resolved_integration.key != "generic":
            console.print(
                "[dim]注意: --ai-commands-dir 已弃用; "
                '请使用 [bold]--integration generic --integration-options="--commands-dir <dir>"[/bold] 代替.[/dim]'
            )

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print("[red]错误:[/red] 不能同时指定项目名称和 --here 标志")
        raise typer.Exit(1)

    if not here and not project_name:
        console.print("[red]错误:[/red] 必须指定项目名称, 使用 '.' 表示当前目录, 或使用 --here 标志")
        raise typer.Exit(1)

    if ai_skills and not ai_assistant:
        console.print("[red]错误:[/red] --ai-skills 需要指定 --ai")
        console.print("[yellow]用法:[/yellow] specify-cn init <项目> --ai <代理> --ai-skills")
        raise typer.Exit(1)

    BRANCH_NUMBERING_CHOICES = {"sequential", "timestamp"}
    if branch_numbering and branch_numbering not in BRANCH_NUMBERING_CHOICES:
        console.print(f"[red]错误:[/red] 无效的 --branch-numbering 值 '{branch_numbering}'. 可选: {', '.join(sorted(BRANCH_NUMBERING_CHOICES))}")
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(f"[yellow]警告:[/yellow] 当前目录非空 ({len(existing_items)} 个项目)")
            console.print("[yellow]模板文件将与现有内容合并, 可能会覆盖已有文件[/yellow]")
            if force:
                console.print("[cyan]已提供 --force: 跳过确认, 直接合并[/cyan]")
            else:
                response = typer.confirm("是否继续?")
                if not response:
                    console.print("[yellow]操作已取消[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"目录 '[cyan]{project_name}[/cyan]' 已存在\n"
                "请选择不同的项目名称或删除已有目录.",
                title="[red]目录冲突[/red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    if ai_assistant:
        if ai_assistant not in AGENT_CONFIG:
            console.print(f"[red]错误:[/red] 无效的 AI 助手 '{ai_assistant}'. 可选: {', '.join(AGENT_CONFIG.keys())}")
            raise typer.Exit(1)
        selected_ai = ai_assistant
    else:
        # Create options dict for selection (agent_key: display_name)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_ai = select_with_arrows(
            ai_choices, 
            "选择 AI 助手:", 
            "copilot"
        )

    # Auto-promote interactively selected agents to the integration path
    if not ai_assistant:
        resolved_integration = get_integration(selected_ai)
        if not resolved_integration:
            console.print(f"[red]错误:[/red] 未知代理 '{selected_ai}'")
            raise typer.Exit(1)

    # Validate --ai-commands-dir usage.
    # Skip validation when --integration-options is provided — the integration
    # will validate its own options in setup().
    if selected_ai == "generic" and not integration_options:
        if not ai_commands_dir:
            console.print("[red]错误:[/red] 使用 --ai generic 或 --integration generic 时需要 --ai-commands-dir")
            console.print('[dim]示例: specify-cn init my-project --integration generic --integration-options="--commands-dir .myagent/commands/"[/dim]')
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify 项目设置[/cyan]",
        "",
        f"{'项目':<15} [green]{project_path.name}[/green]",
        f"{'工作路径':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'目标路径':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print("[yellow]未找到 Git - 将跳过仓库初始化[/yellow]")

    if not ignore_agent_tools:
        agent_config = AGENT_CONFIG.get(selected_ai)
        if agent_config and agent_config["requires_cli"]:
            install_url = agent_config["install_url"]
            if not check_tool(selected_ai):
                error_panel = Panel(
                    f"[cyan]{selected_ai}[/cyan] 未找到\n"
                    f"安装地址: [cyan]{install_url}[/cyan]\n"
                    f"继续此项目类型需要 {agent_config['name']}.\n\n"
                    "提示: 使用 [cyan]--ignore-agent-tools[/cyan] 跳过此检查",
                    title="[red]代理检测错误[/red]",
                    border_style="red",
                    padding=(1, 2)
                )
                console.print()
                console.print(error_panel)
                raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(f"[red]错误:[/red] 无效的脚本类型 '{script_type}'. 可选: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(SCRIPT_TYPE_CHOICES, "选择脚本类型 (或按 Enter)", default_script)
        else:
            selected_script = default_script

    console.print(f"[cyan]已选择 AI 助手:[/cyan] {selected_ai}")
    console.print(f"[cyan]已选择脚本类型:[/cyan] {selected_script}")

    tracker = StepTracker("初始化 Specify 项目")

    sys._specify_tracker_active = True

    tracker.add("precheck", "检查必需工具")
    tracker.complete("precheck", "正常")
    tracker.add("ai-select", "选择 AI 助手")
    tracker.complete("ai-select", f"{selected_ai}")
    tracker.add("script-select", "选择脚本类型")
    tracker.complete("script-select", selected_script)

    tracker.add("integration", "安装集成")
    tracker.add("shared-infra", "安装共享基础设施")

    for key, label in [
        ("chmod", "确保脚本可执行"),
        ("constitution", "章程设置"),
        ("git", "初始化 Git 仓库"),
        ("final", "完成"),
    ]:
        tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            # Integration-based scaffolding
            from .integrations.manifest import IntegrationManifest
            tracker.start("integration")
            manifest = IntegrationManifest(
                resolved_integration.key, project_path, version=get_speckit_version()
            )

            # Forward all legacy CLI flags to the integration as parsed_options.
            # Integrations receive every option and decide what to use;
            # irrelevant keys are simply ignored by the integration's setup().
            integration_parsed_options: dict[str, Any] = {}
            if ai_commands_dir:
                integration_parsed_options["commands_dir"] = ai_commands_dir
            if ai_skills:
                integration_parsed_options["skills"] = True

            resolved_integration.setup(
                project_path, manifest,
                parsed_options=integration_parsed_options or None,
                script_type=selected_script,
                raw_options=integration_options,
            )
            manifest.save()

            # Write .specify/integration.json
            script_ext = "sh" if selected_script == "sh" else "ps1"
            integration_json = project_path / ".specify" / "integration.json"
            integration_json.parent.mkdir(parents=True, exist_ok=True)
            integration_json.write_text(json.dumps({
                "integration": resolved_integration.key,
                "version": get_speckit_version(),
                "scripts": {
                    "update-context": f".specify/integrations/{resolved_integration.key}/scripts/update-context.{script_ext}",
                },
            }, indent=2) + "\n", encoding="utf-8")

            tracker.complete("integration", resolved_integration.config.get("name", resolved_integration.key))

            # Install shared infrastructure (scripts, templates)
            tracker.start("shared-infra")
            _install_shared_infra(project_path, selected_script, tracker=tracker)
            tracker.complete("shared-infra", f"脚本 ({selected_script}) + 模板")

            ensure_executable_scripts(project_path, tracker=tracker)

            ensure_constitution_from_template(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "检测到已有仓库")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "已初始化")
                    else:
                        tracker.error("git", "初始化失败")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "Git 不可用")
            else:
                tracker.skip("git", "--no-git 标志")

            # Persist the CLI options so later operations (e.g. preset add)
            # can adapt their behaviour without re-scanning the filesystem.
            # Must be saved BEFORE preset install so _get_skills_dir() works.
            init_opts = {
                "ai": selected_ai,
                "integration": resolved_integration.key,
                "branch_numbering": branch_numbering or "sequential",
                "here": here,
                "preset": preset,
                "script": selected_script,
                "speckit_version": get_speckit_version(),
            }
            # Ensure ai_skills is set for SkillsIntegration so downstream
            # tools (extensions, presets) emit SKILL.md overrides correctly.
            from .integrations.base import SkillsIntegration as _SkillsPersist
            if isinstance(resolved_integration, _SkillsPersist):
                init_opts["ai_skills"] = True
            save_init_options(project_path, init_opts)

            # Install preset if specified
            if preset:
                try:
                    from .presets import PresetManager, PresetCatalog, PresetError
                    preset_manager = PresetManager(project_path)
                    speckit_ver = get_speckit_version()

                    # Try local directory first, then catalog
                    local_path = Path(preset).resolve()
                    if local_path.is_dir() and (local_path / "preset.yml").exists():
                        preset_manager.install_from_directory(local_path, speckit_ver)
                    else:
                        preset_catalog = PresetCatalog(project_path)
                        pack_info = preset_catalog.get_pack_info(preset)
                        if not pack_info:
                            console.print(f"[yellow]警告:[/yellow] 预设 '{preset}' 未在目录中找到. 已跳过.")
                        else:
                            try:
                                zip_path = preset_catalog.download_pack(preset)
                                preset_manager.install_from_zip(zip_path, speckit_ver)
                                # Clean up downloaded ZIP to avoid cache accumulation
                                try:
                                    zip_path.unlink(missing_ok=True)
                                except OSError:
                                    # Best-effort cleanup; failure to delete is non-fatal
                                    pass
                            except PresetError as preset_err:
                                console.print(f"[yellow]警告:[/yellow] 安装预设 '{preset}' 失败: {preset_err}")
                except Exception as preset_err:
                    console.print(f"[yellow]警告:[/yellow] 安装预设失败: {preset_err}")

            tracker.complete("final", "项目就绪")
        except (typer.Exit, SystemExit):
            raise
        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"初始化失败: {e}", title="失败", border_style="red"))
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]" for k, v in _env_pairs]
                console.print(Panel("\n".join(env_lines), title="调试环境", border_style="magenta"))
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]项目就绪.[/bold green]")
    
    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]警告:[/yellow] Git 仓库初始化失败\n\n"
            f"{git_error_message}\n\n"
            f"[dim]你可以稍后手动初始化 Git:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f"[cyan]git commit -m \"Initial commit\"[/cyan]",
            title="[red]Git 初始化失败[/red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(git_error_panel)

    # Agent folder security notice
    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = ai_commands_dir if selected_ai == "generic" else agent_config["folder"]
        if agent_folder:
            security_notice = Panel(
                f"部分代理可能会在项目中的代理文件夹内存储凭据、认证令牌或其他身份和私有信息.\n"
                f"建议将 [cyan]{agent_folder}[/cyan] (或其中部分) 添加到 [cyan].gitignore[/cyan] 以防止意外泄露凭据.",
                title="[yellow]代理文件夹安全提示[/yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print()
            console.print(security_notice)

    steps_lines = []
    if not here:
        steps_lines.append(f"1. 进入项目目录: [cyan]cd {project_name}[/cyan]")
        step_num = 2
    else:
        steps_lines.append("1. 你已在项目目录中!")
        step_num = 2

    # Determine skill display mode for the next-steps panel.
    # Skills integrations (codex, kimi, agy) should show skill invocation syntax.
    from .integrations.base import SkillsIntegration as _SkillsInt
    _is_skills_integration = isinstance(resolved_integration, _SkillsInt)

    codex_skill_mode = selected_ai == "codex" and (ai_skills or _is_skills_integration)
    claude_skill_mode = selected_ai == "claude" and (ai_skills or _is_skills_integration)
    kimi_skill_mode = selected_ai == "kimi"
    agy_skill_mode = selected_ai == "agy" and _is_skills_integration
    native_skill_mode = codex_skill_mode or claude_skill_mode or kimi_skill_mode or agy_skill_mode

    if codex_skill_mode and not ai_skills:
        # Integration path installed skills; show the helpful notice
        steps_lines.append(f"{step_num}. 在此项目目录中启动 Codex; spec-kit 技能已安装到 [cyan].agents/skills[/cyan]")
        step_num += 1
    if claude_skill_mode and not ai_skills:
        steps_lines.append(f"{step_num}. 在此项目目录中启动 Claude; spec-kit 技能已安装到 [cyan].claude/skills[/cyan]")
        step_num += 1
    usage_label = "技能" if native_skill_mode else "斜杠命令"

    def _display_cmd(name: str) -> str:
        if codex_skill_mode or agy_skill_mode:
            return f"$speckit-{name}"
        if claude_skill_mode:
            return f"/speckit-{name}"
        if kimi_skill_mode:
            return f"/skill:speckit-{name}"
        return f"/speckit.{name}"

    steps_lines.append(f"{step_num}. 开始使用 {usage_label} 与你的 AI 代理交互:")

    steps_lines.append(f"   {step_num}.1 [cyan]{_display_cmd('constitution')}[/] - 建立项目原则")
    steps_lines.append(f"   {step_num}.2 [cyan]{_display_cmd('specify')}[/] - 创建基线规范")
    steps_lines.append(f"   {step_num}.3 [cyan]{_display_cmd('plan')}[/] - 创建实施计划")
    steps_lines.append(f"   {step_num}.4 [cyan]{_display_cmd('tasks')}[/] - 生成可执行任务")
    steps_lines.append(f"   {step_num}.5 [cyan]{_display_cmd('implement')}[/] - 执行实施")

    steps_panel = Panel("\n".join(steps_lines), title="后续步骤", border_style="cyan", padding=(1,2))
    console.print()
    console.print(steps_panel)

    enhancement_intro = (
        "可选技能, 用于提升规范质量 [bright_black](提高质量和可信度)[/bright_black]"
        if native_skill_mode
        else "可选命令, 用于提升规范质量 [bright_black](提高质量和可信度)[/bright_black]"
    )
    enhancement_lines = [
        enhancement_intro,
        "",
        f"○ [cyan]{_display_cmd('clarify')}[/] [bright_black](可选)[/bright_black] - 在规划前提出结构化问题以降低风险 (如需使用, 在 [cyan]{_display_cmd('plan')}[/] 之前运行)",
        f"○ [cyan]{_display_cmd('analyze')}[/] [bright_black](可选)[/bright_black] - 跨制品一致性与对齐报告 (在 [cyan]{_display_cmd('tasks')}[/] 之后, [cyan]{_display_cmd('implement')}[/] 之前)",
        f"○ [cyan]{_display_cmd('checklist')}[/] [bright_black](可选)[/bright_black] - 生成质量检查清单以验证需求的完整性、清晰度和一致性 (在 [cyan]{_display_cmd('plan')}[/] 之后)"
    ]
    enhancements_title = "增强技能" if native_skill_mode else "增强命令"
    enhancements_panel = Panel("\n".join(enhancement_lines), title=enhancements_title, border_style="cyan", padding=(1,2))
    console.print()
    console.print(enhancements_panel)

@app.command()
def check():
    """检查所有必需工具是否已安装."""
    show_banner()
    console.print("[bold]正在检查已安装的工具...[/bold]\n")

    tracker = StepTracker("检查可用工具")

    tracker.add("git", "Git 版本控制")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        if agent_key == "generic":
            continue  # Generic is not a real agent to check
        agent_name = agent_config["name"]
        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:
            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
        else:
            # IDE-based agent - skip CLI check and mark as optional
            tracker.skip(agent_key, "基于 IDE, 无需 CLI 检查")
            agent_results[agent_key] = False  # Don't count IDE agents as "found"

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    check_tool("code-insiders", tracker=tracker)

    console.print(tracker.render())

    console.print("\n[bold green]Specify CN CLI 已就绪![/bold green]")

    if not git_ok:
        console.print("[dim]提示: 安装 Git 以管理仓库[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]提示: 安装 AI 助手以获得最佳体验[/dim]")

@app.command()
def version():
    """显示版本和系统信息."""
    import platform
    import importlib.metadata
    
    show_banner()
    
    # Get CLI version from package metadata
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("specify-cn-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml if running from source
        try:
            import tomllib
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass
    
    # Fetch latest template release version
    repo_owner = "linfee"
    repo_name = "spec-kit-cn"
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    template_version = "unknown"
    release_date = "unknown"
    
    try:
        response = client.get(
            api_url,
            timeout=10,
            follow_redirects=True,
            headers=_github_auth_headers(),
        )
        if response.status_code == 200:
            release_data = response.json()
            template_version = release_data.get("tag_name", "unknown")
            # Remove 'v' prefix if present
            if template_version.startswith("v"):
                template_version = template_version[1:]
            release_date = release_data.get("published_at", "unknown")
            if release_date != "unknown":
                # Format the date nicely
                try:
                    dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                    release_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
    except Exception:
        pass

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="cyan", justify="right")
    info_table.add_column("Value", style="white")

    info_table.add_row("CLI 版本", cli_version)
    info_table.add_row("模板版本", template_version)
    info_table.add_row("发布日期", release_date)
    info_table.add_row("", "")
    info_table.add_row("Python", platform.python_version())
    info_table.add_row("平台", platform.system())
    info_table.add_row("架构", platform.machine())
    info_table.add_row("操作系统版本", platform.version())

    panel = Panel(
        info_table,
        title="[bold cyan]Specify CN CLI 信息[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )

    console.print(panel)
    console.print()


# ===== Extension Commands =====

extension_app = typer.Typer(
    name="extension",
    help="管理 spec-kit 扩展",
    add_completion=False,
)
app.add_typer(extension_app, name="extension")

catalog_app = typer.Typer(
    name="catalog",
    help="管理扩展目录",
    add_completion=False,
)
extension_app.add_typer(catalog_app, name="catalog")

preset_app = typer.Typer(
    name="preset",
    help="管理 spec-kit 预设",
    add_completion=False,
)
app.add_typer(preset_app, name="preset")

preset_catalog_app = typer.Typer(
    name="catalog",
    help="管理预设目录",
    add_completion=False,
)
preset_app.add_typer(preset_catalog_app, name="catalog")


def get_speckit_version() -> str:
    """Get current spec-kit version."""
    import importlib.metadata
    try:
        return importlib.metadata.version("specify-cn-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml
        try:
            import tomllib
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown")
        except Exception:
            # Intentionally ignore any errors while reading/parsing pyproject.toml.
            # If this lookup fails for any reason, we fall back to returning "unknown" below.
            pass
    return "unknown"


# ===== Preset Commands =====


@preset_app.command("list")
def preset_list():
    """列出已安装的预设."""
    from .presets import PresetManager

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = PresetManager(project_root)
    installed = manager.list_installed()

    if not installed:
        console.print("[yellow]未安装任何预设.[/yellow]")
        console.print("\n安装预设:")
        console.print("  [cyan]specify-cn preset add <预设名称>[/cyan]")
        return

    console.print("\n[bold cyan]已安装的预设:[/bold cyan]\n")
    for pack in installed:
        status = "[green]已启用[/green]" if pack.get("enabled", True) else "[red]已禁用[/red]"
        pri = pack.get('priority', 10)
        console.print(f"  [bold]{pack['name']}[/bold] ({pack['id']}) v{pack['version']} — {status} — 优先级 {pri}")
        console.print(f"    {pack['description']}")
        if pack.get("tags"):
            tags_str = ", ".join(pack["tags"])
            console.print(f"    [dim]标签: {tags_str}[/dim]")
        console.print(f"    [dim]模板: {pack['template_count']}[/dim]")
        console.print()


@preset_app.command("add")
def preset_add(
    pack_id: str = typer.Argument(None, help="要从目录安装的预设 ID"),
    from_url: str = typer.Option(None, "--from", help="从 URL 安装 (ZIP 文件)"),
    dev: str = typer.Option(None, "--dev", help="从本地目录安装 (开发模式)"),
    priority: int = typer.Option(10, "--priority", help="解析优先级 (数值越小优先级越高, 默认 10)"),
):
    """安装预设."""
    from .presets import (
        PresetManager,
        PresetCatalog,
        PresetError,
        PresetValidationError,
        PresetCompatibilityError,
    )

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate priority
    if priority < 1:
        console.print("[red]错误:[/red] 优先级必须为正整数 (1 或更大)")
        raise typer.Exit(1)

    manager = PresetManager(project_root)
    speckit_version = get_speckit_version()

    try:
        if dev:
            dev_path = Path(dev).resolve()
            if not dev_path.exists():
                console.print(f"[red]错误:[/red] 目录未找到: {dev}")
                raise typer.Exit(1)

            console.print(f"正在从 [cyan]{dev_path}[/cyan] 安装预设...")
            manifest = manager.install_from_directory(dev_path, speckit_version, priority)
            console.print(f"[green]✓[/green] 预设 '{manifest.name}' v{manifest.version} 已安装 (优先级 {priority})")

        elif from_url:
            # Validate URL scheme before downloading
            from urllib.parse import urlparse as _urlparse
            _parsed = _urlparse(from_url)
            _is_localhost = _parsed.hostname in ("localhost", "127.0.0.1", "::1")
            if _parsed.scheme != "https" and not (_parsed.scheme == "http" and _is_localhost):
                console.print(f"[red]错误:[/red] URL 必须使用 HTTPS (当前为 {_parsed.scheme}://). 仅允许 localhost 使用 HTTP.")
                raise typer.Exit(1)

            console.print(f"正在从 [cyan]{from_url}[/cyan] 安装预设...")
            import urllib.request
            import urllib.error
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = Path(tmpdir) / "preset.zip"
                try:
                    with urllib.request.urlopen(from_url, timeout=60) as response:
                        zip_path.write_bytes(response.read())
                except urllib.error.URLError as e:
                    console.print(f"[red]错误:[/red] 下载失败: {e}")
                    raise typer.Exit(1)

                manifest = manager.install_from_zip(zip_path, speckit_version, priority)

            console.print(f"[green]✓[/green] 预设 '{manifest.name}' v{manifest.version} 已安装 (优先级 {priority})")

        elif pack_id:
            catalog = PresetCatalog(project_root)
            pack_info = catalog.get_pack_info(pack_id)

            if not pack_info:
                console.print(f"[red]错误:[/red] 目录中未找到预设 '{pack_id}'")
                raise typer.Exit(1)

            if not pack_info.get("_install_allowed", True):
                catalog_name = pack_info.get("_catalog_name", "unknown")
                console.print(f"[red]错误:[/red] 预设 '{pack_id}' 来自 '{catalog_name}' 目录, 该目录仅用于浏览 (不允许安装).")
                console.print("请添加带有 --install-allowed 的目录, 或使用 --from 直接从预设仓库安装.")
                raise typer.Exit(1)

            console.print(f"正在安装预设 [cyan]{pack_info.get('name', pack_id)}[/cyan]...")

            try:
                zip_path = catalog.download_pack(pack_id)
                manifest = manager.install_from_zip(zip_path, speckit_version, priority)
                console.print(f"[green]✓[/green] 预设 '{manifest.name}' v{manifest.version} 已安装 (优先级 {priority})")
            finally:
                if 'zip_path' in locals() and zip_path.exists():
                    zip_path.unlink(missing_ok=True)
        else:
            console.print("[red]错误:[/red] 请指定预设 ID, --from URL 或 --dev 路径")
            raise typer.Exit(1)

    except PresetCompatibilityError as e:
        console.print(f"[red]兼容性错误:[/red] {e}")
        raise typer.Exit(1)
    except PresetValidationError as e:
        console.print(f"[red]验证错误:[/red] {e}")
        raise typer.Exit(1)
    except PresetError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)


@preset_app.command("remove")
def preset_remove(
    pack_id: str = typer.Argument(..., help="要移除的预设 ID"),
):
    """移除已安装的预设."""
    from .presets import PresetManager

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = PresetManager(project_root)

    if not manager.registry.is_installed(pack_id):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未安装")
        raise typer.Exit(1)

    if manager.remove(pack_id):
        console.print(f"[green]✓[/green] 预设 '{pack_id}' 已成功移除")
    else:
        console.print(f"[red]错误:[/red] 移除预设 '{pack_id}' 失败")
        raise typer.Exit(1)


@preset_app.command("search")
def preset_search(
    query: str = typer.Argument(None, help="搜索查询"),
    tag: str = typer.Option(None, "--tag", help="按标签筛选"),
    author: str = typer.Option(None, "--author", help="按作者筛选"),
):
    """在目录中搜索预设."""
    from .presets import PresetCatalog, PresetError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    catalog = PresetCatalog(project_root)

    try:
        results = catalog.search(query=query, tag=tag, author=author)
    except PresetError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]未找到匹配条件的预设.[/yellow]")
        return

    console.print(f"\n[bold cyan]预设 (找到 {len(results)} 个):[/bold cyan]\n")
    for pack in results:
        console.print(f"  [bold]{pack.get('name', pack['id'])}[/bold] ({pack['id']}) v{pack.get('version', '?')}")
        console.print(f"    {pack.get('description', '')}")
        if pack.get("tags"):
            tags_str = ", ".join(pack["tags"])
            console.print(f"    [dim]标签: {tags_str}[/dim]")
        console.print()


@preset_app.command("resolve")
def preset_resolve(
    template_name: str = typer.Argument(..., help="要解析的模板名称 (例如 spec-template)"),
):
    """显示给定名称的模板解析结果."""
    from .presets import PresetResolver

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    resolver = PresetResolver(project_root)
    result = resolver.resolve_with_source(template_name)

    if result:
        console.print(f"  [bold]{template_name}[/bold]: {result['path']}")
        console.print(f"    [dim](from: {result['source']})[/dim]")
    else:
        console.print(f"  [yellow]{template_name}[/yellow]: 未找到")
        console.print("    [dim]解析栈中不存在此名称的模板[/dim]")


@preset_app.command("info")
def preset_info(
    pack_id: str = typer.Argument(..., help="要查看信息的预设 ID"),
):
    """显示预设的详细信息."""
    from .extensions import normalize_priority
    from .presets import PresetCatalog, PresetManager, PresetError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Check if installed locally first
    manager = PresetManager(project_root)
    local_pack = manager.get_pack(pack_id)

    if local_pack:
        console.print(f"\n[bold cyan]预设: {local_pack.name}[/bold cyan]\n")
        console.print(f"  ID:          {local_pack.id}")
        console.print(f"  版本:        {local_pack.version}")
        console.print(f"  描述:        {local_pack.description}")
        if local_pack.author:
            console.print(f"  作者:        {local_pack.author}")
        if local_pack.tags:
            console.print(f"  标签:        {', '.join(local_pack.tags)}")
        console.print(f"  模板:        {len(local_pack.templates)}")
        for tmpl in local_pack.templates:
            console.print(f"    - {tmpl['name']} ({tmpl['type']}): {tmpl.get('description', '')}")
        repo = local_pack.data.get("preset", {}).get("repository")
        if repo:
            console.print(f"  仓库:        {repo}")
        license_val = local_pack.data.get("preset", {}).get("license")
        if license_val:
            console.print(f"  许可证:      {license_val}")
        console.print("\n  [green]状态: 已安装[/green]")
        # Get priority from registry
        pack_metadata = manager.registry.get(pack_id)
        priority = normalize_priority(pack_metadata.get("priority") if isinstance(pack_metadata, dict) else None)
        console.print(f"  [dim]优先级:[/dim] {priority}")
        console.print()
        return

    # Fall back to catalog
    catalog = PresetCatalog(project_root)
    try:
        pack_info = catalog.get_pack_info(pack_id)
    except PresetError:
        pack_info = None

    if not pack_info:
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未找到 (未安装且不在目录中)")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]预设: {pack_info.get('name', pack_id)}[/bold cyan]\n")
    console.print(f"  ID:          {pack_info['id']}")
    console.print(f"  版本:        {pack_info.get('version', '?')}")
    console.print(f"  描述:        {pack_info.get('description', '')}")
    if pack_info.get("author"):
        console.print(f"  作者:        {pack_info['author']}")
    if pack_info.get("tags"):
        console.print(f"  标签:        {', '.join(pack_info['tags'])}")
    if pack_info.get("repository"):
        console.print(f"  仓库:        {pack_info['repository']}")
    if pack_info.get("license"):
        console.print(f"  许可证:      {pack_info['license']}")
    console.print("\n  [yellow]状态: 未安装[/yellow]")
    console.print(f"  安装: [cyan]specify-cn preset add {pack_id}[/cyan]")
    console.print()


@preset_app.command("set-priority")
def preset_set_priority(
    pack_id: str = typer.Argument(help="预设 ID"),
    priority: int = typer.Argument(help="新优先级 (数值越小优先级越高)"),
):
    """设置已安装预设的解析优先级."""
    from .presets import PresetManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate priority
    if priority < 1:
        console.print("[red]错误:[/red] 优先级必须为正整数 (1 或更大)")
        raise typer.Exit(1)

    manager = PresetManager(project_root)

    # Check if preset is installed
    if not manager.registry.is_installed(pack_id):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未安装")
        raise typer.Exit(1)

    # Get current metadata
    metadata = manager.registry.get(pack_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未在注册表中找到(状态损坏)")
        raise typer.Exit(1)

    from .extensions import normalize_priority
    raw_priority = metadata.get("priority")
    # Only skip if the stored value is already a valid int equal to requested priority
    # This ensures corrupted values (e.g., "high") get repaired even when setting to default (10)
    if isinstance(raw_priority, int) and raw_priority == priority:
        console.print(f"[yellow]预设 '{pack_id}' 的优先级已经是 {priority}[/yellow]")
        raise typer.Exit(0)

    old_priority = normalize_priority(raw_priority)

    # Update priority
    manager.registry.update(pack_id, {"priority": priority})

    console.print(f"[green]✓[/green] 预设 '{pack_id}' 优先级已更改: {old_priority} → {priority}")
    console.print("\n[dim]优先级数值越小 = 模板解析时优先级越高[/dim]")


@preset_app.command("enable")
def preset_enable(
    pack_id: str = typer.Argument(help="要启用的预设 ID"),
):
    """启用已禁用的预设."""
    from .presets import PresetManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = PresetManager(project_root)

    # Check if preset is installed
    if not manager.registry.is_installed(pack_id):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未安装")
        raise typer.Exit(1)

    # Get current metadata
    metadata = manager.registry.get(pack_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未在注册表中找到(状态损坏)")
        raise typer.Exit(1)

    if metadata.get("enabled", True):
        console.print(f"[yellow]预设 '{pack_id}' 已处于启用状态[/yellow]")
        raise typer.Exit(0)

    # Enable the preset
    manager.registry.update(pack_id, {"enabled": True})

    console.print(f"[green]✓[/green] 预设 '{pack_id}' 已启用")
    console.print("\n此预设的模板将纳入解析.")
    console.print("[dim]注意: 之前注册的命令/技能仍然有效.[/dim]")


@preset_app.command("disable")
def preset_disable(
    pack_id: str = typer.Argument(help="要禁用的预设 ID"),
):
    """禁用预设但不移除."""
    from .presets import PresetManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = PresetManager(project_root)

    # Check if preset is installed
    if not manager.registry.is_installed(pack_id):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未安装")
        raise typer.Exit(1)

    # Get current metadata
    metadata = manager.registry.get(pack_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 预设 '{pack_id}' 未在注册表中找到(状态损坏)")
        raise typer.Exit(1)

    if not metadata.get("enabled", True):
        console.print(f"[yellow]预设 '{pack_id}' 已处于禁用状态[/yellow]")
        raise typer.Exit(0)

    # Disable the preset
    manager.registry.update(pack_id, {"enabled": False})

    console.print(f"[green]✓[/green] 预设 '{pack_id}' 已禁用")
    console.print("\n此预设的模板在解析时将被跳过.")
    console.print("[dim]注意: 之前注册的命令/技能在预设移除前仍然有效.[/dim]")
    console.print(f"重新启用: specify-cn preset enable {pack_id}")


# ===== Preset Catalog Commands =====


@preset_catalog_app.command("list")
def preset_catalog_list():
    """列出所有活跃的预设目录."""
    from .presets import PresetCatalog, PresetValidationError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    catalog = PresetCatalog(project_root)

    try:
        active_catalogs = catalog.get_active_catalogs()
    except PresetValidationError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold cyan]活跃的预设目录:[/bold cyan]\n")
    for entry in active_catalogs:
        install_str = (
            "[green]允许安装[/green]"
            if entry.install_allowed
            else "[yellow]仅浏览[/yellow]"
        )
        console.print(f"  [bold]{entry.name}[/bold] (priority {entry.priority})")
        if entry.description:
            console.print(f"     {entry.description}")
        console.print(f"     URL: {entry.url}")
        console.print(f"     安装: {install_str}")
        console.print()

    config_path = project_root / ".specify" / "preset-catalogs.yml"
    user_config_path = Path.home() / ".specify" / "preset-catalogs.yml"
    if os.environ.get("SPECKIT_PRESET_CATALOG_URL"):
        console.print("[dim]目录通过 SPECKIT_PRESET_CATALOG_URL 环境变量配置.[/dim]")
    else:
        try:
            proj_loaded = config_path.exists() and catalog._load_catalog_config(config_path) is not None
        except PresetValidationError:
            proj_loaded = False
        if proj_loaded:
            console.print(f"[dim]配置: {config_path.relative_to(project_root)}[/dim]")
        else:
            try:
                user_loaded = user_config_path.exists() and catalog._load_catalog_config(user_config_path) is not None
            except PresetValidationError:
                user_loaded = False
            if user_loaded:
                console.print("[dim]配置: ~/.specify/preset-catalogs.yml[/dim]")
            else:
                console.print("[dim]使用内置默认目录栈.[/dim]")
                console.print(
                    "[dim]添加 .specify/preset-catalogs.yml 以自定义.[/dim]"
                )


@preset_catalog_app.command("add")
def preset_catalog_add(
    url: str = typer.Argument(help="目录 URL (必须使用 HTTPS)"),
    name: str = typer.Option(..., "--name", help="目录名称"),
    priority: int = typer.Option(10, "--priority", help="优先级 (数值越小优先级越高)"),
    install_allowed: bool = typer.Option(
        False, "--install-allowed/--no-install-allowed",
        help="允许从此目录安装预设",
    ),
    description: str = typer.Option("", "--description", help="目录描述"),
):
    """添加目录到 .specify/preset-catalogs.yml."""
    from .presets import PresetCatalog, PresetValidationError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate URL
    tmp_catalog = PresetCatalog(project_root)
    try:
        tmp_catalog._validate_catalog_url(url)
    except PresetValidationError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)

    config_path = specify_dir / "preset-catalogs.yml"

    # Load existing config
    if config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            console.print(f"[red]错误:[/red] 读取 {config_path} 失败: {e}")
            raise typer.Exit(1)
    else:
        config = {}

    catalogs = config.get("catalogs", [])
    if not isinstance(catalogs, list):
        console.print("[red]错误:[/red] 无效的目录配置: 'catalogs' 必须为列表.")
        raise typer.Exit(1)

    # Check for duplicate name
    for existing in catalogs:
        if isinstance(existing, dict) and existing.get("name") == name:
            console.print(f"[yellow]警告:[/yellow] 名为 '{name}' 的目录已存在.")
            console.print("请先使用 'specify-cn preset catalog remove' 移除, 或选择其他名称.")
            raise typer.Exit(1)

    catalogs.append({
        "name": name,
        "url": url,
        "priority": priority,
        "install_allowed": install_allowed,
        "description": description,
    })

    config["catalogs"] = catalogs
    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True), encoding="utf-8")

    install_label = "允许安装" if install_allowed else "仅浏览"
    console.print(f"\n[green]✓[/green] 已添加目录 '[bold]{name}[/bold]' ({install_label})")
    console.print(f"  URL: {url}")
    console.print(f"  优先级: {priority}")
    console.print(f"\n配置已保存到 {config_path.relative_to(project_root)}")


@preset_catalog_app.command("remove")
def preset_catalog_remove(
    name: str = typer.Argument(help="要移除的目录名称"),
):
    """从 .specify/preset-catalogs.yml 移除目录."""
    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    config_path = specify_dir / "preset-catalogs.yml"
    if not config_path.exists():
        console.print("[red]错误:[/red] 未找到预设目录配置, 无内容可移除.")
        raise typer.Exit(1)

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        console.print("[red]错误:[/red] 读取预设目录配置失败.")
        raise typer.Exit(1)

    catalogs = config.get("catalogs", [])
    if not isinstance(catalogs, list):
        console.print("[red]错误:[/red] 无效的目录配置: 'catalogs' 必须为列表.")
        raise typer.Exit(1)
    original_count = len(catalogs)
    catalogs = [c for c in catalogs if isinstance(c, dict) and c.get("name") != name]

    if len(catalogs) == original_count:
        console.print(f"[red]错误:[/red] 目录 '{name}' 未找到.")
        raise typer.Exit(1)

    config["catalogs"] = catalogs
    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True), encoding="utf-8")

    console.print(f"[green]✓[/green] 已移除目录 '{name}'")
    if not catalogs:
        console.print("\n[dim]配置中无剩余目录, 将使用内置默认值.[/dim]")


# ===== Extension Commands =====


def _resolve_installed_extension(
    argument: str,
    installed_extensions: list,
    command_name: str = "command",
    allow_not_found: bool = False,
) -> tuple[Optional[str], Optional[str]]:
    """Resolve an extension argument (ID or display name) to an installed extension.

    Args:
        argument: Extension ID or display name provided by user
        installed_extensions: List of installed extension dicts from manager.list_installed()
        command_name: Name of the command for error messages (e.g., "enable", "disable")
        allow_not_found: If True, return (None, None) when not found instead of raising

    Returns:
        Tuple of (extension_id, display_name), or (None, None) if allow_not_found=True and not found

    Raises:
        typer.Exit: If extension not found (and allow_not_found=False) or name is ambiguous
    """
    from rich.table import Table

    # First, try exact ID match
    for ext in installed_extensions:
        if ext["id"] == argument:
            return (ext["id"], ext["name"])

    # If not found by ID, try display name match
    name_matches = [ext for ext in installed_extensions if ext["name"].lower() == argument.lower()]

    if len(name_matches) == 1:
        # Unique display-name match
        return (name_matches[0]["id"], name_matches[0]["name"])
    elif len(name_matches) > 1:
        # Ambiguous display-name match
        console.print(
            f"[red]错误:[/red] 扩展名称 '{argument}' 存在歧义. "
            "多个已安装的扩展共享此名称:"
        )
        table = Table(title="匹配的扩展")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("名称", style="white")
        table.add_column("版本", style="green")
        for ext in name_matches:
            table.add_row(ext.get("id", ""), ext.get("name", ""), str(ext.get("version", "")))
        console.print(table)
        console.print("\n请使用扩展 ID 重新运行:")
        console.print(f"  [bold]specify-cn extension {command_name} <扩展 ID>[/bold]")
        raise typer.Exit(1)
    else:
        # No match by ID or display name
        if allow_not_found:
            return (None, None)
        console.print(f"[red]错误:[/red] 扩展 '{argument}' 未安装")
        raise typer.Exit(1)


def _resolve_catalog_extension(
    argument: str,
    catalog,
    command_name: str = "info",
) -> tuple[Optional[dict], Optional[Exception]]:
    """Resolve an extension argument (ID or display name) from the catalog.

    Args:
        argument: Extension ID or display name provided by user
        catalog: ExtensionCatalog instance
        command_name: Name of the command for error messages

    Returns:
        Tuple of (extension_info, catalog_error)
        - If found: (ext_info_dict, None)
        - If catalog error: (None, error)
        - If not found: (None, None)
    """
    from rich.table import Table
    from .extensions import ExtensionError

    try:
        # First try by ID
        ext_info = catalog.get_extension_info(argument)
        if ext_info:
            return (ext_info, None)

        # Try by display name - search using argument as query, then filter for exact match
        search_results = catalog.search(query=argument)
        name_matches = [ext for ext in search_results if ext["name"].lower() == argument.lower()]

        if len(name_matches) == 1:
            return (name_matches[0], None)
        elif len(name_matches) > 1:
            # Ambiguous display-name match in catalog
            console.print(
                f"[red]错误:[/red] 扩展名称 '{argument}' 存在歧义. "
                "多个目录中的扩展共享此名称:"
            )
            table = Table(title="匹配的扩展")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("名称", style="white")
            table.add_column("版本", style="green")
            table.add_column("目录", style="dim")
            for ext in name_matches:
                table.add_row(
                    ext.get("id", ""),
                    ext.get("name", ""),
                    str(ext.get("version", "")),
                    ext.get("_catalog_name", ""),
                )
            console.print(table)
            console.print("\n请使用扩展 ID 重新运行:")
            console.print(f"  [bold]specify-cn extension {command_name} <扩展 ID>[/bold]")
            raise typer.Exit(1)

        # Not found
        return (None, None)

    except ExtensionError as e:
        return (None, e)


@extension_app.command("list")
def extension_list(
    available: bool = typer.Option(False, "--available", help="显示目录中可用的扩展"),
    all_extensions: bool = typer.Option(False, "--all", help="同时显示已安装和可用的扩展"),
):
    """列出已安装的扩展."""
    from .extensions import ExtensionManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)
    installed = manager.list_installed()

    if not installed and not (available or all_extensions):
        console.print("[yellow]未安装任何扩展.[/yellow]")
        console.print("\n安装扩展:")
        console.print("  specify-cn extension add <扩展名称>")
        return

    if installed:
        console.print("\n[bold cyan]已安装的扩展:[/bold cyan]\n")

        for ext in installed:
            status_icon = "✓" if ext["enabled"] else "✗"
            status_color = "green" if ext["enabled"] else "red"

            console.print(f"  [{status_color}]{status_icon}[/{status_color}] [bold]{ext['name']}[/bold] (v{ext['version']})")
            console.print(f"     [dim]{ext['id']}[/dim]")
            console.print(f"     {ext['description']}")
            console.print(f"     命令: {ext['command_count']} | 钩子: {ext['hook_count']} | 优先级: {ext['priority']} | 状态: {'已启用' if ext['enabled'] else '已禁用'}")
            console.print()

    if available or all_extensions:
        console.print("\n安装扩展:")
        console.print("  [cyan]specify-cn extension add <名称>[/cyan]")


@catalog_app.command("list")
def catalog_list():
    """列出所有活跃的扩展目录."""
    from .extensions import ExtensionCatalog, ValidationError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    catalog = ExtensionCatalog(project_root)

    try:
        active_catalogs = catalog.get_active_catalogs()
    except ValidationError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)

    console.print("\n[bold cyan]活跃的扩展目录:[/bold cyan]\n")
    for entry in active_catalogs:
        install_str = (
            "[green]允许安装[/green]"
            if entry.install_allowed
            else "[yellow]仅浏览[/yellow]"
        )
        console.print(f"  [bold]{entry.name}[/bold] (priority {entry.priority})")
        if entry.description:
            console.print(f"     {entry.description}")
        console.print(f"     URL: {entry.url}")
        console.print(f"     安装: {install_str}")
        console.print()

    config_path = project_root / ".specify" / "extension-catalogs.yml"
    user_config_path = Path.home() / ".specify" / "extension-catalogs.yml"
    if os.environ.get("SPECKIT_CATALOG_URL"):
        console.print("[dim]目录通过 SPECKIT_CATALOG_URL 环境变量配置.[/dim]")
    else:
        try:
            proj_loaded = config_path.exists() and catalog._load_catalog_config(config_path) is not None
        except ValidationError:
            proj_loaded = False
        if proj_loaded:
            console.print(f"[dim]配置: {config_path.relative_to(project_root)}[/dim]")
        else:
            try:
                user_loaded = user_config_path.exists() and catalog._load_catalog_config(user_config_path) is not None
            except ValidationError:
                user_loaded = False
            if user_loaded:
                console.print("[dim]配置: ~/.specify/extension-catalogs.yml[/dim]")
            else:
                console.print("[dim]使用内置默认目录栈.[/dim]")
                console.print(
                    "[dim]添加 .specify/extension-catalogs.yml 以自定义.[/dim]"
                )


@catalog_app.command("add")
def catalog_add(
    url: str = typer.Argument(help="目录 URL (必须使用 HTTPS)"),
    name: str = typer.Option(..., "--name", help="目录名称"),
    priority: int = typer.Option(10, "--priority", help="优先级 (数值越小优先级越高)"),
    install_allowed: bool = typer.Option(
        False, "--install-allowed/--no-install-allowed",
        help="允许从此目录安装扩展",
    ),
    description: str = typer.Option("", "--description", help="目录描述"),
):
    """添加目录到 .specify/extension-catalogs.yml."""
    from .extensions import ExtensionCatalog, ValidationError

    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate URL
    tmp_catalog = ExtensionCatalog(project_root)
    try:
        tmp_catalog._validate_catalog_url(url)
    except ValidationError as e:
        console.print(f"[red]错误:[/red] {e}")
        raise typer.Exit(1)

    config_path = specify_dir / "extension-catalogs.yml"

    # Load existing config
    if config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            console.print(f"[red]错误:[/red] 读取 {config_path} 失败: {e}")
            raise typer.Exit(1)
    else:
        config = {}

    catalogs = config.get("catalogs", [])
    if not isinstance(catalogs, list):
        console.print("[red]错误:[/red] 无效的目录配置: 'catalogs' 必须为列表.")
        raise typer.Exit(1)

    # Check for duplicate name
    for existing in catalogs:
        if isinstance(existing, dict) and existing.get("name") == name:
            console.print(f"[yellow]警告:[/yellow] 名为 '{name}' 的目录已存在.")
            console.print("请先使用 'specify-cn extension catalog remove' 移除, 或选择其他名称.")
            raise typer.Exit(1)

    catalogs.append({
        "name": name,
        "url": url,
        "priority": priority,
        "install_allowed": install_allowed,
        "description": description,
    })

    config["catalogs"] = catalogs
    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True), encoding="utf-8")

    install_label = "允许安装" if install_allowed else "仅浏览"
    console.print(f"\n[green]✓[/green] 已添加目录 '[bold]{name}[/bold]' ({install_label})")
    console.print(f"  URL: {url}")
    console.print(f"  优先级: {priority}")
    console.print(f"\n配置已保存到 {config_path.relative_to(project_root)}")


@catalog_app.command("remove")
def catalog_remove(
    name: str = typer.Argument(help="要移除的目录名称"),
):
    """从 .specify/extension-catalogs.yml 移除目录."""
    project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    config_path = specify_dir / "extension-catalogs.yml"
    if not config_path.exists():
        console.print("[red]错误:[/red] 未找到目录配置, 无内容可移除.")
        raise typer.Exit(1)

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        console.print("[red]错误:[/red] 读取目录配置失败.")
        raise typer.Exit(1)

    catalogs = config.get("catalogs", [])
    if not isinstance(catalogs, list):
        console.print("[red]错误:[/red] 无效的目录配置: 'catalogs' 必须为列表.")
        raise typer.Exit(1)
    original_count = len(catalogs)
    catalogs = [c for c in catalogs if isinstance(c, dict) and c.get("name") != name]

    if len(catalogs) == original_count:
        console.print(f"[red]错误:[/red] 目录 '{name}' 未找到.")
        raise typer.Exit(1)

    config["catalogs"] = catalogs
    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True), encoding="utf-8")

    console.print(f"[green]✓[/green] 已移除目录 '{name}'")
    if not catalogs:
        console.print("\n[dim]配置中无剩余目录, 将使用内置默认值.[/dim]")


@extension_app.command("add")
def extension_add(
    extension: str = typer.Argument(help="扩展名称或路径"),
    dev: bool = typer.Option(False, "--dev", help="从本地目录安装"),
    from_url: Optional[str] = typer.Option(None, "--from", help="从自定义 URL 安装"),
    priority: int = typer.Option(10, "--priority", help="解析优先级 (数值越小优先级越高, 默认 10)"),
):
    """安装扩展."""
    from .extensions import ExtensionManager, ExtensionCatalog, ExtensionError, ValidationError, CompatibilityError

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate priority
    if priority < 1:
        console.print("[red]错误:[/red] 优先级必须为正整数 (1 或更大)")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)
    speckit_version = get_speckit_version()

    try:
        with console.status(f"[cyan]正在安装扩展: {extension}[/cyan]"):
            if dev:
                # Install from local directory
                source_path = Path(extension).expanduser().resolve()
                if not source_path.exists():
                    console.print(f"[red]错误:[/red] 目录未找到: {source_path}")
                    raise typer.Exit(1)

                if not (source_path / "extension.yml").exists():
                    console.print(f"[red]错误:[/red] 在 {source_path} 中未找到 extension.yml")
                    raise typer.Exit(1)

                manifest = manager.install_from_directory(source_path, speckit_version, priority=priority)

            elif from_url:
                # Install from URL (ZIP file)
                import urllib.request
                import urllib.error
                from urllib.parse import urlparse

                # Validate URL
                parsed = urlparse(from_url)
                is_localhost = parsed.hostname in ("localhost", "127.0.0.1", "::1")

                if parsed.scheme != "https" and not (parsed.scheme == "http" and is_localhost):
                    console.print("[red]错误:[/red] URL 必须使用 HTTPS 以确保安全.")
                    console.print("仅 localhost URL 允许使用 HTTP.")
                    raise typer.Exit(1)

                # Warn about untrusted sources
                console.print("[yellow]警告:[/yellow] 正在从外部 URL 安装.")
                console.print("仅从可信来源安装扩展.\n")
                console.print(f"正在从 {from_url} 下载...")

                # Download ZIP to temp location
                download_dir = project_root / ".specify" / "extensions" / ".cache" / "downloads"
                download_dir.mkdir(parents=True, exist_ok=True)
                zip_path = download_dir / f"{extension}-url-download.zip"

                try:
                    with urllib.request.urlopen(from_url, timeout=60) as response:
                        zip_data = response.read()
                    zip_path.write_bytes(zip_data)

                    # Install from downloaded ZIP
                    manifest = manager.install_from_zip(zip_path, speckit_version, priority=priority)
                except urllib.error.URLError as e:
                    console.print(f"[red]错误:[/red] 从 {from_url} 下载失败: {e}")
                    raise typer.Exit(1)
                finally:
                    # Clean up downloaded ZIP
                    if zip_path.exists():
                        zip_path.unlink()

            else:
                # Install from catalog
                catalog = ExtensionCatalog(project_root)

                # Check if extension exists in catalog (supports both ID and display name)
                ext_info, catalog_error = _resolve_catalog_extension(extension, catalog, "add")
                if catalog_error:
                    console.print(f"[red]错误:[/red] 无法查询扩展目录: {catalog_error}")
                    raise typer.Exit(1)
                if not ext_info:
                    console.print(f"[red]错误:[/red] 目录中未找到扩展 '{extension}'")
                    console.print("\n搜索可用扩展:")
                    console.print("  specify-cn extension search")
                    raise typer.Exit(1)

                # Enforce install_allowed policy
                if not ext_info.get("_install_allowed", True):
                    catalog_name = ext_info.get("_catalog_name", "community")
                    console.print(
                        f"[red]错误:[/red] '{extension}' 存在于 "
                        f"'{catalog_name}' 目录中, 但不允许从该目录安装."
                    )
                    console.print(
                        f"\n要启用安装, 请在 .specify/extension-catalogs.yml 中 "
                        f"将 '{extension}' 添加到已批准的目录并设置 install_allowed: true."
                    )
                    raise typer.Exit(1)

                # Download extension ZIP (use resolved ID, not original argument which may be display name)
                extension_id = ext_info['id']
                console.print(f"正在下载 {ext_info['name']} v{ext_info.get('version', 'unknown')}...")
                zip_path = catalog.download_extension(extension_id)

                try:
                    # Install from downloaded ZIP
                    manifest = manager.install_from_zip(zip_path, speckit_version, priority=priority)
                finally:
                    # Clean up downloaded ZIP
                    if zip_path.exists():
                        zip_path.unlink()

        console.print("\n[green]✓[/green] 扩展安装成功!")
        console.print(f"\n[bold]{manifest.name}[/bold] (v{manifest.version})")
        console.print(f"  {manifest.description}")
        console.print("\n[bold cyan]提供的命令:[/bold cyan]")
        for cmd in manifest.commands:
            console.print(f"  • {cmd['name']} - {cmd.get('description', '')}")

        # Report agent skills registration
        reg_meta = manager.registry.get(manifest.id)
        reg_skills = reg_meta.get("registered_skills", []) if reg_meta else []
        # Normalize to guard against corrupted registry entries
        if not isinstance(reg_skills, list):
            reg_skills = []
        if reg_skills:
            console.print(f"\n[green]✓[/green] {len(reg_skills)} 个代理技能已自动注册")

        console.print("\n[yellow]⚠[/yellow]  可能需要配置")
        console.print(f"   检查: .specify/extensions/{manifest.id}/")

    except ValidationError as e:
        console.print(f"\n[red]验证错误:[/red] {e}")
        raise typer.Exit(1)
    except CompatibilityError as e:
        console.print(f"\n[red]兼容性错误:[/red] {e}")
        raise typer.Exit(1)
    except ExtensionError as e:
        console.print(f"\n[red]错误:[/red] {e}")
        raise typer.Exit(1)


@extension_app.command("remove")
def extension_remove(
    extension: str = typer.Argument(help="要移除的扩展 ID 或名称"),
    keep_config: bool = typer.Option(False, "--keep-config", help="不移除配置文件"),
    force: bool = typer.Option(False, "--force", help="跳过确认"),
):
    """卸载扩展."""
    from .extensions import ExtensionManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)

    # Resolve extension ID from argument (handles ambiguous names)
    installed = manager.list_installed()
    extension_id, display_name = _resolve_installed_extension(extension, installed, "remove")

    # Get extension info for command and skill counts
    ext_manifest = manager.get_extension(extension_id)
    cmd_count = len(ext_manifest.commands) if ext_manifest else 0
    reg_meta = manager.registry.get(extension_id)
    raw_skills = reg_meta.get("registered_skills") if reg_meta else None
    skill_count = len(raw_skills) if isinstance(raw_skills, list) else 0

    # Confirm removal
    if not force:
        console.print("\n[yellow]⚠  将移除以下内容:[/yellow]")
        console.print(f"   • {cmd_count} 个 AI 代理命令")
        if skill_count:
            console.print(f"   • {skill_count} 个代理技能")
        console.print(f"   • 扩展目录: .specify/extensions/{extension_id}/")
        if not keep_config:
            console.print("   • 配置文件 (将备份)")
        console.print()

        confirm = typer.confirm("是否继续?")
        if not confirm:
            console.print("已取消")
            raise typer.Exit(0)

    # Remove extension
    success = manager.remove(extension_id, keep_config=keep_config)

    if success:
        console.print(f"\n[green]✓[/green] 扩展 '{display_name}' 已成功移除")
        if keep_config:
            console.print(f"\n配置文件已保留在 .specify/extensions/{extension_id}/")
        else:
            console.print(f"\n配置文件已备份到 .specify/extensions/.backup/{extension_id}/")
        console.print(f"\n重新安装: specify-cn extension add {extension_id}")
    else:
        console.print("[red]错误:[/red] 移除扩展失败")
        raise typer.Exit(1)


@extension_app.command("search")
def extension_search(
    query: str = typer.Argument(None, help="搜索查询 (可选)"),
    tag: Optional[str] = typer.Option(None, "--tag", help="按标签筛选"),
    author: Optional[str] = typer.Option(None, "--author", help="按作者筛选"),
    verified: bool = typer.Option(False, "--verified", help="仅显示已验证的扩展"),
):
    """在目录中搜索可用扩展."""
    from .extensions import ExtensionCatalog, ExtensionError

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    catalog = ExtensionCatalog(project_root)

    try:
        console.print("🔍 正在搜索扩展目录...")
        results = catalog.search(query=query, tag=tag, author=author, verified_only=verified)

        if not results:
            console.print("\n[yellow]未找到匹配条件的扩展[/yellow]")
            if query or tag or author or verified:
                console.print("\n尝试:")
                console.print("  • 更宽泛的搜索词")
                console.print("  • 移除筛选条件")
                console.print("  • specify-cn extension search (显示全部)")
            raise typer.Exit(0)

        console.print(f"\n[green]找到 {len(results)} 个扩展:[/green]\n")

        for ext in results:
            # Extension header
            verified_badge = " [green]✓ 已验证[/green]" if ext.get("verified") else ""
            console.print(f"[bold]{ext['name']}[/bold] (v{ext['version']}){verified_badge}")
            console.print(f"  {ext['description']}")

            # Metadata
            console.print(f"\n  [dim]作者:[/dim] {ext.get('author', '未知')}")
            if ext.get('tags'):
                tags_str = ", ".join(ext['tags'])
                console.print(f"  [dim]标签:[/dim] {tags_str}")

            # Source catalog
            catalog_name = ext.get("_catalog_name", "")
            install_allowed = ext.get("_install_allowed", True)
            if catalog_name:
                if install_allowed:
                    console.print(f"  [dim]目录:[/dim] {catalog_name}")
                else:
                    console.print(f"  [dim]目录:[/dim] {catalog_name} [yellow](仅浏览 — 不可安装)[/yellow]")

            # Stats
            stats = []
            if ext.get('downloads') is not None:
                stats.append(f"下载量: {ext['downloads']:,}")
            if ext.get('stars') is not None:
                stats.append(f"星标数: {ext['stars']}")
            if stats:
                console.print(f"  [dim]{' | '.join(stats)}[/dim]")

            # Links
            if ext.get('repository'):
                console.print(f"  [dim]仓库:[/dim] {ext['repository']}")

            # Install command (show warning if not installable)
            if install_allowed:
                console.print(f"\n  [cyan]安装:[/cyan] specify-cn extension add {ext['id']}")
            else:
                console.print(f"\n  [yellow]⚠[/yellow]  无法从 '{catalog_name}' 直接安装.")
                console.print(
                    f"  请在已批准的目录中添加 install_allowed: true, "
                    f"或从 ZIP URL 安装: specify-cn extension add {ext['id']} --from <zip-url>"
                )
            console.print()

    except ExtensionError as e:
        console.print(f"\n[red]错误:[/red] {e}")
        console.print("\n提示: 目录可能暂时不可用, 请稍后重试.")
        raise typer.Exit(1)


@extension_app.command("info")
def extension_info(
    extension: str = typer.Argument(help="扩展 ID 或名称"),
):
    """显示扩展的详细信息."""
    from .extensions import ExtensionCatalog, ExtensionManager, normalize_priority

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    catalog = ExtensionCatalog(project_root)
    manager = ExtensionManager(project_root)
    installed = manager.list_installed()

    # Try to resolve from installed extensions first (by ID or name)
    # Use allow_not_found=True since the extension may be catalog-only
    resolved_installed_id, resolved_installed_name = _resolve_installed_extension(
        extension, installed, "info", allow_not_found=True
    )

    # Try catalog lookup (with error handling)
    # If we resolved an installed extension by display name, use its ID for catalog lookup
    # to ensure we get the correct catalog entry (not a different extension with same name)
    lookup_key = resolved_installed_id if resolved_installed_id else extension
    ext_info, catalog_error = _resolve_catalog_extension(lookup_key, catalog, "info")

    # Case 1: Found in catalog - show full catalog info
    if ext_info:
        _print_extension_info(ext_info, manager)
        return

    # Case 2: Installed locally but catalog lookup failed or not in catalog
    if resolved_installed_id:
        # Get local manifest info
        ext_manifest = manager.get_extension(resolved_installed_id)
        metadata = manager.registry.get(resolved_installed_id)
        metadata_is_dict = isinstance(metadata, dict)
        if not metadata_is_dict:
            console.print(
                "[yellow]警告:[/yellow] 扩展元数据似乎已损坏, "
                "部分信息可能不可用."
            )
        version = metadata.get("version", "unknown") if metadata_is_dict else "unknown"

        console.print(f"\n[bold]{resolved_installed_name}[/bold] (v{version})")
        console.print(f"ID: {resolved_installed_id}")
        console.print()

        if ext_manifest:
            console.print(f"{ext_manifest.description}")
            console.print()
            # Author is optional in extension.yml, safely retrieve it
            author = ext_manifest.data.get("extension", {}).get("author")
            if author:
                console.print(f"[dim]作者:[/dim] {author}")
                console.print()

            if ext_manifest.commands:
                console.print("[bold]命令:[/bold]")
                for cmd in ext_manifest.commands:
                    console.print(f"  • {cmd['name']}: {cmd.get('description', '')}")
                console.print()

        # Show catalog status
        if catalog_error:
            console.print(f"[yellow]目录不可用:[/yellow] {catalog_error}")
            console.print("[dim]注意: 使用本地已安装的扩展; 无法验证目录信息.[/dim]")
        else:
            console.print("[yellow]注意:[/yellow] 未在目录中找到 (自定义/本地扩展)")

        console.print()
        console.print("[green]✓ 已安装[/green]")
        priority = normalize_priority(metadata.get("priority") if metadata_is_dict else None)
        console.print(f"[dim]优先级:[/dim] {priority}")
        console.print(f"\n移除: specify-cn extension remove {resolved_installed_id}")
        return

    # Case 3: Not found anywhere
    if catalog_error:
        console.print(f"[red]错误:[/red] 无法查询扩展目录: {catalog_error}")
        console.print("\n请在在线时重试, 或直接使用扩展 ID.")
    else:
        console.print(f"[red]错误:[/red] 扩展 '{extension}' 未找到")
        console.print("\n尝试: specify-cn extension search")
    raise typer.Exit(1)


def _print_extension_info(ext_info: dict, manager):
    """Print formatted extension info from catalog data."""
    from .extensions import normalize_priority

    # Header
    verified_badge = " [green]✓ 已验证[/green]" if ext_info.get("verified") else ""
    console.print(f"\n[bold]{ext_info['name']}[/bold] (v{ext_info['version']}){verified_badge}")
    console.print(f"ID: {ext_info['id']}")
    console.print()

    # Description
    console.print(f"{ext_info['description']}")
    console.print()

    # Author and License
    console.print(f"[dim]作者:[/dim] {ext_info.get('author', '未知')}")
    console.print(f"[dim]许可证:[/dim] {ext_info.get('license', '未知')}")

    # Source catalog
    if ext_info.get("_catalog_name"):
        install_allowed = ext_info.get("_install_allowed", True)
        install_note = "" if install_allowed else " [yellow](仅浏览)[/yellow]"
        console.print(f"[dim]来源目录:[/dim] {ext_info['_catalog_name']}{install_note}")
    console.print()

    # Requirements
    if ext_info.get('requires'):
        console.print("[bold]要求:[/bold]")
        reqs = ext_info['requires']
        if reqs.get('speckit_version'):
            console.print(f"  • Spec Kit: {reqs['speckit_version']}")
        if reqs.get('tools'):
            for tool in reqs['tools']:
                tool_name = tool['name']
                tool_version = tool.get('version', 'any')
                required = " (必需)" if tool.get('required') else " (可选)"
                console.print(f"  • {tool_name}: {tool_version}{required}")
        console.print()

    # Provides
    if ext_info.get('provides'):
        console.print("[bold]提供:[/bold]")
        provides = ext_info['provides']
        if provides.get('commands'):
            console.print(f"  • 命令: {provides['commands']}")
        if provides.get('hooks'):
            console.print(f"  • 钩子: {provides['hooks']}")
        console.print()

    # Tags
    if ext_info.get('tags'):
        tags_str = ", ".join(ext_info['tags'])
        console.print(f"[bold]标签:[/bold] {tags_str}")
        console.print()

    # Statistics
    stats = []
    if ext_info.get('downloads') is not None:
        stats.append(f"下载量: {ext_info['downloads']:,}")
    if ext_info.get('stars') is not None:
        stats.append(f"星标数: {ext_info['stars']}")
    if stats:
        console.print(f"[bold]统计:[/bold] {' | '.join(stats)}")
        console.print()

    # Links
    console.print("[bold]链接:[/bold]")
    if ext_info.get('repository'):
        console.print(f"  • 仓库: {ext_info['repository']}")
    if ext_info.get('homepage'):
        console.print(f"  • 主页: {ext_info['homepage']}")
    if ext_info.get('documentation'):
        console.print(f"  • 文档: {ext_info['documentation']}")
    if ext_info.get('changelog'):
        console.print(f"  • 更新日志: {ext_info['changelog']}")
    console.print()

    # Installation status and command
    is_installed = manager.registry.is_installed(ext_info['id'])
    install_allowed = ext_info.get("_install_allowed", True)
    if is_installed:
        console.print("[green]✓ 已安装[/green]")
        metadata = manager.registry.get(ext_info['id'])
        priority = normalize_priority(metadata.get("priority") if isinstance(metadata, dict) else None)
        console.print(f"[dim]优先级:[/dim] {priority}")
        console.print(f"\n移除: specify-cn extension remove {ext_info['id']}")
    elif install_allowed:
        console.print("[yellow]未安装[/yellow]")
        console.print(f"\n[cyan]安装:[/cyan] specify-cn extension add {ext_info['id']}")
    else:
        catalog_name = ext_info.get("_catalog_name", "community")
        console.print("[yellow]未安装[/yellow]")
        console.print(
            f"\n[yellow]⚠[/yellow]  '{ext_info['id']}' 存在于 '{catalog_name}' 目录中, "
            f"但不在你已批准的目录里. 请在 .specify/extension-catalogs.yml 中 "
            f"添加并设置 install_allowed: true 以启用安装."
        )


@extension_app.command("update")
def extension_update(
    extension: str = typer.Argument(None, help="要更新的扩展 ID 或名称 (或全部)"),
):
    """更新扩展到最新版本."""
    from .extensions import (
        ExtensionManager,
        ExtensionCatalog,
        ExtensionError,
        ValidationError,
        CommandRegistrar,
        HookExecutor,
        normalize_priority,
    )
    from packaging import version as pkg_version
    import shutil

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)
    catalog = ExtensionCatalog(project_root)
    speckit_version = get_speckit_version()

    try:
        # Get list of extensions to update
        installed = manager.list_installed()
        if extension:
            # Update specific extension - resolve ID from argument (handles ambiguous names)
            extension_id, _ = _resolve_installed_extension(extension, installed, "update")
            extensions_to_update = [extension_id]
        else:
            # Update all extensions
            extensions_to_update = [ext["id"] for ext in installed]

        if not extensions_to_update:
            console.print("[yellow]未安装任何扩展[/yellow]")
            raise typer.Exit(0)

        console.print("🔄 正在检查更新...\n")

        updates_available = []

        for ext_id in extensions_to_update:
            # Get installed version
            metadata = manager.registry.get(ext_id)
            if metadata is None or not isinstance(metadata, dict) or "version" not in metadata:
                console.print(f"⚠  {ext_id}: 注册表条目已损坏或缺失 (跳过)")
                continue
            try:
                installed_version = pkg_version.Version(metadata["version"])
            except pkg_version.InvalidVersion:
                console.print(
                    f"⚠  {ext_id}: 注册表中的已安装版本 '{metadata.get('version')}' 无效(跳过)"
                )
                continue

            # Get catalog info
            ext_info = catalog.get_extension_info(ext_id)
            if not ext_info:
                console.print(f"⚠  {ext_id}: 目录中未找到 (跳过)")
                continue

            # Check if installation is allowed from this catalog
            if not ext_info.get("_install_allowed", True):
                console.print(f"⚠  {ext_id}: 不允许从 '{ext_info.get('_catalog_name', 'catalog')}' 更新 (跳过)")
                continue

            try:
                catalog_version = pkg_version.Version(ext_info["version"])
            except pkg_version.InvalidVersion:
                console.print(
                    f"⚠  {ext_id}: 目录版本 '{ext_info.get('version')}' 无效(跳过)"
                )
                continue

            if catalog_version > installed_version:
                updates_available.append(
                    {
                        "id": ext_id,
                        "name": ext_info.get("name", ext_id),  # Display name for status messages
                        "installed": str(installed_version),
                        "available": str(catalog_version),
                        "download_url": ext_info.get("download_url"),
                    }
                )
            else:
                console.print(f"✓ {ext_id}: 已是最新 (v{installed_version})")

        if not updates_available:
            console.print("\n[green]所有扩展已是最新![/green]")
            raise typer.Exit(0)

        # Show available updates
        console.print("\n[bold]可用更新:[/bold]\n")
        for update in updates_available:
            console.print(
                f"  • {update['id']}: {update['installed']} → {update['available']}"
            )

        console.print()
        confirm = typer.confirm("更新这些扩展?")
        if not confirm:
            console.print("已取消")
            raise typer.Exit(0)

        # Perform updates with atomic backup/restore
        console.print()
        updated_extensions = []
        failed_updates = []
        registrar = CommandRegistrar()
        hook_executor = HookExecutor(project_root)

        for update in updates_available:
            extension_id = update["id"]
            ext_name = update["name"]  # Use display name for user-facing messages
            console.print(f"📦 正在更新 {ext_name}...")

            # Backup paths
            backup_base = manager.extensions_dir / ".backup" / f"{extension_id}-update"
            backup_ext_dir = backup_base / "extension"
            backup_commands_dir = backup_base / "commands"
            backup_config_dir = backup_base / "config"

            # Store backup state
            backup_registry_entry = None
            backup_hooks = None  # None means no hooks key in config; {} means hooks key existed
            backed_up_command_files = {}

            try:
                # 1. Backup registry entry (always, even if extension dir doesn't exist)
                backup_registry_entry = manager.registry.get(extension_id)

                # 2. Backup extension directory
                extension_dir = manager.extensions_dir / extension_id
                if extension_dir.exists():
                    backup_base.mkdir(parents=True, exist_ok=True)
                    if backup_ext_dir.exists():
                        shutil.rmtree(backup_ext_dir)
                    shutil.copytree(extension_dir, backup_ext_dir)

                    # Backup config files separately so they can be restored
                    # after a successful install (install_from_directory clears dest dir).
                    config_files = list(extension_dir.glob("*-config.yml")) + list(
                        extension_dir.glob("*-config.local.yml")
                    )
                    for cfg_file in config_files:
                        backup_config_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(cfg_file, backup_config_dir / cfg_file.name)

                # 3. Backup command files for all agents
                from .agents import CommandRegistrar as _AgentReg
                registered_commands = backup_registry_entry.get("registered_commands", {})
                for agent_name, cmd_names in registered_commands.items():
                    if agent_name not in registrar.AGENT_CONFIGS:
                        continue
                    agent_config = registrar.AGENT_CONFIGS[agent_name]
                    commands_dir = project_root / agent_config["dir"]

                    for cmd_name in cmd_names:
                        output_name = _AgentReg._compute_output_name(agent_name, cmd_name, agent_config)
                        cmd_file = commands_dir / f"{output_name}{agent_config['extension']}"
                        if cmd_file.exists():
                            backup_cmd_path = backup_commands_dir / agent_name / cmd_file.name
                            backup_cmd_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(cmd_file, backup_cmd_path)
                            backed_up_command_files[str(cmd_file)] = str(backup_cmd_path)

                        # Also backup copilot prompt files
                        if agent_name == "copilot":
                            prompt_file = project_root / ".github" / "prompts" / f"{cmd_name}.prompt.md"
                            if prompt_file.exists():
                                backup_prompt_path = backup_commands_dir / "copilot-prompts" / prompt_file.name
                                backup_prompt_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(prompt_file, backup_prompt_path)
                                backed_up_command_files[str(prompt_file)] = str(backup_prompt_path)

                # 4. Backup hooks from extensions.yml
                # Use backup_hooks=None to indicate config had no "hooks" key (don't create on restore)
                # Use backup_hooks={} to indicate config had "hooks" key with no hooks for this extension
                config = hook_executor.get_project_config()
                if "hooks" in config:
                    backup_hooks = {}  # Config has hooks key - preserve this fact
                    for hook_name, hook_list in config["hooks"].items():
                        ext_hooks = [h for h in hook_list if h.get("extension") == extension_id]
                        if ext_hooks:
                            backup_hooks[hook_name] = ext_hooks

                # 5. Download new version
                zip_path = catalog.download_extension(extension_id)
                try:
                    # 6. Validate extension ID from ZIP BEFORE modifying installation
                    # Handle both root-level and nested extension.yml (GitHub auto-generated ZIPs)
                    with zipfile.ZipFile(zip_path, "r") as zf:
                        import yaml
                        manifest_data = None
                        namelist = zf.namelist()

                        # First try root-level extension.yml
                        if "extension.yml" in namelist:
                            with zf.open("extension.yml") as f:
                                manifest_data = yaml.safe_load(f) or {}
                        else:
                            # Look for extension.yml in a single top-level subdirectory
                            # (e.g., "repo-name-branch/extension.yml")
                            manifest_paths = [n for n in namelist if n.endswith("/extension.yml") and n.count("/") == 1]
                            if len(manifest_paths) == 1:
                                with zf.open(manifest_paths[0]) as f:
                                    manifest_data = yaml.safe_load(f) or {}

                        if manifest_data is None:
                            raise ValueError("Downloaded extension archive is missing 'extension.yml'")

                    zip_extension_id = manifest_data.get("extension", {}).get("id")
                    if zip_extension_id != extension_id:
                        raise ValueError(
                            f"Extension ID mismatch: expected '{extension_id}', got '{zip_extension_id}'"
                        )

                    # 7. Remove old extension (handles command file cleanup and registry removal)
                    manager.remove(extension_id, keep_config=True)

                    # 8. Install new version
                    _ = manager.install_from_zip(zip_path, speckit_version)

                    # Restore user config files from backup after successful install.
                    new_extension_dir = manager.extensions_dir / extension_id
                    if backup_config_dir.exists() and new_extension_dir.exists():
                        for cfg_file in backup_config_dir.iterdir():
                            if cfg_file.is_file():
                                shutil.copy2(cfg_file, new_extension_dir / cfg_file.name)

                    # 9. Restore metadata from backup (installed_at, enabled state)
                    if backup_registry_entry and isinstance(backup_registry_entry, dict):
                        # Copy current registry entry to avoid mutating internal
                        # registry state before explicit restore().
                        current_metadata = manager.registry.get(extension_id)
                        if current_metadata is None or not isinstance(current_metadata, dict):
                            raise RuntimeError(
                                f"Registry entry for '{extension_id}' missing or corrupted after install — update incomplete"
                            )
                        new_metadata = dict(current_metadata)

                        # Preserve the original installation timestamp
                        if "installed_at" in backup_registry_entry:
                            new_metadata["installed_at"] = backup_registry_entry["installed_at"]

                        # Preserve the original priority (normalized to handle corruption)
                        if "priority" in backup_registry_entry:
                            new_metadata["priority"] = normalize_priority(backup_registry_entry["priority"])

                        # If extension was disabled before update, disable it again
                        if not backup_registry_entry.get("enabled", True):
                            new_metadata["enabled"] = False

                        # Use restore() instead of update() because update() always
                        # preserves the existing installed_at, ignoring our override
                        manager.registry.restore(extension_id, new_metadata)

                        # Also disable hooks in extensions.yml if extension was disabled
                        if not backup_registry_entry.get("enabled", True):
                            config = hook_executor.get_project_config()
                            if "hooks" in config:
                                for hook_name in config["hooks"]:
                                    for hook in config["hooks"][hook_name]:
                                        if hook.get("extension") == extension_id:
                                            hook["enabled"] = False
                                hook_executor.save_project_config(config)
                finally:
                    # Clean up downloaded ZIP
                    if zip_path.exists():
                        zip_path.unlink()

                # 10. Clean up backup on success
                if backup_base.exists():
                    shutil.rmtree(backup_base)

                console.print(f"   [green]✓[/green] 已更新到 v{update['available']}")
                updated_extensions.append(ext_name)

            except KeyboardInterrupt:
                raise
            except Exception as e:
                console.print(f"   [red]✗[/red] 失败: {e}")
                failed_updates.append((ext_name, str(e)))

                # Rollback on failure
                console.print(f"   [yellow]↩[/yellow] 正在回滚 {ext_name}...")

                try:
                    # Restore extension directory
                    # Only perform destructive rollback if backup exists (meaning we
                    # actually modified the extension). This avoids deleting a valid
                    # installation when failure happened before changes were made.
                    extension_dir = manager.extensions_dir / extension_id
                    if backup_ext_dir.exists():
                        if extension_dir.exists():
                            shutil.rmtree(extension_dir)
                        shutil.copytree(backup_ext_dir, extension_dir)

                    # Remove any NEW command files created by failed install
                    # (files that weren't in the original backup)
                    try:
                        new_registry_entry = manager.registry.get(extension_id)
                        if new_registry_entry is None or not isinstance(new_registry_entry, dict):
                            new_registered_commands = {}
                        else:
                            new_registered_commands = new_registry_entry.get("registered_commands", {})
                        for agent_name, cmd_names in new_registered_commands.items():
                            if agent_name not in registrar.AGENT_CONFIGS:
                                continue
                            agent_config = registrar.AGENT_CONFIGS[agent_name]
                            commands_dir = project_root / agent_config["dir"]

                            for cmd_name in cmd_names:
                                output_name = _AgentReg._compute_output_name(agent_name, cmd_name, agent_config)
                                cmd_file = commands_dir / f"{output_name}{agent_config['extension']}"
                                # Delete if it exists and wasn't in our backup
                                if cmd_file.exists() and str(cmd_file) not in backed_up_command_files:
                                    cmd_file.unlink()

                                # Also handle copilot prompt files
                                if agent_name == "copilot":
                                    prompt_file = project_root / ".github" / "prompts" / f"{cmd_name}.prompt.md"
                                    if prompt_file.exists() and str(prompt_file) not in backed_up_command_files:
                                        prompt_file.unlink()
                    except KeyError:
                        pass  # No new registry entry exists, nothing to clean up

                    # Restore backed up command files
                    for original_path, backup_path in backed_up_command_files.items():
                        backup_file = Path(backup_path)
                        if backup_file.exists():
                            original_file = Path(original_path)
                            original_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(backup_file, original_file)

                    # Restore hooks in extensions.yml
                    # - backup_hooks=None means original config had no "hooks" key
                    # - backup_hooks={} or {...} means config had hooks key
                    config = hook_executor.get_project_config()
                    if "hooks" in config:
                        modified = False

                        if backup_hooks is None:
                            # Original config had no "hooks" key; remove it entirely
                            del config["hooks"]
                            modified = True
                        else:
                            # Remove any hooks for this extension added by failed install
                            for hook_name, hooks_list in config["hooks"].items():
                                original_len = len(hooks_list)
                                config["hooks"][hook_name] = [
                                    h for h in hooks_list
                                    if h.get("extension") != extension_id
                                ]
                                if len(config["hooks"][hook_name]) != original_len:
                                    modified = True

                            # Add back the backed up hooks if any
                            if backup_hooks:
                                for hook_name, hooks in backup_hooks.items():
                                    if hook_name not in config["hooks"]:
                                        config["hooks"][hook_name] = []
                                    config["hooks"][hook_name].extend(hooks)
                                    modified = True

                        if modified:
                            hook_executor.save_project_config(config)

                    # Restore registry entry (use restore() since entry was removed)
                    if backup_registry_entry:
                        manager.registry.restore(extension_id, backup_registry_entry)

                    console.print("   [green]✓[/green] 回滚成功")
                    # Clean up backup directory only on successful rollback
                    if backup_base.exists():
                        shutil.rmtree(backup_base)
                except Exception as rollback_error:
                    console.print(f"   [red]✗[/red] 回滚失败: {rollback_error}")
                    console.print(f"   [dim]备份保留在: {backup_base}[/dim]")

        # Summary
        console.print()
        if updated_extensions:
            console.print(f"[green]✓[/green] 成功更新 {len(updated_extensions)} 个扩展")
        if failed_updates:
            console.print(f"[red]✗[/red] 更新 {len(failed_updates)} 个扩展失败:")
            for ext_name, error in failed_updates:
                console.print(f"   • {ext_name}: {error}")
            raise typer.Exit(1)

    except ValidationError as e:
        console.print(f"\n[red]验证错误:[/red] {e}")
        raise typer.Exit(1)
    except ExtensionError as e:
        console.print(f"\n[red]错误:[/red] {e}")
        raise typer.Exit(1)


@extension_app.command("enable")
def extension_enable(
    extension: str = typer.Argument(help="要启用的扩展 ID 或名称"),
):
    """启用已禁用的扩展."""
    from .extensions import ExtensionManager, HookExecutor

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)
    hook_executor = HookExecutor(project_root)

    # Resolve extension ID from argument (handles ambiguous names)
    installed = manager.list_installed()
    extension_id, display_name = _resolve_installed_extension(extension, installed, "enable")

    # Update registry
    metadata = manager.registry.get(extension_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 扩展 '{extension_id}' 在注册表中未找到 (状态损坏)")
        raise typer.Exit(1)

    if metadata.get("enabled", True):
        console.print(f"[yellow]扩展 '{display_name}' 已处于启用状态[/yellow]")
        raise typer.Exit(0)

    manager.registry.update(extension_id, {"enabled": True})

    # Enable hooks in extensions.yml
    config = hook_executor.get_project_config()
    if "hooks" in config:
        for hook_name in config["hooks"]:
            for hook in config["hooks"][hook_name]:
                if hook.get("extension") == extension_id:
                    hook["enabled"] = True
        hook_executor.save_project_config(config)

    console.print(f"[green]✓[/green] 扩展 '{display_name}' 已启用")


@extension_app.command("disable")
def extension_disable(
    extension: str = typer.Argument(help="要禁用的扩展 ID 或名称"),
):
    """禁用扩展但不移除."""
    from .extensions import ExtensionManager, HookExecutor

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)
    hook_executor = HookExecutor(project_root)

    # Resolve extension ID from argument (handles ambiguous names)
    installed = manager.list_installed()
    extension_id, display_name = _resolve_installed_extension(extension, installed, "disable")

    # Update registry
    metadata = manager.registry.get(extension_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 扩展 '{extension_id}' 在注册表中未找到 (状态损坏)")
        raise typer.Exit(1)

    if not metadata.get("enabled", True):
        console.print(f"[yellow]扩展 '{display_name}' 已处于禁用状态[/yellow]")
        raise typer.Exit(0)

    manager.registry.update(extension_id, {"enabled": False})

    # Disable hooks in extensions.yml
    config = hook_executor.get_project_config()
    if "hooks" in config:
        for hook_name in config["hooks"]:
            for hook in config["hooks"][hook_name]:
                if hook.get("extension") == extension_id:
                    hook["enabled"] = False
        hook_executor.save_project_config(config)

    console.print(f"[green]✓[/green] 扩展 '{display_name}' 已禁用")
    console.print("\n命令将不再可用, 钩子将不再执行.")
    console.print(f"重新启用: specify-cn extension enable {extension_id}")


@extension_app.command("set-priority")
def extension_set_priority(
    extension: str = typer.Argument(help="扩展 ID 或名称"),
    priority: int = typer.Argument(help="新优先级 (数值越小优先级越高)"),
):
    """设置已安装扩展的解析优先级."""
    from .extensions import ExtensionManager

    project_root = Path.cwd()

    # Check if we're in a spec-kit project
    specify_dir = project_root / ".specify"
    if not specify_dir.exists():
        console.print("[red]错误:[/red] 非 spec-kit 项目 (没有 .specify/ 目录)")
        console.print("请在 spec-kit 项目根目录运行此命令")
        raise typer.Exit(1)

    # Validate priority
    if priority < 1:
        console.print("[red]错误:[/red] 优先级必须为正整数 (1 或更大)")
        raise typer.Exit(1)

    manager = ExtensionManager(project_root)

    # Resolve extension ID from argument (handles ambiguous names)
    installed = manager.list_installed()
    extension_id, display_name = _resolve_installed_extension(extension, installed, "set-priority")

    # Get current metadata
    metadata = manager.registry.get(extension_id)
    if metadata is None or not isinstance(metadata, dict):
        console.print(f"[red]错误:[/red] 扩展 '{extension_id}' 在注册表中未找到 (状态损坏)")
        raise typer.Exit(1)

    from .extensions import normalize_priority
    raw_priority = metadata.get("priority")
    # Only skip if the stored value is already a valid int equal to requested priority
    # This ensures corrupted values (e.g., "high") get repaired even when setting to default (10)
    if isinstance(raw_priority, int) and raw_priority == priority:
        console.print(f"[yellow]扩展 '{display_name}' 的优先级已经是 {priority}[/yellow]")
        raise typer.Exit(0)

    old_priority = normalize_priority(raw_priority)

    # Update priority
    manager.registry.update(extension_id, {"priority": priority})

    console.print(f"[green]✓[/green] 扩展 '{display_name}' 优先级已更改: {old_priority} → {priority}")
    console.print("\n[dim]优先级数值越小 = 模板解析时优先级越高[/dim]")


def main():
    app()

if __name__ == "__main__":
    main()

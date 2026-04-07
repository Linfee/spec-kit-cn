# RFC: Spec Kit 扩展系统

**状态**: 已实现
**作者**: Stats Perform Engineering
**创建**: 2026-01-28
**更新**: 2026-03-11

---

## 目录

1. [概述](#概述)
2. [动机](#动机)
3. [设计原则](#设计原则)
4. [架构概览](#架构概览)
5. [扩展清单规范](#扩展清单规范)
6. [扩展生命周期](#扩展生命周期)
7. [命令注册](#命令注册)
8. [配置管理](#配置管理)
9. [钩子系统](#钩子系统)
10. [扩展发现与目录](#扩展发现与目录)
11. [CLI 命令](#cli-命令)
12. [兼容性与版本控制](#兼容性与版本控制)
13. [安全考量](#安全考量)
14. [迁移策略](#迁移策略)
15. [实现阶段](#实现阶段)
16. [已解决的问题](#已解决的问题)
17. [未解决的问题 (剩余)](#未解决的问题-剩余)
18. [附录](#附录)

---

## 概述

为 Spec Kit 引入扩展系统, 允许模块化集成外部工具 (Jira, Linear, Azure DevOps 等), 而不会膨胀核心框架。扩展是安装到 `.specify/extensions/` 中的自包含包, 具有声明式清单、独立版本控制, 并可通过中央目录发现。

---

## 动机

### 当前问题

1. **单体增长**: 将 Jira 集成添加到核心 spec-kit 会导致:
   - 影响所有用户的大型配置文件
   - 所有人都需要 Jira MCP 服务器依赖
   - 功能累积导致合并冲突

2. **有限的灵活性**: 不同组织使用不同工具:
   - GitHub Issues vs Jira vs Linear vs Azure DevOps
   - 自定义内部工具
   - 无法在不膨胀的情况下支持所有工具

3. **维护负担**: 每个集成都会增加:
   - 文档复杂性
   - 测试矩阵扩展
   - 破坏性变更的表面积

4. **社区摩擦**: 外部贡献者无法轻松添加集成, 需要核心仓库 PR 批准和发布周期。

### 目标

1. **模块化**: 核心 spec-kit 保持精简, 扩展按需选用
2. **可扩展性**: 清晰的 API 用于构建新集成
3. **独立性**: 扩展独立于核心进行版本控制/发布
4. **可发现性**: 中央目录用于查找扩展
5. **安全性**: 验证、兼容性检查、沙箱化

---

## 设计原则

### 1. 约定优于配置

- 标准目录结构 (`.specify/extensions/{name}/`)
- 声明式清单 (`extension.yml`)
- 可预测的命令命名 (`speckit.{extension}.{command}`)

### 2. 故障安全默认值

- 缺失的扩展优雅降级 (跳过钩子)
- 无效的扩展发出警告但不破坏核心功能
- 扩展故障与核心操作隔离

### 3. 向后兼容

- 核心命令保持不变
- 扩展仅为增量添加 (不修改核心)
- 旧项目无需扩展即可工作

### 4. 开发者体验

- 简单安装: `specify-cn extension add jira`
- 兼容性问题的清晰错误消息
- 本地开发模式用于测试扩展

### 5. 安全优先

- 扩展在与 AI 代理相同的上下文中运行 (信任边界)
- 清单验证防止恶意代码
- 未来将验证官方扩展签名

---

## 架构概览

### 目录结构

```text
project/
├── .specify/
│   ├── scripts/                 # Core scripts (unchanged)
│   ├── templates/               # Core templates (unchanged)
│   ├── memory/                  # Session memory
│   ├── extensions/              # Extensions directory (NEW)
│   │   ├── .registry            # Installed extensions metadata (NEW)
│   │   ├── jira/                # Jira extension
│   │   │   ├── extension.yml    # Manifest
│   │   │   ├── jira-config.yml  # Extension config
│   │   │   ├── commands/        # Command files
│   │   │   ├── scripts/         # Helper scripts
│   │   │   └── docs/            # Documentation
│   │   └── linear/              # Linear extension (example)
│   └── extensions.yml           # Project extension configuration (NEW)
└── .gitignore                   # Ignore local extension configs
```

### 组件图

```text
┌─────────────────────────────────────────────────────────┐
│                    Spec Kit Core                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CLI (specify)                                   │   │
│  │  - init, check                                   │   │
│  │  - extension add/remove/list/update  ← NEW       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Extension Manager  ← NEW                        │   │
│  │  - Discovery, Installation, Validation           │   │
│  │  - Command Registration, Hook Execution          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Core Commands                                   │   │
│  │  - /speckit.specify                              │   │
│  │  - /speckit.tasks                                │   │
│  │  - /speckit.implement                            │   │
│  └─────────┬────────────────────────────────────────┘   │
└────────────┼────────────────────────────────────────────┘
             │ Hook Points (after_tasks, after_implement)
             ↓
┌─────────────────────────────────────────────────────────┐
│                    Extensions                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Jira Extension                                  │   │
│  │  - /speckit.jira.specstoissues                   │   │
│  │  - /speckit.jira.discover-fields                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Linear Extension                                │   │
│  │  - /speckit.linear.sync                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
             │ Calls external tools
             ↓
┌─────────────────────────────────────────────────────────┐
│                    External Tools                       │
│  - Jira MCP Server                                      │
│  - Linear API                                           │
│  - GitHub API                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 扩展清单规范

### 模式: `extension.yml`

```yaml
# Extension Manifest Schema v1.0
# All extensions MUST include this file at root

# Schema version for compatibility
schema_version: "1.0"

# Extension metadata (REQUIRED)
extension:
  id: "jira"                    # Unique identifier (lowercase, alphanumeric, hyphens)
  name: "Jira Integration"      # Human-readable name
  version: "1.0.0"              # Semantic version
  description: "Create Jira Epics, Stories, and Issues from spec-kit artifacts"
  author: "Stats Perform"       # Author/organization
  repository: "https://github.com/statsperform/spec-kit-jira"
  license: "MIT"                # SPDX license identifier
  homepage: "https://github.com/statsperform/spec-kit-jira/blob/main/README.md"

# Compatibility requirements (REQUIRED)
requires:
  # Spec-kit version (semantic version range)
  speckit_version: ">=0.1.0,<2.0.0"

  # External tools required by extension
  tools:
    - name: "jira-mcp-server"
      required: true
      version: ">=1.0.0"          # Optional: version constraint
      description: "Jira MCP server for API access"
      install_url: "https://github.com/your-org/jira-mcp-server"
      check_command: "jira --version"  # Optional: CLI command to verify

  # Core spec-kit commands this extension depends on
  commands:
    - "speckit.tasks"             # Extension needs tasks command

  # Core scripts required
  scripts:
    - "check-prerequisites.sh"

# What this extension provides (REQUIRED)
provides:
  # Commands added to AI agent
  commands:
    - name: "speckit.jira.specstoissues"
      file: "commands/specstoissues.md"
      description: "Create Jira hierarchy from spec and tasks"
      aliases: ["speckit.jira.sync"]  # Alternate names

    - name: "speckit.jira.discover-fields"
      file: "commands/discover-fields.md"
      description: "Discover Jira custom fields for configuration"

    - name: "speckit.jira.sync-status"
      file: "commands/sync-status.md"
      description: "Sync task completion status to Jira"

  # Configuration files
  config:
    - name: "jira-config.yml"
      template: "jira-config.template.yml"
      description: "Jira integration configuration"
      required: true              # User must configure before use

  # Helper scripts
  scripts:
    - name: "parse-jira-config.sh"
      file: "scripts/parse-jira-config.sh"
      description: "Parse jira-config.yml to JSON"
      executable: true            # Make executable on install

# Extension configuration defaults (OPTIONAL)
defaults:
  project:
    key: null                     # No default, user must configure
  hierarchy:
    issue_type: "subtask"
  update_behavior:
    mode: "update"
    sync_completion: true

# Configuration schema for validation (OPTIONAL)
config_schema:
  type: "object"
  required: ["project"]
  properties:
    project:
      type: "object"
      required: ["key"]
      properties:
        key:
          type: "string"
          pattern: "^[A-Z]{2,10}$"
          description: "Jira project key (e.g., MSATS)"

# Integration hooks (OPTIONAL)
hooks:
  # Hook fired after /speckit.tasks completes
  after_tasks:
    command: "speckit.jira.specstoissues"
    optional: true
    prompt: "Create Jira issues from tasks?"
    description: "Automatically create Jira hierarchy after task generation"

  # Hook fired after /speckit.implement completes
  after_implement:
    command: "speckit.jira.sync-status"
    optional: true
    prompt: "Sync completion status to Jira?"

# Tags for discovery (OPTIONAL)
tags:
  - "issue-tracking"
  - "jira"
  - "atlassian"
  - "project-management"

# Changelog URL (OPTIONAL)
changelog: "https://github.com/statsperform/spec-kit-jira/blob/main/CHANGELOG.md"

# Support information (OPTIONAL)
support:
  documentation: "https://github.com/statsperform/spec-kit-jira/blob/main/docs/"
  issues: "https://github.com/statsperform/spec-kit-jira/issues"
  discussions: "https://github.com/statsperform/spec-kit-jira/discussions"
  email: "support@statsperform.com"
```

### 验证规则

1. **必须包含** `schema_version`, `extension`, `requires`, `provides`
2. **必须遵循** `version` 的语义化版本
3. **必须具有** 唯一的 `id` (不与其他扩展冲突)
4. **必须声明** 所有外部工具依赖
5. **建议包含** `config_schema` (如果扩展使用配置)
6. **建议包含** `support` 信息
7. 命令 `file` 路径**必须**相对于扩展根目录
8. 钩子 `command` 名称**必须**与 `provides.commands` 中的命令匹配

---

## 扩展生命周期

### 1. 发现

```bash
specify-cn extension search jira
# 在目录中搜索匹配 "jira" 的扩展
```

**流程**:

1. 从 GitHub 获取扩展目录
2. 按搜索词过滤 (名称、标签、描述)
3. 显示结果及元数据

### 2. 安装

```bash
specify-cn extension add jira
```

**流程**:

1. **解析**: 在目录中查找扩展
2. **下载**: 获取扩展包 (GitHub Release 的 ZIP)
3. **验证**: 检查清单模式、兼容性
4. **解压**: 解包到 `.specify/extensions/jira/`
5. **配置**: 复制配置模板
6. **注册**: 将命令添加到 AI 代理配置
7. **记录**: 更新 `.specify/extensions/.registry`

**注册表格式** (`.specify/extensions/.registry`):

```json
{
  "schema_version": "1.0",
  "extensions": {
    "jira": {
      "version": "1.0.0",
      "installed_at": "2026-01-28T14:30:00Z",
      "source": "catalog",
      "manifest_hash": "sha256:abc123...",
      "enabled": true,
      "priority": 10
    }
  }
}
```

**Priority 字段**: 扩展按 `priority` 排序 (数值越低 = 优先级越高)。默认值为 10。用于当多个扩展提供相同模板时的模板解析。

### 3. 配置

```bash
# 用户编辑扩展配置
vim .specify/extensions/jira/jira-config.yml
```

**配置发现顺序**:

1. 扩展默认值 (`extension.yml` -> `defaults`)
2. 项目配置 (`jira-config.yml`)
3. 本地覆盖 (`jira-config.local.yml` - gitignored)
4. 环境变量 (`SPECKIT_JIRA_*`)

### 4. 使用

```bash
claude
> /speckit.jira.specstoissues
```

**命令解析**:

1. AI 代理在 `.claude/commands/speckit.jira.specstoissues.md` 中找到命令
2. 命令文件引用扩展脚本/配置
3. 扩展在完整上下文中执行

### 5. 更新

```bash
specify-cn extension update jira
```

**流程**:

1. 检查目录中是否有更新版本
2. 下载新版本
3. 验证兼容性
4. 备份当前配置
5. 解压新版本 (保留配置)
6. 重新注册命令
7. 更新注册表

### 6. 移除

```bash
specify-cn extension remove jira
```

**流程**:

1. 与用户确认 (显示将被移除的内容)
2. 从 AI 代理注销命令
3. 从 `.specify/extensions/jira/` 移除
4. 更新注册表
5. 可选择保留配置以便重新安装

---

## 命令注册

### 按代理注册

扩展提供**通用命令格式** (基于 Markdown), CLI 在注册期间转换为代理特定格式。

#### 通用命令格式

**位置**: 扩展的 `commands/specstoissues.md`

```markdown
---
# Universal metadata (parsed by all agents)
description: "Create Jira hierarchy from spec and tasks"
tools:
  - 'jira-mcp-server/epic_create'
  - 'jira-mcp-server/story_create'
scripts:
  sh: ../../scripts/bash/check-prerequisites.sh --json
  ps: ../../scripts/powershell/check-prerequisites.ps1 -Json
---

# Command implementation
## User Input
$ARGUMENTS

## Steps
1. Load jira-config.yml
2. Parse spec.md and tasks.md
3. Create Jira items
```

#### Claude Code 注册

**输出**: `.claude/commands/speckit.jira.specstoissues.md`

```markdown
---
description: "Create Jira hierarchy from spec and tasks"
tools:
  - 'jira-mcp-server/epic_create'
  - 'jira-mcp-server/story_create'
scripts:
  sh: .specify/scripts/bash/check-prerequisites.sh --json
  ps: .specify/scripts/powershell/check-prerequisites.ps1 -Json
---

# Command implementation (copied from extension)
## User Input
$ARGUMENTS

## Steps
1. Load jira-config.yml from .specify/extensions/jira/
2. Parse spec.md and tasks.md
3. Create Jira items
```

**转换**:

- 复制 frontmatter 并调整
- 重写脚本路径 (相对于仓库根目录)
- 添加扩展上下文 (配置位置)

#### Gemini CLI 注册

**输出**: `.gemini/commands/speckit.jira.specstoissues.toml`

```toml
[command]
name = "speckit.jira.specstoissues"
description = "Create Jira hierarchy from spec and tasks"

[command.tools]
tools = [
  "jira-mcp-server/epic_create",
  "jira-mcp-server/story_create"
]

[command.script]
sh = ".specify/scripts/bash/check-prerequisites.sh --json"
ps = ".specify/scripts/powershell/check-prerequisites.ps1 -Json"

[command.template]
content = """
# Command implementation
## User Input
{{args}}

## Steps
1. Load jira-config.yml from .specify/extensions/jira/
2. Parse spec.md and tasks.md
3. Create Jira items
"""
```

**转换**:

- 将 Markdown frontmatter 转换为 TOML
- 将 `$ARGUMENTS` 转换为 `{{args}}`
- 重写脚本路径

### 注册代码

**位置**: `src/specify_cli/extensions.py`

```python
def register_extension_commands(
    project_path: Path,
    ai_assistant: str,
    manifest: dict
) -> None:
    """Register extension commands with AI agent."""

    agent_config = AGENT_CONFIG.get(ai_assistant)
    if not agent_config:
        console.print(f"[yellow]Unknown agent: {ai_assistant}[/yellow]")
        return

    ext_id = manifest['extension']['id']
    ext_dir = project_path / ".specify" / "extensions" / ext_id
    agent_commands_dir = project_path / agent_config['folder'].rstrip('/') / "commands"
    agent_commands_dir.mkdir(parents=True, exist_ok=True)

    for cmd_info in manifest['provides']['commands']:
        cmd_name = cmd_info['name']
        source_file = ext_dir / cmd_info['file']

        if not source_file.exists():
            console.print(f"[red]Command file not found:[/red] {cmd_info['file']}")
            continue

        # Convert to agent-specific format
        if ai_assistant == "claude":
            dest_file = agent_commands_dir / f"{cmd_name}.md"
            convert_to_claude(source_file, dest_file, ext_dir)
        elif ai_assistant == "gemini":
            dest_file = agent_commands_dir / f"{cmd_name}.toml"
            convert_to_gemini(source_file, dest_file, ext_dir)
        elif ai_assistant == "copilot":
            dest_file = agent_commands_dir / f"{cmd_name}.md"
            convert_to_copilot(source_file, dest_file, ext_dir)
        # ... other agents

        console.print(f"  ✓ Registered: {cmd_name}")

def convert_to_claude(
    source: Path,
    dest: Path,
    ext_dir: Path
) -> None:
    """Convert universal command to Claude format."""

    # Parse universal command
    content = source.read_text()
    frontmatter, body = parse_frontmatter(content)

    # Adjust script paths (relative to repo root)
    if 'scripts' in frontmatter:
        for key in frontmatter['scripts']:
            frontmatter['scripts'][key] = adjust_path_for_repo_root(
                frontmatter['scripts'][key]
            )

    # Inject extension context
    body = inject_extension_context(body, ext_dir)

    # Write Claude command
    dest.write_text(render_frontmatter(frontmatter) + "\n" + body)
```

---

## 配置管理

### 配置文件层次

```yaml
# .specify/extensions/jira/jira-config.yml (Project config)
project:
  key: "MSATS"

hierarchy:
  issue_type: "subtask"

defaults:
  epic:
    labels: ["spec-driven", "typescript"]
```

```yaml
# .specify/extensions/jira/jira-config.local.yml (Local overrides - gitignored)
project:
  key: "MYTEST"  # Override for local testing
```

```bash
# Environment variables (highest precedence)
export SPECKIT_JIRA_PROJECT_KEY="DEVTEST"
```

### 配置加载函数

**位置**: 扩展命令 (如 `commands/specstoissues.md`)

````markdown
## Load Configuration

1. Run helper script to load and merge config:

```bash
config_json=$(bash .specify/extensions/jira/scripts/parse-jira-config.sh)
echo "$config_json"
```

1. Parse JSON and use in subsequent steps
````

**脚本**: `.specify/extensions/jira/scripts/parse-jira-config.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

EXT_DIR=".specify/extensions/jira"
CONFIG_FILE="$EXT_DIR/jira-config.yml"
LOCAL_CONFIG="$EXT_DIR/jira-config.local.yml"

# Start with defaults from extension.yml
defaults=$(yq eval '.defaults' "$EXT_DIR/extension.yml" -o=json)

# Merge project config
if [ -f "$CONFIG_FILE" ]; then
  project_config=$(yq eval '.' "$CONFIG_FILE" -o=json)
  defaults=$(echo "$defaults $project_config" | jq -s '.[0] * .[1]')
fi

# Merge local config
if [ -f "$LOCAL_CONFIG" ]; then
  local_config=$(yq eval '.' "$LOCAL_CONFIG" -o=json)
  defaults=$(echo "$defaults $local_config" | jq -s '.[0] * .[1]')
fi

# Apply environment variable overrides
if [ -n "${SPECKIT_JIRA_PROJECT_KEY:-}" ]; then
  defaults=$(echo "$defaults" | jq ".project.key = \"$SPECKIT_JIRA_PROJECT_KEY\"")
fi

# Output merged config as JSON
echo "$defaults"
```

### 配置验证

**在命令文件中**:

````markdown
## Validate Configuration

1. Load config (from previous step)
2. Validate against schema from extension.yml:

```python
import jsonschema

schema = load_yaml(".specify/extensions/jira/extension.yml")['config_schema']
config = json.loads(config_json)

try:
    jsonschema.validate(config, schema)
except jsonschema.ValidationError as e:
    print(f"❌ Invalid jira-config.yml: {e.message}")
    print(f"   Path: {'.'.join(str(p) for p in e.path)}")
    exit(1)
```

1. Proceed with validated config
````

---

## 钩子系统

### 钩子定义

**在 extension.yml 中:**

```yaml
hooks:
  after_tasks:
    command: "speckit.jira.specstoissues"
    optional: true
    prompt: "Create Jira issues from tasks?"
    description: "Automatically create Jira hierarchy"
    condition: "config.project.key is set"
```

### 钩子注册

**在扩展安装期间**, 将钩子记录到项目配置:

**文件**: `.specify/extensions.yml` (项目级扩展配置)

```yaml
# Extensions installed in this project
installed:
  - jira
  - linear

# Global extension settings
settings:
  auto_execute_hooks: true  # Prompt for optional hooks after commands

# Hook configuration
hooks:
  after_tasks:
    - extension: jira
      command: speckit.jira.specstoissues
      enabled: true
      optional: true
      prompt: "Create Jira issues from tasks?"

  after_implement:
    - extension: jira
      command: speckit.jira.sync-status
      enabled: true
      optional: true
      prompt: "Sync completion status to Jira?"
```

### 钩子执行

**在核心命令中** (如 `templates/commands/tasks.md`):

在命令末尾添加:

````markdown
## Extension Hooks

After task generation completes, check for registered hooks:

```bash
# Check if extensions.yml exists and has after_tasks hooks
if [ -f ".specify/extensions.yml" ]; then
  # Parse hooks for after_tasks
  hooks=$(yq eval '.hooks.after_tasks[] | select(.enabled == true)' .specify/extensions.yml -o=json)

  if [ -n "$hooks" ]; then
    echo ""
    echo "📦 Extension hooks available:"

    # Iterate hooks
    echo "$hooks" | jq -c '.' | while read -r hook; do
      extension=$(echo "$hook" | jq -r '.extension')
      command=$(echo "$hook" | jq -r '.command')
      optional=$(echo "$hook" | jq -r '.optional')
      prompt_text=$(echo "$hook" | jq -r '.prompt')

      if [ "$optional" = "true" ]; then
        # Prompt user
        echo ""
        read -p "$prompt_text (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          echo "▶ Executing: $command"
          # Let AI agent execute the command
          # (AI agent will see this and execute)
          echo "EXECUTE_COMMAND: $command"
        fi
      else
        # Auto-execute mandatory hooks
        echo "▶ Executing: $command (required)"
        echo "EXECUTE_COMMAND: $command"
      fi
    done
  fi
fi
```
````

**AI 代理处理**:

AI 代理在输出中看到 `EXECUTE_COMMAND: speckit.jira.specstoissues` 并自动调用该命令。

**替代方案**: 在代理上下文中直接调用 (如果代理支持):

```python
# In AI agent's command execution engine
def execute_command_with_hooks(command_name: str, args: str):
    # Execute main command
    result = execute_command(command_name, args)

    # Check for hooks
    hooks = load_hooks_for_phase(f"after_{command_name}")
    for hook in hooks:
        if hook.optional:
            if confirm(hook.prompt):
                execute_command(hook.command, args)
        else:
            execute_command(hook.command, args)

    return result
```

### 钩子条件

扩展可以为钩子指定**条件**:

```yaml
hooks:
  after_tasks:
    command: "speckit.jira.specstoissues"
    optional: true
    condition: "config.project.key is set and config.enabled == true"
```

**条件评估** (在钩子执行器中):

```python
def should_execute_hook(hook: dict, config: dict) -> bool:
    """Evaluate hook condition."""
    condition = hook.get('condition')
    if not condition:
        return True  # No condition = always eligible

    # Simple expression evaluator
    # "config.project.key is set" → check if config['project']['key'] exists
    # "config.enabled == true" → check if config['enabled'] is True

    return eval_condition(condition, config)
```

---

## 扩展发现与目录

### 双目录系统

Spec Kit 使用两种不同用途的目录文件:

#### 用户目录 (`catalog.json`)

**URL**: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json`

- **用途**: 组织策划的已批准扩展目录
- **默认状态**: 默认为空 - 用户填充信任的扩展
- **用法**: 默认栈中的主目录 (优先级 1, `install_allowed: true`)
- **控制**: 组织维护自己的分叉/版本供团队使用

#### 社区参考目录 (`catalog.community.json`)

**URL**: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json`

- **用途**: 可用的社区贡献扩展的参考目录
- **验证**: 社区扩展初始时可能有 `verified: false`
- **状态**: 活跃 - 开放社区贡献
- **提交**: 通过 Pull Request, 遵循扩展发布指南
- **用法**: 默认栈中的辅助目录 (优先级 2, `install_allowed: false`) - 仅发现

**工作原理 (默认栈)**:

1. **发现**: `specify-cn extension search` 搜索两个目录 - 社区扩展自动出现
2. **审查**: 评估社区扩展的安全性、质量和组织适配性
3. **策划**: 将批准的条目从社区目录复制到你的 `catalog.json`, 或添加到 `.specify/extension-catalogs.yml` 并设置 `install_allowed: true`
4. **安装**: 使用 `specify-cn extension add <name>` - 仅允许从 `install_allowed: true` 的目录安装

此方法为组织提供了对可安装扩展的完全控制, 同时仍开箱即用地提供社区发现功能。

### 目录格式

**格式** (两个目录相同):

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-01-28T14:30:00Z",
  "extensions": {
    "jira": {
      "name": "Jira Integration",
      "id": "jira",
      "description": "Create Jira Epics, Stories, and Issues from spec-kit artifacts",
      "author": "Stats Perform",
      "version": "1.0.0",
      "download_url": "https://github.com/statsperform/spec-kit-jira/releases/download/v1.0.0/spec-kit-jira-1.0.0.zip",
      "repository": "https://github.com/statsperform/spec-kit-jira",
      "homepage": "https://github.com/statsperform/spec-kit-jira/blob/main/README.md",
      "documentation": "https://github.com/statsperform/spec-kit-jira/blob/main/docs/",
      "changelog": "https://github.com/statsperform/spec-kit-jira/blob/main/CHANGELOG.md",
      "license": "MIT",
      "requires": {
        "speckit_version": ">=0.1.0,<2.0.0",
        "tools": [
          {
            "name": "jira-mcp-server",
            "version": ">=1.0.0"
          }
        ]
      },
      "tags": ["issue-tracking", "jira", "atlassian", "project-management"],
      "verified": true,
      "downloads": 1250,
      "stars": 45
    },
    "linear": {
      "name": "Linear Integration",
      "id": "linear",
      "description": "Sync spec-kit tasks with Linear issues",
      "author": "Community",
      "version": "0.9.0",
      "download_url": "https://github.com/example/spec-kit-linear/releases/download/v0.9.0/spec-kit-linear-0.9.0.zip",
      "repository": "https://github.com/example/spec-kit-linear",
      "requires": {
        "speckit_version": ">=0.1.0"
      },
      "tags": ["issue-tracking", "linear"],
      "verified": false
    }
  }
}
```

### 目录发现命令

```bash
# 列出所有可用扩展
specify-cn extension search

# 按关键词搜索
specify-cn extension search jira

# 按标签搜索
specify-cn extension search --tag issue-tracking

# 显示扩展详情
specify-cn extension info jira
```

### 自定义目录

Spec Kit 支持**目录栈** - CLI 跨越多个目录合并和搜索的有序列表。这允许组织维护自己的组织批准扩展, 同时包含内部目录和社区发现, 一切并行。

#### 目录栈解析

活跃目录栈按以下顺序解析 (首次匹配优先):

1. **`SPECKIT_CATALOG_URL` 环境变量** - 单个目录替换所有默认值 (向后兼容)
2. **项目级 `.specify/extension-catalogs.yml`** - 项目的完全控制
3. **用户级 `~/.specify/extension-catalogs.yml`** - 个人默认值
4. **内置默认栈** - `catalog.json` (install_allowed: true) + `catalog.community.json` (install_allowed: false)

#### 默认内置栈

当没有配置文件时, CLI 使用:

| 优先级 | 目录 | install_allowed | 用途 |
|----------|---------|-----------------|---------|
| 1 | `catalog.json` (默认) | `true` | 可安装的策划扩展 |
| 2 | `catalog.community.json` (社区) | `false` | 仅发现 - 浏览但不可安装 |

这意味着 `specify-cn extension search` 开箱即用地显示社区扩展, 而 `specify-cn extension add` 仍限制为来自 `install_allowed: true` 目录的条目。

#### `.specify/extension-catalogs.yml` 配置文件

```yaml
catalogs:
  - name: "default"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json"
    priority: 1          # Highest — only approved entries can be installed
    install_allowed: true
    description: "Built-in catalog of installable extensions"

  - name: "internal"
    url: "https://internal.company.com/spec-kit/catalog.json"
    priority: 2
    install_allowed: true
    description: "Internal company extensions"

  - name: "community"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json"
    priority: 3          # Lowest — discovery only, not installable
    install_allowed: false
    description: "Community-contributed extensions (discovery only)"
```

用户级别的等效文件位于 `~/.specify/extension-catalogs.yml`。当项目级配置存在并包含一个或多个目录条目时, 它完全控制, 内置默认值不应用。空的 `catalogs: []` 列表被视为与无配置文件相同, 回退到默认值。

#### 目录 CLI 命令

```bash
# 列出活跃目录及名称、URL、优先级和 install_allowed
specify-cn extension catalog list

# 添加目录 (项目级)
specify-cn extension catalog add --name "internal" --install-allowed \
  https://internal.company.com/spec-kit/catalog.json

# 添加仅发现目录
specify-cn extension catalog add --name "community" \
  https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json

# 移除目录
specify-cn extension catalog remove internal

# 显示扩展来自哪个目录
specify-cn extension info jira
# → Source catalog: default
```

#### 合并冲突解决

当相同的扩展 `id` 出现在多个目录中时, 优先级更高 (优先级数值更低) 的目录优先。来自较低优先级目录中相同 `id` 的扩展被忽略。

#### `install_allowed: false` 行为

来自仅发现目录的扩展会出现在 `specify-cn extension search` 结果中, 但不能直接安装:

```
⚠  'linear' is available in the 'community' catalog but installation is not allowed from that catalog.

To enable installation, add 'linear' to an approved catalog (install_allowed: true) in .specify/extension-catalogs.yml.
```

#### `SPECKIT_CATALOG_URL` (向后兼容)

`SPECKIT_CATALOG_URL` 环境变量仍然可用 - 它被视为单个 `install_allowed: true` 目录, **替换两个默认值**以实现完全向后兼容:

```bash
# 指向你组织的目录
export SPECKIT_CATALOG_URL="https://internal.company.com/spec-kit/catalog.json"

# 所有扩展命令现在使用你的自定义目录
specify-cn extension search       # Uses custom catalog
specify-cn extension add jira     # Installs from custom catalog
```

**要求**:
- URL 必须使用 HTTPS (仅 localhost 测试允许 HTTP)
- 目录必须遵循标准 catalog.json 模式
- 必须可公开访问或可在你的网络内访问

**测试示例**:
```bash
# 开发期间使用 localhost 测试
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"
specify-cn extension search
```

---

## CLI 命令

### `specify-cn extension` 子命令

#### `specify-cn extension list`

列出当前项目中已安装的扩展。

```bash
$ specify-cn extension list

Installed Extensions:
  ✓ Jira Integration (v1.0.0)
     jira
     Create Jira issues from spec-kit artifacts
     Commands: 3 | Hooks: 2 | Priority: 10 | Status: Enabled

  ✓ Linear Integration (v0.9.0)
     linear
     Create Linear issues from spec-kit artifacts
     Commands: 1 | Hooks: 1 | Priority: 10 | Status: Enabled
```

**选项**:

- `--available`: 显示目录中可用 (未安装) 的扩展
- `--all`: 同时显示已安装和可用的扩展

#### `specify-cn extension search [QUERY]`

搜索扩展目录。

```bash
$ specify-cn extension search jira

Found 1 extension:

┌─────────────────────────────────────────────────────────┐
│ jira (v1.0.0) ✓ Verified                                │
│ Jira Integration                                        │
│                                                         │
│ Create Jira Epics, Stories, and Issues from spec-kit   │
│ artifacts                                               │
│                                                         │
│ Author: Stats Perform                                   │
│ Tags: issue-tracking, jira, atlassian                   │
│ Downloads: 1,250                                        │
│                                                         │
│ Repository: github.com/statsperform/spec-kit-jira       │
│ Documentation: github.com/.../docs                      │
└─────────────────────────────────────────────────────────┘

Install: specify-cn extension add jira
```

**选项**:

- `--tag TAG`: 按标签过滤
- `--author AUTHOR`: 按作者过滤
- `--verified`: 仅显示已验证的扩展

#### `specify-cn extension info NAME`

显示扩展的详细信息。

```bash
$ specify-cn extension info jira

Jira Integration (jira) v1.0.0

Description:
  Create Jira Epics, Stories, and Issues from spec-kit artifacts

Author: Stats Perform
License: MIT
Repository: https://github.com/statsperform/spec-kit-jira
Documentation: https://github.com/statsperform/spec-kit-jira/blob/main/docs/

Requirements:
  • Spec Kit: >=0.1.0,<2.0.0
  • Tools: jira-mcp-server (>=1.0.0)

Provides:
  Commands:
    • speckit.jira.specstoissues - Create Jira hierarchy from spec and tasks
    • speckit.jira.discover-fields - Discover Jira custom fields
    • speckit.jira.sync-status - Sync task completion status

  Hooks:
    • after_tasks - Prompt to create Jira issues
    • after_implement - Prompt to sync status

Tags: issue-tracking, jira, atlassian, project-management

Downloads: 1,250 | Stars: 45 | Verified: ✓

Install: specify-cn extension add jira
```

#### `specify-cn extension add NAME`

安装扩展。

```bash
$ specify-cn extension add jira

Installing extension: Jira Integration

✓ Downloaded spec-kit-jira-1.0.0.zip (245 KB)
✓ Validated manifest
✓ Checked compatibility (spec-kit 0.1.0 ≥ 0.1.0)
✓ Extracted to .specify/extensions/jira/
✓ Registered 3 commands with claude
✓ Installed config template (jira-config.yml)

⚠  Configuration required:
   Edit .specify/extensions/jira/jira-config.yml to set your Jira project key

Extension installed successfully!

Next steps:
  1. Configure: vim .specify/extensions/jira/jira-config.yml
  2. Discover fields: /speckit.jira.discover-fields
  3. Use commands: /speckit.jira.specstoissues
```

**选项**:

- `--from URL`: 从远程 URL (归档) 安装。不接受直接的 Git 仓库。
- `--dev`: 从本地路径以开发模式安装 (PATH 是位置参数 `extension`)。
- `--priority NUMBER`: 设置解析优先级 (数值越低 = 优先级越高, 默认 10)

#### `specify-cn extension remove NAME`

卸载扩展。

```bash
$ specify-cn extension remove jira

⚠  This will remove:
   • 3 commands from AI agent
   • Extension directory: .specify/extensions/jira/
   • Config file: jira-config.yml (will be backed up)

Continue? (yes/no): yes

✓ Unregistered commands
✓ Backed up config to .specify/extensions/.backup/jira-config.yml
✓ Removed extension directory
✓ Updated registry

Extension removed successfully.

To reinstall: specify-cn extension add jira
```

**选项**:

- `--keep-config`: 不移除配置文件
- `--force`: 跳过确认

#### `specify-cn extension update [NAME]`

更新扩展到最新版本。

```bash
$ specify-cn extension update jira

Checking for updates...

jira: 1.0.0 → 1.1.0 available

Changes in v1.1.0:
  • Added support for custom workflows
  • Fixed issue with parallel tasks
  • Improved error messages

Update? (yes/no): yes

✓ Downloaded spec-kit-jira-1.1.0.zip
✓ Validated manifest
✓ Backed up current version
✓ Extracted new version
✓ Preserved config file
✓ Re-registered commands

Extension updated successfully!

Changelog: https://github.com/statsperform/spec-kit-jira/blob/main/CHANGELOG.md#v110
```

**选项**:

- `--all`: 更新所有扩展
- `--check`: 检查更新但不安装
- `--force`: 即使已是最新版本也强制更新

#### `specify-cn extension enable/disable NAME`

启用或禁用扩展而不移除它。

```bash
$ specify-cn extension disable jira

✓ Disabled extension: jira
  • Commands unregistered (but files preserved)
  • Hooks will not execute

To re-enable: specify-cn extension enable jira
```

#### `specify-cn extension set-priority NAME PRIORITY`

更改已安装扩展的解析优先级。

```bash
$ specify-cn extension set-priority jira 5

✓ Extension 'Jira Integration' priority changed: 10 → 5

Lower priority = higher precedence in template resolution
```

**优先级值**:

- 数值越低 = 优先级越高 (解析时首先检查)
- 默认优先级为 10
- 必须为正整数 (1 或更高)

**使用场景**:

- 确保关键扩展的模板优先
- 当多个扩展提供类似模板时覆盖默认解析顺序

---

## 兼容性与版本控制

### 语义化版本

扩展遵循 [SemVer 2.0.0](https://semver.org/):

- **MAJOR**: 破坏性变更 (命令 API 变更, 配置模式变更)
- **MINOR**: 新功能 (新命令, 新配置选项)
- **PATCH**: 缺陷修复 (无 API 变更)

### 兼容性检查

**安装时**:

```python
def check_compatibility(extension_manifest: dict) -> bool:
    """Check if extension is compatible with current environment."""

    requires = extension_manifest['requires']

    # 1. Check spec-kit version
    current_speckit = get_speckit_version()  # e.g., "0.1.5"
    required_speckit = requires['speckit_version']  # e.g., ">=0.1.0,<2.0.0"

    if not version_satisfies(current_speckit, required_speckit):
        raise IncompatibleVersionError(
            f"Extension requires spec-kit {required_speckit}, "
            f"but {current_speckit} is installed. "
            f"Upgrade spec-kit with: uv tool install specify-cn-cli --force"
        )

    # 2. Check required tools
    for tool in requires.get('tools', []):
        tool_name = tool['name']
        tool_version = tool.get('version')

        if tool.get('required', True):
            if not check_tool(tool_name):
                raise MissingToolError(
                    f"Extension requires tool: {tool_name}\n"
                    f"Install from: {tool.get('install_url', 'N/A')}"
                )

            if tool_version:
                installed = get_tool_version(tool_name, tool.get('check_command'))
                if not version_satisfies(installed, tool_version):
                    raise IncompatibleToolVersionError(
                        f"Extension requires {tool_name} {tool_version}, "
                        f"but {installed} is installed"
                    )

    # 3. Check required commands
    for cmd in requires.get('commands', []):
        if not command_exists(cmd):
            raise MissingCommandError(
                f"Extension requires core command: {cmd}\n"
                f"Update spec-kit to latest version"
            )

    return True
```

### 弃用策略

**扩展清单可以标记功能为已弃用:**

```yaml
provides:
  commands:
    - name: "speckit.jira.old-command"
      file: "commands/old-command.md"
      deprecated: true
      deprecated_message: "Use speckit.jira.new-command instead"
      removal_version: "2.0.0"
```

**运行时显示警告:**

```text
⚠️  Warning: /speckit.jira.old-command is deprecated
   Use /speckit.jira.new-command instead
   This command will be removed in v2.0.0
```

---

## 安全考量

### 信任模型

扩展以**与 AI 代理相同的权限**运行:

- 可以执行 Shell 命令
- 可以读写项目中的文件
- 可以发起网络请求

**信任边界**: 用户必须信任扩展作者。

### 验证

**已验证的扩展** (在目录中):

- 由已知组织发布 (GitHub, Stats Perform 等)
- 由 spec-kit 维护者进行代码审查
- 在目录中标记 ✓ 标志

**社区扩展**:

- 未验证, 使用需自担风险
- 安装时显示警告:

  ```text
  ⚠️  This extension is not verified.
     Review code before installing: https://github.com/...

     Continue? (yes/no):
  ```

### 沙箱化 (未来)

**Phase 2** (不在初始发布中):

- 扩展在清单中声明所需权限
- CLI 强制执行权限边界
- 示例权限: `filesystem:read`, `network:external`, `env:read`

```yaml
# Future extension.yml
permissions:
  - "filesystem:read:.specify/extensions/jira/"  # Can only read own config
  - "filesystem:write:.specify/memory/"          # Can write to memory
  - "network:external:*.atlassian.net"           # Can call Jira API
  - "env:read:SPECKIT_JIRA_*"                    # Can read own env vars
```

### 包完整性

**未来**: 使用 GPG/Sigstore 签名扩展包

```yaml
# catalog.json
"jira": {
  "download_url": "...",
  "checksum": "sha256:abc123...",
  "signature": "https://github.com/.../spec-kit-jira-1.0.0.sig",
  "signing_key": "https://github.com/statsperform.gpg"
}
```

CLI 在解压前验证签名。

---

## 迁移策略

### 向后兼容

**目标**: 现有 spec-kit 项目无需更改即可工作。

**策略**:

1. **核心命令不变**: `/speckit.tasks`, `/speckit.implement` 等保留在核心中

2. **可选扩展**: 用户按需选用扩展

3. **渐进迁移**: 现有 `taskstoissues` 保留在核心中, Jira 扩展是替代方案

4. **弃用时间线**:
   - **v0.2.0**: 引入扩展系统, 保留核心 `taskstoissues`
   - **v0.3.0**: 将核心 `taskstoissues` 标记为 "legacy" (仍然可用)
   - **v1.0.0**: 考虑移除核心 `taskstoissues`, 改用扩展

### 用户迁移路径

**场景 1**: 用户没有使用 `taskstoissues`

- 无需迁移, 扩展是可选的

**场景 2**: 用户使用核心 `taskstoissues` (GitHub Issues)

- 照常工作
- 可选: 迁移到 `github-projects` 扩展以获取更多功能

**场景 3**: 用户需要 Jira (新需求)

- `specify-cn extension add jira`
- 配置并使用

**场景 4**: 用户有调用 `taskstoissues` 的自定义脚本

- 脚本仍然可用 (核心命令保留)
- 迁移指南说明如何改为调用扩展命令

### 扩展迁移指南

**对于扩展作者** (如果核心命令变为扩展):

```bash
# 旧 (核心命令)
/speckit.taskstoissues

# 新 (扩展命令)
specify-cn extension add github-projects
/speckit.github.taskstoissues
```

**迁移别名** (如需要):

```yaml
# extension.yml
provides:
  commands:
    - name: "speckit.github.taskstoissues"
      file: "commands/taskstoissues.md"
      aliases: ["speckit.github.sync-taskstoissues"]  # Alternate namespaced entry point
```

AI 代理注册两个名称, 因此调用者可以迁移到替代别名, 而无需依赖已弃用的全局快捷方式如 `/speckit.taskstoissues`。

---

## 实现阶段

### Phase 1: 核心扩展系统 ✅ 已完成

**目标**: 基础扩展基础设施

**交付物**:

- [x] 扩展清单模式 (`extension.yml`)
- [x] 扩展目录结构
- [x] CLI 命令:
  - [x] `specify-cn extension list`
  - [x] `specify-cn extension add` (从 URL 和本地 `--dev`)
  - [x] `specify-cn extension remove`
- [x] 扩展注册表 (`.specify/extensions/.registry`)
- [x] 命令注册 (Claude 和 15+ 其他代理)
- [x] 基础验证 (清单模式, 兼容性)
- [x] 文档 (扩展开发指南)

**测试**:

- [x] 清单解析的单元测试
- [x] 集成测试: 安装虚拟扩展
- [x] 集成测试: 向 Claude 注册命令

### Phase 2: Jira 扩展 ✅ 已完成

**目标**: 第一个生产扩展

**交付物**:

- [x] 创建 `spec-kit-jira` 仓库
- [x] 将 Jira 功能迁移到扩展
- [x] 创建 `jira-config.yml` 模板
- [x] 命令:
  - [x] `specstoissues.md`
  - [x] `discover-fields.md`
  - [x] `sync-status.md`
- [x] 辅助脚本
- [x] 文档 (README, 配置指南, 示例)
- [x] 发布 v3.0.0

**测试**:

- [x] 在 `eng-msa-ts` 项目上测试
- [x] 验证 spec->Epic, phase->Story, task->Issue 映射
- [x] 测试配置加载和验证
- [x] 测试自定义字段应用

### Phase 3: 扩展目录 ✅ 已完成

**目标**: 发现与分发

**交付物**:

- [x] 中央目录 (`extensions/catalog.json` 在 spec-kit 仓库中)
- [x] 社区目录 (`extensions/catalog.community.json`)
- [x] 目录获取和解析, 支持多目录
- [x] CLI 命令:
  - [x] `specify-cn extension search`
  - [x] `specify-cn extension info`
  - [x] `specify-cn extension catalog list`
  - [x] `specify-cn extension catalog add`
  - [x] `specify-cn extension catalog remove`
- [x] 文档 (如何发布扩展)

**测试**:

- [x] 测试目录获取
- [x] 测试扩展搜索/过滤
- [x] 测试目录缓存
- [x] 测试带优先级的多目录合并

### Phase 4: 高级功能 ✅ 已完成

**目标**: 钩子、更新、多代理支持

**交付物**:

- [x] 钩子系统 (`hooks` 在 extension.yml 中)
- [x] 钩子注册和执行
- [x] 项目扩展配置 (`.specify/extensions.yml`)
- [x] CLI 命令:
  - [x] `specify-cn extension update` (带原子备份/恢复)
  - [x] `specify-cn extension enable/disable`
- [x] 多代理命令注册 (15+ 代理, 包括 Claude, Copilot, Gemini, Cursor 等)
- [x] 扩展更新通知 (版本比较)
- [x] 配置层解析 (项目、本地、环境变量)

**超出原始 RFC 实现的额外功能**:

- [x] **显示名称解析**: 所有命令除了 ID 外还接受扩展显示名称
- [x] **模糊名称处理**: 当多个扩展匹配一个名称时显示用户友好的表格
- [x] **带回滚的原子更新**: 扩展目录、命令、钩子和注册表的完整备份, 失败时自动回滚
- [x] **安装前 ID 验证**: 安装前从 ZIP 验证扩展 ID (安全)
- [x] **启用状态保留**: 禁用的扩展更新后保持禁用状态
- [x] **注册表更新/恢复方法**: 用于启用/禁用和回滚操作的简洁 API
- [x] **目录错误回退**: `extension info` 在目录不可用时回退到本地信息
- [x] **`_install_allowed` 标志**: 仅发现的目录不能用于安装
- [x] **缓存失效**: `SPECKIT_CATALOG_URL` 变更时缓存失效

**测试**:

- [x] 在核心命令中测试钩子
- [x] 测试扩展更新 (保留配置)
- [x] 测试多代理注册
- [x] 测试更新失败时的原子回滚
- [x] 测试启用状态保留
- [x] 测试显示名称解析

### Phase 5: 完善与文档 ✅ 已完成

**目标**: 生产就绪

**交付物**:

- [x] 全面文档:
  - [x] 用户指南 (EXTENSION-USER-GUIDE.md)
  - [x] 扩展开发指南 (EXTENSION-DEV-GUIDE.md)
  - [x] 扩展 API 参考 (EXTENSION-API-REFERENCE.md)
- [x] 错误消息和验证改进
- [x] CLI 帮助文本更新

**测试**:

- [x] 多个项目的端到端测试
- [x] 163 个单元测试通过

---

## 已解决的问题

原始 RFC 中的以下问题在实现过程中已解决:

### 1. 扩展命名空间 ✅ 已解决

**问题**: 扩展命令是否应使用命名空间前缀?

**决策**: **方案 C** - 同时支持前缀和别名。命令使用 `speckit.{extension}.{command}` 作为规范名称, 并可在清单中定义可选别名。

**实现**: `extension.yml` 中的 `aliases` 字段允许扩展注册额外的命令名称。

---

### 2. 配置文件位置 ✅ 已解决

**问题**: 扩展配置应放在哪里?

**决策**: **方案 A** - 扩展目录 (`.specify/extensions/{ext-id}/{ext-id}-config.yml`)。这保持了扩展的自包含性和易管理性。

**实现**: 每个扩展在其目录内有自己的配置文件, 采用分层解析 (默认值 -> 项目 -> 本地 -> 环境变量)。

---

### 3. 命令文件格式 ✅ 已解决

**问题**: 扩展应使用通用格式还是代理特定格式?

**决策**: **方案 A** - 通用 Markdown 格式。扩展编写一次命令, CLI 在注册期间转换为代理特定格式。

**实现**: `CommandRegistrar` 类处理转换为 15+ 代理格式 (Claude, Copilot, Gemini, Cursor 等)。

---

### 4. 钩子执行模型 ✅ 已解决

**问题**: 钩子应如何执行?

**决策**: **方案 A** - 钩子注册在 `.specify/extensions.yml` 中, 当 AI 代理看到钩子触发时执行。钩子状态 (启用/禁用) 按扩展管理。

**实现**: `HookExecutor` 类管理 `extensions.yml` 中的钩子注册和状态。

---

### 5. 扩展分发 ✅ 已解决

**问题**: 扩展应如何打包?

**决策**: **方案 A** - 从 GitHub Releases 下载 ZIP 归档 (通过目录 `download_url`)。本地开发使用 `--dev` 标志和目录路径。

**实现**: `ExtensionManager.install_from_zip()` 处理 ZIP 解压和验证。

---

### 6. 多版本支持 ✅ 已解决

**问题**: 同一扩展的多个版本能否共存?

**决策**: **方案 A** - 仅支持单版本。更新时替换现有版本, 失败时原子回滚。

**实现**: `extension update` 执行原子备份/恢复以确保安全更新。

---

## 未解决的问题 (剩余)

### 1. 沙箱化/权限 (未来)

**问题**: 扩展是否应声明所需权限?

**选项**:

- A) 无沙箱化 (当前): 扩展以与 AI 代理相同的权限运行
- B) 权限声明: 扩展声明 `filesystem:read`, `network:external` 等
- C) 选择性沙箱化: 组织可以启用权限强制执行

**状态**: 推迟到未来版本。当前使用基于信任的模型, 用户信任扩展作者。

---

### 2. 包签名 (未来)

**问题**: 扩展是否应进行加密签名?

**选项**:

- A) 无签名 (当前): 基于目录来源的信任
- B) GPG/Sigstore 签名: 验证包完整性
- C) 目录级验证: 目录维护者验证包

**状态**: 推迟到未来版本。目录模式中提供了 `checksum` 字段但未强制执行。

---

## 附录

### 附录 A: 示例扩展结构

**`spec-kit-jira` 扩展的完整结构:**

```text
spec-kit-jira/
├── README.md                        # Overview, features, installation
├── LICENSE                          # MIT license
├── CHANGELOG.md                     # Version history
├── .gitignore                       # Ignore local configs
│
├── extension.yml                    # Extension manifest (required)
├── jira-config.template.yml         # Config template
│
├── commands/                        # Command files
│   ├── specstoissues.md            # Main command
│   ├── discover-fields.md          # Helper: Discover custom fields
│   └── sync-status.md              # Helper: Sync completion status
│
├── scripts/                         # Helper scripts
│   ├── parse-jira-config.sh        # Config loader (bash)
│   ├── parse-jira-config.ps1       # Config loader (PowerShell)
│   └── validate-jira-connection.sh # Connection test
│
├── docs/                            # Documentation
│   ├── installation.md             # Installation guide
│   ├── configuration.md            # Configuration reference
│   ├── usage.md                    # Usage examples
│   ├── troubleshooting.md          # Common issues
│   └── examples/
│       ├── eng-msa-ts-config.yml   # Real-world config example
│       └── simple-project.yml      # Minimal config example
│
├── tests/                           # Tests (optional)
│   ├── test-extension.sh           # Extension validation
│   └── test-commands.sh            # Command execution tests
│
└── .github/                         # GitHub integration
    └── workflows/
        └── release.yml              # Automated releases
```

### 附录 B: 扩展开发指南 (大纲)

**创建新扩展的文档:**

1. **入门**
   - 先决条件 (所需工具)
   - 扩展模板 (cookiecutter)
   - 目录结构

2. **扩展清单**
   - 模式参考
   - 必填与可选字段
   - 版本控制指南

3. **命令开发**
   - 通用命令格式
   - Frontmatter 规范
   - 模板变量
   - 脚本引用

4. **配置**
   - 配置文件结构
   - 模式验证
   - 分层配置解析
   - 环境变量覆盖

5. **钩子**
   - 可用的钩子点
   - 钩子注册
   - 条件执行
   - 最佳实践

6. **测试**
   - 本地开发设置
   - 使用 `--dev` 标志测试
   - 验证检查清单
   - 集成测试

7. **发布**
   - 打包 (ZIP 格式)
   - GitHub Releases
   - 目录提交
   - 版本控制策略

8. **示例**
   - 最小扩展
   - 带钩子的扩展
   - 带配置的扩展
   - 带多命令的扩展

### 附录 C: 兼容性矩阵

**计划的支持矩阵:**

| 扩展功能 | Spec Kit 版本 | AI 代理支持 |
|-------------------|------------------|------------------|
| Basic commands | 0.2.0+ | Claude, Gemini, Copilot |
| Hooks (after_tasks) | 0.3.0+ | Claude, Gemini |
| Config validation | 0.2.0+ | All |
| Multiple catalogs | 0.4.0+ | All |
| Permissions (sandboxing) | 1.0.0+ | TBD |

### 附录 D: 扩展目录模式

**`catalog.json` 的完整模式:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "updated_at", "extensions"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "extensions": {
      "type": "object",
      "patternProperties": {
        "^[a-z0-9-]+$": {
          "type": "object",
          "required": ["name", "id", "version", "download_url", "repository"],
          "properties": {
            "name": { "type": "string" },
            "id": { "type": "string", "pattern": "^[a-z0-9-]+$" },
            "description": { "type": "string" },
            "author": { "type": "string" },
            "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
            "download_url": { "type": "string", "format": "uri" },
            "repository": { "type": "string", "format": "uri" },
            "homepage": { "type": "string", "format": "uri" },
            "documentation": { "type": "string", "format": "uri" },
            "changelog": { "type": "string", "format": "uri" },
            "license": { "type": "string" },
            "requires": {
              "type": "object",
              "properties": {
                "speckit_version": { "type": "string" },
                "tools": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                      "name": { "type": "string" },
                      "version": { "type": "string" }
                    }
                  }
                }
              }
            },
            "tags": {
              "type": "array",
              "items": { "type": "string" }
            },
            "verified": { "type": "boolean" },
            "downloads": { "type": "integer" },
            "stars": { "type": "integer" },
            "checksum": { "type": "string" }
          }
        }
      }
    }
  }
}
```

---

## 总结与下一步

本 RFC 提出了 Spec Kit 的综合扩展系统, 具有:

1. **保持核心精简** 同时支持无限集成
2. **支持多代理** (Claude, Gemini, Copilot 等)
3. **提供清晰的扩展 API** 用于社区贡献
4. **实现独立版本控制** 的扩展和核心
5. **包含安全机制** (验证、兼容性检查)

### 即时下一步

1. **与利益相关者审查** 本 RFC
2. **收集反馈** 关于未解决的问题
3. **基于反馈完善** 设计
4. **进入 Phase A**: 实现核心扩展系统
5. **然后 Phase B**: 构建 Jira 扩展作为概念验证

---

## 讨论问题

1. 扩展架构是否满足你对 Jira 集成的需求?
2. 是否有我们应该考虑的额外钩子点?
3. 我们是否应该支持扩展依赖 (扩展 A 依赖扩展 B)?
4. 我们应如何处理扩展从目录中弃用/移除?
5. 在 v1.0 中我们需要什么级别的沙箱化/权限?

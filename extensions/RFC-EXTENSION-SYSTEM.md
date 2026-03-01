# RFC: Spec Kit 扩展系统

**状态**: Draft
**作者**: Stats Perform Engineering
**创建日期**: 2026-01-28
**更新日期**: 2026-01-28

---

## 目录

1. [摘要](#摘要)
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
13. [安全考虑](#安全考虑)
14. [迁移策略](#迁移策略)
15. [实现阶段](#实现阶段)
16. [开放问题](#开放问题)
17. [附录](#附录)

---

## 摘要

为 Spec Kit 引入扩展系统, 允许与外部工具 (Jira, Linear, Azure DevOps 等) 进行模块化集成, 而不会膨胀核心框架. 扩展是安装到 `.specify/extensions/` 的自包含包, 具有声明式清单, 独立版本化, 并可通过中央目录发现. 

---

## 动机

### 当前问题

1. **单体增长**: 将 Jira 集成添加到核心 spec-kit 会导致:
   - 影响所有用户的大型配置文件
   - 每个人都依赖 Jira MCP server
   - 随着功能累积产生合并冲突

2. **灵活性有限**: 不同组织使用不同工具:
   - GitHub Issues vs Jira vs Linear vs Azure DevOps
   - 自定义内部工具
   - 无法在不膨胀的情况下支持所有工具

3. **维护负担**: 每个集成都会增加:
   - 文档复杂性
   - 测试矩阵扩展
   - 破坏性变更表面积

4. **社区摩擦**: 外部贡献者无法轻松添加集成, 需要核心仓库 PR 批准和发布周期. 

### 目标

1. **模块化**: 核心 spec-kit 保持精简, 扩展为可选
2. **可扩展性**: 用于构建新集成的清晰 API
3. **独立性**: 扩展与核心分开版本化/发布
4. **可发现性**: 用于查找扩展的中央目录
5. **安全性**: 验证, 兼容性检查, 沙箱

---

## 设计原则

### 1. 约定优于配置

- 标准目录结构 (`.specify/extensions/{name}/`)
- 声明式清单 (`extension.yml`)
- 可预测的命令命名 (`speckit.{extension}.{command}`)

### 2. 故障安全默认值

- 缺失的扩展优雅降级 (跳过钩子)
- 无效的扩展会警告但不会破坏核心功能
- 扩展故障与核心操作隔离

### 3. 向后兼容

- 核心命令保持不变
- 扩展仅添加 (不修改核心)
- 旧项目无需扩展即可工作

### 4. 开发者体验

- 简单安装: `specify extension add jira`
- 兼容性问题的清晰错误消息
- 用于测试扩展的本地开发模式

### 5. 安全优先

- 扩展在与 AI 代理相同的上下文中运行 (信任边界)
- 清单验证防止恶意代码
- 验证官方扩展的签名 (未来)

---

## 架构概览

### 目录结构

```text
project/
├── .specify/
│   ├── scripts/                 # 核心脚本 (不变)
│   ├── templates/               # 核心模板 (不变)
│   ├── memory/                  # 会话内存
│   ├── extensions/              # 扩展目录 (新增)
│   │   ├── .registry            # 已安装扩展元数据 (新增)
│   │   ├── jira/                # Jira 扩展
│   │   │   ├── extension.yml    # 清单
│   │   │   ├── jira-config.yml  # 扩展配置
│   │   │   ├── commands/        # 命令文件
│   │   │   ├── scripts/         # 辅助脚本
│   │   │   └── docs/            # 文档
│   │   └── linear/              # Linear 扩展 (示例)
│   └── extensions.yml           # 项目扩展配置 (新增)
└── .gitignore                   # 忽略本地扩展配置
```

### 组件图

```text
┌─────────────────────────────────────────────────────────┐
│                    Spec Kit Core                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CLI (specify)                                   │   │
│  │  - init, check                                   │   │
│  │  - extension add/remove/list/update  ← 新增      │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Extension Manager  ← 新增                       │   │
│  │  - 发现, 安装, 验证                              │   │
│  │  - 命令注册, 钩子执行                            │   │
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
             │ 调用外部工具
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

### Schema: `extension.yml`

```yaml
# Extension Manifest Schema v1.0
# 所有扩展必须在根目录包含此文件

# 用于兼容性的 schema 版本
schema_version: "1.0"

# 扩展元数据 (必需)
extension:
  id: "jira"                    # 唯一标识符 (小写, 字母数字, 连字符)
  name: "Jira Integration"      # 人类可读名称
  version: "1.0.0"              # 语义版本
  description: "Create Jira Epics, Stories, and Issues from spec-kit artifacts"
  author: "Stats Perform"       # 作者/组织
  repository: "https://github.com/statsperform/spec-kit-jira"
  license: "MIT"                # SPDX 许可证标识符
  homepage: "https://github.com/statsperform/spec-kit-jira/blob/main/README.md"

# 兼容性要求 (必需)
requires:
  # Spec-kit 版本 (语义版本范围)
  speckit_version: ">=0.1.0,<2.0.0"

  # 扩展所需的外部工具
  tools:
    - name: "jira-mcp-server"
      required: true
      version: ">=1.0.0"          # 可选: 版本约束
      description: "Jira MCP server for API access"
      install_url: "https://github.com/your-org/jira-mcp-server"
      check_command: "jira --version"  # 可选: 用于验证的 CLI 命令

  # 此扩展依赖的核心 spec-kit 命令
  commands:
    - "speckit.tasks"             # 扩展需要 tasks 命令

  # 需要的核心脚本
  scripts:
    - "check-prerequisites.sh"

# 此扩展提供的内容 (必需)
provides:
  # 添加到 AI 代理的命令
  commands:
    - name: "speckit.jira.specstoissues"
      file: "commands/specstoissues.md"
      description: "Create Jira hierarchy from spec and tasks"
      aliases: ["speckit.specstoissues"]  # 替代名称

    - name: "speckit.jira.discover-fields"
      file: "commands/discover-fields.md"
      description: "Discover Jira custom fields for configuration"

    - name: "speckit.jira.sync-status"
      file: "commands/sync-status.md"
      description: "Sync task completion status to Jira"

  # 配置文件
  config:
    - name: "jira-config.yml"
      template: "jira-config.template.yml"
      description: "Jira integration configuration"
      required: true              # 使用前用户必须配置

  # 辅助脚本
  scripts:
    - name: "parse-jira-config.sh"
      file: "scripts/parse-jira-config.sh"
      description: "Parse jira-config.yml to JSON"
      executable: true            # 安装时设为可执行

# 扩展配置默认值 (可选)
defaults:
  project:
    key: null                     # 无默认值, 用户必须配置
  hierarchy:
    issue_type: "subtask"
  update_behavior:
    mode: "update"
    sync_completion: true

# 用于验证的配置 schema (可选)
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

# 集成钩子 (可选)
hooks:
  # 在 /speckit.tasks 完成后触发的钩子
  after_tasks:
    command: "speckit.jira.specstoissues"
    optional: true
    prompt: "Create Jira issues from tasks?"
    description: "Automatically create Jira hierarchy after task generation"

  # 在 /speckit.implement 完成后触发的钩子
  after_implement:
    command: "speckit.jira.sync-status"
    optional: true
    prompt: "Sync completion status to Jira?"

# 用于发现的标签 (可选)
tags:
  - "issue-tracking"
  - "jira"
  - "atlassian"
  - "project-management"

# 变更日志 URL (可选)
changelog: "https://github.com/statsperform/spec-kit-jira/blob/main/CHANGELOG.md"

# 支持信息 (可选)
support:
  documentation: "https://github.com/statsperform/spec-kit-jira/blob/main/docs/"
  issues: "https://github.com/statsperform/spec-kit-jira/issues"
  discussions: "https://github.com/statsperform/spec-kit-jira/discussions"
  email: "support@statsperform.com"
```

### 验证规则

1. **必须有** `schema_version`, `extension`, `requires`, `provides`
2. **必须遵循** `version` 的语义版本控制
3. **必须有** 唯一的 `id` (与其他扩展不冲突)
4. **必须声明** 所有外部工具依赖
5. **应该包含** `config_schema` (如果扩展使用配置)
6. **应该包含** `support` 信息
7. 命令 `file` 路径**必须是** 相对于扩展根目录
8. 钩子 `command` 名称**必须匹配** `provides.commands` 中的命令

---

## 扩展生命周期

### 1. 发现

```bash
specify extension search jira
# 在目录中搜索匹配 "jira" 的扩展
```

**流程:**

1. 从 GitHub 获取扩展目录
2. 按搜索词过滤 (名称, 标签, 描述)
3. 显示结果及元数据

### 2. 安装

```bash
specify extension add jira
```

**流程:**

1. **解析**: 在目录中查找扩展
2. **下载**: 获取扩展包 (来自 GitHub release 的 ZIP)
3. **验证**: 检查清单 schema, 兼容性
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
      "enabled": true
    }
  }
}
```

### 3. 配置

```bash
# 用户编辑扩展配置
vim .specify/extensions/jira/jira-config.yml
```

**配置发现顺序:**

1. 扩展默认值 (`extension.yml` → `defaults`)
2. 项目配置 (`jira-config.yml`)
3. 本地覆盖 (`jira-config.local.yml` - gitignored)
4. 环境变量 (`SPECKIT_JIRA_*`)

### 4. 使用

```bash
claude
> /speckit.jira.specstoissues
```

**命令解析:**

1. AI 代理在 `.claude/commands/speckit.jira.specstoissues.md` 中找到命令
2. 命令文件引用扩展脚本/配置
3. 扩展在完整上下文中执行

### 5. 更新

```bash
specify extension update jira
```

**流程:**

1. 检查目录中的新版本
2. 下载新版本
3. 验证兼容性
4. 备份当前配置
5. 解压新版本 (保留配置)
6. 重新注册命令
7. 更新注册表

### 6. 移除

```bash
specify extension remove jira
```

**流程:**

1. 与用户确认 (显示将被移除的内容)
2. 从 AI 代理注销命令
3. 从 `.specify/extensions/jira/` 移除
4. 更新注册表
5. 可选保留配置以便重新安装

---

## 命令注册

### 每代理注册

扩展提供**通用命令格式** (基于 Markdown), CLI 在注册时转换为代理特定格式. 

#### 通用命令格式

**位置**: 扩展的 `commands/specstoissues.md`

```markdown
---
# 通用元数据 (所有代理解析)
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

**转换:**

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

**转换:**

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

### 配置文件层级

```yaml
# .specify/extensions/jira/jira-config.yml (项目配置)
project:
  key: "MSATS"

hierarchy:
  issue_type: "subtask"

defaults:
  epic:
    labels: ["spec-driven", "typescript"]
```

```yaml
# .specify/extensions/jira/jira-config.local.yml (本地覆盖 - gitignored)
project:
  key: "MYTEST"  # 本地测试覆盖
```

```bash
# 环境变量 (最高优先级)
export SPECKIT_JIRA_PROJECT_KEY="DEVTEST"
```

### 配置加载函数

**位置**: 扩展命令 (如 `commands/specstoissues.md`)

````markdown
## Load Configuration

1. 运行辅助脚本加载和合并配置:

```bash
config_json=$(bash .specify/extensions/jira/scripts/parse-jira-config.sh)
echo "$config_json"
```

1. 解析 JSON 并在后续步骤中使用
````

**脚本**: `.specify/extensions/jira/scripts/parse-jira-config.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

EXT_DIR=".specify/extensions/jira"
CONFIG_FILE="$EXT_DIR/jira-config.yml"
LOCAL_CONFIG="$EXT_DIR/jira-config.local.yml"

# 从 extension.yml 的默认值开始
defaults=$(yq eval '.defaults' "$EXT_DIR/extension.yml" -o=json)

# 合并项目配置
if [ -f "$CONFIG_FILE" ]; then
  project_config=$(yq eval '.' "$CONFIG_FILE" -o=json)
  defaults=$(echo "$defaults $project_config" | jq -s '.[0] * .[1]')
fi

# 合并本地配置
if [ -f "$LOCAL_CONFIG" ]; then
  local_config=$(yq eval '.' "$LOCAL_CONFIG" -o=json)
  defaults=$(echo "$defaults $local_config" | jq -s '.[0] * .[1]')
fi

# 应用环境变量覆盖
if [ -n "${SPECKIT_JIRA_PROJECT_KEY:-}" ]; then
  defaults=$(echo "$defaults" | jq ".project.key = \"$SPECKIT_JIRA_PROJECT_KEY\"")
fi

# 输出合并后的配置为 JSON
echo "$defaults"
```

### 配置验证

**在命令文件中**:

````markdown
## Validate Configuration

1. 加载配置 (来自上一步)
2. 根据 extension.yml 的 schema 验证:

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

1. 继续使用验证过的配置
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

**在扩展安装期间**, 在项目配置中记录钩子:

**文件**: `.specify/extensions.yml` (项目级扩展配置)

```yaml
# 此项目中安装的扩展
installed:
  - jira
  - linear

# 全局扩展设置
settings:
  auto_execute_hooks: true  # 命令后提示可选钩子

# 钩子配置
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

任务生成完成后, 检查已注册的钩子:

```bash
# 检查 extensions.yml 是否存在且有 after_tasks 钩子
if [ -f ".specify/extensions.yml" ]; then
  # 解析 after_tasks 的钩子
  hooks=$(yq eval '.hooks.after_tasks[] | select(.enabled == true)' .specify/extensions.yml -o=json)

  if [ -n "$hooks" ]; then
    echo ""
    echo "📦 Extension hooks available:"

    # 遍历钩子
    echo "$hooks" | jq -c '.' | while read -r hook; do
      extension=$(echo "$hook" | jq -r '.extension')
      command=$(echo "$hook" | jq -r '.command')
      optional=$(echo "$hook" | jq -r '.optional')
      prompt_text=$(echo "$hook" | jq -r '.prompt')

      if [ "$optional" = "true" ]; then
        # 提示用户
        echo ""
        read -p "$prompt_text (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          echo "▶ Executing: $command"
          # 让 AI 代理执行命令
          # (AI 代理会看到这个并执行)
          echo "EXECUTE_COMMAND: $command"
        fi
      else
        # 自动执行强制性钩子
        echo "▶ Executing: $command (required)"
        echo "EXECUTE_COMMAND: $command"
      fi
    done
  fi
fi
```
````

**AI 代理处理:**

AI 代理在输出中看到 `EXECUTE_COMMAND: speckit.jira.specstoissues` 并自动调用该命令. 

**替代方案**: 在代理上下文中直接调用 (如果代理支持):

```python
# 在 AI 代理的命令执行引擎中
def execute_command_with_hooks(command_name: str, args: str):
    # 执行主命令
    result = execute_command(command_name, args)

    # 检查钩子
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
        return True  # 无条件 = 始终符合条件

    # 简单表达式评估器
    # "config.project.key is set" → 检查 config['project']['key'] 是否存在
    # "config.enabled == true" → 检查 config['enabled'] 是否为 True

    return eval_condition(condition, config)
```

---

## 扩展发现与目录

### 双目录系统

Spec Kit 使用两个不同用途的目录文件:

#### 用户目录 (`catalog.json`)

**URL**: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json`

- **用途**: 组织的已批准扩展精选目录
- **默认状态**: 默认为空 - 用户用他们信任的扩展填充
- **用法**: `specify extension` CLI 命令使用的默认目录
- **控制**: 组织维护自己的分支/版本供团队使用

#### 社区参考目录 (`catalog.community.json`)

**URL**: `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json`

- **用途**: 可用社区贡献扩展的参考目录
- **验证**: 社区扩展最初可能有 `verified: false`
- **状态**: 活跃 - 开放社区贡献
- **提交**: 通过 Pull Request, 遵循扩展发布指南
- **用法**: 浏览发现扩展, 然后复制到你的 `catalog.json`

**工作原理:**

1. **发现**: 浏览 `catalog.community.json` 查找可用扩展
2. **审查**: 评估扩展的安全性, 质量和组织适应性
3. **精选**: 将已批准的扩展条目从社区目录复制到你的 `catalog.json`
4. **安装**: 使用 `specify extension add <name>` (从你的精选目录拉取)

这种方法让组织完全控制团队可用的扩展, 同时维护共享的社区资源用于发现. 

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
specify extension search

# 按关键词搜索
specify extension search jira

# 按标签搜索
specify extension search --tag issue-tracking

# 显示扩展详情
specify extension info jira
```

### 自定义目录

**⚠️ 未来功能 - 尚未实现**

以下目录管理命令是提议的设计概念, 但在当前实现中尚不可用:

```bash
# 添加自定义目录 (未来 - 不可用)
specify extension add-catalog https://internal.company.com/spec-kit/catalog.json

# 设置为默认 (未来 - 不可用)
specify extension set-catalog --default https://internal.company.com/spec-kit/catalog.json

# 列出目录 (未来 - 不可用)
specify extension catalogs
```

**提议的目录优先级** (未来设计):

1. 项目特定目录 (`.specify/extension-catalogs.yml`) - *未实现*
2. 用户级目录 (`~/.specify/extension-catalogs.yml`) - *未实现*
3. 默认 GitHub 目录

#### 当前实现: SPECKIT_CATALOG_URL

**当前可用** 的使用自定义目录的方法是 `SPECKIT_CATALOG_URL` 环境变量:

```bash
# 指向你组织的目录
export SPECKIT_CATALOG_URL="https://internal.company.com/spec-kit/catalog.json"

# 所有扩展命令现在使用你的自定义目录
specify extension search       # 使用自定义目录
specify extension add jira     # 从自定义目录安装
```

**要求:**
- URL 必须使用 HTTPS (仅 localhost 测试允许 HTTP)
- 目录必须遵循标准 catalog.json schema
- 必须公开可访问或在你网络内可访问

**测试示例:**
```bash
# 开发期间使用 localhost 测试
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"
specify extension search
```

---

## CLI 命令

### `specify extension` 子命令

#### `specify extension list`

列出当前项目中已安装的扩展. 

```bash
$ specify extension list

Installed Extensions:
  ✓ jira (v1.0.0) - Jira Integration
    Commands: 3 | Hooks: 2 | Status: Enabled

  ✓ linear (v0.9.0) - Linear Integration
    Commands: 1 | Hooks: 1 | Status: Enabled
```

**选项:**

- `--available`: 显示目录中可用 (未安装) 的扩展
- `--all`: 显示已安装和可用的

#### `specify extension search [QUERY]`

搜索扩展目录. 

```bash
$ specify extension search jira

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

Install: specify extension add jira
```

**选项:**

- `--tag TAG`: 按标签过滤
- `--author AUTHOR`: 按作者过滤
- `--verified`: 仅显示已验证的扩展

#### `specify extension info NAME`

显示扩展的详细信息. 

```bash
$ specify extension info jira

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

Install: specify extension add jira
```

#### `specify extension add NAME`

安装扩展. 

```bash
$ specify extension add jira

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

**选项:**

- `--from URL`: 从自定义 URL 或 Git 仓库安装
- `--version VERSION`: 安装特定版本
- `--dev PATH`: 从本地路径安装 (开发模式)
- `--no-register`: 跳过命令注册 (手动设置)

#### `specify extension remove NAME`

卸载扩展. 

```bash
$ specify extension remove jira

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

To reinstall: specify extension add jira
```

**选项:**

- `--keep-config`: 不移除配置文件
- `--force`: 跳过确认

#### `specify extension update [NAME]`

更新扩展到最新版本. 

```bash
$ specify extension update jira

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

**选项:**

- `--all`: 更新所有扩展
- `--check`: 检查更新但不安装
- `--force`: 即使已是最新也强制更新

#### `specify extension enable/disable NAME`

启用或禁用扩展而不移除它. 

```bash
$ specify extension disable jira

✓ Disabled extension: jira
  • Commands unregistered (but files preserved)
  • Hooks will not execute

To re-enable: specify extension enable jira
```

---

## 兼容性与版本控制

### 语义版本控制

扩展遵循 [SemVer 2.0.0](https://semver.org/):

- **MAJOR**: 破坏性变更 (命令 API 变更, 配置 schema 变更)
- **MINOR**: 新功能 (新命令, 新配置选项)
- **PATCH**: Bug 修复 (无 API 变更)

### 兼容性检查

**安装时:**

```python
def check_compatibility(extension_manifest: dict) -> bool:
    """Check if extension is compatible with current environment."""

    requires = extension_manifest['requires']

    # 1. 检查 spec-kit 版本
    current_speckit = get_speckit_version()  # 如 "0.1.5"
    required_speckit = requires['speckit_version']  # 如 ">=0.1.0,<2.0.0"

    if not version_satisfies(current_speckit, required_speckit):
        raise IncompatibleVersionError(
            f"Extension requires spec-kit {required_speckit}, "
            f"but {current_speckit} is installed. "
            f"Upgrade spec-kit with: uv tool install specify-cli --force"
        )

    # 2. 检查所需工具
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

    # 3. 检查所需命令
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

## 安全考虑

### 信任模型

扩展以**与 AI 代理相同的权限**运行:

- 可以执行 shell 命令
- 可以读/写项目中的文件
- 可以进行网络请求

**信任边界**: 用户必须信任扩展作者. 

### 验证

**已验证扩展** (在目录中):

- 由知名组织发布 (GitHub, Stats Perform 等)
- 由 spec-kit 维护者进行代码审查
- 在目录中标记 ✓ 徽章

**社区扩展**:

- 未验证, 使用风险自负
- 安装时显示警告:

  ```text
  ⚠️  This extension is not verified.
     Review code before installing: https://github.com/...

     Continue? (yes/no):
  ```

### 沙箱 (未来)

**Phase 2** (不在初始版本中):

- 扩展在清单中声明所需权限
- CLI 强制权限边界
- 示例权限: `filesystem:read`, `network:external`, `env:read`

```yaml
# 未来 extension.yml
permissions:
  - "filesystem:read:.specify/extensions/jira/"  # 只能读取自己的配置
  - "filesystem:write:.specify/memory/"          # 可以写入 memory
  - "network:external:*.atlassian.net"           # 可以调用 Jira API
  - "env:read:SPECKIT_JIRA_*"                    # 可以读取自己的环境变量
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

CLI 在解压前验证签名. 

---

## 迁移策略

### 向后兼容

**目标**: 现有 spec-kit 项目无需更改即可工作. 

**策略:**

1. **核心命令不变**: `/speckit.tasks`, `/speckit.implement` 等保留在核心

2. **可选扩展**: 用户选择加入扩展

3. **渐进迁移**: 现有 `taskstoissues` 保留在核心, Jira 扩展是替代方案

4. **弃用时间表**:
   - **v0.2.0**: 引入扩展系统, 保留核心 `taskstoissues`
   - **v0.3.0**: 将核心 `taskstoissues` 标记为 "legacy" (仍然工作)
   - **v1.0.0**: 考虑移除核心 `taskstoissues` 以支持扩展

### 用户迁移路径

**场景 1**: 用户没有 `taskstoissues` 使用

- 无需迁移, 扩展是可选的

**场景 2**: 用户使用核心 `taskstoissues` (GitHub Issues)

- 像以前一样工作
- 可选: 迁移到 `github-projects` 扩展以获得更多功能

**场景 3**: 用户需要 Jira (新需求)

- `specify extension add jira`
- 配置并使用

**场景 4**: 用户有调用 `taskstoissues` 的自定义脚本

- 脚本仍然工作 (核心命令保留)
- 迁移指南显示如何调用扩展命令

### 扩展迁移指南

**对于扩展作者** (如果核心命令变为扩展):

```bash
# 旧 (核心命令)
/speckit.taskstoissues

# 新 (扩展命令)
specify extension add github-projects
/speckit.github.taskstoissues
```

**兼容性 shim** (如果需要):

```yaml
# extension.yml
provides:
  commands:
    - name: "speckit.github.taskstoissues"
      file: "commands/taskstoissues.md"
      aliases: ["speckit.taskstoissues"]  # 向后兼容
```

AI 代理注册两个名称, 所以旧脚本仍然工作. 

---

## 实现阶段

### Phase 1: 核心扩展系统 (第 1-2 周)

**目标**: 基础扩展基础设施

**交付物**:

- [ ] 扩展清单 schema (`extension.yml`)
- [ ] 扩展目录结构
- [ ] CLI 命令:
  - [ ] `specify extension list`
  - [ ] `specify extension add` (从 URL)
  - [ ] `specify extension remove`
- [ ] 扩展注册表 (`.specify/extensions/.registry`)
- [ ] 命令注册 (最初仅 Claude)
- [ ] 基本验证 (清单 schema, 兼容性)
- [ ] 文档 (扩展开发指南)

**测试**:

- [ ] 清单解析单元测试
- [ ] 集成测试: 安装虚拟扩展
- [ ] 集成测试: 向 Claude 注册命令

### Phase 2: Jira 扩展 (第 3 周)

**目标**: 第一个生产扩展

**交付物**:

- [ ] 创建 `spec-kit-jira` 仓库
- [ ] 将 Jira 功能移植到扩展
- [ ] 创建 `jira-config.yml` 模板
- [ ] 命令:
  - [ ] `specstoissues.md`
  - [ ] `discover-fields.md`
  - [ ] `sync-status.md`
- [ ] 辅助脚本
- [ ] 文档 (README, 配置指南, 示例)
- [ ] 发布 v1.0.0

**测试**:

- [ ] 在 `eng-msa-ts` 项目上测试
- [ ] 验证 spec→Epic, phase→Story, task→Issue 映射
- [ ] 测试配置加载和验证
- [ ] 测试自定义字段应用

### Phase 3: 扩展目录 (第 4 周)

**目标**: 发现和分发

**交付物**:

- [ ] 中央目录 (spec-kit 仓库中的 `extensions/catalog.json`)
- [ ] 目录获取和解析
- [ ] CLI 命令:
  - [ ] `specify extension search`
  - [ ] `specify extension info`
- [ ] 目录发布流程 (GitHub Action)
- [ ] 文档 (如何发布扩展)

**测试**:

- [ ] 测试目录获取
- [ ] 测试扩展搜索/过滤
- [ ] 测试目录缓存

### Phase 4: 高级功能 (第 5-6 周)

**目标**: 钩子, 更新, 多代理支持

**交付物**:

- [ ] 钩子系统 (`extension.yml` 中的 `hooks`)
- [ ] 钩子注册和执行
- [ ] 项目扩展配置 (`.specify/extensions.yml`)
- [ ] CLI 命令:
  - [ ] `specify extension update`
  - [ ] `specify extension enable/disable`
- [ ] 多代理命令注册 (Gemini, Copilot)
- [ ] 扩展更新通知
- [ ] 配置层解析 (项目, 本地, 环境)

**测试**:

- [ ] 测试核心命令中的钩子
- [ ] 测试扩展更新 (保留配置)
- [ ] 测试多代理注册

### Phase 5: 完善与文档 (第 7 周)

**目标**: 生产就绪

**交付物**:

- [ ] 全面的文档:
  - [ ] 用户指南 (安装/使用扩展)
  - [ ] 扩展开发指南
  - [ ] 扩展 API 参考
  - [ ] 迁移指南 (核心 → 扩展)
- [ ] 错误消息和验证改进
- [ ] CLI 帮助文本更新
- [ ] 示例扩展模板 (cookiecutter)
- [ ] 博客文章 / 公告
- [ ] 视频教程

**测试**:

- [ ] 多项目端到端测试
- [ ] 社区 beta 测试
- [ ] 性能测试 (大型项目)

---

## 开放问题

### 1. 扩展命名空间

**问题**: 扩展命令是否应该使用命名空间前缀?

**选项**:

- A) 有前缀: `/speckit.jira.specstoissues` (明确, 避免冲突)
- B) 短别名: `/jira.specstoissues` (更短, 不那么冗长)
- C) 两者都有: 注册两个名称, 文档中优先使用有前缀的

**建议**: C (两者都有), 有前缀的是规范的

---

### 2. 配置文件位置

**问题**: 扩展配置应该放在哪里?

**选项**:

- A) 扩展目录: `.specify/extensions/jira/jira-config.yml` (封装)
- B) 根级别: `.specify/jira-config.yml` (更可见)
- C) 统一: `.specify/extensions.yml` (所有扩展配置在一个文件中)

**建议**: A (扩展目录), 更清晰的分离

---

### 3. 命令文件格式

**问题**: 扩展应该使用通用格式还是代理特定格式?

**选项**:

- A) 通用 Markdown: 扩展编写一次, CLI 按代理转换
- B) 代理特定: 扩展为每个代理提供单独的文件
- C) 混合: 通用默认, 代理特定覆盖

**建议**: A (通用), 减少重复

---

### 4. 钩子执行模型

**问题**: 钩子应该如何执行?

**选项**:

- A) AI 代理解释: 核心命令输出 `EXECUTE_COMMAND: name`
- B) CLI 执行: 核心命令调用 `specify extension hook after_tasks`
- C) 代理内置: 扩展系统内置到 AI 代理 (Claude SDK)

**建议**: 最初 A (更简单), 长期转向 C

---

### 5. 扩展分发

**问题**: 扩展应该如何打包?

**选项**:

- A) ZIP 归档: 从 GitHub releases 下载
- B) Git 仓库: 直接克隆 (`git clone`)
- C) Python 包: 通过 `uv tool install` 安装

**建议**: A (ZIP), 对未来非 Python 扩展更简单

---

### 6. 多版本支持

**问题**: 同一扩展的多个版本可以共存吗?

**选项**:

- A) 单一版本: 一次只安装一个版本
- B) 多版本: 并排版本 (`.specify/extensions/jira@1.0/`, `.specify/extensions/jira@2.0/`)
- C) 每分支: 不同分支使用不同版本

**建议**: 最初 A (更简单), 如果需要将来考虑 B

---

## 附录

### 附录 A: 示例扩展结构

**`spec-kit-jira` 扩展的完整结构:**

```text
spec-kit-jira/
├── README.md                        # 概述, 功能, 安装
├── LICENSE                          # MIT 许可证
├── CHANGELOG.md                     # 版本历史
├── .gitignore                       # 忽略本地配置
│
├── extension.yml                    # 扩展清单 (必需)
├── jira-config.template.yml         # 配置模板
│
├── commands/                        # 命令文件
│   ├── specstoissues.md            # 主命令
│   ├── discover-fields.md          # 辅助: 发现自定义字段
│   └── sync-status.md              # 辅助: 同步完成状态
│
├── scripts/                         # 辅助脚本
│   ├── parse-jira-config.sh        # 配置加载器 (bash)
│   ├── parse-jira-config.ps1       # 配置加载器 (PowerShell)
│   └── validate-jira-connection.sh # 连接测试
│
├── docs/                            # 文档
│   ├── installation.md             # 安装指南
│   ├── configuration.md            # 配置参考
│   ├── usage.md                    # 使用示例
│   ├── troubleshooting.md          # 常见问题
│   └── examples/
│       ├── eng-msa-ts-config.yml   # 真实世界配置示例
│       └── simple-project.yml      # 最小配置示例
│
├── tests/                           # 测试 (可选)
│   ├── test-extension.sh           # 扩展验证
│   └── test-commands.sh            # 命令执行测试
│
└── .github/                         # GitHub 集成
    └── workflows/
        └── release.yml              # 自动化发布
```

### 附录 B: 扩展开发指南 (大纲)

**创建新扩展的文档:**

1. **入门**
   - 先决条件 (所需工具)
   - 扩展模板 (cookiecutter)
   - 目录结构

2. **扩展清单**
   - Schema 参考
   - 必需 vs 可选字段
   - 版本控制指南

3. **命令开发**
   - 通用命令格式
   - Frontmatter 规范
   - 模板变量
   - 脚本引用

4. **配置**
   - 配置文件结构
   - Schema 验证
   - 分层配置解析
   - 环境变量覆盖

5. **钩子**
   - 可用钩子点
   - 钩子注册
   - 条件执行
   - 最佳实践

6. **测试**
   - 本地开发设置
   - 使用 `--dev` 标志测试
   - 验证清单
   - 集成测试

7. **发布**
   - 打包 (ZIP 格式)
   - GitHub releases
   - 目录提交
   - 版本控制策略

8. **示例**
   - 最小扩展
   - 带钩子的扩展
   - 带配置的扩展
   - 带多个命令的扩展

### 附录 C: 兼容性矩阵

**计划支持矩阵:**

| 扩展功能 | Spec Kit 版本 | AI 代理支持 |
|----------|---------------|-------------|
| 基本命令 | 0.2.0+ | Claude, Gemini, Copilot |
| 钩子 (after_tasks) | 0.3.0+ | Claude, Gemini |
| 配置验证 | 0.2.0+ | 全部 |
| 多目录 | 0.4.0+ | 全部 |
| 权限 (沙箱) | 1.0.0+ | TBD |

### 附录 D: 扩展目录 Schema

**`catalog.json` 的完整 schema:**

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

本 RFC 提出了一个全面的 Spec Kit 扩展系统:

1. **保持核心精简** 同时支持无限集成
2. **支持多代理** (Claude, Gemini, Copilot 等)
3. **提供清晰的扩展 API** 用于社区贡献
4. **启用独立版本控制** 扩展和核心
5. **包含安全机制** (验证, 兼容性检查)

### 立即下一步

1. **与利益相关者审查此 RFC**
2. **收集对开放问题的反馈**
3. **根据反馈完善设计**
4. **进入 Phase A**: 实现核心扩展系统
5. **然后 Phase B**: 构建 Jira 扩展作为概念验证

---

## 讨论问题

1. 扩展架构是否满足你对 Jira 集成的需求?
2. 是否有我们应该考虑的其他钩子点?
3. 我们应该支持扩展依赖吗 (扩展 A 需要扩展 B)?
4. 我们应该如何处理目录中的扩展弃用/移除?
5. 我们在 v1.0 中需要什么级别的沙箱/权限?
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

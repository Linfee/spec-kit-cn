# 扩展 API 参考

Spec Kit 扩展系统 API 和清单模式的技术参考。

## 目录

1. [扩展清单](#扩展清单)
2. [Python API](#python-api)
3. [命令文件格式](#命令文件格式)
4. [配置模式](#配置模式)
5. [钩子系统](#钩子系统)
6. [CLI 命令](#cli-命令)

---

## 扩展清单

### 模式版本 1.0

文件: `extension.yml`

```yaml
schema_version: "1.0"  # Required

extension:
  id: string           # Required, pattern: ^[a-z0-9-]+$
  name: string         # Required, human-readable name
  version: string      # Required, semantic version (X.Y.Z)
  description: string  # Required, brief description (<200 chars)
  author: string       # Required
  repository: string   # Required, valid URL
  license: string      # Required (e.g., "MIT", "Apache-2.0")
  homepage: string     # Optional, valid URL

requires:
  speckit_version: string  # Required, version specifier (>=X.Y.Z)
  tools:                   # Optional, array of tool requirements
    - name: string         # Tool name
      version: string      # Optional, version specifier
      required: boolean    # Optional, default: false

provides:
  commands:              # Required, at least one command
    - name: string       # Required, pattern: ^speckit\.[a-z0-9-]+\.[a-z0-9-]+$
      file: string       # Required, relative path to command file
      description: string # Required
      aliases: [string]  # Optional, same pattern as name; namespace must match extension.id and must not shadow core or installed extension commands

  config:                # Optional, array of config files
    - name: string       # Config file name
      template: string   # Template file path
      description: string
      required: boolean  # Default: false

hooks:                   # Optional, event hooks
  event_name:            # e.g., "after_specify", "after_plan", "after_tasks", "after_implement"
    command: string      # Command to execute
    optional: boolean    # Default: true
    prompt: string       # Prompt text for optional hooks
    description: string  # Hook description
    condition: string    # Optional, condition expression

tags:                    # Optional, array of tags (2-10 recommended)
  - string

defaults:                # Optional, default configuration values
  key: value             # Any YAML structure
```

### 字段规格

#### `extension.id`

- **类型**: string
- **模式**: `^[a-z0-9-]+$`
- **描述**: 唯一的扩展标识符
- **示例**: `jira`, `linear`, `azure-devops`
- **无效**: `Jira`, `my_extension`, `extension.id`

#### `extension.version`

- **类型**: string
- **格式**: 语义化版本 (X.Y.Z)
- **描述**: 扩展版本
- **示例**: `1.0.0`, `0.9.5`, `2.1.3`
- **无效**: `v1.0`, `1.0`, `1.0.0-beta`

#### `requires.speckit_version`

- **类型**: string
- **格式**: 版本说明符
- **描述**: 所需的 spec-kit 版本范围
- **示例**:
  - `>=0.1.0` - 0.1.0 或更高版本
  - `>=0.1.0,<2.0.0` - 0.1.x 或 1.x 版本
  - `==0.1.0` - 精确匹配 0.1.0
- **无效**: `0.1.0`, `>= 0.1.0` (有空格), `latest`

#### `provides.commands[].name`

- **类型**: string
- **模式**: `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
- **描述**: 带命名空间的命令名称
- **格式**: `speckit.{extension-id}.{command-name}`
- **示例**: `speckit.jira.specstoissues`, `speckit.linear.sync`
- **无效**: `jira.specstoissues`, `speckit.command`, `speckit.jira.CreateIssues`

#### `hooks`

- **类型**: object
- **键**: 事件名称(如 `after_specify`, `after_plan`, `after_tasks`, `after_implement`, `before_commit`)
- **描述**: 在生命周期事件时执行的钩子
- **事件**: 由核心 spec-kit 命令定义

---

## Python API

### ExtensionManifest

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionManifest

manifest = ExtensionManifest(Path("extension.yml"))
```

**属性**:

```python
manifest.id                        # str: Extension ID
manifest.name                      # str: Extension name
manifest.version                   # str: Version
manifest.description               # str: Description
manifest.requires_speckit_version  # str: Required spec-kit version
manifest.commands                  # List[Dict]: Command definitions
manifest.hooks                     # Dict: Hook definitions
```

**方法**:

```python
manifest.get_hash()  # str: SHA256 hash of manifest file
```

**异常**:

```python
ValidationError       # Invalid manifest structure
CompatibilityError    # Incompatible with current spec-kit version
```

### ExtensionRegistry

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionRegistry

registry = ExtensionRegistry(extensions_dir)
```

**方法**:

```python
# Add extension to registry
registry.add(extension_id: str, metadata: dict)

# Remove extension from registry
registry.remove(extension_id: str)

# Get extension metadata
metadata = registry.get(extension_id: str)  # Optional[dict]

# List all extensions
extensions = registry.list()  # Dict[str, dict]

# Check if installed
is_installed = registry.is_installed(extension_id: str)  # bool
```

**注册表格式**:

```json
{
  "schema_version": "1.0",
  "extensions": {
    "jira": {
      "version": "1.0.0",
      "source": "catalog",
      "manifest_hash": "sha256...",
      "enabled": true,
      "registered_commands": ["speckit.jira.specstoissues", ...],
      "installed_at": "2026-01-28T..."
    }
  }
}
```

### ExtensionManager

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionManager

manager = ExtensionManager(project_root)
```

**方法**:

```python
# Install from directory
manifest = manager.install_from_directory(
    source_dir: Path,
    speckit_version: str,
    register_commands: bool = True
)  # Returns: ExtensionManifest

# Install from ZIP
manifest = manager.install_from_zip(
    zip_path: Path,
    speckit_version: str
)  # Returns: ExtensionManifest

# Remove extension
success = manager.remove(
    extension_id: str,
    keep_config: bool = False
)  # Returns: bool

# List installed extensions
extensions = manager.list_installed()  # List[Dict]

# Get extension manifest
manifest = manager.get_extension(extension_id: str)  # Optional[ExtensionManifest]

# Check compatibility
manager.check_compatibility(
    manifest: ExtensionManifest,
    speckit_version: str
)  # Raises: CompatibilityError if incompatible
```

### CatalogEntry

**模块**: `specify_cli.extensions`

表示活跃目录栈中的单个目录。

```python
from specify_cli.extensions import CatalogEntry

entry = CatalogEntry(
    url="https://example.com/catalog.json",
    name="default",
    priority=1,
    install_allowed=True,
    description="Built-in catalog of installable extensions",
)
```

**字段**:

| 字段 | 类型 | 描述 |
|------|------|------|
| `url` | `str` | 目录 URL (必须使用 HTTPS, 或 localhost 使用 HTTP) |
| `name` | `str` | 人类可读的目录名称 |
| `priority` | `int` | 排序顺序 (数值越低 = 优先级越高, 冲突时优先) |
| `install_allowed` | `bool` | 是否允许从此目录安装扩展 |
| `description` | `str` | 可选的目录描述 (默认: 空) |

### ExtensionCatalog

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionCatalog

catalog = ExtensionCatalog(project_root)
```

**类属性**:

```python
ExtensionCatalog.DEFAULT_CATALOG_URL    # default catalog URL
ExtensionCatalog.COMMUNITY_CATALOG_URL  # community catalog URL
```

**方法**:

```python
# Get the ordered list of active catalogs
entries = catalog.get_active_catalogs()  # List[CatalogEntry]

# Fetch catalog (primary catalog, backward compat)
catalog_data = catalog.fetch_catalog(force_refresh: bool = False)  # Dict

# Search extensions across all active catalogs
# Each result includes _catalog_name and _install_allowed
results = catalog.search(
    query: Optional[str] = None,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    verified_only: bool = False
)  # Returns: List[Dict]  — each dict includes _catalog_name, _install_allowed

# Get extension info (searches all active catalogs)
# Returns None if not found; includes _catalog_name and _install_allowed
ext_info = catalog.get_extension_info(extension_id: str)  # Optional[Dict]

# Check cache validity (primary catalog)
is_valid = catalog.is_cache_valid()  # bool

# Clear all catalog caches
catalog.clear_cache()
```

**结果注解字段**:

`search()` 和 `get_extension_info()` 返回的每个扩展字典包含:

| 字段 | 类型 | 描述 |
|------|------|------|
| `_catalog_name` | `str` | 源目录名称 |
| `_install_allowed` | `bool` | 是否允许从此目录安装 |

**目录配置文件**(`.specify/extension-catalogs.yml`):

```yaml
catalogs:
  - name: "default"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json"
    priority: 1
    install_allowed: true
    description: "Built-in catalog of installable extensions"
  - name: "community"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json"
    priority: 2
    install_allowed: false
    description: "Community-contributed extensions (discovery only)"
```

### HookExecutor

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import HookExecutor

hook_executor = HookExecutor(project_root)
```

**方法**:

```python
# Get project config
config = hook_executor.get_project_config()  # Dict

# Save project config
hook_executor.save_project_config(config: Dict)

# Register hooks
hook_executor.register_hooks(manifest: ExtensionManifest)

# Unregister hooks
hook_executor.unregister_hooks(extension_id: str)

# Get hooks for event
hooks = hook_executor.get_hooks_for_event(event_name: str)  # List[Dict]

# Check if hook should execute
should_run = hook_executor.should_execute_hook(hook: Dict)  # bool

# Format hook message
message = hook_executor.format_hook_message(
    event_name: str,
    hooks: List[Dict]
)  # str
```

### CommandRegistrar

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import CommandRegistrar

registrar = CommandRegistrar()
```

**方法**:

```python
# Register commands for Claude Code
registered = registrar.register_commands_for_claude(
    manifest: ExtensionManifest,
    extension_dir: Path,
    project_root: Path
)  # Returns: List[str] (command names)

# Parse frontmatter
frontmatter, body = registrar.parse_frontmatter(content: str)

# Render frontmatter
yaml_text = registrar.render_frontmatter(frontmatter: Dict)  # str
```

---

## 命令文件格式

### 通用命令格式

**文件**: `commands/{command-name}.md`

```markdown
---
description: "Command description"
tools:
  - 'mcp-server/tool_name'
  - 'other-mcp-server/other_tool'
---

# Command Title

Command documentation in Markdown.

## Prerequisites

1. Requirement 1
2. Requirement 2

## User Input

$ARGUMENTS

## Steps

### Step 1: Description

Instruction text...

\`\`\`bash
# Shell commands
\`\`\`

### Step 2: Another Step

More instructions...

## Configuration Reference

Information about configuration options.

## Notes

Additional notes and tips.
```

### Frontmatter 字段

```yaml
description: string   # Required, brief command description
tools: [string]       # Optional, MCP tools required
```

### 特殊变量

- `$ARGUMENTS` - 用户提供的参数占位符
- 扩展上下文自动注入:

  ```markdown
  <!-- Extension: {extension-id} -->
  <!-- Config: .specify/extensions/{extension-id}/ -->
  ```

---

## 配置模式

### 扩展配置文件

**文件**: `.specify/extensions/{extension-id}/{extension-id}-config.yml`

扩展定义自己的配置模式。常见模式:

```yaml
# Connection settings
connection:
  url: string
  api_key: string

# Project settings
project:
  key: string
  workspace: string

# Feature flags
features:
  enabled: boolean
  auto_sync: boolean

# Defaults
defaults:
  labels: [string]
  assignee: string

# Custom fields
field_mappings:
  internal_name: "external_field_id"
```

### 配置层

1. **扩展默认值** (来自 `extension.yml` 的 `defaults` 部分)
2. **项目配置** (`{extension-id}-config.yml`)
3. **本地覆盖** (`{extension-id}-config.local.yml`, gitignored)
4. **环境变量** (`SPECKIT_{EXTENSION}_*`)

### 环境变量模式

格式: `SPECKIT_{EXTENSION}_{KEY}`

示例:

- `SPECKIT_JIRA_PROJECT_KEY`
- `SPECKIT_LINEAR_API_KEY`
- `SPECKIT_GITHUB_TOKEN`

---

## 钩子系统

### 钩子定义

**在 extension.yml 中**:

```yaml
hooks:
  after_tasks:
    command: "speckit.jira.specstoissues"
    optional: true
    prompt: "Create Jira issues from tasks?"
    description: "Automatically create Jira hierarchy"
    condition: null
```

### 钩子事件

标准事件(由核心定义):

- `before_specify` - 规范生成之前
- `after_specify` - 规范生成之后
- `before_plan` - 实施计划之前
- `after_plan` - 实施计划之后
- `before_tasks` - 任务生成之前
- `after_tasks` - 任务生成之后
- `before_implement` - 实施之前
- `after_implement` - 实施之后
- `before_commit` - Git 提交之前 *(计划中 - 尚未接入核心模板)*
- `after_commit` - Git 提交之后 *(计划中 - 尚未接入核心模板)*

### 钩子配置

**在 `.specify/extensions.yml` 中**:

```yaml
hooks:
  after_tasks:
    - extension: jira
      command: speckit.jira.specstoissues
      enabled: true
      optional: true
      prompt: "Create Jira issues from tasks?"
      description: "..."
      condition: null
```

### 钩子消息格式

```markdown
## Extension Hooks

**Optional Hook**: {extension}
Command: `/{command}`
Description: {description}

Prompt: {prompt}
To execute: `/{command}`
```

或对于强制钩子:

```markdown
**Automatic Hook**: {extension}
Executing: `/{command}`
EXECUTE_COMMAND: {command}
```

---

## CLI 命令

### extension list

**用法**: `specify-cn extension list [OPTIONS]`

**选项**:

- `--available` - 显示目录中可用的扩展
- `--all` - 同时显示已安装和可用的扩展

**输出**: 已安装扩展列表及元数据

### extension catalog list

**用法**: `specify-cn extension catalog list`

列出当前目录栈中所有活跃的目录, 显示名称、描述、URL、优先级和 `install_allowed` 状态。

### extension catalog add

**用法**: `specify-cn extension catalog add URL [OPTIONS]`

**选项**:

- `--name NAME` - 目录名称 (必填)
- `--priority INT` - 优先级 (数值越低 = 优先级越高, 默认: 10)
- `--install-allowed / --no-install-allowed` - 是否允许从此目录安装 (默认: false)
- `--description TEXT` - 可选的目录描述

**参数**:

- `URL` - 目录 URL (必须使用 HTTPS)

将目录条目添加到 `.specify/extension-catalogs.yml`。

### extension catalog remove

**用法**: `specify-cn extension catalog remove NAME`

**参数**:

- `NAME` - 要移除的目录名称

从 `.specify/extension-catalogs.yml` 中移除目录条目。

### extension add

**用法**: `specify-cn extension add EXTENSION [OPTIONS]`

**选项**:

- `--from URL` - 从自定义 URL 安装
- `--dev PATH` - 从本地目录安装

**参数**:

- `EXTENSION` - 扩展名称或 URL

**注意**: 来自 `install_allowed: false` 的目录的扩展无法通过此命令安装。

### extension remove

**用法**: `specify-cn extension remove EXTENSION [OPTIONS]`

**选项**:

- `--keep-config` - 保留配置文件
- `--force` - 跳过确认

**参数**:

- `EXTENSION` - 扩展 ID

### extension search

**用法**: `specify-cn extension search [QUERY] [OPTIONS]`

同时搜索所有活跃目录。结果包含源目录名称和 install_allowed 状态。

**选项**:

- `--tag TAG` - 按标签过滤
- `--author AUTHOR` - 按作者过滤
- `--verified` - 仅显示已验证的扩展

**参数**:

- `QUERY` - 可选的搜索查询

### extension info

**用法**: `specify-cn extension info EXTENSION`

显示源目录和 install_allowed 状态。

**参数**:

- `EXTENSION` - 扩展 ID

### extension update

**用法**: `specify-cn extension update [EXTENSION]`

**参数**:

- `EXTENSION` - 可选, 扩展 ID (默认: 全部)

### extension enable

**用法**: `specify-cn extension enable EXTENSION`

**参数**:

- `EXTENSION` - 扩展 ID

### extension disable

**用法**: `specify-cn extension disable EXTENSION`

**参数**:

- `EXTENSION` - 扩展 ID

---

## 异常

### ValidationError

当扩展清单验证失败时抛出。

```python
from specify_cli.extensions import ValidationError

try:
    manifest = ExtensionManifest(path)
except ValidationError as e:
    print(f"Invalid manifest: {e}")
```

### CompatibilityError

当扩展与当前 spec-kit 版本不兼容时抛出。

```python
from specify_cli.extensions import CompatibilityError

try:
    manager.check_compatibility(manifest, "0.1.0")
except CompatibilityError as e:
    print(f"Incompatible: {e}")
```

### ExtensionError

所有扩展相关错误的基础异常。

```python
from specify_cli.extensions import ExtensionError

try:
    manager.install_from_directory(path, "0.1.0")
except ExtensionError as e:
    print(f"Extension error: {e}")
```

---

## 版本函数

### version_satisfies

检查版本是否满足说明符。

```python
from specify_cli.extensions import version_satisfies

# True if 1.2.3 satisfies >=1.0.0,<2.0.0
satisfied = version_satisfies("1.2.3", ">=1.0.0,<2.0.0")  # bool
```

---

## 文件系统布局

```text
.specify/
├── extensions/
│   ├── .registry               # Extension registry (JSON)
│   ├── .cache/                 # Catalog cache
│   │   ├── catalog.json
│   │   └── catalog-metadata.json
│   ├── .backup/                # Config backups
│   │   └── {ext}-{config}.yml
│   ├── {extension-id}/         # Extension directory
│   │   ├── extension.yml       # Manifest
│   │   ├── {ext}-config.yml    # User config
│   │   ├── {ext}-config.local.yml  # Local overrides (gitignored)
│   │   ├── {ext}-config.template.yml  # Template
│   │   ├── commands/           # Command files
│   │   │   └── *.md
│   │   ├── scripts/            # Helper scripts
│   │   │   └── *.sh
│   │   ├── docs/               # Documentation
│   │   └── README.md
│   └── extensions.yml          # Project extension config
└── scripts/                    # (existing spec-kit)

.claude/
└── commands/
    └── speckit.{ext}.{cmd}.md  # Registered commands
```

---

*最后更新: 2026-01-28*
*API 版本: 1.0*
*Spec Kit 版本: 0.1.0*

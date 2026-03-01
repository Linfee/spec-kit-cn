# 扩展 API 参考

Spec Kit 扩展系统 API 和清单 schema 的技术参考. 

## 目录

1. [扩展清单](#扩展清单)
2. [Python API](#python-api)
3. [命令文件格式](#命令文件格式)
4. [配置 Schema](#配置-schema)
5. [钩子系统](#钩子系统)
6. [CLI 命令](#cli-命令)

---

## 扩展清单

### Schema 版本 1.0

文件: `extension.yml`

```yaml
schema_version: "1.0"  # 必需

extension:
  id: string           # 必需, 模式: ^[a-z0-9-]+$
  name: string         # 必需, 人类可读名称
  version: string      # 必需, 语义版本 (X.Y.Z)
  description: string  # 必需, 简短描述 (<200 字符)
  author: string       # 必需
  repository: string   # 必需, 有效 URL
  license: string      # 必需 (如 "MIT", "Apache-2.0")
  homepage: string     # 可选, 有效 URL

requires:
  speckit_version: string  # 必需, 版本说明符 (>=X.Y.Z)
  tools:                   # 可选, 工具要求数组
    - name: string         # 工具名称
      version: string      # 可选, 版本说明符
      required: boolean    # 可选, 默认: false

provides:
  commands:              # 必需, 至少一个命令
    - name: string       # 必需, 模式: ^speckit\.[a-z0-9-]+\.[a-z0-9-]+$
      file: string       # 必需, 命令文件的相对路径
      description: string # 必需
      aliases: [string]  # 可选, 替代名称数组

  config:                # 可选, 配置文件数组
    - name: string       # 配置文件名称
      template: string   # 模板文件路径
      description: string
      required: boolean  # 默认: false

hooks:                   # 可选, 事件钩子
  event_name:            # 如 "after_tasks", "after_implement"
    command: string      # 要执行的命令
    optional: boolean    # 默认: true
    prompt: string       # 可选钩子的提示文本
    description: string  # 钩子描述
    condition: string    # 可选, 条件表达式

tags:                    # 可选, 标签数组 (推荐 2-10 个)
  - string

defaults:                # 可选, 默认配置值
  key: value             # 任何 YAML 结构
```

### 字段规范

#### `extension.id`

- **类型**: string
- **模式**: `^[a-z0-9-]+$`
- **描述**: 唯一的扩展标识符
- **示例**: `jira`, `linear`, `azure-devops`
- **无效**: `Jira`, `my_extension`, `extension.id`

#### `extension.version`

- **类型**: string
- **格式**: 语义版本控制 (X.Y.Z)
- **描述**: 扩展版本
- **示例**: `1.0.0`, `0.9.5`, `2.1.3`
- **无效**: `v1.0`, `1.0`, `1.0.0-beta`

#### `requires.speckit_version`

- **类型**: string
- **格式**: 版本说明符
- **描述**: 必需的 spec-kit 版本范围
- **示例**:
  - `>=0.1.0` - 任何 0.1.0 或更高版本
  - `>=0.1.0,<2.0.0` - 版本 0.1.x 或 1.x
  - `==0.1.0` - 精确的 0.1.0
- **无效**: `0.1.0`, `>= 0.1.0` (空格), `latest`

#### `provides.commands[].name`

- **类型**: string
- **模式**: `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
- **描述**: 命名空间的命令名称
- **格式**:  `speckit.{extension-id}.{command-name}`
- **示例**: `speckit.jira.specstoissues`, `speckit.linear.sync`
- **无效**: `jira.specstoissues`, `speckit.command`, `speckit.jira.CreateIssues`

#### `hooks`

- **类型**: object
- **键**: 事件名称 (如 `after_tasks`, `after_implement`, `before_commit`)
- **描述**: 在生命周期事件执行的钩子
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
manifest.id                        # str: 扩展 ID
manifest.name                      # str: 扩展名称
manifest.version                   # str: 版本
manifest.description               # str: 描述
manifest.requires_speckit_version  # str: 必需的 spec-kit 版本
manifest.commands                  # List[Dict]: 命令定义
manifest.hooks                     # Dict: 钩子定义
```

**方法**:

```python
manifest.get_hash()  # str: 清单文件的 SHA256 哈希
```

**异常**:

```python
ValidationError       # 无效的清单结构
CompatibilityError    # 与当前 spec-kit 版本不兼容
```

### ExtensionRegistry

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionRegistry

registry = ExtensionRegistry(extensions_dir)
```

**方法**:

```python
# 添加扩展到注册表
registry.add(extension_id: str, metadata: dict)

# 从注册表移除扩展
registry.remove(extension_id: str)

# 获取扩展元数据
metadata = registry.get(extension_id: str)  # Optional[dict]

# 列出所有扩展
extensions = registry.list()  # Dict[str, dict]

# 检查是否已安装
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
# 从目录安装
manifest = manager.install_from_directory(
    source_dir: Path,
    speckit_version: str,
    register_commands: bool = True
)  # 返回: ExtensionManifest

# 从 ZIP 安装
manifest = manager.install_from_zip(
    zip_path: Path,
    speckit_version: str
)  # 返回: ExtensionManifest

# 移除扩展
success = manager.remove(
    extension_id: str,
    keep_config: bool = False
)  # 返回: bool

# 列出已安装的扩展
extensions = manager.list_installed()  # List[Dict]

# 获取扩展清单
manifest = manager.get_extension(extension_id: str)  # Optional[ExtensionManifest]

# 检查兼容性
manager.check_compatibility(
    manifest: ExtensionManifest,
    speckit_version: str
)  # 如果不兼容则抛出: CompatibilityError
```

### ExtensionCatalog

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import ExtensionCatalog

catalog = ExtensionCatalog(project_root)
```

**方法**:

```python
# 获取目录
catalog_data = catalog.fetch_catalog(force_refresh: bool = False)  # Dict

# 搜索扩展
results = catalog.search(
    query: Optional[str] = None,
    tag: Optional[str] = None,
    author: Optional[str] = None,
    verified_only: bool = False
)  # 返回: List[Dict]

# 获取扩展信息
ext_info = catalog.get_extension_info(extension_id: str)  # Optional[Dict]

# 检查缓存有效性
is_valid = catalog.is_cache_valid()  # bool

# 清除缓存
catalog.clear_cache()
```

### HookExecutor

**模块**: `specify_cli.extensions`

```python
from specify_cli.extensions import HookExecutor

hook_executor = HookExecutor(project_root)
```

**方法**:

```python
# 获取项目配置
config = hook_executor.get_project_config()  # Dict

# 保存项目配置
hook_executor.save_project_config(config: Dict)

# 注册钩子
hook_executor.register_hooks(manifest: ExtensionManifest)

# 注销钩子
hook_executor.unregister_hooks(extension_id: str)

# 获取事件的钩子
hooks = hook_executor.get_hooks_for_event(event_name: str)  # List[Dict]

# 检查钩子是否应该执行
should_run = hook_executor.should_execute_hook(hook: Dict)  # bool

# 格式化钩子消息
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
# 为 Claude Code 注册命令
registered = registrar.register_commands_for_claude(
    manifest: ExtensionManifest,
    extension_dir: Path,
    project_root: Path
)  # 返回: List[str] (命令名称)

# 解析 frontmatter
frontmatter, body = registrar.parse_frontmatter(content: str)

# 渲染 frontmatter
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
description: string   # 必需, 简短命令描述
tools: [string]       # 可选, 必需的 MCP 工具
```

### 特殊变量

- `$ARGUMENTS` - 用户提供的参数占位符
- 扩展上下文自动注入:

  ```markdown
  <!-- Extension: {extension-id} -->
  <!-- Config: .specify/extensions/{extension-id}/ -->
  ```

---

## 配置 Schema

### 扩展配置文件

**文件**: `.specify/extensions/{extension-id}/{extension-id}-config.yml`

扩展定义自己的配置 schema. 常见模式:

```yaml
# 连接设置
connection:
  url: string
  api_key: string

# 项目设置
project:
  key: string
  workspace: string

# 功能标志
features:
  enabled: boolean
  auto_sync: boolean

# 默认值
defaults:
  labels: [string]
  assignee: string

# 自定义字段
field_mappings:
  internal_name: "external_field_id"
```

### 配置层

1. **扩展默认值** (来自 `extension.yml` `defaults` 部分)
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

标准事件 (由核心定义):

- `after_tasks` - 任务生成后
- `after_implement` - 实现后
- `before_commit` - git commit 前
- `after_commit` - git commit 后

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

或对于强制性钩子:

```markdown
**Automatic Hook**: {extension}
Executing: `/{command}`
EXECUTE_COMMAND: {command}
```

---

## CLI 命令

### extension list

**用法**: `specify extension list [OPTIONS]`

**选项**:

- `--available` - 显示目录中的可用扩展
- `--all` - 显示已安装和可用的

**输出**: 已安装扩展列表及其元数据

### extension add

**用法**: `specify extension add EXTENSION [OPTIONS]`

**选项**:

- `--from URL` - 从自定义 URL 安装
- `--dev PATH` - 从本地目录安装
- `--version VERSION` - 安装特定版本
- `--no-register` - 跳过命令注册

**参数**:

- `EXTENSION` - 扩展名称或 URL

### extension remove

**用法**: `specify extension remove EXTENSION [OPTIONS]`

**选项**:

- `--keep-config` - 保留配置文件
- `--force` - 跳过确认

**参数**:

- `EXTENSION` - 扩展 ID

### extension search

**用法**: `specify extension search [QUERY] [OPTIONS]`

**选项**:

- `--tag TAG` - 按标签过滤
- `--author AUTHOR` - 按作者过滤
- `--verified` - 仅显示已验证的扩展

**参数**:

- `QUERY` - 可选的搜索查询

### extension info

**用法**: `specify extension info EXTENSION`

**参数**:

- `EXTENSION` - 扩展 ID

### extension update

**用法**: `specify extension update [EXTENSION]`

**参数**:

- `EXTENSION` - 可选, 扩展 ID (默认: 全部)

### extension enable

**用法**: `specify extension enable EXTENSION`

**参数**:

- `EXTENSION` - 扩展 ID

### extension disable

**用法**: `specify extension disable EXTENSION`

**参数**:

- `EXTENSION` - 扩展 ID

---

## 异常

### ValidationError

当扩展清单验证失败时抛出. 

```python
from specify_cli.extensions import ValidationError

try:
    manifest = ExtensionManifest(path)
except ValidationError as e:
    print(f"Invalid manifest: {e}")
```

### CompatibilityError

当扩展与当前 spec-kit 版本不兼容时抛出. 

```python
from specify_cli.extensions import CompatibilityError

try:
    manager.check_compatibility(manifest, "0.1.0")
except CompatibilityError as e:
    print(f"Incompatible: {e}")
```

### ExtensionError

所有扩展相关错误的基础异常. 

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

检查版本是否满足说明符. 

```python
from specify_cli.extensions import version_satisfies

# 如果 1.2.3 满足 >=1.0.0,<2.0.0 则为 True
satisfied = version_satisfies("1.2.3", ">=1.0.0,<2.0.0")  # bool
```

---

## 文件系统布局

```text
.specify/
├── extensions/
│   ├── .registry               # 扩展注册表 (JSON)
│   ├── .cache/                 # 目录缓存
│   │   ├── catalog.json
│   │   └── catalog-metadata.json
│   ├── .backup/                # 配置备份
│   │   └── {ext}-{config}.yml
│   ├── {extension-id}/         # 扩展目录
│   │   ├── extension.yml       # 清单
│   │   ├── {ext}-config.yml    # 用户配置
│   │   ├── {ext}-config.local.yml  # 本地覆盖 (gitignored)
│   │   ├── {ext}-config.template.yml  # 模板
│   │   ├── commands/           # 命令文件
│   │   │   └── *.md
│   │   ├── scripts/            # 辅助脚本
│   │   │   └── *.sh
│   │   ├── docs/               # 文档
│   │   └── README.md
│   └── extensions.yml          # 项目扩展配置
└── scripts/                    # (现有 spec-kit)

.claude/
└── commands/
    └── speckit.{ext}.{cmd}.md  # 注册的命令
```

---

*最后更新: 2026-01-28*
*API 版本: 1.0*
*Spec Kit 版本: 0.1.0*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

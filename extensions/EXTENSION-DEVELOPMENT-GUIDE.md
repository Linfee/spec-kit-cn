# 扩展开发指南

创建 Spec Kit 扩展的指南。

---

## 快速开始

### 1. 创建扩展目录

```bash
mkdir my-extension
cd my-extension
```

### 2. 创建 `extension.yml` 清单

```yaml
schema_version: "1.0"

extension:
  id: "my-ext"                          # Lowercase, alphanumeric + hyphens only
  name: "My Extension"
  version: "1.0.0"                      # Semantic versioning
  description: "My custom extension"
  author: "Your Name"
  repository: "https://github.com/you/spec-kit-my-ext"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"            # Minimum spec-kit version
  tools:                                # Optional: External tools required
    - name: "my-tool"
      required: true
      version: ">=1.0.0"
  commands:                             # Optional: Core commands needed
    - "speckit.tasks"

provides:
  commands:
    - name: "speckit.my-ext.hello"      # Must follow pattern: speckit.{ext-id}.{cmd}
      file: "commands/hello.md"
      description: "Say hello"
      aliases: ["speckit.my-ext.hi"]    # Optional aliases, same pattern

  config:                               # Optional: Config files
    - name: "my-ext-config.yml"
      template: "my-ext-config.template.yml"
      description: "Extension configuration"
      required: false

hooks:                                  # Optional: Integration hooks
  after_tasks:
    command: "speckit.my-ext.hello"
    optional: true
    prompt: "Run hello command?"

tags:                                   # Optional: For catalog search
  - "example"
  - "utility"
```

### 3. 创建命令目录

```bash
mkdir commands
```

### 4. 创建命令文件

**文件**: `commands/hello.md`

```markdown
---
description: "Say hello command"
tools:                              # Optional: AI tools this command uses
  - 'some-tool/function'
scripts:                            # Optional: Helper scripts
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---

# Hello Command

This command says hello!

## User Input

$ARGUMENTS

## Steps

1. Greet the user
2. Show extension is working

```bash
echo "Hello from my extension!"
echo "Arguments: $ARGUMENTS"
```

## Extension Configuration

Load extension config from `.specify/extensions/my-ext/my-ext-config.yml`.

### 5. 本地测试

```bash
cd /path/to/spec-kit-project
specify-cn extension add --dev /path/to/my-extension
```

### 6. 验证安装

```bash
specify-cn extension list

# 应该显示:
#  ✓ My Extension (v1.0.0)
#     My custom extension
#     Commands: 1 | Hooks: 1 | Status: Enabled
```

### 7. 测试命令

如果使用 Claude:

```bash
claude
> /speckit.my-ext.hello world
```

命令将位于 `.claude/commands/speckit.my-ext.hello.md`。

---

## 清单模式参考

### 必填字段

#### `schema_version`

扩展清单模式版本。当前值: `"1.0"`

#### `extension`

扩展元数据块。

**必填子字段**:

- `id`: 扩展标识符 (小写, 字母数字, 连字符)
- `name`: 人类可读名称
- `version`: 语义化版本 (如 "1.0.0")
- `description`: 简短描述

**可选子字段**:

- `author`: 扩展作者
- `repository`: 源代码 URL
- `license`: SPDX 许可证标识符
- `homepage`: 扩展主页 URL

#### `requires`

兼容性要求。

**必填子字段**:

- `speckit_version`: 语义化版本说明符 (如 ">=0.1.0,<2.0.0")

**可选子字段**:

- `tools`: 所需的外部工具 (工具对象数组)
- `commands`: 所需的核心 spec-kit 命令 (命令名称数组)
- `scripts`: 所需的核心脚本 (脚本名称数组)

#### `provides`

扩展提供的内容。

**必填子字段**:

- `commands`: 命令对象数组 (至少一个)

**命令对象**:

- `name`: 命令名称 (必须匹配 `speckit.{ext-id}.{command}`)
- `file`: 命令文件路径 (相对于扩展根目录)
- `description`: 命令描述 (可选)
- `aliases`: 替代命令名称 (可选, 数组; 每个必须匹配 `speckit.{ext-id}.{command}`)

### 可选字段

#### `hooks`

用于自动执行的集成钩子。

可用的钩子点:

- `after_tasks`: `/speckit.tasks` 完成后
- `after_implement`: `/speckit.implement` 完成后 (未来)

钩子对象:

- `command`: 要执行的命令 (必须在 `provides.commands` 中)
- `optional`: 如果为 true, 执行前提示用户
- `prompt`: 可选钩子的提示文本
- `description`: 钩子描述
- `condition`: 执行条件 (未来)

#### `tags`

用于目录发现的标签数组。

#### `defaults`

默认的扩展配置值。

#### `config_schema`

用于验证扩展配置的 JSON Schema。

---

## 命令文件格式

### Frontmatter (YAML)

```yaml
---
description: "Command description"          # Required
tools:                                      # Optional
  - 'tool-name/function'
scripts:                                    # Optional
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---
```

### 正文 (Markdown)

使用标准 Markdown 和特殊占位符:

- `$ARGUMENTS`: 用户提供的参数
- `{SCRIPT}`: 注册时替换为脚本路径

**示例**:

````markdown
## Steps

1. Parse arguments
2. Execute logic

```bash
args="$ARGUMENTS"
echo "Running with args: $args"
```
````

### 脚本路径重写

扩展命令使用相对路径, 在注册时会被重写:

**在扩展中**:

```yaml
scripts:
  sh: ../../scripts/bash/helper.sh
```

**注册后**:

```yaml
scripts:
  sh: .specify/scripts/bash/helper.sh
```

这允许脚本引用核心 spec-kit 脚本。

---

## 配置文件

### 配置模板

**文件**: `my-ext-config.template.yml`

```yaml
# My Extension Configuration
# Copy this to my-ext-config.yml and customize

# Example configuration
api:
  endpoint: "https://api.example.com"
  timeout: 30

features:
  feature_a: true
  feature_b: false

credentials:
  # DO NOT commit credentials!
  # Use environment variables instead
  api_key: "${MY_EXT_API_KEY}"
```

### 配置加载

在你的命令中, 使用分层优先级加载配置:

1. 扩展默认值 (`extension.yml` -> `defaults`)
2. 项目配置 (`.specify/extensions/my-ext/my-ext-config.yml`)
3. 本地覆盖 (`.specify/extensions/my-ext/my-ext-config.local.yml` - gitignored)
4. 环境变量 (`SPECKIT_MY_EXT_*`)

**示例加载脚本**:

```bash
#!/usr/bin/env bash
EXT_DIR=".specify/extensions/my-ext"

# Load and merge config
config=$(yq eval '.' "$EXT_DIR/my-ext-config.yml" -o=json)

# Apply env overrides
if [ -n "${SPECKIT_MY_EXT_API_KEY:-}" ]; then
  config=$(echo "$config" | jq ".api.api_key = \"$SPECKIT_MY_EXT_API_KEY\"")
fi

echo "$config"
```

---

## 使用 `.extensionignore` 排除文件

扩展作者可以在扩展根目录创建 `.extensionignore` 文件, 以在用户使用 `specify-cn extension add` 安装扩展时排除不需要复制的文件和文件夹。这对于将开发专用文件 (测试、CI 配置、文档源等) 排除在安装副本之外非常有用。

### 格式

该文件使用与 `.gitignore` 兼容的模式 (每行一个), 由 [`pathspec`](https://pypi.org/project/pathspec/) 库提供支持:

- 空行被忽略
- 以 `#` 开头的行是注释
- `*` 匹配除 `/` 之外的任何内容 (不跨目录边界)
- `**` 匹配零个或多个目录 (如 `docs/**/*.draft.md`)
- `?` 匹配除 `/` 之外的任何单个字符
- 尾部 `/` 将模式限制为仅目录
- 包含 `/` 的模式 (尾部斜杠除外) 锚定到扩展根目录
- 不包含 `/` 的模式在树的任何深度匹配
- `!` 否定先前排除的模式 (重新包含文件)
- 模式中的反斜杠会被规范化为正斜杠, 以实现跨平台兼容性
- `.extensionignore` 文件本身总是自动排除

### 示例

```gitignore
# .extensionignore

# Development files
tests/
.github/
.gitignore

# Build artifacts
__pycache__/
*.pyc
dist/

# Documentation source (keep only the built README)
docs/
CONTRIBUTING.md
```

### 模式匹配

| 模式 | 匹配 | 不匹配 |
|------|------|--------|
| `*.pyc` | 任何目录中的 `.pyc` 文件 | — |
| `tests/` | `tests` 目录(及其所有内容) | 名为 `tests` 的文件 |
| `docs/*.draft.md` | `docs/api.draft.md` (直接在 `docs/` 内) | `docs/sub/api.draft.md` (嵌套) |
| `.env` | 任何层级的 `.env` 文件 | — |
| `!README.md` | 重新包含 `README.md`, 即使被之前的模式匹配 | — |
| `docs/**/*.draft.md` | `docs/api.draft.md`, `docs/sub/api.draft.md` | — |

### 不支持的功能

以下 `.gitignore` 功能在此上下文中**不适用**:

- **多个 `.extensionignore` 文件**: 仅支持扩展根目录中的单个文件 (`.gitignore` 支持子目录中的文件)
- **`$GIT_DIR/info/exclude` 和 `core.excludesFile`**: 这些是 Git 特有的, 这里没有等效功能
- **被排除目录内的否定**: 由于文件复制使用 `shutil.copytree`, 排除目录会完全阻止递归进入它。否定模式无法重新包含被排除目录内的文件。例如, `tests/` 后跟 `!tests/important.py` 的组合**不会**保留 `tests/important.py` — `tests/` 目录在根级别被跳过, 其内容永远不会被评估。要解决此问题, 请单独排除目录的内容而不是目录本身 (如使用 `tests/*.pyc` 和 `tests/.cache/` 而不是 `tests/`)。

---

## 验证规则

### 扩展 ID

- **模式**: `^[a-z0-9-]+$`
- **有效**: `my-ext`, `tool-123`, `awesome-plugin`
- **无效**: `MyExt` (大写), `my_ext` (下划线), `my ext` (空格)

### 扩展版本

- **格式**: 语义化版本 (MAJOR.MINOR.PATCH)
- **有效**: `1.0.0`, `0.1.0`, `2.5.3`
- **无效**: `1.0`, `v1.0.0`, `1.0.0-beta`

### 命令名称

- **模式**: `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
- **有效**: `speckit.my-ext.hello`, `speckit.tool.cmd`
- **无效**: `my-ext.hello` (缺少前缀), `speckit.hello` (没有扩展命名空间)

### 命令文件路径

- **必须**相对于扩展根目录
- **有效**: `commands/hello.md`, `commands/subdir/cmd.md`
- **无效**: `/absolute/path.md`, `../outside.md`

---

## 测试扩展

### 手动测试

1. **创建测试扩展**
2. **本地安装**:

   ```bash
   specify-cn extension add --dev /path/to/extension
   ```

3. **验证安装**:

   ```bash
   specify-cn extension list
   ```

4. 使用你的 AI 代理**测试命令**
5. **检查命令注册**:

   ```bash
   ls .claude/commands/speckit.my-ext.*
   ```

6. **移除扩展**:

   ```bash
   specify-cn extension remove my-ext
   ```

### 自动化测试

为你的扩展创建测试:

```python
# tests/test_my_extension.py
import pytest
from pathlib import Path
from specify_cli.extensions import ExtensionManifest

def test_manifest_valid():
    """Test extension manifest is valid."""
    manifest = ExtensionManifest(Path("extension.yml"))
    assert manifest.id == "my-ext"
    assert len(manifest.commands) >= 1

def test_command_files_exist():
    """Test all command files exist."""
    manifest = ExtensionManifest(Path("extension.yml"))
    for cmd in manifest.commands:
        cmd_file = Path(cmd["file"])
        assert cmd_file.exists(), f"Command file not found: {cmd_file}"
```

---

## 分发

### 方式 1: GitHub 仓库

1. **创建仓库**: `spec-kit-my-ext`
2. **添加文件**:

   ```text
   spec-kit-my-ext/
   ├── extension.yml
   ├── commands/
   ├── scripts/
   ├── docs/
   ├── README.md
   ├── LICENSE
   └── CHANGELOG.md
   ```

3. **创建发布**: 使用版本标签 (如 `v1.0.0`)
4. **从仓库安装**:

   ```bash
   git clone https://github.com/you/spec-kit-my-ext
   specify-cn extension add --dev spec-kit-my-ext/
   ```

### 方式 2: ZIP 归档 (未来)

创建 ZIP 归档并托管在 GitHub Releases 上:

```bash
zip -r spec-kit-my-ext-1.0.0.zip extension.yml commands/ scripts/ docs/
```

用户安装:

```bash
specify-cn extension add <extension-name> --from https://github.com/.../spec-kit-my-ext-1.0.0.zip
```

### 方式 3: 社区参考目录

提交到社区目录以供公开发现:

1. **Fork** spec-kit 仓库
2. **添加条目**到 `extensions/catalog.community.json`
3. **更新** README.md 中的社区扩展表, 包含你的扩展信息
4. 按照[扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md)**创建 PR**
5. **合并后**, 你的扩展将可用:
   - 用户可以浏览 `catalog.community.json` 来发现你的扩展
   - 用户将条目复制到自己的 `catalog.json`
   - 用户安装: `specify-cn extension add my-ext` (从他们的目录)

详细提交说明请参见[扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md)。

---

## 最佳实践

### 命名约定

- **扩展 ID**: 使用描述性的连字符名称 (`jira-integration`, 而不是 `ji`)
- **命令**: 使用动词-名词模式 (`create-issue`, `sync-status`)
- **配置文件**: 与扩展 ID 匹配 (`jira-config.yml`)

### 文档

- **README.md**: 概述、安装、用法
- **CHANGELOG.md**: 版本历史
- **docs/**: 详细指南
- **命令描述**: 清晰、简洁

### 版本控制

- **遵循 SemVer**: `MAJOR.MINOR.PATCH`
- **MAJOR**: 破坏性变更
- **MINOR**: 新功能
- **PATCH**: 缺陷修复

### 安全

- **绝不提交密钥**: 使用环境变量
- **验证输入**: 净化用户参数
- **记录权限**: 文档说明访问了哪些文件/API

### 兼容性

- **指定版本范围**: 不要要求精确版本
- **测试多个版本**: 确保兼容性
- **优雅降级**: 处理缺失功能

---

## 示例扩展

### 最小扩展

尽可能小的扩展:

```yaml
# extension.yml
schema_version: "1.0"
extension:
  id: "minimal"
  name: "Minimal Extension"
  version: "1.0.0"
  description: "Minimal example"
requires:
  speckit_version: ">=0.1.0"
provides:
  commands:
    - name: "speckit.minimal.hello"
      file: "commands/hello.md"
```

````markdown
<!-- commands/hello.md -->
---
description: "Hello command"
---

# Hello World

```bash
echo "Hello, $ARGUMENTS!"
```
````

### 带配置的扩展

使用配置的扩展:

```yaml
# extension.yml
# ... metadata ...
provides:
  config:
    - name: "tool-config.yml"
      template: "tool-config.template.yml"
      required: true
```

```yaml
# tool-config.template.yml
api_endpoint: "https://api.example.com"
timeout: 30
```

````markdown
<!-- commands/use-config.md -->
# Use Config

Load config:
```bash
config_file=".specify/extensions/tool/tool-config.yml"
endpoint=$(yq eval '.api_endpoint' "$config_file")
echo "Using endpoint: $endpoint"
```
````

### 带钩子的扩展

自动运行的扩展:

```yaml
# extension.yml
hooks:
  after_tasks:
    command: "speckit.auto.analyze"
    optional: false  # Always run
    description: "Analyze tasks after generation"
```

---

## 故障排除

### 扩展无法安装

**错误**: `Invalid extension ID`

- **修复**: 仅使用小写字母、数字和连字符

**错误**: `Extension requires spec-kit >=0.2.0`

- **修复**: 使用 `uv tool install specify-cn-cli --force` 更新 spec-kit

**错误**: `Command file not found`

- **修复**: 确保命令文件存在于清单中指定的路径

### 命令未注册

**症状**: 命令没有出现在 AI 代理中

**检查**:

1. `.claude/commands/` 目录是否存在
2. 扩展是否安装成功
3. 命令是否在注册表中注册:

   ```bash
   cat .specify/extensions/.registry
   ```

**修复**: 重新安装扩展以触发注册

### 配置未加载

**检查**:

1. 配置文件是否存在: `.specify/extensions/{ext-id}/{ext-id}-config.yml`
2. YAML 语法是否有效: `yq eval '.' config.yml`
3. 环境变量是否正确设置

---

## 获取帮助

- **Issues**: 在 GitHub 仓库报告缺陷
- **讨论**: 在 GitHub Discussions 提问
- **示例**: 参见 `spec-kit-jira` 获取完整功能示例 (Phase B)

---

## 下一步

1. 按照本指南**创建你的扩展**
2. 使用 `--dev` 标志**本地测试**
3. **与社区分享** (GitHub, 目录)
4. 基于反馈**迭代改进**

祝你扩展开发愉快!

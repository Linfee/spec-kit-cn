# 扩展开发指南

创建 Spec Kit 扩展的指南. 

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
  id: "my-ext"                          # 小写, 字母数字 + 连字符
  name: "My Extension"
  version: "1.0.0"                      # 语义版本
  description: "My custom extension"
  author: "Your Name"
  repository: "https://github.com/you/spec-kit-my-ext"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"            # 最低 spec-kit 版本
  tools:                                # 可选: 需要的外部工具
    - name: "my-tool"
      required: true
      version: ">=1.0.0"
  commands:                             # 可选: 需要的核心命令
    - "speckit.tasks"

provides:
  commands:
    - name: "speckit.my-ext.hello"      # 必须遵循模式: speckit.{ext-id}.{cmd}
      file: "commands/hello.md"
      description: "Say hello"
      aliases: ["speckit.hello"]        # 可选别名

  config:                               # 可选: 配置文件
    - name: "my-ext-config.yml"
      template: "my-ext-config.template.yml"
      description: "Extension configuration"
      required: false

hooks:                                  # 可选: 集成钩子
  after_tasks:
    command: "speckit.my-ext.hello"
    optional: true
    prompt: "Run hello command?"

tags:                                   # 可选: 用于目录搜索
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
tools:                              # 可选: 此命令使用的 AI 工具
  - 'some-tool/function'
scripts:                            # 可选: 辅助脚本
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
```

### 5. 本地测试

```bash
cd /path/to/spec-kit-project
specify extension add --dev /path/to/my-extension
```

### 6. 验证安装

```bash
specify extension list

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

命令将在 `.claude/commands/speckit.my-ext.hello.md` 中可用. 

---

## 清单 Schema 参考

### 必需字段

#### `schema_version`

扩展清单 schema 版本. 当前: `"1.0"`

#### `extension`

扩展元数据块. 

**必需子字段**:

- `id`: 扩展标识符 (小写, 字母数字, 连字符)
- `name`: 人类可读名称
- `version`: 语义版本 (如 "1.0.0")
- `description`: 简短描述

**可选子字段**:

- `author`: 扩展作者
- `repository`: 源代码 URL
- `license`: SPDX 许可证标识符
- `homepage`: 扩展主页 URL

#### `requires`

兼容性要求. 

**必需子字段**:

- `speckit_version`: 语义版本说明符 (如 ">=0.1.0,<2.0.0")

**可选子字段**:

- `tools`: 需要的外部工具 (工具对象数组)
- `commands`: 需要的核心 spec-kit 命令 (命令名数组)
- `scripts`: 需要的核心脚本 (脚本名数组)

#### `provides`

扩展提供的内容. 

**必需子字段**:

- `commands`: 命令对象数组 (必须至少有一个)

**命令对象**:

- `name`: 命令名称 (必须匹配 `speckit.{ext-id}.{command}`)
- `file`: 命令文件路径 (相对于扩展根目录)
- `description`: 命令描述 (可选)
- `aliases`: 替代命令名称 (可选, 数组)

### 可选字段

#### `hooks`

自动执行的集成钩子. 

可用的钩子点:

- `after_tasks`: 在 `/speckit.tasks` 完成后
- `after_implement`: 在 `/speckit.implement` 完成后 (未来)

钩子对象:

- `command`: 要执行的命令 (必须在 `provides.commands` 中)
- `optional`: 如果为 true, 执行前提示用户
- `prompt`: 可选钩子的提示文本
- `description`: 钩子描述
- `condition`: 执行条件 (未来)

#### `tags`

用于目录发现的标签数组. 

#### `defaults`

默认扩展配置值. 

#### `config_schema`

用于验证扩展配置的 JSON Schema. 

---

## 命令文件格式

### Frontmatter (YAML)

```yaml
---
description: "Command description"          # 必需
tools:                                      # 可选
  - 'tool-name/function'
scripts:                                    # 可选
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---
```

### 正文 (Markdown)

使用带有特殊占位符的标准 Markdown:

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

这允许脚本引用核心 spec-kit 脚本. 

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

在你的命令中, 按分层优先级加载配置:

1. 扩展默认值 (`extension.yml` → `defaults`)
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

## 验证规则

### 扩展 ID

- **模式**: `^[a-z0-9-]+$`
- **有效**: `my-ext`, `tool-123`, `awesome-plugin`
- **无效**: `MyExt` (大写), `my_ext` (下划线), `my ext` (空格)

### 扩展版本

- **格式**: 语义版本 (MAJOR.MINOR.PATCH)
- **有效**: `1.0.0`, `0.1.0`, `2.5.3`
- **无效**: `1.0`, `v1.0.0`, `1.0.0-beta`

### 命令名称

- **模式**: `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
- **有效**: `speckit.my-ext.hello`, `speckit.tool.cmd`
- **无效**: `my-ext.hello` (缺少前缀), `speckit.hello` (没有扩展命名空间)

### 命令文件路径

- **必须是** 相对于扩展根目录
- **有效**: `commands/hello.md`, `commands/subdir/cmd.md`
- **无效**: `/absolute/path.md`, `../outside.md`

---

## 测试扩展

### 手动测试

1. **创建测试扩展**
2. **本地安装**:

   ```bash
   specify extension add --dev /path/to/extension
   ```

3. **验证安装**:

   ```bash
   specify extension list
   ```

4. **用你的 AI agent 测试命令**
5. **检查命令注册**:

   ```bash
   ls .claude/commands/speckit.my-ext.*
   ```

6. **移除扩展**:

   ```bash
   specify extension remove my-ext
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

### 选项 1: GitHub 仓库

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

3. **创建 release**: 用版本打标签 (如 `v1.0.0`)
4. **从仓库安装**:

   ```bash
   git clone https://github.com/you/spec-kit-my-ext
   specify extension add --dev spec-kit-my-ext/
   ```

### 选项 2: ZIP 归档 (未来)

创建 ZIP 归档并托管在 GitHub Releases:

```bash
zip -r spec-kit-my-ext-1.0.0.zip extension.yml commands/ scripts/ docs/
```

用户安装:

```bash
specify extension add --from https://github.com/.../spec-kit-my-ext-1.0.0.zip
```

### 选项 3: 社区参考目录

提交到社区目录以供公开发现:

1. **Fork** spec-kit 仓库
2. **添加条目** 到 `extensions/catalog.community.json`
3. **更新** `extensions/README.md` 包含你的扩展
4. **创建 PR** 遵循 [扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md)
5. **合并后**, 你的扩展变为可用:
   - 用户可以浏览 `catalog.community.json` 发现你的扩展
   - 用户复制条目到他们自己的 `catalog.json`
   - 用户安装: `specify extension add my-ext` (从他们的目录)

详细提交说明请参阅 [扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md). 

---

## 最佳实践

### 命名约定

- **扩展 ID**: 使用描述性的, 连字符名称 (`jira-integration`, 不是 `ji`)
- **命令**: 使用动词-名词模式 (`create-issue`, `sync-status`)
- **配置文件**: 匹配扩展 ID (`jira-config.yml`)

### 文档

- **README.md**: 概述, 安装, 用法
- **CHANGELOG.md**: 版本历史
- **docs/**: 详细指南
- **命令描述**: 清晰, 简洁

### 版本控制

- **遵循 SemVer**: `MAJOR.MINOR.PATCH`
- **MAJOR**: 破坏性变更
- **MINOR**: 新功能
- **PATCH**: Bug 修复

### 安全

- **永远不要提交机密**: 使用环境变量
- **验证输入**: 清理用户参数
- **文档化权限**: 访问哪些文件/API

### 兼容性

- **指定版本范围**: 不要要求精确版本
- **测试多个版本**: 确保兼容性
- **优雅降级**: 处理缺失功能

---

## 示例扩展

### 最小扩展

最小可能的扩展:

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

- **修复**: 只使用小写, 字母数字 + 连字符

**错误**: `Extension requires spec-kit >=0.2.0`

- **修复**: 用 `uv tool install specify-cli --force` 更新 spec-kit

**错误**: `Command file not found`

- **修复**: 确保命令文件存在于清单中指定的路径

### 命令未注册

**症状**: 命令没有出现在 AI agent 中

**检查**:

1. `.claude/commands/` 目录存在
2. 扩展安装成功
3. 命令已在注册表中注册:

   ```bash
   cat .specify/extensions/.registry
   ```

**修复**: 重新安装扩展以触发注册

### 配置未加载

**检查**:

1. 配置文件存在: `.specify/extensions/{ext-id}/{ext-id}-config.yml`
2. YAML 语法有效: `yq eval '.' config.yml`
3. 环境变量设置正确

---

## 获取帮助

- **问题**: 在 GitHub 仓库报告 bug
- **讨论**: 在 GitHub Discussions 提问
- **示例**: 参见 `spec-kit-jira` 获取完整功能示例 (Phase B)

---

## 下一步

1. **创建你的扩展** 遵循本指南
2. **本地测试** 使用 `--dev` 标志
3. **与社区分享** (GitHub, 目录)
4. **迭代** 基于反馈

祝你扩展开发愉快! 🚀
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

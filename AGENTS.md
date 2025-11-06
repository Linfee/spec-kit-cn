## 关于 Spec Kit 与 Specify

**GitHub Spec Kit** 是一个用于实现规范驱动开发（Spec-Driven Development, SDD）的完整工具包，包含模板、脚本与工作流，帮助团队在编写代码之前先定义可执行的规范。

**Specify CLI** 是用于引导项目的命令行工具，负责搭建必要的目录结构、模板与 AI 智能体集成，以支持规范驱动开发的工作流程。

该工具包支持多种 AI 编码助手，使团队可以在保持一致项目结构和开发实践的同时，使用自己偏好的工具。

---

## 通用实践

- 对 `Specify CLI` 的 `__init__.py` 做任何修改，都应在 `pyproject.toml` 中更新版本号并在 `CHANGELOG.md` 中添加对应条目。

## 新增代理支持指南

下面说明如何向 Specify CLI 中添加新的 AI 智能体支持。此流程可作为集成新智能体时的参考。

### 概览

Specify 在初始化项目时，会针对不同智能体生成智能体专属的命令文件与目录结构。每个智能体在以下方面可能有所不同：

- 命令文件格式（Markdown、TOML 等）
- 目录结构（例如 `.claude/commands/`、`.windsurf/workflows/` 等）
- 命令调用方式（斜杠命令、CLI 工具等）
- 参数传递约定（如 `$ARGUMENTS`、`{{args}}`）

### 当前已支持的智能体

| 智能体 | 目录 | 格式 | CLI 工具 | 说明 |
|------|------|------|----------|------|
| Claude Code | `.claude/commands/` | Markdown | `claude` | Anthropic 的 Claude Code CLI |
| Gemini CLI | `.gemini/commands/` | TOML | `gemini` | Google 的 Gemini CLI |
| GitHub Copilot | `.github/prompts/` | Markdown | N/A (IDE 集成) | VS Code 中的 Copilot |
| Cursor | `.cursor/commands/` | Markdown | `cursor-agent` | Cursor CLI |
| Qwen Code | `.qwen/commands/` | TOML | `qwen` | 阿里云通义千问代码助手 |
| opencode | `.opencode/command/` | Markdown | `opencode` | opencode CLI |
| Codex CLI | `.codex/commands/` | Markdown | `codex` | Codex CLI |
| Windsurf | `.windsurf/workflows/` | Markdown | N/A (IDE 集成) | Windsurf IDE 工作流 |
| Kilo Code | `.kilocode/rules/` | Markdown | N/A (IDE 集成) | Kilo Code |
| Auggie CLI | `.augment/rules/` | Markdown | `auggie` | Auggie CLI |
| Roo Code | `.roo/rules/` | Markdown | N/A (IDE 集成) | Roo Code |
| CodeBuddy CLI | `.codebuddy/commands/` | Markdown | `codebuddy` | CodeBuddy CLI |
| Amazon Q Developer CLI | `.amazonq/prompts/` | Markdown | `q` | Amazon Q Developer CLI |
| Amp | `.agents/commands/` | Markdown | `amp` | Amp CLI |

### 集成步骤（示例）

按下面步骤添加新代理支持（以假设的新代理为例）：

#### 1. 在 AGENT_CONFIG 中新增条目

在 `src/specify_cli/__init__.py` 中将新智能体加入 `AGENT_CONFIG` 字典。注意：字典的键应为实际的 CLI 可执行名（即用户在终端中输入的名称）：

```python
AGENT_CONFIG = {
    # ... 现有代理 ...
    "new-agent-cli": {  # 使用实际的可执行名
        "name": "New Agent Display Name",
        "folder": ".newagent/",
        "install_url": "https://example.com/install",
        "requires_cli": True,
    },
}
```

重要原则：字典键应直接对应可执行文件名，这样无需在其它地方做特殊映射（例如 `cursor-agent` 而非 `cursor`）。

字段说明：
- `name`：对用户可读的展示名称
- `folder`：代理文件存放目录（相对项目根目录）
- `install_url`：安装文档链接（IDE 集成类代理可设为 `None`）
- `requires_cli`：是否需要 CLI 工具进行检查

#### 2. 更新 CLI 帮助文本

在 `init()` 命令的 `--ai` 参数帮助文本中加入新智能体名称，确保用户能在帮助中看到可选项。

#### 3. 更新 README 文档

在 README 的“支持的 AI 智能体”部分添加新条目，并在 AGENTS 列表或表格中说明支持级别与安装链接。

#### 4. 更新发布脚本

修改 `.github/workflows/scripts/create-release-packages.sh`，将新智能体加入 `ALL_AGENTS` 数组，并在打包时处理对应目录/格式。

#### 5. 更新 agent context 脚本

更新 `scripts/bash/update-agent-context.sh` 与 `scripts/powershell/update-agent-context.ps1`，为新智能体增加对应文件变量并在 switch/case 中处理。

#### 6. （可选）更新 CLI 工具检查

对于需要 CLI 的智能体，在 `check()` 命令中将其纳入检查清单（`requires_cli` 字段会推动自动检查逻辑）。

### 重要设计决策

始终使用实际的 CLI 可执行名称作为 `AGENT_CONFIG` 的键，以避免在代码库中出现分散的特殊映射逻辑。

### 更新 Devcontainer（可选）

对于基于 VS Code 扩展或需要在 devcontainer 中安装的 CLI 工具的智能体，分别在 `.devcontainer/devcontainer.json` 和 `.devcontainer/post-create.sh` 中添加相应配置或安装脚本。

### 智能体分类

CLI 型智能体（需在系统 PATH 中存在可执行工具）：

- Claude Code (`claude`)
- Gemini CLI (`gemini`)
- Cursor (`cursor-agent`)
- Qwen Code (`qwen`)
- opencode (`opencode`)
- Amazon Q Developer CLI (`q`)
- CodeBuddy CLI (`codebuddy`)
- Amp (`amp`)

IDE 集成型智能体（不需要 CLI 可执行）：

- GitHub Copilot
- Windsurf

### 命令文件格式

- Markdown：用于 Claude、Cursor、opencode、Windsurf、Amazon Q、Amp 等智能体
- TOML：用于 Gemini、Qwen 等代理

不同智能体使用不同的占位符：Markdown 类命令使用 `$ARGUMENTS`，TOML 使用 `{{args}}`，脚本路径用 `{SCRIPT}` 占位。

### 目录约定

- CLI 智能体通常位于 `.<agent-name>/commands/`
- Copilot（IDE）使用 `.github/prompts/`
- Windsurf 使用 `.windsurf/workflows/`

---

此文件为 `AGENTS.md` 的中文本地化副本；如需将其合并回主分支或在 PR 中进一步处理，请告知分支/PR 偏好。

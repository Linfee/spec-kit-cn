# 升级指南

> 您已安装 Spec Kit 并希望升级到最新版本以获取新功能、错误修复或更新的斜杠命令。本指南涵盖升级 CLI 工具和更新项目文件。

---

## 快速参考

| 升级内容 | 命令 | 使用场景 |
|----------|-------|----------|
| **仅 CLI 工具** | `uv tool install specify-cn-cli --force --from git+https://github.com/linfee/spec-kit-cn.git` | 获取最新 CLI 功能而不影响项目文件 |
| **项目文件** | `specify-cn init --here --force --ai <your-agent>` | 更新项目中的斜杠命令、模板和脚本 |
| **两者** | 运行 CLI 升级，然后项目更新 | 推荐用于主要版本更新 |

---

## 第 1 部分：升级 CLI 工具

CLI 工具 (`specify-cn`) 与您的项目文件是分开的。升级它以获得最新功能和错误修复。

### 如果您使用 `uv tool install` 安装

```bash
uv tool install specify-cn-cli --force --from git+https://github.com/linfee/spec-kit-cn.git
```

### 如果您使用一次性 `uvx` 命令

无需升级——`uvx` 总是获取最新版本。只需正常运行您的命令：

```bash
uvx --from git+https://github.com/linfee/spec-kit-cn.git specify-cn init --here --ai copilot
```

### 验证升级

```bash
specify-cn check
```

这将显示已安装的工具并确认 CLI 正常工作。

---

## 第 2 部分：更新项目文件

当 Spec Kit 发布新功能（如新的斜杠命令或更新的模板）时，您需要刷新项目的 Spec Kit 文件。

### 什么会更新？

运行 `specify-cn init --here --force` 将更新：

- ✅ **斜杠命令文件** (`.claude/commands/`, `.github/prompts/`, 等)
- ✅ **脚本文件** (`.specify/scripts/`)
- ✅ **模板文件** (`.specify/templates/`)
- ✅ **共享内存文件** (`.specify/memory/`) - **⚠️ 请参阅下面的警告**

### 什么是安全的？

这些文件在升级过程中**永远不会被触碰**——模板包甚至不包含它们：

- ✅ **您的规范** (`specs/001-my-feature/spec.md`, 等) - **确认安全**
- ✅ **您的实施计划** (`specs/001-my-feature/plan.md`, `tasks.md`, 等) - **确认安全**
- ✅ **您的源代码** - **确认安全**
- ✅ **您的 git 历史** - **确认安全**

`specs/` 目录完全从模板包中排除，在升级过程中永远不会被修改。

### 更新命令

在您的项目目录中运行：

```bash
specify-cn init --here --force --ai <your-agent>
```

将 `<your-agent>` 替换为您的 AI 助手。请参阅 [支持的 AI 助手](../README.md#-supported-ai-agents) 列表

**示例：**

```bash
specify-cn init --here --force --ai copilot
```

### 理解 `--force` 标志

没有 `--force`，CLI 会警告您并要求确认：

```
警告：当前目录不为空（25 项）
模板文件将与现有内容合并，并可能覆盖现有文件
是否继续？[y/N]
```

使用 `--force`，它会跳过确认并立即继续。

**重要：您的 `specs/` 目录始终是安全的。** `--force` 标志只影响模板文件（命令、脚本、模板、内存）。您在 `specs/` 中的功能规范、计划和任务永远不会包含在升级包中，也无法被覆盖。

---

## ⚠️ 重要警告

### 1. 章程文件将被覆盖

**已知问题：** `specify-cn init --here --force` 目前会用默认模板覆盖 `.specify/memory/constitution.md`，删除您所做的任何自定义设置。

**解决方法：**

```bash
# 1. 在升级前备份您的章程
cp .specify/memory/constitution.md .specify/memory/constitution-backup.md

# 2. 运行升级
specify-cn init --here --force --ai copilot

# 3. 恢复您的自定义章程
mv .specify/memory/constitution-backup.md .specify/memory/constitution.md
```

或使用 git 来恢复它：

```bash
# 升级后，从 git 历史恢复
git restore .specify/memory/constitution.md
```

### 2. 自定义模板修改

如果您自定义了 `.specify/templates/` 中的任何模板，升级将覆盖它们。先备份它们：

```bash
# 备份自定义模板
cp -r .specify/templates .specify/templates-backup

# 升级后，手动合并回您的更改
```

### 3. 重复的斜杠命令（基于 IDE 的代理）

一些基于 IDE 的代理（如 Kilo Code、Windsurf）在升级后可能显示**重复的斜杠命令**——旧版本和新版本都会出现。

**解决方案：** 手动从代理的文件夹中删除旧的命令文件。

**Kilo Code 示例：**

```bash
# 导航到代理的命令文件夹
cd .kilocode/rules/

# 列出文件并识别重复项
ls -la

# 删除旧版本（示例文件名 - 您的可能不同）
rm speckit.specify-old.md
rm speckit.plan-v1.md
```

重启您的 IDE 以刷新命令列表。

---

## 常见场景

### 场景 1："我只想要新的斜杠命令"

```bash
# 升级 CLI（如果使用持久安装）
uv tool install specify-cn-cli --force --from git+https://github.com/linfee/spec-kit-cn.git

# 更新项目文件以获取新命令
specify-cn init --here --force --ai copilot

# 如果自定义了章程，则恢复
git restore .specify/memory/constitution.md
```

### 场景 2："我自定义了模板和章程"

```bash
# 1. 备份自定义内容
cp .specify/memory/constitution.md /tmp/constitution-backup.md
cp -r .specify/templates /tmp/templates-backup

# 2. 升级 CLI
uv tool install specify-cn-cli --force --from git+https://github.com/linfee/spec-kit-cn.git

# 3. 更新项目
specify-cn init --here --force --ai copilot

# 4. 恢复自定义内容
mv /tmp/constitution-backup.md .specify/memory/constitution.md
# 如需要，手动合并模板更改
```

### 场景 3："我在 IDE 中看到重复的斜杠命令"

这发生在基于 IDE 的代理中（Kilo Code、Windsurf、Roo Code 等）。

```bash
# 查找代理文件夹（示例：.kilocode/rules/）
cd .kilocode/rules/

# 列出所有文件
ls -la

# 删除旧命令文件
rm speckit.old-command-name.md

# 重启您的 IDE
```

### 场景 4："我在没有 Git 的项目中工作"

如果您使用 `--no-git` 初始化项目，仍然可以升级：

```bash
# 手动备份您自定义的文件
cp .specify/memory/constitution.md /tmp/constitution-backup.md

# 运行升级
specify-cn init --here --force --ai copilot --no-git

# 恢复自定义内容
mv /tmp/constitution-backup.md .specify/memory/constitution.md
```

`--no-git` 标志跳过 git 初始化，但不影响文件更新。

---

## 使用 `--no-git` 标志

`--no-git` 标志告诉 Spec Kit **跳过 git 仓库初始化**。这在以下情况下有用：

- 您以不同方式管理版本控制（Mercurial、SVN 等）
- 您的项目是具有现有 git 设置的更大 monorepo 的一部分
- 您在实验中，还不想使用版本控制

**在初始设置期间：**

```bash
specify-cn init my-project --ai copilot --no-git
```

**在升级期间：**

```bash
specify-cn init --here --force --ai copilot --no-git
```

### `--no-git` 不做什么

❌ 不阻止文件更新
❌ 不跳过斜杠命令安装
❌ 不影响模板合并

它**只**跳过运行 `git init` 和创建初始提交。

### 没有 Git 的工作

如果您使用 `--no-git`，您需要手动管理功能目录：

**在使用规划命令之前设置 `SPECIFY_FEATURE` 环境变量：**

```bash
# Bash/Zsh
export SPECIFY_FEATURE="001-my-feature"

# PowerShell
$env:SPECIFY_FEATURE = "001-my-feature"
```

这告诉 Spec Kit 在创建规范、计划和任务时要使用哪个功能目录。

**为什么这很重要：** 没有 git，Spec Kit 无法检测您当前的分支名来确定活动功能。环境变量手动提供该上下文。

---

## 故障排除

### "升级后斜杠命令不显示"

**原因：** 代理没有重新加载命令文件。

**修复：**

1. **完全重启您的 IDE/编辑器**（不只是重新加载窗口）
2. **对于基于 CLI 的代理**，验证文件存在：
   ```bash
   ls -la .claude/commands/      # Claude Code
   ls -la .gemini/commands/       # Gemini
   ls -la .cursor/commands/       # Cursor
   ```
3. **检查代理特定设置：**
   - Codex 需要 `CODEX_HOME` 环境变量
   - 一些代理需要工作区重启或缓存清除

### "我丢失了章程的自定义内容"

**修复：** 从 git 或备份恢复：

```bash
# 如果您在升级前提交了
git restore .specify/memory/constitution.md

# 如果您手动备份了
cp /tmp/constitution-backup.md .specify/memory/constitution.md
```

**预防：** 在升级前始终提交或备份 `constitution.md`。

### "警告：当前目录不为空"

**完整警告消息：**
```
警告：当前目录不为空（25 项）
模板文件将与现有内容合并，并可能覆盖现有文件
是否继续？[y/N]
```

**这意味着什么：**

当您在已有文件的目录中运行 `specify-cn init --here`（或 `specify-cn init .`）时会出现此警告。它告诉您：

1. **目录有现有内容** - 在示例中，25 个文件/文件夹
2. **文件将合并** - 新模板文件将添加到现有文件旁边
3. **一些文件可能被覆盖** - 如果您已有 Spec Kit 文件（`.claude/`、`.specify/` 等），它们将被新版本替换

**什么会被覆盖：**

只有 Spec Kit 基础设施文件：
- 代理命令文件（`.claude/commands/`、`.github/prompts/` 等）
- `.specify/scripts/` 中的脚本
- `.specify/templates/` 中的模板
- `.specify/memory/` 中的内存文件（包括章程）

**什么不会被触动：**

- 您的 `specs/` 目录（规范、计划、任务）
- 您的源代码文件
- 您的 `.git/` 目录和 git 历史
- 任何不属于 Spec Kit 模板的其他文件

**如何响应：**

- **输入 `y` 并按 Enter** - 继续合并（推荐升级时）
- **输入 `n` 并按 Enter** - 取消操作
- **使用 `--force` 标志** - 完全跳过此确认：
  ```bash
  specify-cn init --here --force --ai copilot
  ```

**当您看到此警告时：**

- ✅ **预期** 在升级现有 Spec Kit 项目时
- ✅ **预期** 在将 Spec Kit 添加到现有代码库时
- ⚠️ **意外** 如果您认为您在空目录中创建新项目

**预防提示：** 在升级前，如果您自定义了 `.specify/memory/constitution.md`，请提交或备份它。

### "CLI 升级似乎不工作"

验证安装：

```bash
# 检查已安装的工具
uv tool list

# 应该显示 specify-cn-cli

# 验证路径
which specify-cn

# 应该指向 uv 工具安装目录
```

如果未找到，重新安装：

```bash
uv tool uninstall specify-cn-cli
uv tool install specify-cn-cli --from git+https://github.com/linfee/spec-kit-cn.git
```

### "我每次打开项目都需要运行 specify 吗？"

**简短回答：** 不，您只需要每个项目运行一次 `specify-cn init`（或升级时）。

**解释：**

`specify-cn` CLI 工具用于：
- **初始设置：** `specify-cn init` 在您的项目中引导 Spec Kit
- **升级：** `specify-cn init --here --force` 更新模板和命令
- **诊断：** `specify-cn check` 验证工具安装

一旦您运行了 `specify-cn init`，斜杠命令（如 `/speckit.specify`、`/speckit.plan` 等）就**永久安装**在您项目的代理文件夹中（`.claude/`、`.github/prompts/` 等）。您的 AI 助手直接读取这些命令文件——无需再次运行 `specify-cn`。

**如果您的代理无法识别斜杠命令：**

1. **验证命令文件存在：**
   ```bash
   # 对于 GitHub Copilot
   ls -la .github/prompts/

   # 对于 Claude
   ls -la .claude/commands/
   ```

2. **完全重启您的 IDE/编辑器**（不只是重新加载窗口）

3. **检查您在正确的目录**中运行了 `specify-cn init`

4. **对于某些代理**，您可能需要重新加载工作区或清除缓存

**相关问题：** 如果 Copilot 无法打开本地文件或意外使用 PowerShell 命令，这通常是 IDE 上下文问题，与 `specify-cn` 无关。请尝试：
- 重启 VS Code
- 检查文件权限
- 确保工作区文件夹正确打开

---

## 版本兼容性

Spec Kit 在主要版本中遵循语义版本控制。CLI 和项目文件设计为在同一主要版本内兼容。

**最佳实践：** 通过在主要版本更改时一起升级两者来保持 CLI 和项目文件同步。

---

## 后续步骤

升级后：

- **测试新的斜杠命令：** 运行 `/speckit.constitution` 或其他命令以验证一切正常
- **查看发布说明：** 检查 [GitHub Releases](https://github.com/linfee/spec-kit-cn/releases) 获取新功能和重大更改
- **更新工作流：** 如果添加了新命令，更新您团队的开发工作流
- **检查文档：** 访问 [github.io/spec-kit](https://github.github.io/spec-kit/) 获取更新的指南
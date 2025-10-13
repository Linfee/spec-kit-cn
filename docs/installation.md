# 安装指南

## 前置要求

- **Linux/macOS**（或在 Windows 上的 WSL2）
- AI编码助手：[Claude Code](https://www.anthropic.com/claude-code)、[GitHub Copilot](https://code.visualstudio.com/)或[Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [uv](https://docs.astral.sh/uv/) 用于包管理
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## 安装

### 初始化新项目

最简单的入门方式是初始化一个新项目：

```bash
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init <PROJECT_NAME>
```

或者在当前目录中初始化：

```bash
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init .
# 或使用 --here 标志
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init --here
```

### 指定 AI 助手

您可以在初始化时主动指定您的 AI 助手：

```bash
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init <project_name> --ai claude
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init <project_name> --ai gemini
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init <project_name> --ai copilot
```

### 忽略助手工具检查

如果您希望获取模板而不检查正确的工具：

```bash
uvx --from git+https://github.com/Linfee/spec-kit-cn.git specify-cn init <project_name> --ai claude --ignore-agent-tools
```

## 验证

初始化后，您应该在 AI 助手中看到以下可用命令：
- `/speckit.specify` - 创建规范
- `/speckit.plan` - 生成实施计划
- `/speckit.tasks` - 分解为可执行任务

## 故障排除

### Linux 上的 Git 凭据管理器

如果您在 Linux 上遇到 Git 身份验证问题，可以安装 Git 凭据管理器：

```bash
#!/usr/bin/env bash
set -e
echo "正在下载Git凭据管理器v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "正在安装Git凭据管理器..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "正在配置Git使用GCM..."
git config --global credential.helper manager
echo "正在清理..."
rm gcm-linux_amd64.2.6.1.deb
```
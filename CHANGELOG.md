# 变更日志

本项目的重要变更将记录在此文件中.

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
并且本项目遵循[语义化版本](https://semver.org/lang/zh-CN/).

## [Unreleased]

### 变更
- **CLI 命令描述翻译**: 翻译 `init` 和 `check` 命令的帮助文档字符串
  - `init`: "Initialize a new Specify project..." → "从最新模板初始化新的 Specify 项目..."
  - `check`: "Check that all required tools are installed." → "检查所有必需的工具是否已安装。"
- **AGENTS.md 用途变更**: 从原版同步文件改为独立维护的 Agent 入口文件
  - 内容改为引用 `@CLAUDE.md`, 让所有 AI Code Agent 共用同一份项目指南
  - 无需与原版同步, 独立维护
- **新增 `/punctuation-fix` 命令**: 批量规范化 Markdown 文件中的标点符号

### 文档更新
- 更新 `CLAUDE.md` 中关于 AGENTS.md 的说明
- 更新 `TRANSLATION_STANDARDS.md` 中的翻译范围说明
- 更新 `/translation-review` 和 `/translation-sync` 命令中的相关检查逻辑

## [0.3.2] - 2026-03-24

### 同步原版
- 同步原版 [v0.3.2](https://github.com/github/spec-kit/releases/tag/v0.3.2)
- 对应原版范围: v0.2.1 → v0.3.2

### 🚀 新增功能
- 引入 Preset 系统（`presets/`、`preset` 子命令与优先级/启用状态管理）
- 新增 `specify-cn status` 与 `specify-cn doctor` 能力
- 扩展系统继续增强（catalog、社区扩展、selftest 扩展等）
- 新增/扩展 AI 助手支持（Trae、iFlow、PI 等）与命令模板联动

### 🔧 技术更新
- 新增核心模块：`src/specify_cli/presets.py`、`src/specify_cli/agents.py`
- `src/specify_cli/__init__.py`、`extensions.py` 同步到 v0.3.2 逻辑
- `pyproject.toml` 版本更新到 `0.3.2`，并包含 `json5` 依赖
- 同步并通过新增测试：`tests/test_presets.py`、`tests/test_merge.py`

## [0.2.1] - 2026-03-24

### 同步原版
- 同步原版 [v0.2.1](https://github.com/github/spec-kit/releases/tag/v0.2.1)
- 对应原版范围: v0.1.13 → v0.2.1

### 🚀 新增功能
- 扩展系统支持多 Catalog 叠加与优先级解析
- 新增扩展 Catalog 管理命令（list/add/remove）
- 支持 `.extensionignore` 过滤扩展安装文件
- 新增/完善 AI 助手支持：Tabnine、Kimi、Mistral Vibe 等
- 新增 `templates/commands/tasks.md` 模板并接入相关 hooks

### 🔧 技术更新
- `src/specify_cli/extensions.py` 引入多 Catalog 与安装策略校验
- `src/specify_cli/__init__.py` 同步 v0.2.1 命令与初始化逻辑
- 同步 `update-agent-context` 与 release 打包脚本更新
- `pyproject.toml` 新增依赖 `pathspec>=0.12.0`

## [0.1.13] - 2026-03-07

### 同步原版
- 同步原版 [v0.1.13](https://github.com/github/spec-kit/releases/tag/v0.1.13)
- 对应原版范围: v0.1.10 → v0.1.13

### 🚀 新增功能
- **Kiro CLI 支持**: 替换 Amazon Q Developer CLI 为 Kiro CLI
  - 新增 kiro-cli 和 kiro 别名到 AGENT_CONFIG
  - 更新 CLI 工具检测和帮助文档
- **社区扩展更新**: 新增多个社区扩展
  - Retrospective Extension - 回顾分析扩展
  - Spec Sync - 规格同步扩展
  - Verify Extension - 验证扩展
- **Copilot 扩展修复**: 修复 Copilot 扩展命令注册
  - 扩展命令文件从 `.md` 改为 `.agent.md`
  - 新增 `.prompt.md` 伴随文件生成
  - 扩展移除时清理 `.prompt.md` 文件

### 🔧 技术更新
- **脚本增强**: 改进脚本错误处理
  - create-new-feature.sh: 新增空描述验证和分支创建错误处理
  - update-agent-context.sh/.ps1: Amazon Q → Kiro CLI 替换
- **Devcontainer 更新**: 更新开发容器配置
  - 移除 Amazon Q Developer 安装
  - 新增 Kiro CLI 安装
  - 更新 VS Code 扩展列表

### 📝 文档更新
- **README.md**: 更新 AI 助手列表
- **CHANGELOG.md**: 同步原版更新记录

## [0.1.10] - 2025-06-17

### 同步原版
- 同步原版 [v0.1.10](https://github.com/github/spec-kit/releases/tag/v0.1.10)

### 🚀 新增功能
- **Windsurf 支持**: 新增 Windsurf AI 助手支持
- **CodeBuddy 支持**: 新增 CodeBuddy AI 助手支持
- **扩展系统**: 新增社区扩展支持
  - 新增 `/extension` 命令: 安装、列出、移除扩展
  - 支持从 GitHub 仓库安装扩展
  - 支持扩展元数据和验证

### 🔧 技术更新
- **模板系统**: 改进模板下载和解压
  - 新增 `.specify/` 前缀路径重写
  - 改进跨平台兼容性
- **CLI 增强**: 改进命令行界面
  - 新增 `--skip-tls` 选项
  - 新增 `--debug` 选项
  - 新增 `--github-token` 选项

## [0.1.9] - 2025-06-10

### 同步原版
- 同步原版 [v0.1.9](https://github.com/github/spec-kit/releases/tag/v0.1.9)

### 🚀 新增功能
- **Codex CLI 支持**: 新增 OpenAI Codex CLI 支持
- **Auggie CLI 支持**: 新增 Auggie CLI 支持

### 📝 文档更新
- 更新 README.md 中的 AI 助手列表
- 更新安装说明

## [0.1.8] - 2025-06-03

### 同步原版
- 同步原版 [v0.1.8](https://github.com/github/spec-kit/releases/tag/v0.1.8)

### 🚀 新增功能
- **Qwen Code 支持**: 新增通义千问 Qwen Code CLI 支持
- **OpenCode 支持**: 新增 OpenCode CLI 支持

### 🔧 技术更新
- **模板系统**: 改进模板下载机制
  - 支持 GitHub Releases API
  - 改进错误处理和重试逻辑

## [0.1.7] - 2025-05-27

### 同步原版
- 同步原版 [v0.1.7](https://github.com/github/spec-kit/releases/tag/v0.1.7)

### 🚀 新增功能
- **Cursor 支持**: 新增 Cursor AI 助手支持
  - CLI 工具: `cursor-agent`
  - 命令目录: `.cursor/commands/`

### 📝 文档更新
- 更新 README.md 中的 AI 助手列表
- 更新 CLAUDE.md 项目说明

## [0.1.6] - 2025-05-20

### 同步原版
- 同步原版 [v0.1.6](https://github.com/github/spec-kit/releases/tag/v0.1.6)

### 🚀 新增功能
- **Gemini CLI 支持**: 新增 Google Gemini CLI 支持
  - 命令目录: `.gemini/commands/`
  - 配置格式: TOML

### 🔧 技术更新
- **模板系统**: 改进模板处理
  - 支持多种配置格式 (Markdown, TOML)
  - 改进路径处理

## [0.1.5] - 2025-05-13

### 同步原版
- 同步原版 [v0.1.5](https://github.com/github/spec-kit/releases/tag/v0.1.5)

### 🚀 新增功能
- **GitHub Copilot 支持**: 新增 GitHub Copilot AI 助手支持
  - 命令目录: `.github/prompts/`
  - IDE 集成模式

### 📝 文档更新
- 新增 AI 助手选择指南
- 更新项目模板说明

## [0.1.4] - 2025-05-06

### 同步原版
- 同步原版 [v0.1.4](https://github.com/github/spec-kit/releases/tag/v0.1.4)

### 🚀 新增功能
- **Claude Code 支持**: 新增 Anthropic Claude Code CLI 支持
  - 命令目录: `.claude/commands/`
  - 配置格式: Markdown

### 🔧 技术更新
- **CLI 重构**: 改进命令行界面
  - 使用 Typer 框架
  - 改进帮助文本
  - 新增进度显示

## [0.1.3] - 2025-04-29

### 同步原版
- 同步原版 [v0.1.3](https://github.com/github/spec-kit/releases/tag/v0.1.3)

### 🚀 新增功能
- **模板系统**: 新增项目模板支持
  - 从 GitHub Releases 下载模板
  - 支持多种 AI 助手模板

### 📝 文档更新
- 新增 README.md 中文版
- 新增 CLAUDE.md 项目说明

## [0.1.2] - 2025-04-22

### 同步原版
- 同步原版 [v0.1.2](https://github.com/github/spec-kit/releases/tag/v0.1.2)

### 🚀 新增功能
- **初始化命令**: 新增 `specify-cn init` 命令
  - 支持项目名称和路径参数
  - 支持 AI 助手选择
  - 支持 Git 初始化选项

## [0.1.1] - 2025-04-15

### 同步原版
- 同步原版 [v0.1.1](https://github.com/github/spec-kit/releases/tag/v0.1.1)

### 🚀 新增功能
- **CLI 基础**: 建立命令行界面基础
  - 使用 Typer 和 Rich 库
  - 支持命令行参数和选项

## [0.1.0] - 2025-04-08

### 🎉 初始发布
- **项目创建**: 创建 Spec Kit CN 项目
  - 从 GitHub Spec Kit 复刻
  - 中文本地化适配
  - 独立维护和发布

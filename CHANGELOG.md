# 变更日志

本项目的重要变更将记录在此文件中。

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [0.0.62] - 2025-10-13

### 同步原版
- 同步原版 [v0.0.62](https://github.com/github/spec-kit/releases/tag/v0.0.62)
- 对应原版提交：`e65660f...`（完整包含v0.0.58到v0.0.62的所有变更）

### 核心功能更新
- **Agent配置系统重构**：从简单的AI_CHOICES改为结构化的AGENT_CONFIG，支持更详细的代理元数据管理
- **新增CodeBuddy AI助手支持**：完整的CLI工具集成，支持命令和配置文件生成
- **Cursor名称标准化**：从`cursor`更改为`cursor-agent`，确保与实际CLI工具名称一致
- **忽略文件自动验证功能**：在implement命令中新增智能项目设置验证，支持多种技术栈的忽略文件自动创建
- **Git错误高亮显示**：Git初始化失败时现在会显示详细的错误面板，包含具体的错误信息和修复建议
- **TOML输出转义修复**：修复Gemini CLI中反斜杠转义问题，确保配置文件格式正确

### 中文本地化更新
- **CLI输出完全中文化**：所有错误消息、状态提示、交互界面均保持中文显示
- **模板文件中文翻译**：implement.md新增的忽略文件验证功能完全中文化
- **AGENTS.md文档更新**：同步最新的代理集成指南，保持技术准确性的同时提供中文说明
- **品牌标识一致性**：保持中文版特有的品牌标识和命令名称（specify-cn）

### 构建和脚本更新
- **构建脚本完全同步**：所有bash和PowerShell脚本与原版保持同步
- **代理上下文更新工具**：支持新增的CodeBuddy和修正后的cursor-agent
- **VS Code设置模板**：同步最新的配置选项和快捷键支持

### Bug修复
- **🐛 修复speckit.前缀缺失问题**：修复了`.github/workflows/scripts/create-release-packages.sh`中命令文件生成时缺少`speckit.`前缀的关键问题，确保所有AI助手的命令文件正确生成（如`speckit.analyze.md`而非`analyze.md`）
- **命令兼容性恢复**：修复后用户可以正常使用`/speckit.constitution`、`/speckit.specify`等命令，与CLI显示的命令提示完全匹配

### 已知问题
- 无重大已知问题，所有功能正常工作

## [0.0.58] - 2025-01-09

### 同步原版
- 同步原版 [v0.0.58](https://github.com/github/spec-kit/releases/tag/v0.0.58)
- 对应原版提交：多个提交（详见git log v0.0.55..v0.0.58）
- 主要提交：
  - `de1db34` - feat(agent): Added Amazon Q Developer CLI Integration
  - `af2b14e` - Add escaping guidelines to command templates
  - `ba8144d` - Package up VS Code settings for Copilot
  - `4dc4887` - Update templates/tasks-template.md
  - `a6be9be` - Update checklist.md

### 新增功能
- ✨ Amazon Q Developer CLI 支持（新增 AI 助手）
- ✨ Checklist 功能：新增 `/speckit.checklist` 命令用于需求质量验证
- ✨ VS Code 设置模板：为 GitHub Copilot 用户提供配置支持
- 🔧 命令模板转义指南：处理特殊字符的标准化方法

### 中文本地化更新
- 完整中文翻译所有新增内容
- 优化现有模板的中文表达
- 更新 CLI 输出中文界面
- 本地化 checklist-template.md 模板

### 已知问题
- Amazon Q Developer CLI 不支持自定义参数（原版限制）

## [0.0.55] - 2025-10-02

### 同步原版
- 同步原版 [v0.0.55](https://github.com/github/spec-kit/releases/tag/v0.0.55)
- 对应原版提交：`e3b456c` (包含13个功能增强和bug修复提交)
- 主要提交：
  - `68eba52` - feat: support 'specify init .' for current directory initialization
  - `721ecc9` - feat: Add emacs-style up/down keys
  - `6a3e81f` - docs: fix the paths of generated files (moved under a `.specify/` folder)
  - `b2f749e` - fix: add UTF-8 encoding to file read/write operations in update-agent-context.ps1
  - `cc75a22` - Update URLs to Contributing and Support Guides in Docs

### 新增功能
- **新增 `specify init .` 支持**：可以使用 `.` 作为当前目录初始化的简写，等同于 `--here` 标志但更直观
- **Emacs 风格快捷键**：添加 Ctrl+P (上) 和 Ctrl+N (下) 键盘支持
- **项目文件结构更新**：生成的文件现在统一放在 `.specify/` 目录下

### 修复
- **UTF-8 编码支持**：修复 PowerShell 脚本中的文件读写编码问题
- **文档链接修正**：更新贡献指南和支持指南的链接地址

### 中文本地化更新
- 更新 README.md 中的命令行参数说明和示例
- 完善所有新增功能的使用示例和中文说明
- 更新项目结构描述，反映 `.specify/` 目录变更

### 已知问题
- 无

## [未发布]

### 新增
- 初始中文版本发布

### 变更
- 将所有文档从英文翻译为中文
- 更新命令引用从`specify`改为`specify-cn`

### 修复
- 修复文档中的链接引用

## [1.0.0] - 2024-09-16

### 新增
- 初始版本发布

## [1.0.54] - 2025-09-28

### 同步原版
- 同步原版 [v0.0.54](https://github.com/github/spec-kit/releases/tag/v0.0.54)
- 对应原版提交：`1c0e7d14d5d5388fbb98b7856ce9f486cc273997`

### 中文本地化更新
- 更新 README.md 中的版本信息和原版对应关系
- 更新 `src/specify_cli/__init__.py` 文件，从原版 spec-kit 项目复制并完全本地化
- 品牌标识更新：包名 `specify-cn-cli`，命令名 `specify-cn`，GitHub 仓库 `Linfee/spec-kit-cn`
- 用户界面完全中文化：所有错误消息、状态提示、帮助文档、操作指导均已翻译为中文
- 功能完整性验证：核心 CLI 功能与原版完全对等，11 种 AI 助手支持完全一致

### 技术架构同步
- 核心代码架构：所有类和函数名称、方法签名、算法逻辑与原版保持一致
- 依赖管理：typer、rich、httpx 等依赖库版本与原版同步
- 构建配置：hatchling 构建系统配置保持同步
- AI 助手支持：Claude Code、Gemini CLI、GitHub Copilot、Cursor、Qwen Code 等 11 种助手完全支持

### 已知问题
- 无
- Spec-Driven Development方法论完整实现
- CLI工具支持
- 模板系统
- 文档生成功能

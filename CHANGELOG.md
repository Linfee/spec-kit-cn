# 变更日志

本项目的重要变更将记录在此文件中.

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/), 
并且本项目遵循[语义化版本](https://semver.org/lang/zh-CN/).

## [0.0.72] - 2025-10-19

### 同步原版
- 同步原版 [v0.0.72](https://github.com/github/spec-kit/releases/tag/v0.0.72)
- 对应原版提交: `3e85f46 Merge pull request #910 from zidoshare/create-new-feature`

### 🚀 重要功能增强
- **VS Code Settings 智能合并**: `.vscode/settings.json` 现在采用智能合并而非覆盖
  - 保留现有用户设置
  - 新增 Spec Kit 设置项
  - 嵌套对象递归合并
  - 防止意外丢失自定义 VS Code 工作区配置

- **IDE代理检查优化**: 优化 `check` 命令中的代理检测逻辑
  - 区分 CLI 和 IDE 类型的 AI 助手
  - IDE 助手跳过 CLI 检查，标记为可选
  - 更准确的工具链检测结果

### 📝 文档更新
- **README.md**: 添加 AI 助手使用说明提示
- **脚本修复**: 修复 `create-new-feature.sh` 参数解析问题
- **Agent配置**: 同步最新的AI助手配置信息

### 🔧 技术改进
- **媒体文件优化**: 减小GIF和图片文件体积
- **代码质量**: 添加类型提示和代码优化

## [0.0.69] - 2025-10-16

### 同步原版
- 同步原版 [v0.0.69](https://github.com/github/spec-kit/releases/tag/v0.0.69)
- 对应原版提交: `3b000fc Merge pull request #881 from github/localden/fixes`

### 🔥 关键品牌更新
- **CodeBuddy → CodeBuddy CLI**: 同步原版品牌名称变更
- **安装链接更新**: CodeBuddy安装地址从 `https://www.codebuddy.ai` 更新为 `https://www.codebuddy.ai/cli`
- **CLI配置同步**: 更新 `src/specify_cli/__init__.py` 中的AGENT_CONFIG

### 📝 文档格式优化
- **README标题统一**: 原版标题大小写规范化("Get started" → "Get Started")
- **项目描述更新**: 同步原版新的项目描述文本
- **AGENTS.md完整同步**: 包含最新的AI助手集成指南

### 🌐 新增语言支持
- **编程语言扩展**: Ruby, PHP, Rust, Kotlin, C, C++
- **模板系统增强**: 支持更多编程语言的项目模板

### 🔧 功能修复
- **命令格式化修正**: 修复代理上下文文件中的命令格式问题
- **参数处理优化**: 改进CLI参数处理逻辑
- **脚本同步**: 完全同步 `scripts/` 目录的所有构建脚本

### 质量验证
- **CLI功能测试**: 验证 `specify-cn --help` 和 `specify-cn check` 正常工作
- **CodeBuddy CLI检测**: 确认工具检查中正确显示"CodeBuddy CLI"
- **版本信息验证**: 所有版本号已更新至v0.0.69

## [0.0.63] - 2025-10-14

### 同步原版
- 同步原版 [v0.0.63](https://github.com/github/spec-kit/releases/tag/v0.0.63)
- 对应原版提交: `e7bb98de42ef10fc36f2b2f01f17a7c70b92d29a`

### 核心功能修复
- **🔧 CodeBuddy路径修复**: 修复CodeBuddy AI助手的配置文件路径从 `.codebuddy/rules/specify-rules.md` 更改为根目录的 `CODEBUDDY.md`
- **脚本同步更新**: 同步 `scripts/bash/update-agent-context.sh` 和 `scripts/powershell/update-agent-context.ps1`
- **Agent集成优化**: 确保CodeBuddy助手能够正确找到和读取配置文件

### 文档更新
- **📚 README.md全面同步**: 与原版v0.0.63保持完全一致
- **版本信息更新**: 对应原版版本从v0.0.62更新至v0.0.63
- **新增升级命令**: 添加 `uv tool install specify-cn-cli --force` 升级说明
- **流程文档完善**: 新增STEP 6详细说明 `/speckit.tasks` 任务分解流程
- **命令结构优化**: 斜杠命令重新分类为"核心命令"和"可选命令"
- **步骤编号调整**: 原STEP 6调整为STEP 7, 插入新的任务分解步骤

### 新增内容
- **🆕 任务分解流程**: 详细的 `/speckit.tasks` 命令说明, 包含: 
  - 按用户故事组织的任务分解
  - 依赖管理和并行执行标记
  - 文件路径规范和TDD结构
  - 检查点验证机制
- **🆕 升级指导**: 提供明确的工具升级命令和说明
- **🆕 命令分类**: 核心命令(5个)和可选命令(3个)的清晰分类

### 技术同步
- **脚本文件同步**: Bash和PowerShell脚本与原版完全同步
- **路径配置修复**: CodeBuddy配置文件路径简化, 提高可访问性
- **CLI功能验证**: 所有AI助手集成功能正常工作

### Bug修复
- **🐛 修复CodeBuddy集成问题**: 解决因路径错误导致的CodeBuddy助手无法正常工作的问题
- **🐛 文档一致性修复**: 确保中文版文档与原版功能描述完全一致

### 已知问题
- 无重大已知问题, 所有功能正常工作

## [0.0.62] - 2025-10-13

### 同步原版
- 同步原版 [v0.0.62](https://github.com/github/spec-kit/releases/tag/v0.0.62)
- 对应原版提交: `e65660f...`(完整包含v0.0.58到v0.0.62的所有变更)

### 核心功能更新
- **Agent配置系统重构**: 从简单的AI_CHOICES改为结构化的AGENT_CONFIG, 支持更详细的代理元数据管理
- **新增CodeBuddy AI助手支持**: 完整的CLI工具集成, 支持命令和配置文件生成
- **Cursor名称标准化**: 从`cursor`更改为`cursor-agent`, 确保与实际CLI工具名称一致
- **忽略文件自动验证功能**: 在implement命令中新增智能项目设置验证, 支持多种技术栈的忽略文件自动创建
- **Git错误高亮显示**: Git初始化失败时现在会显示详细的错误面板, 包含具体的错误信息和修复建议
- **TOML输出转义修复**: 修复Gemini CLI中反斜杠转义问题, 确保配置文件格式正确

### 中文本地化更新
- **CLI输出完全中文化**: 所有错误消息、状态提示、交互界面均保持中文显示
- **模板文件中文翻译**: implement.md新增的忽略文件验证功能完全中文化
- **AGENTS.md文档更新**: 同步最新的代理集成指南, 保持技术准确性的同时提供中文说明
- **品牌标识一致性**: 保持中文版特有的品牌标识和命令名称(specify-cn)

### 构建和脚本更新
- **构建脚本完全同步**: 所有bash和PowerShell脚本与原版保持同步
- **代理上下文更新工具**: 支持新增的CodeBuddy和修正后的cursor-agent
- **VS Code设置模板**: 同步最新的配置选项和快捷键支持

### Bug修复
- **🐛 修复speckit.前缀缺失问题**: 修复了`.github/workflows/scripts/create-release-packages.sh`中命令文件生成时缺少`speckit.`前缀的关键问题, 确保所有AI助手的命令文件正确生成(如`speckit.analyze.md`而非`analyze.md`)
- **命令兼容性恢复**: 修复后用户可以正常使用`/speckit.constitution`、`/speckit.specify`等命令, 与CLI显示的命令提示完全匹配

### 已知问题
- 无重大已知问题, 所有功能正常工作

## [0.0.58] - 2025-01-09

### 同步原版
- 同步原版 [v0.0.58](https://github.com/github/spec-kit/releases/tag/v0.0.58)
- 对应原版提交: 多个提交(详见git log v0.0.55..v0.0.58)
- 主要提交: 
  - `de1db34` - feat(agent): Added Amazon Q Developer CLI Integration
  - `af2b14e` - Add escaping guidelines to command templates
  - `ba8144d` - Package up VS Code settings for Copilot
  - `4dc4887` - Update templates/tasks-template.md
  - `a6be9be` - Update checklist.md

### 新增功能
- ✨ Amazon Q Developer CLI 支持(新增 AI 助手)
- ✨ Checklist 功能: 新增 `/speckit.checklist` 命令用于需求质量验证
- ✨ VS Code 设置模板: 为 GitHub Copilot 用户提供配置支持
- 🔧 命令模板转义指南: 处理特殊字符的标准化方法

### 中文本地化更新
- 完整中文翻译所有新增内容
- 优化现有模板的中文表达
- 更新 CLI 输出中文界面
- 本地化 checklist-template.md 模板

### 已知问题
- Amazon Q Developer CLI 不支持自定义参数(原版限制)

## [0.0.55] - 2025-10-02

### 同步原版
- 同步原版 [v0.0.55](https://github.com/github/spec-kit/releases/tag/v0.0.55)
- 对应原版提交: `e3b456c` (包含13个功能增强和bug修复提交)
- 主要提交: 
  - `68eba52` - feat: support 'specify init .' for current directory initialization
  - `721ecc9` - feat: Add emacs-style up/down keys
  - `6a3e81f` - docs: fix the paths of generated files (moved under a `.specify/` folder)
  - `b2f749e` - fix: add UTF-8 encoding to file read/write operations in update-agent-context.ps1
  - `cc75a22` - Update URLs to Contributing and Support Guides in Docs

### 新增功能
- **新增 `specify init .` 支持**: 可以使用 `.` 作为当前目录初始化的简写, 等同于 `--here` 标志但更直观
- **Emacs 风格快捷键**: 添加 Ctrl+P (上) 和 Ctrl+N (下) 键盘支持
- **项目文件结构更新**: 生成的文件现在统一放在 `.specify/` 目录下

### 修复
- **UTF-8 编码支持**: 修复 PowerShell 脚本中的文件读写编码问题
- **文档链接修正**: 更新贡献指南和支持指南的链接地址

### 中文本地化更新
- 更新 README.md 中的命令行参数说明和示例
- 完善所有新增功能的使用示例和中文说明
- 更新项目结构描述, 反映 `.specify/` 目录变更

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
- 对应原版提交: `1c0e7d14d5d5388fbb98b7856ce9f486cc273997`

### 中文本地化更新
- 更新 README.md 中的版本信息和原版对应关系
- 更新 `src/specify_cli/__init__.py` 文件, 从原版 spec-kit 项目复制并完全本地化
- 品牌标识更新: 包名 `specify-cn-cli`, 命令名 `specify-cn`, GitHub 仓库 `Linfee/spec-kit-cn`
- 用户界面完全中文化: 所有错误消息、状态提示、帮助文档、操作指导均已翻译为中文
- 功能完整性验证: 核心 CLI 功能与原版完全对等, 11 种 AI 助手支持完全一致

### 技术架构同步
- 核心代码架构: 所有类和函数名称、方法签名、算法逻辑与原版保持一致
- 依赖管理: typer、rich、httpx 等依赖库版本与原版同步
- 构建配置: hatchling 构建系统配置保持同步
- AI 助手支持: Claude Code、Gemini CLI、GitHub Copilot、Cursor、Qwen Code 等 11 种助手完全支持

### 已知问题
- 无
- Spec-Driven Development方法论完整实现
- CLI工具支持
- 模板系统
- 文档生成功能

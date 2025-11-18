# Spec Kit CN

> **项目性质**: GitHub Spec Kit 的官方中文复刻版本, 仅做中文本地化, 不开发新特性

## 项目标识

### 核心信息
- **项目名称**: Spec Kit CN
- **原版项目**: [github/spec-kit](https://github.com/github/spec-kit)
- **当前项目**: [linfee/spec-kit-cn](https://github.com/linfee/spec-kit-cn)
- **包名**: `specify-cn`(原版: `specify-cli` 不做更改)
- **命令**: `specify-cn`(原版: `specify`)
- **文档语言**: 中文(原版: 英文)

### 核心原则
1. **功能对等**: 与原版保持完全一致的功能, 不添加新特性
2. **仅做本地化**: 专注于中文翻译和本地化适配
3. **同步优先**: 定期与原版同步, 保持技术更新

### 关键差异
| 项目     | 原版            | 中文版           |
| -------- | --------------- | ---------------- |
| 包名     | `specify-cli`   | `specify-cn-cli` |
| 命令     | `specify`       | `specify-cn`     |
| 文档     | 英文            | 中文             |
| 功能     | 持续开发        | 仅做本地化       |
| 斜杠命令 | `/speckit.plan` | 保持一致         |

---

## 快速参考

### 常用命令
```bash
# 开发环境
uv sync                              # 同步依赖
uv run specify-cn --help             # 运行 CLI
uv run specify-cn check              # 检查工具链

# 测试功能
specify-cn init test-project --ai claude    # 测试项目初始化
specify-cn --help | grep -E "中文|Spec Kit CN"  # 验证中文输出
```

### 自动化翻译工作流
```bash
# 一键自动化翻译(推荐)
/translation-auto      # 全自动翻译流程

# 原版更新处理
/translation-sync      # 智能同步原版更新

# 质量管理
/translation-qa        # 质量保证检查
/translation-fix       # 智能修复问题

# 人工审核
/translation-review    # 人工审核(已存在)
/translation-workflow  # 工作流指南
```

### 项目目录结构
```
项目根目录/
├── src/specify_cli/           # 核心代码(必须同步)
├── templates/                 # 模板文件(需要本地化)
├── scripts/                   # 构建脚本(完全同步, 不翻译)
├── .devcontainer/             # 开发容器配置(完全同步, 不翻译)
├── .github/                   # CI配置(谨慎同步, 不翻译)
├── docs/                     # 项目文档(需要本地化)
├── memory/                    # 项目章程(需要本地化)
├── spec-kit/                 # 原版项目(.gitignore)
├── .claude/commands/         # 翻译自动化命令
├── TERMINOLOGY.md            # 术语表
├── TRANSLATION_STANDARDS.md  # 翻译标准
├── CHANGELOG.md              # 版本记录(独立维护)
└── CLAUDE.md                 # 项目记忆文件
```

### 文件分类与处理策略
| 类别       | 目录/文件                     | 同步策略 | 本地化策略          |
| ---------- | ----------------------------- | -------- | ------------------- |
| 核心代码   | `src/specify_cli/`            | 必须同步 | CLI输出信息需要中文 |
| 模板系统   | `templates/`                  | 结构同步 | 完全中文翻译        |
| 构建脚本   | `scripts/`                    | 完全同步 | 不翻译              |
| 开发环境   | `.devcontainer/`              | 完全同步 | 不翻译              |
| CI配置     | `.github/`                    | 谨慎同步 | 不翻译              |
| 项目文档   | `docs/`, `README.md`          | 结构参考 | 完全中文翻译        |
| 项目章程   | `memory/constitution.md`      | 结构同步 | 完全中文翻译        |
| 原版追踪   | `spec-kit/`                   | 不提交   | 不适用              |
| 项目描述   | `AGENTS.md`                   | 完全同步 | 不翻译              |

---

## 技术架构

### 核心组件

#### Specify CLI 结构 (`src/specify_cli/__init__.py`)
**主要类和函数**: 
- `StepTracker` - 分层步骤进度跟踪 UI 组件
- `select_with_arrows()` - 交互式箭头键选择界面
- `download_template_from_github()` - GitHub releases 模板下载
- `download_and_extract_template()` - 模板下载和解压
- `init()` - 主要项目初始化命令
- `check()` - 工具可用性检查

**关键特性**: 
- 支持多种 AI 编码助手
- 实时进度跟踪和树形显示
- 跨平台支持(Linux/macOS/Windows)
- 自动脚本权限设置(POSIX)
- Git 仓库自动初始化

### 同步策略
**核心策略**: 采用"**核心同步, 界面本地化**"的策略, 确保与原版功能完全对等的同时, 为中文用户提供友好的母语界面.

#### 必须同步的内容
- ✅ **所有类和函数名称**
- ✅ **方法签名和参数**: 完全与原版一致, 确保功能对等
- ✅ **核心算法逻辑**: 模板下载、解压、Git初始化等核心流程
- ✅ **依赖库和版本**: typer、rich、httpx 等依赖保持同步
- ✅ **AI助手支持**: 所有AI助手的支持逻辑完全一致
- ✅ **构建配置**: hatchling 构建系统保持同步

#### 需要本地化的内容
- 📝 **品牌标识**: 包名、命令名、GitHub仓库、横幅标语
- 📝 **用户界面文本**: 错误消息、状态提示、交互界面
- 📝 **帮助文档**: 使用说明、操作指导、调试信息
- 📝 **输出信息**: CLI 输出、进度显示、工具检查结果

### AI 助手支持
| 助手           | CLI 工具       | 目录格式               | 命令格式 | 类型   |
| -------------- | -------------- | ---------------------- | -------- | ------ |
| Claude Code    | `claude`       | `.claude/commands/`    | Markdown | CLI    |
| Gemini CLI     | `gemini`       | `.gemini/commands/`    | TOML     | CLI    |
| GitHub Copilot | 无(IDE 集成) | `.github/prompts/`     | Markdown | IDE    |
| Cursor         | `cursor-agent` | `.cursor/commands/`    | Markdown | CLI    |
| Qwen Code      | `qwen`         | `.qwen/commands/`      | TOML     | CLI    |
| opencode       | `opencode`     | `.opencode/command/`   | Markdown | CLI    |
| Windsurf       | 无(IDE 集成) | `.windsurf/workflows/` | Markdown | IDE    |
| Codex          | `codex`        | `.codex/`              | Markdown | CLI    |
| Kilocode       | `kilocode`     | `.kilocode/`           | Markdown | CLI    |
| Auggie         | `auggie`       | `.auggie/`             | Markdown | CLI    |
| Amazon Q Developer CLI | `q` | `.amazonq/prompts/` | Markdown | CLI    |

---

## 开发环境配置 (.devcontainer/)

### Devcontainer 概述
`.devcontainer/` 目录是 v0.0.78 新增的开发容器配置，提供完整的开发环境自动化设置。

### 配置文件结构
```
.devcontainer/
├── devcontainer.json     # 主配置文件，定义容器环境和工具
└── post-create.sh       # 容器创建后自动执行脚本
```

### 核心功能
- **预配置开发环境**: Python 3.13 + uv 包管理器
- **AI助手自动安装**: 自动安装所有支持的AI编码助手
- **VS Code集成**: 预装必要的扩展和设置
- **多语言支持**: Node.js, .NET, Git 等开发工具
- **端口转发**: 8080端口用于文档站点预览

### 包含的AI助手
- GitHub Copilot CLI
- Claude Code CLI
- Codex CLI
- Gemini CLI
- Auggie CLI
- Qwen Code CLI
- OpenCode CLI
- Amazon Q Developer CLI
- CodeBuddy CLI

### 使用方式
1. 在 VS Code 中打开项目
2. 提示"在容器中重新打开"时选择确定
3. 等待容器构建和脚本执行完成
4. 所有AI助手将自动安装并可用

### 同步策略
- **完全同步**: 与原版保持100%一致
- **不翻译**: 所有配置文件保持英文
- **自动更新**: 随原版版本同步更新

---

## 维护工作流程

### 自动化翻译工作流

#### 推荐使用流程
1. **首次设置**: `/translation-auto` 执行完整翻译
2. **原版更新**: `/translation-sync` 智能同步更新
3. **日常维护**: `/translation-qa` + `/translation-fix` 质量管理
4. **发布检查**: `/translation-review` 最终审核

#### 工作流特性
- **90%+ 自动化**: 大幅减少人工干预
- **智能检测**: 自动识别翻译需求和质量问题
- **增量更新**: 仅处理变更内容, 保持现有翻译稳定
- **质量保证**: 多层检查确保翻译质量
- **安全机制**: 分支操作、自动备份、渐进式发布

### 版本同步策略

#### 基本原则
- **版本号**: 本项目tag单独迭代, 不需要和原版同步
- **功能同步**: 定期从上游合并, 不添加新功能
- **发布节奏**: 跟随原版发布, 不独立发布新功能

#### 同步机制
**spec-kit 目录工作机制**: 
```
项目根目录/
├── spec-kit/              # 原版项目目录(.gitignore)
│   ├── .git/             # 原版 git 历史
│   ├── src/              # 原版源代码
│   ├── templates/        # 原版模板
│   └── ...
├── .gitignore            # 忽略 spec-kit/ 目录
└── ...                   # 本项目文件
```

**同步工作流程**:
1. 检查当前版本对应的原版 tag/commit
2. 在 `spec-kit/` 目录检出对应原版版本
3. 完全同步scripts: `rsync -avp spec-kit/scripts/ scripts/`
4. **关键步骤**: 同步AGENTS.md: `cp spec-kit/AGENTS.md AGENTS.md`
5. 同步开发环境配置: `rsync -avp spec-kit/.devcontainer/ .devcontainer/`
6. 执行自动化翻译: `/translation-sync`
7. 更新 CHANGELOG.md 记录同步信息

#### AGENTS.md 比对的重要性
- 原版 `AGENTS.md` 包含最新的 AI 助手支持信息和技术细节
- 每次同步时必须比对, 确保项目记忆的准确性
- 重点关注: 新助手支持、版本管理要求、集成步骤变化

### 版本管理要求
- **重要**: 任何对 `src/specify_cli/__init__.py` 的修改都需要: 
  - 更新 `pyproject.toml` 中的版本号
  - 在 `CHANGELOG.md` 中添加相应条目
  - 同步原版更新时记录对应的原版提交信息

### CHANGELOG 维护
**维护原则**: 
- `CHANGELOG.md` 由本项目独立维护, 不与原版同步
- 记录每个版本同步的原版信息和中文本地化更新

---

## 翻译标准和质量保证

### 翻译标准文件
- **@TRANSLATION_STANDARDS.md**: 详细的翻译标准和规范
- **@TERMINOLOGY.md**: 标准术语表, 确保翻译一致性

### 核心翻译原则
- **用户导向**: 面向中文开发者, 翻译用户界面和文档
- **技术保留**: 代码层面保持英文, 确保技术准确性
- **功能对等**: 翻译后功能必须与原版完全一致
- **术语一致**: 严格遵循术语表, 保持翻译一致性

### 本地化范围
**需要完全中文本地化的内容**: 
- 用户文档: `README.md`、`spec-driven.md`、`docs/` 目录
- 模板系统: `templates/` 和 `templates/commands/` 目录下的所有文件
- 项目章程: `memory/constitution.md`(包括占位符和说明文本)
- CLI 界面: `src/specify_cli/` 中的输出信息、帮助文本、错误消息

**保持英文不翻译的内容**:
- 构建脚本: `scripts/` 目录(完全同步原版)
- 开发环境: `.devcontainer/` 目录(完全同步原版)
- 媒体资源: `media/` 目录(完全同步原版)
- CI配置: `.github/` 目录(谨慎同步, 不翻译)
- 代码层面: 变量名、函数名、类名等标识符
- 章程占位符: 如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]` 等(保持原格式)

### 质量保证机制
- **自动化检查**: `/translation-qa` 进行全面质量检查
- **智能修复**: `/translation-fix` 自动修复常见问题
- **人工审核**: `/translation-review` 最终质量把关
- **持续改进**: 基于用户反馈持续优化翻译质量

---

## 打包发布

**发布触发**: 推送格式为 `v*.*.*` 的 tag 时自动触发 GitHub Actions, push 到 main 分支不会触发.

**版本规则**: Tag 使用 `v0.0.85` 格式, 生成的包名去掉 v 前缀为 `spec-kit-template-*-0.0.85.zip`.

**发布命令**: `git tag v0.0.85 && git push origin v0.0.85` 即可自动创建包含 24 个包的完整 release.

---

## 紧急情况处理

### 常见问题解决方案
1. **同步冲突**: 优先保留原版功能, 仅在本地化内容上保留修改
2. **版本不一致**: 检查 `pyproject.toml` 和 `CHANGELOG.md`
3. **功能异常**: 对比原版项目, 确认是否为同步问题
4. **翻译质量问题**: 使用 `/translation-fix` 智能修复

---

## 参考链接

- **原版项目**: [github/spec-kit](https://github.com/github/spec-kit)
- **原版文档**: [spec-kit/docs](https://github.com/github/spec-kit/tree/main/docs)
- **原版项目标书**: [spec-kit/AGENTS.md](https://github.com/github/spec-kit/blob/main/AGENTS.md)
- **GitHub Releases**: [spec-kit/releases](https://github.com/github/spec-kit/releases)
- **中文版仓库**: [linfee/spec-kit-cn](https://github.com/linfee/spec-kit-cn)
- **翻译标准**: @TRANSLATION_STANDARDS.md
- **术语表**: @TERMINOLOGY.md

## 其他Rule

- 原版项目位于`./spec-kit`, 如果没有, 就将它克隆到这个位置, 始终从该位置访问原版文件
- 同步src下脚本文件时, 务必将repo_name和repo_user替换为本项目的
- 记得在提交代码前更新README.md中的版本信息

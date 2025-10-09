# Spec Kit CN

> **项目性质**：GitHub Spec Kit 的官方中文复刻版本，仅做中文本地化，不开发新特性

## 项目标识

### 核心信息
- **项目名称**：Spec Kit CN
- **原版项目**：[github/spec-kit](https://github.com/github/spec-kit)
- **当前项目**：[linfee/spec-kit-cn](https://github.com/linfee/spec-kit-cn)
- **包名**：`specify-cn`（原版：`specify-cli` 不做更改）
- **命令**：`specify-cn`（原版：`specify`）
- **文档语言**：中文（原版：英文）

### 核心原则
1. **功能对等**：与原版保持完全一致的功能，不添加新特性
2. **仅做本地化**：专注于中文翻译和本地化适配
3. **同步优先**：定期与原版同步，保持技术更新

### 关键差异
| 项目 | 原版          | 中文版       |
| ---- | ------------- | ------------ |
| 包名 | `specify-cli` | `specify-cn-cli` |
| 命令 | `specify`     | `specify-cn` |
| 文档 | 英文          | 中文         |
| 功能 | 持续开发      | 仅做本地化   |

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

### 项目目录结构
```
项目根目录/
├── src/specify_cli/           # 核心代码（必须同步）
├── templates/                 # 模板文件（需要本地化）
│   ├── 核心模板/             # 需要中文翻译
│   └── commands/             # 需要中文翻译
├── scripts/                   # 构建脚本（完全同步，不翻译）
├── .github/                   # CI配置（谨慎同步，不翻译）
├── docs/                     # 项目文档（需要本地化）
├── memory/                    # 项目章程（需要本地化）
│   └── constitution.md       # 项目章程文件
├── spec-kit/                 # 原版项目（.gitignore）
├── CHANGELOG.md              # 版本记录（独立维护）
└── CLAUDE.md                 # 项目记忆文件
```

### 文件分类与处理策略
| 类别     | 目录/文件                     | 同步策略 | 本地化策略          |
| -------- | ----------------------------- | -------- | ------------------- |
| 核心代码 | `src/specify_cli/`            | 必须同步 | CLI输出信息需要中文 |
| 模板系统 | `templates/`                  | 结构同步 | 完全中文翻译        |
| 构建脚本 | `scripts/`                    | 完全同步 | 不翻译              |
| CI配置   | `.github/`                    | 谨慎同步 | 不翻译              |
| 项目文档 | `docs/`, `README.md`          | 结构参考 | 完全中文翻译        |
| 项目章程 | `memory/constitution.md`      | 结构同步 | 完全中文翻译        |
| 原版追踪 | `spec-kit/`                   | 不提交   | 不适用              |
| 项目描述 | `AGENTS.md`                   | 完全同步 | 不翻译              |

### 版本对应关系
- 当前版本：v0.0.58（查看 `pyproject.toml` 中的 `version` 字段）
- 原版版本：v0.0.58（查看 `pyproject.toml` 中的 `description` 字段）
- 同步状态：已同步至 v0.0.58（查看 `CHANGELOG.md` 中的同步记录）

### 紧急情况处理
1. **同步冲突**：优先保留原版功能，仅在本地化内容上保留修改
2. **版本不一致**：检查 `pyproject.toml` 和 `CHANGELOG.md`
3. **功能异常**：对比原版项目，确认是否为同步问题

### 版本管理要求
- **重要**：任何对 `src/specify_cli/__init__.py` 的修改都需要：
  - 更新 `pyproject.toml` 中的版本号
  - 在 `CHANGELOG.md` 中添加相应条目
  - 同步原版更新时记录对应的原版提交信息

### AGENTS.md 比对检查清单
每次同步原版版本时，必须检查：
- [ ] 新增的 AI 助手支持
- [ ] 版本管理要求变化
- [ ] 集成步骤更新
- [ ] 重要技术细节补充
- [ ] CLI 工具检查要求变化
- [ ] 目录结构变更
- [ ] 命令格式调整

---

## 技术架构

### 核心组件

#### Specify CLI 结构 (`src/specify_cli/__init__.py`)
**主要类和函数**：
- `StepTracker` - 分层步骤进度跟踪 UI 组件
- `select_with_arrows()` - 交互式箭头键选择界面
- `download_template_from_github()` - GitHub releases 模板下载
- `download_and_extract_template()` - 模板下载和解压
- `init()` - 主要项目初始化命令
- `check()` - 工具可用性检查

**关键特性**：
- 支持多种 AI 编码助手
- 实时进度跟踪和树形显示
- 跨平台支持（Linux/macOS/Windows）
- 自动脚本权限设置（POSIX）
- Git 仓库自动初始化

### `__init__.py` 同步策略

#### 同步原则
**核心策略**：采用"**核心同步，界面本地化**"的策略，确保与原版功能完全对等的同时，为中文用户提供友好的母语界面。

#### 必须同步的内容
- ✅ **所有类和函数名称**
- ✅ **方法签名和参数**：完全与原版一致，确保功能对等
- ✅ **核心算法逻辑**：模板下载、解压、Git初始化等核心流程
- ✅ **依赖库和版本**：typer、rich、httpx 等依赖保持同步, 同步更新pyproject.toml
- ✅ **AI助手支持**：所有AI助手的支持逻辑完全一致
- ✅ **构建配置**：hatchling 构建系统保持同步

#### 需要本地化的内容
- 📝 **品牌标识**：包名、命令名、GitHub仓库、横幅标语
- 📝 **用户界面文本**：错误消息、状态提示、交互界面
- 📝 **帮助文档**：使用说明、操作指导、调试信息
- 📝 **输出信息**：CLI 输出、进度显示、工具检查结果


### AI 助手支持
| 助手           | CLI 工具       | 目录格式               | 命令格式 | 类型   |
| -------------- | -------------- | ---------------------- | -------- | ------ |
| Claude Code    | `claude`       | `.claude/commands/`    | Markdown | CLI    |
| Gemini CLI     | `gemini`       | `.gemini/commands/`    | TOML     | CLI    |
| GitHub Copilot | 无（IDE 集成） | `.github/prompts/`     | Markdown | IDE    |
| Cursor         | `cursor-agent` | `.cursor/commands/`    | Markdown | CLI    |
| Qwen Code      | `qwen`         | `.qwen/commands/`      | TOML     | CLI    |
| opencode       | `opencode`     | `.opencode/command/`   | Markdown | CLI    |
| Windsurf       | 无（IDE 集成） | `.windsurf/workflows/` | Markdown | IDE    |
| Codex          | `codex`        | `.codex/`              | Markdown | CLI    |
| Kilocode       | `kilocode`     | `.kilocode/`           | Markdown | CLI    |
| Auggie         | `auggie`       | `.auggie/`             | Markdown | CLI    |
| Amazon Q Developer CLI | `q` | `.amazonq/prompts/` | Markdown | CLI    |

### 模板系统

#### 核心模板 (`templates/`)
- `spec-template.md` - 功能规范模板
- `plan-template.md` - 实施计划模板
- `tasks-template.md` - 任务生成模板
- `agent-file-template.md` - AI 助手配置模板

#### 项目章程 (`memory/`)
- `constitution.md` - 项目章程模板（v0.0.54 新增）
  - 作用：定义项目核心原则和开发标准
  - 特点：AI 开发时必须遵循的"架构DNA"
  - 格式：使用占位符模板，项目初始化时填充具体内容

#### 命令模板 (`templates/commands/`)
- `analyze.md` - 分析问题的命令
- `clarify.md` - 澄清需求的命令
- `constitution.md` - 管理项目章程的命令
- `implement.md` - 实施功能的命令
- `plan.md` - 生成实施计划的命令
- `specify.md` - 创建功能规格的命令
- `tasks.md` - 生成可执行任务的命令

### 脚本系统

#### Bash 脚本 (`scripts/bash/`)
- `check-prerequisites.sh` - 检查前置条件
- `common.sh` - 通用函数和变量
- `create-new-feature.sh` - 创建新功能分支和规范
- `setup-plan.sh` - 设置计划环境
- `update-agent-context.sh` - 更新 AI 助手上下文文件

#### PowerShell 脚本 (`scripts/powershell/`)
- 对应的 PowerShell 版本，提供相同功能

---

## 维护工作流程

### 版本同步策略

#### 基本原则
- **版本号**：本项目tag单独迭代，不需要和原版同步
- **功能同步**：定期从上游合并，不添加新功能
- **发布节奏**：跟随原版发布，不独立发布新功能

#### 同步机制

**spec-kit 目录工作机制**：
```
项目根目录/
├── spec-kit/              # 原版项目目录（.gitignore）
│   ├── .git/             # 原版 git 历史
│   ├── src/              # 原版源代码
│   ├── templates/        # 原版模板
│   └── ...
├── .gitignore            # 忽略 spec-kit/ 目录
└── ...                   # 本项目文件
```

**同步工作流程**：
1. 检查当前版本对应的原版 tag/commit
2. 在 `spec-kit/` 目录检出对应原版版本
3. 始终完全同步scripts, 使用命令`rsync -avp spec-kit/scripts/ scripts/`
4. **关键步骤**：将原版 `AGENTS.md` 拷贝到当前项目，比对项目记忆是否有缺失并补充, 使用命令`cp spec-kit/AGENTS.md AGENTS.md`
5. 对比分析原版变更内容
6. 根据文件分类策略执行同步
7. 更新 CHANGELOG.md 记录同步信息

**AGENTS.md 比对的重要性**：
- 原版 `AGENTS.md` 包含最新的 AI 助手支持信息和技术细节
- 每次同步时必须比对，确保项目记忆的准确性
- 重点关注：新助手支持、版本管理要求、集成步骤变化
- 比对后及时更新 `CLAUDE.md` 中的相关内容

**新 AI 助手集成注意事项**：
- 如需添加新的 AI 助手支持，必须同步原版更新
- 需要更新的文件包括：`src/specify_cli/__init__.py`、`scripts/` 目录下脚本、`.github/` 工作流
- 参考原版 `AGENTS.md` 文件获取完整的集成步骤

### CHANGELOG 维护

**维护原则**：
- `CHANGELOG.md` 由本项目独立维护，不与原版同步
- 记录每个版本同步的原版信息和中文本地化更新

**记录格式**：
```markdown
## [0.0.17] - 2024-01-15

### 同步原版
- 同步原版 [v0.0.17](https://github.com/github/spec-kit/releases/tag/v0.0.17)
- 对应原版提交：`1c0e7d14d5d5388fbb98b7856ce9f486cc273997`

### 中文本地化更新
- 更新 README.md 中文翻译
- 修复模板文件中的中文编码问题
- 补充 CLI 帮助文本的中文版本

### 已知问题
- 无
```

### 中文本地化标准

#### 本地化范围

**需要完全中文本地化的内容**：
- 用户文档：`README.md`、`spec-driven.md`、`docs/` 目录
- 模板系统：`templates/` 和 `templates/commands/` 目录下的所有文件
- 项目章程：`memory/constitution.md`（包括占位符和说明文本）
- CLI 界面：`src/specify_cli/` 中的输出信息、帮助文本、错误消息

**保持英文不翻译的内容**：
- 构建脚本：`scripts/` 目录（完全同步原版）
- 媒体资源：`media/` 目录（完全同步原版）
- CI配置：`.github/` 目录（谨慎同步，不翻译）
- 代码层面：变量名、函数名、类名等标识符
- 章程占位符：如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]` 等（保持原格式）

#### 翻译标准

**翻译原则**：
- **用户导向**：面向中文开发者，翻译用户界面和文档
- **技术保留**：代码层面保持英文，确保技术准确性
- **功能对等**：翻译后功能必须与原版完全一致

**术语处理**：

**不翻译的英文术语**：
- CLI, API, JSON, TOML, YAML
- Git, GitHub, Repository, Branch, Commit
- Python, JavaScript, TypeScript
- Framework, Library, Package, Dependency
- Template, Script, Command, Argument
- AI 助手名称：Claude Code, Gemini CLI, GitHub Copilot, Cursor

**需要翻译的概念**：
- "Spec-Driven Development" → "规范驱动开发"
- "User Story" → "用户故事"
- "Acceptance Criteria" → "验收标准"
- "Implementation Plan" → "实施计划"
- "Code Quality" → "代码质量"
- "Feature Specification" → "功能规范"

**语言风格**：
- 使用简洁、准确的技术中文
- 避免过度口语化，保持专业性
- 句式结构清晰，避免长难句
- 统一术语使用

**中英文混排规则**：
```markdown
✅ 推荐：
- 使用 Claude Code CLI 进行开发
- 支持 JSON 格式的配置文件
- 通过 GitHub API 获取数据

❌ 避免：
- 使用Claude Code CLI进行开发
- 支持 JSON 格式的配置文件
```

**标点符号**：
- 使用中文标点（，。：；！？）
- 英文术语后使用英文标点
- 代码示例中使用英文标点

**品牌处理**：
- GitHub → GitHub（不翻译）
- Claude Code → Claude Code（不翻译）
- Spec Kit → Spec Kit（不翻译，可加注"规范工具包"）
- 版本号保持原样（v0.0.17）

---

## 质量保证

### 翻译质量检查清单

翻译完成后必须检查：
- [ ] 术语使用是否一致
- [ ] 中英文混排是否恰当
- [ ] 技术准确性是否保持
- [ ] 语句是否通顺易懂
- [ ] 格式是否统一规范
- [ ] 链接和引用是否正确
- [ ] 代码示例是否保持原样
- [ ] 与原版功能是否完全一致

### 功能一致性检查

**必须保持一致**：
- 核心功能和 API
- 项目结构和文件组织
- 支持的 AI 助手列表
- 模板和命令的工作流

**允许差异**：
- 包名和命令名（specify-cn vs specify）
- 文档语言（中文 vs 英文）
- GitHub releases 下载源
- 默认配置和选项

### 代码质量检查

由于是复刻项目，重点关注：
- 测试基本功能
- 检查模板文件是否包含中文
- 验证 CLI 输出是否正确本地化
- 确保同步后的功能完整性

---

## 附录

### 术语表

| 英文                    | 中文         | 说明                   |
| ----------------------- | ------------ | ---------------------- |
| Spec-Driven Development | 规范驱动开发 | SDD 方法论             |
| User Story              | 用户故事     | 需求描述方式           |
| Acceptance Criteria     | 验收标准     | 功能完成条件           |
| Implementation Plan     | 实施计划     | 开发执行方案           |
| Feature Specification   | 功能规范     | 功能详细说明           |
| CLI                     | CLI          | 命令行界面（不翻译）   |
| API                     | API          | 应用程序接口（不翻译） |
| Template                | 模板         | 项目初始化模板         |


### 文件模板

**新版本同步记录模板**：
```markdown
## [x.x.x] - YYYY-MM-DD

### 同步原版
- 同步原版 [v.x.x](链接)
- 对应原版提交：`commit-hash`

### 中文本地化更新
- [具体的本地化更新内容]

### 已知问题
- [已知问题和解决方案]
```

### 参考链接

- **原版项目**：[github/spec-kit](https://github.com/github/spec-kit)
- **原版文档**：[spec-kit/docs](https://github.com/github/spec-kit/tree/main/docs)
- **原版 AGENTS.md**：[spec-kit/AGENTS.md](https://github.com/github/spec-kit/blob/main/AGENTS.md)
- **GitHub Releases**：[spec-kit/releases](https://github.com/github/spec-kit/releases)
- **中文版仓库**：[linfee/spec-kit-cn](https://github.com/linfee/spec-kit-cn)

---

## 文档维护说明

本文档是 Spec Kit CN 项目的核心记忆文件，用于指导 Claude Code 进行项目维护。请确保：

1. **及时更新**：同步原版更新后及时更新相关内容
2. **保持准确**：所有命令、路径、版本号必须准确
3. **结构清晰**：维护良好的文档结构，便于快速查找
4. **内容完整**：确保所有重要的维护信息都已包含

**最后更新**：由 Claude Code 根据项目需求重新组织和优化

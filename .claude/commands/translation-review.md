---
name: translation-review
description: "全面审核翻译质量: 对比原版、专项检查、质量评分与发布验证, 发现问题时自动衔接修复流程"
---

用户输入可以直接由代理提供或作为命令参数提供给你 - 你**必须**考虑它(如果不为空).

用户输入:
$ARGUMENTS

目标: 系统性审核翻译质量, 包含对比原版 review、关键修复点专项检查、质量评分和发布验证, 确保翻译达到发布标准.

确保本地版本号与原版严格对齐, 禁止本地版本自增.

## 第一阶段: 环境与基础验证

### 1. 验证环境准备
- 确认 spec-kit 目录存在且包含原版文件
- 确认各目录结构与原版一致: templates/, docs/, memory/, src/, scripts/, .devcontainer/, media/
- 确认 AGENTS.md 文件存在且正确引用 CLAUDE.md
- 确认 pyproject.toml 配置文件与原版结构一致

**rsync 使用安全规则**:
- **禁止同步**: `.github/` 目录(本项目有独立的工作流)
- **完全同步目录** (可使用 rsync --delete): `scripts/`, `.devcontainer/`, `tests/`, `media/`
- **翻译目录禁止 --delete** (增量合并): `templates/`, `docs/`, `memory/`, 根目录文档
- **禁止使用**: `rsync --delete` 同步翻译目录, 会永久丢失中文翻译

### 2. 关键修复点专项检查

以下检查必须全部通过才能继续后续步骤, 任何一项失败都必须优先修复:

**A. GitHub 仓库配置** (严重)
```bash
grep -n 'repo_owner = "linfee"' src/specify_cli/__init__.py   # 期望: repo_owner = "linfee"
grep -n 'repo_name = "spec-kit-cn"' src/specify_cli/__init__.py  # 期望: repo_name = "spec-kit-cn"
```

**B. CLI 命令统一性** (严重)
```bash
grep -n 'name="specify-cn"' src/specify_cli/__init__.py  # 期望: 匹配
grep -n "specify[^-]" src/specify_cli/__init__.py         # 期望: 无匹配(无遗留 specify)
grep -n "specify-cn init" src/specify_cli/__init__.py | wc -l  # 期望: >5
```

**C. 用户界面翻译** (重要)
```bash
grep -n "已准备就绪\|正在检查\|提示 : " src/specify_cli/__init__.py  # 期望: 找到中文
grep -n -E "(Tip:|Checking for|ready to use|Display version)" src/specify_cli/__init__.py  # 期望: 无匹配
```

**D. 包名一致性** (重要)
```bash
grep -n "specify-cn-cli" src/specify_cli/__init__.py  # 只在文档字符串中出现
```

**E. 技术变量保护** (严重)
```bash
grep -n "_specify_tracker_active" src/specify_cli/__init__.py  # 保持不变
grep -n "scripts_root.*specify" src/specify_cli/__init__.py    # .specify 路径不变
```

**F. 斜杠命令格式** (重要)
```bash
grep -n "/speckit\." src/specify_cli/__init__.py  # 期望: 无匹配
grep -n -E "(建立项目原则|创建基线规范|创建实施计划|生成可执行任务|执行实施)" src/specify_cli/__init__.py  # 期望: 找到中文
```

**翻译覆盖检测**:
```bash
grep -c "用户输入\|概述\|执行步骤\|目标:" templates/commands/specify.md  # 期望: >10
grep -r "规范驱动开发\|用户故事\|验收标准" templates/ || echo "关键术语缺失"
```

## 第二阶段: 翻译质量审核

### 3. review 核心 md 文件翻译质量
- 深度遍历 templates/, memory/, docs/ 目录, 对每个 md 文件对比原版对应文件, review 翻译质量
- 使用 Task 工具并行执行

### 4. review 项目级 md 文件翻译质量
使用 Task 工具并行处理:
- review spec-driven.md (对比原版 spec-kit/spec-driven.md)
- review SUPPORT.md (对比原版 spec-kit/SUPPORT.md)
- review SECURITY.md (对比原版 spec-kit/SECURITY.md)
- review README.md (对比原版 spec-kit/README.md)
- review CONTRIBUTING.md (对比原版 spec-kit/CONTRIBUTING.md)
- review CODE_OF_CONDUCT.md (对比原版 spec-kit/CODE_OF_CONDUCT.md)

### 5. review src/specify_cli 目录下 python 文件
- 遍历 src/specify_cli 下的 python 文件, 对比原版文件, review 功能一致性和文案翻译
- 必须额外检查: `typer.Typer(help=...)`, `add_typer(..., help=...)`, 命令函数 docstring, `typer.Argument/Option(..., help=...)`, 以及 Click/Typer 默认 help 标签
- 必须实际运行 `--help` 验证长 docstring、步骤说明和 Examples 注释没有遗漏英文

## 第三阶段: 完整性与发布验证

### 6. 翻译完整性检查
- 文件完整性: 确保所有需要翻译的文件都已处理
- 格式完整性: 检查 Markdown 格式、链接、图片引用
- 结构完整性: 验证目录结构、标题层级、列表格式
- 同步保护: 同步原版后必须重新验证 repo_owner、命令名称和中文界面

### 7. 检查 .github/ 目录更新情况
- 对比原版 .github/ 目录结构, 列出新增或修改的文件
- 如有更新, 详细说明变更内容并提供同步建议
- 不强制要求同步, 仅提供信息供用户决策

### 8. 输出结构化报告和质量评分
报告应包含:
- **执行摘要**: 检查文件总数、问题总数、严重错误数量、整体质量评估
- **详细问题列表**: 按文件分类, 包含位置、错误级别和修复建议
- **术语一致性检查**: 术语使用情况、不一致术语列表
- **功能验证结果**: CLI 功能测试、模板文件验证
- **修复建议**: 优先修复的问题列表和具体方案

质量评分:
- **10/10**: 所有关键修复点正确, 可以发布
- **8-9/10**: 存在重要问题, 必须修复
- **<8/10**: 存在严重问题, 不建议发布

### 9. 运行自动化验证
- 执行 `./tests/e2e/quality-check.sh` — 综合质量检查(包含关键修复点、术语、格式等)
- 执行 `./tests/e2e/check-cli-help-localization.py` — CLI Help 本地化专项检查
- 执行 `./tests/e2e/check-yaml-unicode.py` — YAML Unicode 配置检查
- 执行 `./tests/e2e/check-markdown-translation-coverage.py` — Markdown 翻译覆盖率检查
- 执行 `./tests/e2e/validate-release.sh` — 发布前完整端到端验证
- 验证项必须包含: ruff, pytest, CLI 冒烟, init 端到端(多 agent), wheel 安装冒烟
- 任一脚本验证失败时不得建议发布, 必须先修复并复跑

## 第四阶段: 工作流衔接

### 10. 根据检查结果决定后续操作
- **所有检查通过**: 直接告知用户, 无需修复
- **发现问题**: 使用 AskUserQuestion 工具询问用户:
  > "翻译审核发现 N 个问题(严重: X, 重要: Y, 一般: Z). 是否执行 /translation-fix 进行自动修复?"
  - 用户确认 → 使用 Skill 工具执行 /translation-fix, 将问题摘要作为参数传入
  - 用户拒绝 → 结束流程, 输出报告供手动处理

## 行为规则
- 必须对比原版 spec-kit 中的对应文件
- 使用 Task 工具并行对比
- 所有文件翻译后, 必须确保和原版表达一样的语义, 不能新增或减少内容
- 确保修复后的功能与原版完全一致
- 翻译标准参考 @TRANSLATION_STANDARDS.md, 术语表参考 @TERMINOLOGY.md
- 第一阶段专项检查未通过时, 优先修复后再继续后续步骤
- 输出报告按错误分类进行优先级排序
- 所有没有问题, 请直接告诉用户
- 不要将本项目自定义测试脚本放到 `scripts/` 目录(会被 rsync --delete 覆盖), 统一放到 `tests/e2e/`

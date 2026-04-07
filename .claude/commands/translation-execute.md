---
name: translation-execute
description: "智能执行文件翻译, 可独立使用或由 /translation-detect 自动衔接调用"
---

用户输入可以直接由代理提供或作为命令参数提供给你 - 你**必须**考虑它(如果不为空).

用户输入:
$ARGUMENTS

目标: 基于检测结果或手动指定, 智能执行高质量的文件翻译, 确保语义准确性和本地化质量.

## 调用方式

### 独立使用
直接执行 `/translation-execute` 翻译所有检测到的文件, 或传入参数指定范围:
```
/translation-execute templates/commands/implement.md
```

### 由 /translation-detect 自动调用
当 detect 检测到差异并经用户确认后, detect 会自动调用本命令:
- detect 的同步计划会作为参数传入
- 翻译完成后应建议执行 /translation-review 进行审核

## 执行步骤

### 1. 翻译准备
- 加载翻译标准(@TRANSLATION_STANDARDS.md)和术语表(@TERMINOLOGY.md)
- 解析输入参数: 来自 detect 的同步计划 或 手动指定的文件列表
- 验证原版文件完整性
- 确定翻译优先级

### 2. 按优先级执行翻译
优先级顺序:
1. 完全同步目录: 执行 rsync 同步 scripts/, .devcontainer/, media/
2. 核心模板文件(templates/核心模板)
3. CLI 相关文件(src/specify_cli/ 中的文案)
4. 项目文档(docs/, README.md 等)
5. 辅助文件(memory/, templates/commands/)

对每个文件执行:
- 读取原版文件, 分析内容和结构
- 上下文感知的智能翻译(对比同目录已翻译文件保持风格一致)
- 术语一致性检查(对照术语表)
- 格式和链接保持
- 代码块和占位符保护

### 3. 翻译质量控制
- 语义准确性验证: 对比原版确保内容完整性
- 术语一致性检查: 同一术语在整个项目中的使用
- 格式完整性: Markdown 格式、链接、图片引用
- 中文表达自然度: 避免机器翻译痕迹

### 4. 特殊处理规则
- CLI 命令: `specify` → `specify-cn`
- 包名: `specify-cli` → `specify-cn-cli`
- 路径引用: 保持原版路径不变, 不添加 `.specify/` 前缀
- 代码块: 完全保持原样
- 占位符: 保持格式不变(如 [PROJECT_NAME])
- 技术标记: NEEDS CLARIFICATION, N/A, TODO, TKTK, ??? 绝对不翻译
- yaml.dump/yaml.safe_dump: 必须使用 allow_unicode=True

### 5. 同步后验证
- 对比原版确保内容完整性, 无新增或遗漏
- 检查 CLI 输出: `uv run specify-cn --help` 等命令
- 验证特殊规则执行情况
- 检查 repo_owner/repo_name/name 是否正确
- 运行 `./tests/e2e/check-yaml-unicode.py` 确保 yaml.dump 配置正确
- 运行 `./tests/e2e/check-cli-help-localization.py` 验证 CLI Help 完全本地化
- 对于 presets/extensions 更新, 运行 `./tests/e2e/check-markdown-translation-coverage.py`

### 6. 输出翻译报告并衔接工作流

生成翻译报告:
- 翻译文件列表和处理结果
- 遇到的问题和决策记录
- 需要人工审核的标记

工作流衔接:
- 使用 AskUserQuestion 询问用户:
  > "翻译完成. 是否执行 /translation-review 进行质量审核?"
  - 用户确认 → 使用 Skill 工具执行 /translation-review
  - 用户拒绝 → 输出报告, 结束

## 行为规则
- 严格遵循 @TRANSLATION_STANDARDS.md 翻译标准
- 使用 @TERMINOLOGY.md 确保术语一致性
- 采用上下文感知的翻译策略, 避免孤立翻译
- 保护所有技术元素(代码, 链接, 占位符)
- 确保翻译后的功能与原版完全一致
- 对不确定的翻译标记为需要人工审核
- 由 detect 调用时, 优先处理 detect 报告中的文件
- 翻译 src/specify_cli/ 时必须重新设置 repo_owner="linfee", repo_name="spec-kit-cn"

---
name: translation-detect
description: "同步原版更新、检测翻译状态、制定同步计划, 完成后自动建议执行翻译"
---

用户输入可以直接由代理提供或作为命令参数提供给你 - 你**必须**考虑它(如果不为空).

用户输入:
$ARGUMENTS

目标: 将 spec-kit 更新到最新正式版本, 检测与当前中文版的差异, 制定同步和翻译计划.

## 第一阶段: 更新原版与准备

### 1. 更新 spec-kit 到最新正式版本
- 确认 spec-kit 目录存在, 不存在则克隆: `git clone https://github.com/github/spec-kit.git spec-kit`
- 获取最新版本: `cd spec-kit && git fetch --tags`
- 查看可用版本: `git tag --sort=-v:refname | head -10`
- 切换到最新正式版本: `git checkout <latest-tag>`
- 记录当前版本: 记录 spec-kit 版本号和对应的 commit hash

### 2. 准备工作
- **版本对齐**: 对比原版和本地 `pyproject.toml` 版本号, 禁止本地版本自增
- **创建工作分支**: `git checkout -b sync/v<version>`
- **备份翻译文件**:
  ```bash
  BACKUP_DIR=".backup/translation-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  cp -r templates/ "$BACKUP_DIR/"
  cp -r memory/ "$BACKUP_DIR/" 2>/dev/null || true
  cp -r docs/ "$BACKUP_DIR/" 2>/dev/null || true
  git stash push -m "pre-sync-backup" -- templates/ memory/ docs/ 2>/dev/null || true
  ```

## 第二阶段: 差异检测

### 3. 同步完全同步目录
以下目录与原版完全一致, 可直接 rsync:
```bash
# 完全同步(可使用 rsync --delete)
rsync -avp spec-kit/scripts/ scripts/
rsync -avp spec-kit/.devcontainer/ .devcontainer/
rsync -avp spec-kit/media/ media/
# tests/ 按需同步(本项目有自定义测试)
```

### 4. 检测翻译目录差异
对以下目录进行增量差异检测(禁止 --delete):
- `templates/` — 对比每个文件, 标记新增/修改/删除
- `docs/` — 对比每个文件
- `memory/` — 对比每个文件
- 根目录 md 文件 — 逐文件对比

对每个文件执行:
- 读取原版文件和中文版文件
- 分类: 未翻译(与原版相同) / 需更新(原版有改动) / 已翻译且最新 / 新增文件
- 标记差异点和变更范围

### 5. 检测 src/ 差异
- 对比 `src/specify_cli/` 下所有文件
- 标记功能变更和需要重新翻译的文案
- 注意保护本地化标记(repo_owner, repo_name, name="specify-cn")

## 第三阶段: 输出同步计划

### 6. 生成同步计划

输出结构化同步计划, 包含:

**同步操作清单**(按优先级):
1. 完全同步目录(步骤3已列出命令)
2. 需要翻译的文件清单:
   - 新增文件(需要首次翻译)
   - 修改文件(需要更新翻译)
   - 未翻译文件(需要首次翻译)
3. 需要重新本地化的代码变更
4. 风险评估(大范围变更 vs 小范围修改)

**版本信息**:
- 原版版本: <tag>
- 当前中文版版本: 读取 pyproject.toml 中的版本
- 是否需要版本号更新

**rsync 安全规则**(提醒):
- **禁止同步**: `.github/` 目录
- **禁止 --delete**: `templates/`, `docs/`, `memory/` 翻译目录
- 完全同步目录需确认后执行

## 第四阶段: 工作流衔接

### 7. 根据检测结果决定后续操作
- **无差异**: 告知用户当前已是最新, 无需操作
- **有差异**: 使用 AskUserQuestion 询问用户:
  > "检测到 N 个文件需要处理(新增: X, 修改: Y, 未翻译: Z). 是否执行 /translation-execute 进行翻译?"
  - 用户确认 → 使用 Skill 工具执行 /translation-execute, 将同步计划作为参数传入
  - 用户拒绝 → 输出计划供手动处理

## 同步后验证(翻译完成后执行)

翻译完成后必须运行以下验证:
```bash
# 检查翻译是否被意外覆盖
grep -c "用户输入\|概述\|执行步骤" templates/commands/specify.md
# 检查关键中文术语
grep -r "规范驱动开发\|用户故事\|验收标准" templates/
# 如果验证失败, 从备份恢复
# cp -r "$BACKUP_DIR/templates/" templates/
```

## 行为规则
- 使用 git 命令管理 spec-kit 版本, 禁止手动修改原版目录
- 差异检测必须对比原版文件内容, 不能仅凭文件时间戳判断
- 参考 @TRANSLATION_STANDARDS.md 和 @TERMINOLOGY.md
- 同步计划需包含具体的执行命令
- 重点关注 CLI 相关文件的变更
- 完全同步目录的 rsync 命令需要用户确认后执行
- 不要将本项目自定义测试脚本放到 `scripts/` 目录(会被 rsync --delete 覆盖)
- 优先保持现有翻译的稳定性, 仅更新确实变更的部分

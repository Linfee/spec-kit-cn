---
name: translation-sync
description: "同步原版更新并自动翻译新增内容"
---

用户输入: 
$ARGUMENTS

目标: 自动同步原版更新, 智能识别变更内容, 并自动翻译新增或修改的内容.

执行步骤: 

1. 原版同步准备
   - 检查当前Git状态, 确保工作目录干净
   - 获取原版最新版本信息
   - 创建同步工作分支

   - **版本对齐规则**: 本地版本号必须与原版严格对齐
     * 检查原版 pyproject.toml 中的版本号
     * 更新本地 pyproject.toml 为相同版本
     * 禁止本地版本自增, 必须与原版完全一致

2. 原版更新获取
   - 在spec-kit目录拉取最新原版代码
   - 识别版本变更和新增内容
   - 分析文件变更类型(新增/修改/删除)
   - 生成变更影响报告

3. 变更内容分类
   - **必须同步（直接 rsync）**: scripts/, .devcontainer/, tests/
   - **需要翻译（增量合并）**: templates/, docs/, memory/, 根目录文档
   - **禁止同步**: .github/ (本项目有独立的工作流)
   - **无需处理**: 媒体文件, 纯技术文件

4. **同步前备份检查（必须执行）**
   ```bash
   # 备份当前翻译文件
   BACKUP_DIR=".backup/translation-$(date +%Y%m%d-%H%M%S)"
   mkdir -p "$BACKUP_DIR"
   cp -r templates/ "$BACKUP_DIR/"
   cp -r memory/ "$BACKUP_DIR/" 2>/dev/null || true

   # 记录当前翻译状态
   git stash push -m "pre-sync-translation-backup" -- templates/ memory/ 2>/dev/null || true
   git stash push -m "pre-sync-docs-backup" -- README.md CHANGELOG.md 2>/dev/null || true
   ```

5. 智能同步执行
   - **必须同步目录（完全覆盖，使用 rsync --delete）**:
     ```bash
     rsync -av --delete spec-kit/scripts/ scripts/
     rsync -av --delete spec-kit/.devcontainer/ .devcontainer/
     rsync -av --delete spec-kit/tests/ tests/
     ```
   - **需要翻译目录（增量合并，禁止 --delete）**:
     ```bash
     # 仅查看差异，不直接覆盖
     diff -r spec-kit/templates/ templates/ > /tmp/template-diff.txt

     # 手动合并新增内容，保留现有翻译
     # 禁止使用: rsync --delete 同步翻译目录
     ```
   - **禁止同步**:
     * `.github/` - 本项目有独立的 CI/CD 配置
     * 仅报告差异供人工决策

6. 翻译更新处理
   - 调用翻译引擎处理变更内容
   - 保持现有翻译的风格和术语
   - 更新相关的翻译记忆
   - 验证翻译后的功能完整性

7. **同步后验证（必须通过）**
   ```bash
   # 检查翻译是否被意外覆盖
   grep -c "用户输入\|概述\|执行步骤" templates/commands/specify.md || echo "❌ 翻译可能被覆盖"

   # 检查关键中文术语
   grep -r "规范驱动开发\|用户故事\|验收标准" templates/ || echo "❌ 关键术语缺失"

   # 如果验证失败，从备份恢复
   if [ 验证失败 ]; then
       cp -r "$BACKUP_DIR/templates/" templates/
       git stash pop
   fi
   ```

8. 质量验证和集成
   - 运行翻译质量检查: `/translation-qa`
   - 验证CLI功能正常: `uv run specify-cn --help`
   - 检查文档和模板完整性
   - 更新版本信息和CHANGELOG

9. 同步报告
   - 生成详细的同步报告
   - 列出所有变更内容
   - 标识需要人工审核的项目
   - 提供发布建议

智能特性: 
- **增量更新**: 仅处理变更内容, 避免重复工作
- **智能合并**: 保持现有翻译, 仅更新必要部分
- **冲突检测**: 自动识别和解决翻译冲突
- **版本感知**: 基于版本差异进行精确更新

安全机制: 
- 分支操作保证安全性
- 关键变更需要人工确认
- 详细的操作日志记录

行为规则: 
- 优先保持现有翻译的稳定性
- 仅对确实需要更新的内容执行翻译
- 确保同步后功能与原版完全一致
- 维护翻译质量和一致性标准
- 提供清晰的变更追踪和审计
- 在不确定时选择保守的更新策略

使用场景: 
- 原版发布新版本后的自动同步
- 定期的原版更新跟进
- 特定功能或修复的快速同步
- 翻译版本与原版的一致性维护

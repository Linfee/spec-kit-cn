---
name: translation-qa
description: "自动化翻译质量保证检查和验证"
---

用户输入: 
$ARGUMENTS

目标: 对翻译结果进行全面的质量检查, 确保翻译质量达到发布标准.

执行步骤: 

1. 完整性检查
   - 文件完整性: 确保所有需要翻译的文件都已处理
   - 内容完整性: 对比原版确保没有遗漏内容
   - 格式完整性: 检查Markdown格式, 链接, 图片引用
   - 结构完整性: 验证目录结构, 标题层级, 列表格式

2. 翻译质量检查
   - 术语一致性: 对照术语表检查术语使用
   - 语言质量: 检查语法, 表达, 流畅度
   - 技术准确性: 验证技术概念翻译的准确性
   - 上下文一致性: 检查相关文件间的翻译一致性

3. 功能验证检查
   - CLI命令: 验证命令名称和参数翻译
   - 路径引用: 确保路径引用保持正确
   - 代码示例: 验证代码块保持原样
   - 占位符: 检查占位符格式和内容
   - **GitHub仓库配置**: 验证模板下载源为中文版仓库
   - **包名一致性**: 确保包名使用 specify-cn
   - **命令统一性**: 检查所有用户可见命令使用 specify-cn

4. 自动化测试
   - 链接有效性测试
   - 格式渲染测试
   - CLI帮助文本测试
   - 模板文件可用性测试
   - 发布前E2E自动化: `./tests/e2e/validate-release.sh`

5. 质量评分和报告
   - 为每个文件生成质量评分
   - 识别需要人工审核的问题
   - 生成详细的质量检查报告
   - 提供修复建议和优化方案

行为规则:
- 参考 @TRANSLATION_STANDARDS.md 和 @TERMINOLOGY.md 进行多维评估
- 对关键文件(如CLI相关)进行更严格检查
- 识别并标记机器翻译痕迹
- 检查文化适应性和本地化质量
- 确保翻译后的用户体验与原版一致
- 生成可操作的质量改进建议
- 建立质量基线, 便于后续版本对比

## 🔍 关键修复点专项检查

### A. GitHub仓库配置检查 (必须通过)
```bash
# 检查仓库所有者
grep -n 'repo_owner = "linfee"' src/specify_cli/__init__.py
# 期望结果: repo_owner = "linfee"

# 检查仓库名称
grep -n 'repo_name = "spec-kit-cn"' src/specify_cli/__init__.py
# 期望结果: repo_name = "spec-kit-cn"
```
**重要性**: 🔴 **严重** - 确保下载中文模板而非原版模板

### B. CLI命令统一性检查 (必须通过)
```bash
# 检查应用名称
grep -n 'name="specify-cn"' src/specify_cli/__init__.py
# 期望结果: name="specify-cn"

# 检查是否还有未修复的 specify 命令
grep -n "specify[^-]" src/specify_cli/__init__.py
# 期望结果: 无匹配项

# 检查示例命令
grep -n "specify-cn init" src/specify_cli/__init__.py | wc -l
# 期望结果: 多个匹配项 (>5)
```
**重要性**: 🔴 **严重** - 确保用户体验一致性

### C. 用户界面翻译检查 (必须通过)
```bash
# 检查关键中文翻译
grep -n "已准备就绪\|正在检查\|提示 : " src/specify_cli/__init__.py
# 期望结果: 找到对应的中文翻译

# 检查是否还有未翻译的英文界面
grep -n -E "(Tip:|Checking for|ready to use|Display version)" src/specify_cli/__init__.py
# 期望结果: 无匹配项
```
**重要性**: 🟡 **重要** - 确保中文用户体验

### D. 包名一致性检查 (必须通过)
```bash
# 检查包名使用规范
grep -n "specify-cn-cli" src/specify_cli/__init__.py
# 期望结果: 只在文档字符串中出现, 不在代码逻辑中
```
**重要性**: 🟡 **重要** - 确保项目命名规范

### E. 技术变量保护检查 (必须通过)
```bash
# 检查技术变量名是否被错误翻译
# ❌ 错误: 将 sys._specify_tracker_active 改为 sys._specify_cn_tracker_active
# ✅ 正确: 保持技术变量名为英文原样
grep -n "_specify_tracker_active" src/specify_cli/__init__.py
# 期望结果: _specify_tracker_active (保持不变)

grep -n "scripts_root.*specify" src/specify_cli/__init__.py
# 期望结果: scripts_root = project_path / ".specify" / "scripts" (保持 .specify 不变)
```
**重要性**: 🔴 **严重** - 技术变量名不能翻译, 会影响功能

### F. 斜杠命令格式检查 (必须通过)
```bash
# 检查斜杠命令是否保持原版格式 (不添加 /speckit. 前缀)
grep -n "/speckit\." src/specify_cli/__init__.py
# 期望结果: 无匹配项 (不应该有 /speckit. 前缀)

# 检查斜杠命令内容是否翻译
grep -n -E "(建立项目原则|创建基线规范|创建实施计划|生成可执行任务|执行实施)" src/specify_cli/__init__.py
# 期望结果: 找到对应的中文翻译
```
**重要性**: 🟡 **重要** - 确保斜杠命令符合翻译标准

## ⚠️ 同步保护机制

### 原版同步后的必检项
1. **仓库配置回滚**: 每次同步原版后必须重新设置 `repo_owner = "linfee"`
2. **命令名称保护**: 确保 `name="specify-cn"` 不被覆盖
3. **翻译保护**: 确保中文界面文本不被英文覆盖
4. **功能验证**: 同步后必须测试模板下载功能

### 🛠️ 快速验证脚本
```bash
#!/bin/bash
# quick-verify-fixes.sh - 快速验证关键修复点
echo "🔍 验证 Spec Kit CN 关键修复点..."

echo ""
echo "📍 A. GitHub仓库配置检查"
if grep -q 'repo_owner = "linfee"' src/specify_cli/__init__.py; then
    echo "✅ 仓库所有者正确 (linfee)"
else
    echo "❌ 仓库所有者需要修复"
fi

if grep -q 'repo_name = "spec-kit-cn"' src/specify_cli/__init__.py; then
    echo "✅ 仓库名称正确 (spec-kit-cn)"
else
    echo "❌ 仓库名称需要修复"
fi

echo ""
echo "📍 B. CLI命令统一性检查"
if grep -q 'name="specify-cn"' src/specify_cli/__init__.py; then
    echo "✅ 应用名称正确 (specify-cn)"
else
    echo "❌ 应用名称需要修复"
fi

unfixed_specify=$(grep -c "specify[^-]" src/specify_cli/__init__.py || true)
if [ "$unfixed_specify" -eq 0 ]; then
    echo "✅ 命令名称已统一 (无遗留 specify)"
else
    echo "❌ 发现 $unfixed_specify 处未修复的 specify 命令"
fi

specify_cn_count=$(grep -c "specify-cn init" src/specify_cli/__init__.py || true)
if [ "$specify_cn_count" -gt 5 ]; then
    echo "✅ 示例命令已更新 ($specify_cn_count 处)"
else
    echo "❌ 示例命令需要更新 (当前: $specify_cn_count 处)"
fi

echo ""
echo "📍 C. 用户界面翻译检查"
if grep -q "已准备就绪" src/specify_cli/__init__.py; then
    echo "✅ 状态信息已翻译"
else
    echo "❌ 状态信息需要翻译"
fi

if grep -q "正在检查" src/specify_cli/__init__.py; then
    echo "✅ 检查信息已翻译"
else
    echo "❌ 检查信息需要翻译"
fi

if grep -q "提示 : " src/specify_cli/__init__.py; then
    echo "✅ 提示信息已翻译"
else
    echo "❌ 提示信息需要翻译"
fi

unfixed_english=$(grep -c -E "(Tip:|Checking for|ready to use|Display version)" src/specify_cli/__init__.py || true)
if [ "$unfixed_english" -eq 0 ]; then
    echo "✅ 英文界面文本已处理"
else
    echo "❌ 发现 $unfixed_english 处未翻译的英文文本"
fi

echo ""
echo "📊 检查汇总"
total_checks=10
passed_checks=$(
    grep -q 'repo_owner = "linfee"' src/specify_cli/__init__.py && echo 1 ||
    grep -q 'repo_name = "spec-kit-cn"' src/specify_cli/__init__.py && echo 1 ||
    grep -q 'name="specify-cn"' src/specify_cli/__init__.py && echo 1 ||
    [ "$unfixed_specify" -eq 0 ] && echo 1 ||
    [ "$specify_cn_count" -gt 5 ] && echo 1 ||
    grep -q '已准备就绪' src/specify_cli/__init__.py && echo 1 ||
    grep -q '正在检查' src/specify_cli/__init__.py && echo 1 ||
    grep -q '提示 : ' src/specify_cli/__init__.py && echo 1 ||
    [ "$unfixed_english" -eq 0 ] && echo 1 ||
    grep -q '_specify_tracker_active' src/specify_cli/__init__.py && echo 1 ||
    grep -q 'scripts_root.*specify' src/specify_cli/__init__.py && echo 1 ||
    grep -n "/speckit\." src/specify_cli/__init__.py | head -1 && echo 0 || echo 1
) | wc -l

echo "通过检查: $passed_checks/$total_checks"
if [ "$passed_checks" -eq "$total_checks" ]; then
    echo "🎉 所有关键修复点验证通过!"
    exit 0
else
    echo "⚠️  发现问题, 需要修复"
    exit 1
fi
```

## ✅ 发布前验证基线

执行以下命令并确保通过:

```bash
./tests/e2e/validate-release.sh
```

说明:
- 自定义测试脚本必须放在 `tests/e2e/`, 不得放到 `scripts/`(会被上游同步覆盖).
- E2E 必须覆盖: ruff、pytest、CLI 冒烟、init 产物校验、wheel 安装冒烟、临时文件清理.

### 📝 检查结果解读
- **10/10 通过**: 所有关键修复点正确, 可以进行发布
- **8-9/10 通过**: 存在重要问题, 必须修复
- **<8/10 通过**: 存在严重问题, 不建议发布

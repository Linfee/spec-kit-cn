#!/bin/bash

# Spec Kit CN 翻译质量检查脚本
# 执行全面的质量检查并生成报告

set -e

echo "========================================="
echo "  Spec Kit CN 翻译质量检查报告"
echo "  生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""

# 计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
check_pass() {
    echo "✅ $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo "❌ $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_info() {
    echo "ℹ️  $1"
    ((TOTAL_CHECKS++))
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  A. GitHub仓库配置检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q 'repo_owner = "linfee"' src/specify_cli/__init__.py; then
    check_pass "仓库所有者正确 (linfee)"
else
    check_fail "仓库所有者需要修复"
fi

if grep -q 'repo_name = "spec-kit-cn"' src/specify_cli/__init__.py; then
    check_pass "仓库名称正确 (spec-kit-cn)"
else
    check_fail "仓库名称需要修复"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  B. CLI命令统一性检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q 'name="specify-cn"' src/specify_cli/__init__.py; then
    check_pass "应用名称正确 (specify-cn)"
else
    check_fail "应用名称需要修复"
fi

# 检查 specify-cn init 出现次数
specify_cn_count=$(grep -c "specify-cn init" src/specify_cli/__init__.py || true)
if [ "$specify_cn_count" -gt 5 ]; then
    check_pass "示例命令已更新 ($specify_cn_count 处)"
else
    check_fail "示例命令需要更新 (当前: $specify_cn_count 处, 需要 > 5)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  C. 用户界面翻译检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "正在检查" src/specify_cli/__init__.py; then
    check_pass "状态信息已翻译"
else
    check_fail "状态信息需要翻译"
fi

if grep -q "项目已就绪" src/specify_cli/__init__.py; then
    check_pass "完成信息已翻译"
else
    check_fail "完成信息需要翻译"
fi

# 检查是否还有未翻译的英文界面
unfixed_english=$(grep -c -E "(Tip:|Checking for|ready to use|Display version)" src/specify_cli/__init__.py || true)
if [ "$unfixed_english" -eq 0 ]; then
    check_pass "英文界面文本已处理"
else
    check_fail "发现 $unfixed_english 处未翻译的英文文本"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  D. 包名一致性检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 specify-cn-cli 使用是否正确（只在文档字符串和元数据中出现）
cli_count=$(grep -c "specify-cn-cli" src/specify_cli/__init__.py || true)
if [ "$cli_count" -gt 0 ]; then
    check_info "specify-cn-cli 使用: $cli_count 处（需人工确认是否仅在文档/元数据中）"
else
    check_info "未发现 specify-cn-cli 使用"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  E. 技术变量保护检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "_specify_tracker_active" src/specify_cli/__init__.py; then
    check_pass "技术变量名保持不变 (_specify_tracker_active)"
else
    check_fail "技术变量名可能被修改"
fi

# 检查 .specify 路径是否正确
if grep -q 'scripts_root = project_path / ".specify" / "scripts"' src/specify_cli/__init__.py; then
    check_pass "技术路径 .specify 保持不变"
else
    check_fail "技术路径可能被修改"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  F. 斜杠命令格式检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查斜杠命令翻译
slash_cmd_count=$(grep -c "建立项目原则\|创建基础规范\|创建实施计划\|生成可执行任务\|执行实施" src/specify_cli/__init__.py || true)
if [ "$slash_cmd_count" -ge 5 ]; then
    check_pass "斜杠命令已翻译 ($slash_cmd_count 处)"
else
    check_fail "斜杠命令翻译不完整 (当前: $slash_cmd_count 处, 需要 >= 5)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  G. 文件完整性检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查关键文件是否存在
files_to_check=(
    "TRANSLATION_STANDARDS.md"
    "TERMINOLOGY.md"
    "README.md"
    "spec-driven.md"
    "CLAUDE.md"
    "src/specify_cli/__init__.py"
    "templates/commands/specify.md"
    "templates/commands/plan.md"
    "templates/commands/tasks.md"
    "templates/commands/implement.md"
)

missing_files=0
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        check_info "文件存在: $file"
    else
        check_fail "文件缺失: $file"
        ((missing_files++))
    fi
done

if [ "$missing_files" -eq 0 ]; then
    check_pass "所有关键文件完整"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  H. 术语一致性检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查关键术语翻译
term_count=$(grep -r "规范驱动开发\|用户故事\|验收标准" templates/ 2>/dev/null | wc -l || true)
if [ "$term_count" -gt 10 ]; then
    check_pass "关键术语翻译存在 ($term_count 处)"
else
    check_fail "关键术语翻译缺失或不完整 (当前: $term_count 处)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  I. 格式和结构检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查技术标记是否保持英文
tech_markers=(
    "NEEDS CLARIFICATION"
    "N/A"
    "TODO"
)

marker_issues=0
for marker in "${tech_markers[@]}"; do
    if grep -rq "$marker" templates/ 2>/dev/null; then
        check_info "技术标记保持英文: $marker"
    else
        check_fail "技术标记可能被翻译或缺失: $marker"
        ((marker_issues++))
    fi
done

if [ "$marker_issues" -eq 0 ]; then
    check_pass "所有技术标记保持英文"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  J. 功能性测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查CLI是否可以正常导入
if python3 -c "import sys; sys.path.insert(0, 'src'); from specify_cli import app" 2>/dev/null; then
    check_pass "CLI 模块可以正常导入"
else
    check_fail "CLI 模块导入失败"
fi

# 检查 pyproject.toml 配置
if [ -f "pyproject.toml" ]; then
    if grep -q 'name = "specify-cn-cli"' pyproject.toml; then
        check_pass "pyproject.toml 包名配置正确"
    else
        check_fail "pyproject.toml 包名配置错误"
    fi
else
    check_fail "pyproject.toml 文件缺失"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  检查结果汇总"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL_SCORE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo ""
echo "📊 总体统计:"
echo "   总检查项: $TOTAL_CHECKS"
echo "   通过: $PASSED_CHECKS"
echo "   失败: $FAILED_CHECKS"
echo "   通过率: ${TOTAL_SCORE}%"
echo ""

if [ "$TOTAL_SCORE" -ge 90 ]; then
    echo "🎉 质量等级: 优秀 (可以发布)"
    echo ""
    exit_code=0
elif [ "$TOTAL_SCORE" -ge 75 ]; then
    echo "✅ 质量等级: 良好 (建议修复部分问题后发布)"
    echo ""
    exit_code=0
elif [ "$TOTAL_SCORE" -ge 60 ]; then
    echo "⚠️  质量等级: 一般 (需要修复重要问题)"
    echo ""
    exit_code=1
else
    echo "❌ 质量等级: 不合格 (存在严重问题, 不建议发布)"
    echo ""
    exit_code=1
fi

# 生成建议
if [ "$FAILED_CHECKS" -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  修复建议"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "请参考以下文档进行修复:"
    echo "  • TRANSLATION_STANDARDS.md - 翻译标准"
    echo "  • TERMINOLOGY.md - 术语表"
    echo "  • CLAUDE.md - 项目记忆"
    echo ""
fi

exit $exit_code

---
name: translation-review
description: "Review and fix translation quality between spec-kit original and Chinese localized version"
---

用户输入可以直接由代理提供或作为命令参数提供给你 - 你**必须**考虑它(如果不为空).

用户输入: 

$ARGUMENTS

目标: 系统性地review原项目spec-kit与中文版之间的翻译质量, 识别并修复所有翻译错误、术语不一致和功能逻辑问题.

执行步骤: 

1. 验证环境准备, 使用tree命令来检查这些项, 需要完全同步的使用rsync命令确保同步
   - 确认spec-kit目录存在且包含原版文件
   - 确认templates目录结构和spec-kit/templates保持一致
   - 确认memory目录结构和spec-kit/docs保持一致
   - 确认docs目录结构和spec-kit/docs保持一致
   - 确认src目录结构和spec-kit/src保持一致
   - 确认scripts目录结构和spec-kit/scripts保持一致(需完全同步)
   - 确认.devcontainer目录结构和spec-kit/.devcontainer保持一致(需完全同步)
   - 确认media目录结构和spec-kit/media保持一致(需完全同步)
   - 确认AGENTS.md文件存在且与spec-kit/AGENTS.md一致(需完全同步)
   - 确认pyproject.toml配置文件与原版结构一致
   
2. review核心md文件翻译质量
  - 深度遍历 templates, memory, docs 三个目录, 对找到的每个md文件, 对比原版对应文件, review翻译质量. 此步骤使用Task工具并行执行

3. review项目级别md文件翻译质量, 以下子项务必使用Task工具并行处理
  - review spec-driven.md (对比原版 spec-kit/spec-driven.md) 的翻译质量
  - review SUPPORT.md (对比原版 spec-kit/SUPPORT.md) 的翻译质量
  - review SECURITY.md (对比原版 spec-kit/SECURITY.md) 的翻译质量
  - review README.md (对比原版 spec-kit/README.md) 的翻译质量
  - review CONTRIBUTING.md (对比原版 spec-kit/CONTRIBUTING.md) 的翻译质量
  - review CODE_OF_CONDUCT.md (对比原版 spec-kit/CODE_OF_CONDUCT.md) 的翻译质量
  
4. review src/specify_cli 目录下python文件的功能与翻译质量
   - 遍历 src/specify_cli 下的python文件, 对比原版文件, review其功能是否保持一致, 是否对脚本中的文案进行了适当的翻译

5. 检查.github/目录更新情况
   - 对比原版.github/目录结构, 列出新增或修改的文件
   - 如有更新, 详细说明变更内容并提供同步建议
   - 不强制要求同步, 仅提供信息供用户决策

6. 输出结构化报告等待人类审核: 
   - 报告应包含执行摘要、详细问题列表、术语一致性检查、功能验证结果和修复建议
   - 参考 @TRANSLATION_STANDARDS.md 中的输出报告结构要求

行为规则: 
- 必须对比原版spec-kit中的对应文件
- 使用Task工具并行对比
- 所有文件翻译后, 必须确保和原版表达是一样的语义, 不能新增或减少内容
- 确保修复后的功能与原版完全一致
- 翻译标准参考 @TRANSLATION_STANDARDS.md, 术语表参考 @TERMINOLOGY.md
- 输出详细的修复报告, 按照错误分类进行优先级排序
- 所有没有问题, 请直接告诉用户

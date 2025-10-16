---
name: translation-workflow
description: "翻译工作流管理 - 提供完整的使用指南和最佳实践"
---

用户输入: 
$ARGUMENTS

目标: 为翻译项目提供完整的工作流指南, 确保团队能够高效使用自动化翻译系统.

## 工作流概览

### 核心命令体系
```
translation-auto      # 全自动翻译(一键式)
translation-sync      # 同步原版更新
translation-detect    # 检测翻译需求
translation-execute   # 执行翻译任务
translation-qa        # 质量保证检查
translation-fix       # 修复翻译问题
translation-review    # 人工审核(已存在)
```

### 推荐工作流程

#### 1. 首次设置翻译项目
```bash
/translation-detect    # 检测需要翻译的文件
/translation-auto      # 执行完整翻译流程
/translation-qa        # 质量检查
/translation-fix       # 修复发现的问题
```

#### 2. 原版更新后的同步
```bash
/translation-sync      # 同步原版更新
/translation-qa        # 验证同步质量
/translation-fix       # 修复同步问题
```

#### 3. 日常翻译维护
```bash
/translation-detect    # 检测新增翻译需求
/translation-execute   # 执行翻译
/translation-qa        # 质量检查
```

#### 4. 发布前质量检查
```bash
/translation-qa        # 全面质量检查
/translation-fix       # 修复关键问题
/translation-review    # 最终人工审核
```

## 最佳实践指南

### 自动化策略
1. **最大化自动化**: 优先使用 `translation-auto` 处理常规翻译任务
2. **增量更新**: 使用 `translation-sync` 进行增量更新, 避免重复工作
3. **质量优先**: 每次翻译后都要运行 `translation-qa` 进行质量检查
4. **持续改进**: 定期使用 `translation-fix` 优化翻译质量

### 质量保证策略
1. **多层检查**: 自动化检查 + 人工审核的双重保障
2. **重点关注**: CLI相关文件和核心模板需要更严格检查
3. **一致性维护**: 定期检查术语使用和翻译风格一致性
4. **用户反馈**: 建立用户反馈机制, 持续改进翻译质量

### 风险控制策略
1. **分支操作**: 所有翻译操作都在分支进行, 确保主分支稳定
2. **渐进式发布**: 分阶段发布翻译更新, 降低风险
3. **回滚准备**: 保持回滚能力, 快速响应问题

## 常见场景处理

### 场景1: 原版大版本更新
```bash
# 推荐流程
/translation-sync      # 智能同步更新
/translation-qa        # 全面质量检查
/translation-fix       # 修复问题
/translation-review    # 人工审核关键文件
```

### 场景2: 发现翻译错误
```bash
# 针对性修复
/translation-detect    # 定位问题文件
/translation-fix       # 智能修复
/translation-qa        # 验证修复效果
```

### 场景3: 新增功能翻译
```bash
# 快速响应
/translation-detect    # 识别新增内容
/translation-execute   # 快速翻译
/translation-qa        # 质量验证
```

### 场景4: 发布前检查
```bash
# 全面检查
/translation-qa        # 完整质量检查
/translation-fix       # 修复所有问题
/translation-review    # 最终审核
```

## 性能优化建议

### 并行处理
- 利用Task工具并行处理多个文件
- 合理分配翻译任务, 提高效率
- 监控系统资源使用情况

### 缓存策略
- 建立翻译记忆库, 避免重复翻译
- 缓存常用术语和表达方式
- 保持翻译风格一致性

### 增量处理
- 仅处理变更内容, 避免全量重翻
- 智能识别翻译需求, 精确处理
- 保持现有翻译稳定性

## 团队协作指南

### 角色分工
- **翻译负责人**: 负责整体翻译策略和质量把控
- **技术审核**: 负责CLI功能和技术准确性验证
- **语言审核**: 负责翻译质量和语言表达优化
- **用户测试**: 负责用户体验和实际使用验证

### 协作流程
1. **需求分析**: 使用 `translation-detect` 分析翻译需求
2. **任务分配**: 基于检测结果分配翻译任务
3. **并行执行**: 使用 `translation-execute` 并行处理
4. **质量检查**: 使用 `translation-qa` 统一质量标准
5. **问题修复**: 使用 `translation-fix` 处理质量问题
6. **最终审核**: 使用 `translation-review` 人工审核

### 沟通机制
- 建立翻译问题反馈渠道
- 定期召开翻译质量评审会议
- 维护翻译知识库和最佳实践
- 跟踪翻译指标和持续改进

## 监控和度量

### 质量指标
- 翻译完成度
- 术语一致性率
- 用户反馈评分
- 问题修复率

### 效率指标
- 翻译速度
- 自动化率
- 人工干预率
- 发布周期

### 持续改进
- 定期分析翻译数据
- 优化翻译流程
- 更新翻译标准
- 改进自动化工具

行为规则: 
- 根据项目具体情况选择合适的工作流程
- 保持翻译质量和效率的平衡
- 重视用户反馈和持续改进
- 建立完善的翻译知识管理体系
- 确保团队协作的高效性和一致性

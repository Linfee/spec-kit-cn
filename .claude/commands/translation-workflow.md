---
name: translation-workflow
description: "翻译工作流使用指南"
---

用户输入:
$ARGUMENTS

目标: 提供翻译工作流的快速参考和使用指南.

## 工作流概览

```
/translation-detect   同步原版 + 检测差异 + 制定计划
       ↓ (自动询问确认)
/translation-execute  执行翻译
       ↓ (自动询问确认)
/translation-review   审核质量 + 专项检查 + 发布验证
       ↓ (有问题时建议)
/translation-fix      修复问题
```

每个环节通过询问自动衔接, 用户可在任意节点中断.

## 独立工具

| 命令 | 用途 |
|------|------|
| `/punctuation-fix [路径]` | 批量修复 Markdown 标点符号 |
| `./tests/e2e/quality-check.sh` | 快速质量检查脚本(终端直接运行) |

## 常见场景

### 原版更新
```bash
/translation-detect    # 一键同步原版, 检测差异, 自动衔接翻译
```

### 发布前检查
```bash
/translation-review    # 全面审核 + 发布验证
```

### 修复翻译问题
```bash
/translation-fix                    # 修复所有问题
/translation-fix templates/xxx.md   # 修复指定文件
```

### 标点符号修复
```bash
/punctuation-fix                    # 处理所有 md 文件
/punctuation-fix templates/         # 处理指定目录
```

## rsync 安全规则

| 目录 | 策略 | 说明 |
|------|------|------|
| `scripts/`, `.devcontainer/`, `media/` | rsync --delete | 完全同步原版 |
| `templates/`, `docs/`, `memory/` | 增量合并 | **禁止 --delete**, 会丢失翻译 |
| `.github/` | **禁止同步** | 本项目有独立 CI/CD |
| `tests/e2e/` | 不同步 | 本项目自定义测试 |

## 测试脚本位置约束

自定义测试脚本统一放在 `tests/e2e/`, 不要放在 `scripts/` (同步时会被 `rsync --delete` 覆盖).

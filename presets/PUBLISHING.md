# Preset 发布指南

本指南解释如何将你的 preset 发布到 Spec Kit preset 目录, 使其可以通过 `specify-cn preset search` 被发现.

## 目录

1. [先决条件](#先决条件)
2. [准备你的 Preset](#准备你的-preset)
3. [提交到目录](#提交到目录)
4. [验证流程](#验证流程)
5. [发布工作流](#发布工作流)
6. [最佳实践](#最佳实践)

---

## 先决条件

在发布 preset 之前, 确保你有:

1. **有效的 Preset**: 带有有效 `preset.yml` 清单的工作 preset
2. **Git 仓库**: Preset 托管在 GitHub(或其他公共 git 托管平台)
3. **文档**: 带有描述和使用说明的 README.md
4. **许可证**: 开源许可证文件(MIT, Apache 2.0 等)
5. **版本控制**: 语义版本控制(例如 1.0.0)
6. **测试**: 使用 `specify-cn preset add --dev` 在真实项目上测试过的 preset

---

## 准备你的 Preset

### 1. Preset 结构

确保你的 preset 遵循标准结构:

```text
your-preset/
├── preset.yml                 # 必需: Preset 清单
├── README.md                  # 必需: 文档
├── LICENSE                    # 必需: 许可证文件
├── CHANGELOG.md               # 推荐: 版本历史
│
├── templates/                 # 模板覆盖
│   ├── spec-template.md
│   ├── plan-template.md
│   └── ...
│
└── commands/                  # 命令覆盖(可选)
    └── speckit.specify.md
```

如果你正在创建新 preset, 请从 [scaffold](scaffold/) 开始.

### 2. preset.yml 验证

验证你的清单是否有效:

```yaml
schema_version: "1.0"

preset:
  id: "your-preset"               # 唯一的小写连字符 ID
  name: "Your Preset Name"        # 人类可读名称
  version: "1.0.0"                # 语义版本
  description: "Brief description (one sentence)"
  author: "Your Name or Organization"
  repository: "https://github.com/your-org/spec-kit-preset-your-preset"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"      # 需要的 spec-kit 版本

provides:
  templates:
    - type: "template"
      name: "spec-template"
      file: "templates/spec-template.md"
      description: "Custom spec template"
      replaces: "spec-template"

tags:                              # 2-5 个相关标签
  - "category"
  - "workflow"
```

**验证清单**:

- ✅ `id` 只有小写字母和连字符(没有下划线, 空格或特殊字符)
- ✅ `version` 遵循语义版本控制(X.Y.Z)
- ✅ `description` 简洁(200 字符以内)
- ✅ `repository` URL 有效且公开
- ✅ 所有模板和命令文件存在于 preset 目录中
- ✅ 模板名称只有小写字母和连字符
- ✅ 命令名称使用点表示法(例如 `speckit.specify`)
- ✅ 标签是小写且描述性的

### 3. 本地测试

```bash
# 从本地目录安装
specify-cn preset add --dev /path/to/your-preset

# 验证模板从你的 preset 解析
specify-cn preset resolve spec-template

# 验证 preset 信息
specify-cn preset info your-preset

# 列出已安装的 presets
specify-cn preset list

# 测试完成后移除
specify-cn preset remove your-preset
```

如果你的 preset 包含命令覆盖, 验证它们出现在代理目录中:

```bash
# 检查 Claude 命令(如果使用 Claude)
ls .claude/commands/speckit.*.md

# 检查 Copilot 命令(如果使用 Copilot)
ls .github/agents/speckit.*.agent.md

# 检查 Gemini 命令(如果使用 Gemini)
ls .gemini/commands/speckit.*.toml
```

### 4. 创建 GitHub Release

为你的 preset 版本创建 GitHub release:

```bash
# 标记 release
git tag v1.0.0
git push origin v1.0.0
```

Release 归档 URL 将是:

```text
https://github.com/your-org/spec-kit-preset-your-preset/archive/refs/tags/v1.0.0.zip
```

### 5. 从归档测试安装

```bash
specify-cn preset add --from https://github.com/your-org/spec-kit-preset-your-preset/archive/refs/tags/v1.0.0.zip
```

---

## 提交到目录

### 理解目录

Spec Kit 使用双目录系统:

- **`catalog.json`** — 官方, 已验证的 presets(默认允许安装)
- **`catalog.community.json`** — 社区贡献的 presets(默认仅发现)

所有社区 presets 应该提交到 `catalog.community.json`.

### 1. Fork spec-kit 仓库

```bash
git clone https://github.com/YOUR-USERNAME/spec-kit.git
cd spec-kit
```

### 2. 将 Preset 添加到社区目录

编辑 `presets/catalog.community.json` 并添加你的 preset.

> **⚠️ 条目必须按 preset ID 字母顺序排序.** 在 `"presets"` 对象中将你的 preset 插入到正确位置.

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-03-10T00:00:00Z",
  "catalog_url": "https://raw.githubusercontent.com/github/spec-kit/main/presets/catalog.community.json",
  "presets": {
    "your-preset": {
      "name": "Your Preset Name",
      "description": "Brief description of what your preset provides",
      "author": "Your Name",
      "version": "1.0.0",
      "download_url": "https://github.com/your-org/spec-kit-preset-your-preset/archive/refs/tags/v1.0.0.zip",
      "repository": "https://github.com/your-org/spec-kit-preset-your-preset",
      "license": "MIT",
      "requires": {
        "speckit_version": ">=0.1.0"
      },
      "provides": {
        "templates": 3,
        "commands": 1
      },
      "tags": [
        "category",
        "workflow"
      ],
      "created_at": "2026-03-10T00:00:00Z",
      "updated_at": "2026-03-10T00:00:00Z"
    }
  }
}
```

### 3. 提交 Pull Request

```bash
git checkout -b add-your-preset
git add presets/catalog.community.json
git commit -m "Add your-preset to community catalog

- Preset ID: your-preset
- Version: 1.0.0
- Author: Your Name
- Description: Brief description
"
git push origin add-your-preset
```

**Pull Request 清单**:

```markdown
## Preset Submission

**Preset Name**: Your Preset Name
**Preset ID**: your-preset
**Version**: 1.0.0
**Repository**: https://github.com/your-org/spec-kit-preset-your-preset

### Checklist
- [ ] 有效的 preset.yml 清单
- [ ] 带有描述和用法的 README.md
- [ ] 包含 LICENSE 文件
- [ ] 已创建 GitHub release
- [ ] 使用 `specify-cn preset add --dev` 测试过 preset
- [ ] 模板正确解析(`specify-cn preset resolve`)
- [ ] 命令注册到代理目录(如适用)
- [ ] 命令与模板部分匹配(命令 + 模板一致)
- [ ] 已添加到 presets/catalog.community.json
```

---

## 验证流程

提交后, 维护者将审查:

1. **清单验证** — 有效的 `preset.yml`, 所有文件存在
2. **模板质量** — 模板有用且结构良好
3. **命令一致性** — 命令引用模板中存在的部分
4. **安全性** — 无恶意内容, 安全的文件操作
5. **文档** — 清晰的 README 解释 preset 的作用

一旦验证通过, 会设置 `verified: true`, preset 会出现在 `specify-cn preset search` 中.

---

## 发布工作流

发布新版本时:

1. 更新 `preset.yml` 中的 `version`
2. 更新 CHANGELOG.md
3. 标记并推送: `git tag v1.1.0 && git push origin v1.1.0`
4. 提交 PR 以更新 `presets/catalog.community.json` 中的 `version` 和 `download_url`

---

## 最佳实践

### 模板设计

- **保持部分清晰** — 使用标题和 LLM 可以替换的占位符文本
- **使命令与模板匹配** — 如果你的 preset 覆盖命令, 确保它引用模板中的部分
- **记录自定义点** — 使用 HTML 注释指导用户更改什么

### 命名

- Preset ID 应该具有描述性: `healthcare-compliance`, `enterprise-safe`, `startup-lean`
- 避免通用名称: `my-preset`, `custom`, `test`

### 堆叠

- 设计 presets 以便与其他 presets 堆叠时良好工作
- 只覆盖你需要更改的模板
- 记录你的 preset 修改哪些模板和命令

### 命令覆盖

- 只在工作流需要更改时覆盖命令, 而不仅仅是输出格式
- 如果你只需要不同的模板部分, 模板覆盖就足够了
- 使用多个代理(Claude, Gemini, Copilot)测试命令覆盖

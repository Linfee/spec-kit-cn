# 扩展发布指南

本指南说明如何将你的扩展发布到 Spec Kit 扩展目录, 使其可以通过 `specify extension search` 被发现. 

## 目录

1. [先决条件](#先决条件)
2. [准备你的扩展](#准备你的扩展)
3. [提交到目录](#提交到目录)
4. [验证流程](#验证流程)
5. [发布工作流程](#发布工作流程)
6. [最佳实践](#最佳实践)

---

## 先决条件

在发布扩展之前, 请确保你有:

1. **有效的扩展**: 具有有效 `extension.yml` 清单的工作扩展
2. **Git 仓库**: 托管在 GitHub (或其他公共 git 托管) 的扩展
3. **文档**: 包含安装和使用说明的 README.md
4. **许可证**: 开源许可证文件 (MIT, Apache 2.0 等)
5. **版本控制**: 语义版本控制 (如 1.0.0)
6. **测试**: 在真实项目上测试过的扩展

---

## 准备你的扩展

### 1. 扩展结构

确保你的扩展遵循标准结构:

```text
your-extension/
├── extension.yml              # 必需: 扩展清单
├── README.md                  # 必需: 文档
├── LICENSE                    # 必需: 许可证文件
├── CHANGELOG.md               # 推荐: 版本历史
├── .gitignore                 # 推荐: Git 忽略规则
│
├── commands/                  # 扩展命令
│   ├── command1.md
│   └── command2.md
│
├── config-template.yml        # 配置模板 (如果需要)
│
└── docs/                      # 额外文档
    ├── usage.md
    └── examples/
```

### 2. extension.yml 验证

验证你的清单是否有效:

```yaml
schema_version: "1.0"

extension:
  id: "your-extension"           # 唯一的小写连字符 ID
  name: "Your Extension Name"     # 人类可读名称
  version: "1.0.0"                # 语义版本
  description: "Brief description (one sentence)"
  author: "Your Name or Organization"
  repository: "https://github.com/your-org/spec-kit-your-extension"
  license: "MIT"
  homepage: "https://github.com/your-org/spec-kit-your-extension"

requires:
  speckit_version: ">=0.1.0"    # 必需的 spec-kit 版本

provides:
  commands:                       # 列出所有命令
    - name: "speckit.your-extension.command"
      file: "commands/command.md"
      description: "Command description"

tags:                             # 2-5 个相关标签
  - "category"
  - "tool-name"
```

**验证清单**:

- ✅ `id` 仅包含小写和连字符 (没有下划线, 空格或特殊字符)
- ✅ `version` 遵循语义版本控制 (X.Y.Z)
- ✅ `description` 简洁 (100 字符以内)
- ✅ `repository` URL 有效且公开
- ✅ 所有命令文件存在于扩展目录中
- ✅ 标签为小写且具有描述性

### 3. 创建 GitHub Release

为你的扩展版本创建 GitHub release:

```bash
# 为 release 打标签
git tag v1.0.0
git push origin v1.0.0

# 在 GitHub 上创建 release
# 访问: https://github.com/your-org/spec-kit-your-extension/releases/new
# - Tag: v1.0.0
# - Title: v1.0.0 - Release Name
# - Description: Changelog/release notes
```

Release 归档 URL 将是:

```text
https://github.com/your-org/spec-kit-your-extension/archive/refs/tags/v1.0.0.zip
```

### 4. 测试安装

测试用户可以从你的 release 安装:

```bash
# 测试开发安装
specify extension add --dev /path/to/your-extension

# 从 GitHub 归档测试
specify extension add --from https://github.com/your-org/spec-kit-your-extension/archive/refs/tags/v1.0.0.zip
```

---

## 提交到目录

### 理解目录

Spec Kit 使用双目录系统. 有关目录如何工作的详细信息, 请参阅主 [扩展 README](README.md#扩展目录). 

**对于扩展发布**: 所有社区扩展应该添加到 `catalog.community.json`. 用户浏览此目录并将他们信任的扩展复制到自己的 `catalog.json`. 

### 1. Fork spec-kit 仓库

```bash
# 在 GitHub 上 Fork
# https://github.com/github/spec-kit/fork

# 克隆你的 fork
git clone https://github.com/YOUR-USERNAME/spec-kit.git
cd spec-kit
```

### 2. 添加扩展到社区目录

编辑 `extensions/catalog.community.json` 并添加你的扩展:

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-01-28T15:54:00Z",
  "catalog_url": "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json",
  "extensions": {
    "your-extension": {
      "name": "Your Extension Name",
      "id": "your-extension",
      "description": "Brief description of your extension",
      "author": "Your Name",
      "version": "1.0.0",
      "download_url": "https://github.com/your-org/spec-kit-your-extension/archive/refs/tags/v1.0.0.zip",
      "repository": "https://github.com/your-org/spec-kit-your-extension",
      "homepage": "https://github.com/your-org/spec-kit-your-extension",
      "documentation": "https://github.com/your-org/spec-kit-your-extension/blob/main/docs/",
      "changelog": "https://github.com/your-org/spec-kit-your-extension/blob/main/CHANGELOG.md",
      "license": "MIT",
      "requires": {
        "speckit_version": ">=0.1.0",
        "tools": [
          {
            "name": "required-mcp-tool",
            "version": ">=1.0.0",
            "required": true
          }
        ]
      },
      "provides": {
        "commands": 3,
        "hooks": 1
      },
      "tags": [
        "category",
        "tool-name",
        "feature"
      ],
      "verified": false,
      "downloads": 0,
      "stars": 0,
      "created_at": "2026-01-28T00:00:00Z",
      "updated_at": "2026-01-28T00:00:00Z"
    }
  }
}
```

**重要**:

- 设置 `verified: false` (维护者将验证)
- 设置 `downloads: 0` 和 `stars: 0` (稍后自动更新)
- 使用当前时间戳作为 `created_at` 和 `updated_at`
- 将顶层 `updated_at` 更新为当前时间

### 3. 更新扩展 README

将你的扩展添加到 `extensions/README.md` 中的可用扩展表:

```markdown
| Your Extension Name | Brief description of what it does | [repo-name](https://github.com/your-org/spec-kit-your-extension) |
```

按字母顺序将你的扩展插入表中. 

### 4. 提交 Pull Request

```bash
# 创建分支
git checkout -b add-your-extension

# 提交你的更改
git add extensions/catalog.community.json extensions/README.md
git commit -m "Add your-extension to community catalog

- Extension ID: your-extension
- Version: 1.0.0
- Author: Your Name
- Description: Brief description
"

# 推送到你的 fork
git push origin add-your-extension

# 在 GitHub 上创建 Pull Request
# https://github.com/github/spec-kit/compare
```

**Pull Request 模板**:

```markdown
## Extension Submission

**Extension Name**: Your Extension Name
**Extension ID**: your-extension
**Version**: 1.0.0
**Author**: Your Name
**Repository**: https://github.com/your-org/spec-kit-your-extension

### Description
Brief description of what your extension does.

### Checklist
- [x] Valid extension.yml manifest
- [x] README.md with installation and usage docs
- [x] LICENSE file included
- [x] GitHub release created (v1.0.0)
- [x] Extension tested on real project
- [x] All commands working
- [x] No security vulnerabilities
- [x] Added to extensions/catalog.community.json
- [x] Added to extensions/README.md Available Extensions table

### Testing
Tested on:
- macOS 13.0+ with spec-kit 0.1.0
- Project: [Your test project]

### Additional Notes
Any additional context or notes for reviewers.
```

---

## 验证流程

### 提交后会发生什么

1. **自动检查** (如果可用):
   - 清单验证
   - 下载 URL 可访问性
   - 仓库存在性
   - 许可证文件存在

2. **手动审核**:
   - 代码质量审核
   - 安全审计
   - 功能测试
   - 文档审核

3. **验证**:
   - 如果批准, 设置 `verified: true`
   - 扩展出现在 `specify extension search --verified`

### 验证标准

要获得验证, 你的扩展必须:

✅ **功能性**:

- 按文档描述工作
- 所有命令执行无错误
- 对用户工作流程没有破坏性变更

✅ **安全性**:

- 没有已知漏洞
- 没有恶意代码
- 安全处理用户数据
- 正确验证输入

✅ **代码质量**:

- 干净, 可读的代码
- 遵循扩展最佳实践
- 正确的错误处理
- 有帮助的错误消息

✅ **文档**:

- 清晰的安装说明
- 使用示例
- 故障排除部分
- 准确的描述

✅ **维护**:

- 活跃的仓库
- 及时响应问题
- 定期更新
- 遵循语义版本控制

### 典型审核时间线

- **自动检查**: 立即 (如果已实现)
- **手动审核**: 3-7 个工作日
- **验证**: 成功审核后

---

## 发布工作流程

### 发布新版本

发布新版本时:

1. **更新版本** 在 `extension.yml` 中:

   ```yaml
   extension:
     version: "1.1.0"  # 更新的版本
   ```

2. **更新 CHANGELOG.md**:

   ```markdown
   ## [1.1.0] - 2026-02-15

   ### Added
   - New feature X

   ### Fixed
   - Bug fix Y
   ```

3. **创建 GitHub release**:

   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   # 在 GitHub 上创建 release
   ```

4. **更新目录**:

   ```bash
   # Fork spec-kit repo (或更新现有 fork)
   cd spec-kit

   # 更新 extensions/catalog.json
   jq '.extensions["your-extension"].version = "1.1.0"' extensions/catalog.json > tmp.json && mv tmp.json extensions/catalog.json
   jq '.extensions["your-extension"].download_url = "https://github.com/your-org/spec-kit-your-extension/archive/refs/tags/v1.1.0.zip"' extensions/catalog.json > tmp.json && mv tmp.json extensions/catalog.json
   jq '.extensions["your-extension"].updated_at = "2026-02-15T00:00:00Z"' extensions/catalog.json > tmp.json && mv tmp.json extensions/catalog.json
   jq '.updated_at = "2026-02-15T00:00:00Z"' extensions/catalog.json > tmp.json && mv tmp.json extensions/catalog.json

   # 提交 PR
   git checkout -b update-your-extension-v1.1.0
   git add extensions/catalog.json
   git commit -m "Update your-extension to v1.1.0"
   git push origin update-your-extension-v1.1.0
   ```

5. **提交更新 PR** 并在描述中包含变更日志

---

## 最佳实践

### 扩展设计

1. **单一职责**: 每个扩展应该专注于一个工具/集成
2. **清晰命名**: 使用描述性的, 无歧义的名称
3. **最小依赖**: 避免不必要的依赖
4. **向后兼容**: 严格遵循语义版本控制

### 文档

1. **README.md 结构**:
   - 概述和功能
   - 安装说明
   - 配置指南
   - 使用示例
   - 故障排除
   - 贡献指南

2. **命令文档**:
   - 清晰的描述
   - 列出先决条件
   - 分步说明
   - 错误处理指南
   - 示例

3. **配置**:
   - 提供模板文件
   - 文档化所有选项
   - 包含示例
   - 解释默认值

### 安全

1. **输入验证**: 验证所有用户输入
2. **不要硬编码机密**: 永远不要包含凭据
3. **安全依赖**: 只使用可信的依赖
4. **定期审计**: 检查漏洞

### 维护

1. **响应问题**: 在 1-2 周内解决问题
2. **定期更新**: 保持依赖更新
3. **变更日志**: 维护详细的变更日志
4. **弃用**: 提前通知破坏性变更

### 社区

1. **许可证**: 使用宽松的开源许可证 (MIT, Apache 2.0)
2. **贡献**: 欢迎贡献
3. **行为准则**: 保持尊重和包容
4. **支持**: 提供获取帮助的方式 (问题, 讨论, 邮件)

---

## 常见问题

### Q: 我可以发布私有/专有扩展吗?

A: 主目录仅用于公共扩展. 对于私有扩展:

- 托管你自己的 catalog.json 文件
- 用户添加你的目录: `specify extension add-catalog https://your-domain.com/catalog.json`
- 尚未实现 - 将在 Phase 4 中推出

### Q: 验证需要多长时间?

A: 初次审核通常需要 3-7 个工作日. 对已验证扩展的更新通常更快. 

### Q: 如果我的扩展被拒绝怎么办?

A: 你会收到关于需要修复内容的反馈. 进行更改后重新提交. 

### Q: 我可以随时更新我的扩展吗?

A: 可以, 提交 PR 以使用新版本更新目录. 对于重大变更, 验证状态可能会重新评估. 

### Q: 我需要被验证才能进入目录吗?

A: 不需要, 未验证的扩展仍然可以搜索到. 验证只是增加了信任和可见性. 

### Q: 扩展可以有付费功能吗?

A: 扩展应该是免费和开源的. 商业支持/服务是允许的, 但核心功能必须免费. 

---

## 支持

- **目录问题**: <https://github.com/statsperform/spec-kit/issues>
- **扩展模板**: <https://github.com/statsperform/spec-kit-extension-template> (即将推出)
- **开发指南**: 参见 EXTENSION-DEVELOPMENT-GUIDE.md
- **社区**: 讨论和问答

---

## 附录: 目录 Schema

### 完整目录条目 Schema

```json
{
  "name": "string (required)",
  "id": "string (required, unique)",
  "description": "string (required, <200 chars)",
  "author": "string (required)",
  "version": "string (required, semver)",
  "download_url": "string (required, valid URL)",
  "repository": "string (required, valid URL)",
  "homepage": "string (optional, valid URL)",
  "documentation": "string (optional, valid URL)",
  "changelog": "string (optional, valid URL)",
  "license": "string (required)",
  "requires": {
    "speckit_version": "string (required, version specifier)",
    "tools": [
      {
        "name": "string (required)",
        "version": "string (optional, version specifier)",
        "required": "boolean (default: false)"
      }
    ]
  },
  "provides": {
    "commands": "integer (optional)",
    "hooks": "integer (optional)"
  },
  "tags": ["array of strings (2-10 tags)"],
  "verified": "boolean (default: false)",
  "downloads": "integer (auto-updated)",
  "stars": "integer (auto-updated)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)"
}
```

### 有效标签

推荐的标签类别:

- **集成**: jira, linear, github, gitlab, azure-devops
- **类别**: issue-tracking, vcs, ci-cd, documentation, testing
- **平台**: atlassian, microsoft, google
- **功能**: automation, reporting, deployment, monitoring

使用 2-5 个最能描述你扩展的标签. 

---

*最后更新: 2026-01-28*
*目录格式版本: 1.0*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

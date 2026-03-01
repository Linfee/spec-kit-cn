# 扩展用户指南

使用 Spec Kit 扩展增强工作流程的完整指南. 

## 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [查找扩展](#查找扩展)
4. [安装扩展](#安装扩展)
5. [使用扩展](#使用扩展)
6. [管理扩展](#管理扩展)
7. [配置](#配置)
8. [故障排除](#故障排除)
9. [最佳实践](#最佳实践)

---

## 简介

### 什么是扩展?

扩展是模块化的包, 可以在不膨胀核心框架的情况下为 Spec Kit 添加新命令和功能. 它们允许你:

- **集成** 外部工具 (Jira, Linear, GitHub 等)
- **自动化** 重复性任务
- **自定义** 你团队的工作流程
- **共享** 跨项目的解决方案

### 为什么使用扩展?

- **精简核心**: 保持 spec-kit 轻量级和专注
- **可选功能**: 只安装你需要的
- **社区驱动**: 任何人都可以创建和分享扩展
- **版本控制**: 扩展独立版本化

---

## 快速开始

### 先决条件

- Spec Kit 版本 0.1.0 或更高
- 一个 spec-kit 项目 (包含 `.specify/` 文件夹的目录)

### 检查你的版本

```bash
specify version
# 应该显示 0.1.0 或更高
```

### 第一个扩展

让我们以安装 Jira 扩展为例:

```bash
# 1. 搜索扩展
specify extension search jira

# 2. 获取详细信息
specify extension info jira

# 3. 安装它
specify extension add jira

# 4. 配置它
vim .specify/extensions/jira/jira-config.yml

# 5. 使用它
# (命令现在在 Claude Code 中可用)
/speckit.jira.specstoissues
```

---

## 查找扩展

**注意**: 默认情况下, `specify extension search` 使用你组织的目录 (`catalog.json`). 如果目录为空, 你不会看到任何结果. 请参阅 [扩展目录](#扩展目录) 了解如何从社区参考目录填充你的目录. 

### 浏览所有扩展

```bash
specify extension search
```

显示你组织目录中的所有扩展. 

### 按关键词搜索

```bash
# 搜索 "jira"
specify extension search jira

# 搜索 "issue tracking"
specify extension search issue
```

### 按标签过滤

```bash
# 查找所有问题跟踪扩展
specify extension search --tag issue-tracking

# 查找所有 Atlassian 工具
specify extension search --tag atlassian
```

### 按作者过滤

```bash
# Stats Perform 的扩展
specify extension search --author "Stats Perform"
```

### 仅显示已验证的

```bash
# 只显示已验证的扩展
specify extension search --verified
```

### 获取扩展详情

```bash
# 详细信息
specify extension info jira
```

显示:

- 描述
- 要求
- 提供的命令
- 可用的钩子
- 链接 (文档, 仓库, 变更日志)
- 安装状态

---

## 安装扩展

### 从目录安装

```bash
# 按名称 (从目录)
specify extension add jira
```

这将:

1. 从 GitHub 下载扩展
2. 验证清单
3. 检查与你的 spec-kit 版本的兼容性
4. 安装到 `.specify/extensions/jira/`
5. 向你的 AI 代理注册命令
6. 创建配置模板

### 从 URL 安装

```bash
# 从 GitHub release
specify extension add --from https://github.com/org/spec-kit-ext/archive/refs/tags/v1.0.0.zip
```

### 从本地目录安装 (开发)

```bash
# 用于测试或开发
specify extension add --dev /path/to/extension
```

### 安装输出

```text
✓ 扩展安装成功!

Jira Integration (v1.0.0)
  从 spec-kit 制品创建 Jira Epic, Story 和 Issue

提供的命令:
  • speckit.jira.specstoissues - 从规范和任务创建 Jira 层级结构
  • speckit.jira.discover-fields - 发现 Jira 自定义字段用于配置
  • speckit.jira.sync-status - 将任务完成状态同步到 Jira

⚠  可能需要配置
   检查: .specify/extensions/jira/
```

---

## 使用扩展

### 使用扩展命令

扩展添加的命令会出现在你的 AI 代理 (Claude Code) 中:

```text
# 在 Claude Code 中
> /speckit.jira.specstoissues

# 或使用短别名 (如果提供)
> /speckit.specstoissues
```

### 扩展配置

大多数扩展需要配置:

```bash
# 1. 找到配置文件
ls .specify/extensions/jira/

# 2. 从模板复制配置
cp .specify/extensions/jira/jira-config.template.yml \
   .specify/extensions/jira/jira-config.yml

# 3. 编辑配置
vim .specify/extensions/jira/jira-config.yml

# 4. 使用扩展
# (命令现在将使用你的配置工作)
```

### 扩展钩子

一些扩展提供在核心命令后执行的钩子:

**示例**: Jira 扩展挂钩到 `/speckit.tasks`

```text
# 运行核心命令
> /speckit.tasks

# 输出包括:
## 扩展钩子

**可选钩子**: jira
命令: `/speckit.jira.specstoissues`
描述: 任务生成后自动创建 Jira 层级结构

提示: 从任务创建 Jira issue?
执行: `/speckit.jira.specstoissues`
```

然后你可以选择运行钩子或跳过它. 

---

## 管理扩展

### 列出已安装的扩展

```bash
specify extension list
```

输出:

```text
已安装的扩展:

  ✓ Jira Integration (v1.0.0)
     从 spec-kit 制品创建 Jira Epic, Story 和 Issue
     命令: 3 | 钩子: 1 | 状态: 已启用
```

### 更新扩展

```bash
# 检查更新 (所有扩展)
specify extension update

# 更新特定扩展
specify extension update jira
```

输出:

```text
🔄 检查更新...

可用更新:

  • jira: 1.0.0 → 1.1.0

更新这些扩展? [y/N]:
```

### 临时禁用扩展

```bash
# 禁用但不移除
specify extension disable jira

✓ 扩展 'jira' 已禁用

命令将不再可用. 钩子将不会执行. 
重新启用: specify extension enable jira
```

### 重新启用扩展

```bash
specify extension enable jira

✓ 扩展 'jira' 已启用
```

### 移除扩展

```bash
# 移除扩展 (带确认)
specify extension remove jira

# 移除时保留配置
specify extension remove jira --keep-config

# 强制移除 (无确认)
specify extension remove jira --force
```

---

## 配置

### 配置文件

扩展可以有多个配置文件:

```text
.specify/extensions/jira/
├── jira-config.yml           # 主配置 (版本控制)
├── jira-config.local.yml     # 本地覆盖 (gitignore)
└── jira-config.template.yml  # 模板 (参考)
```

### 配置层级

配置按以下顺序合并 (最后优先级最高):

1. **扩展默认值** (来自 `extension.yml`)
2. **项目配置** (`jira-config.yml`)
3. **本地覆盖** (`jira-config.local.yml`)
4. **环境变量** (`SPECKIT_JIRA_*`)

### 示例: Jira 配置

**项目配置** (`.specify/extensions/jira/jira-config.yml`):

```yaml
project:
  key: "MSATS"

defaults:
  epic:
    labels: ["spec-driven"]
```

**本地覆盖** (`.specify/extensions/jira/jira-config.local.yml`):

```yaml
project:
  key: "MYTEST"  # 本地开发覆盖
```

**环境变量**:

```bash
export SPECKIT_JIRA_PROJECT_KEY="DEVTEST"
```

最终解析的配置使用来自环境变量的 `DEVTEST`. 

### 项目级扩展设置

文件: `.specify/extensions.yml`

```yaml
# 此项目中安装的扩展
installed:
  - jira
  - linear

# 全局设置
settings:
  auto_execute_hooks: true

# 钩子配置
hooks:
  after_tasks:
    - extension: jira
      command: speckit.jira.specstoissues
      enabled: true
      optional: true
      prompt: "从任务创建 Jira issue?"
```

### 核心环境变量

除了扩展特定的环境变量 (`SPECKIT_{EXT_ID}_*`), spec-kit 还支持核心环境变量:

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `SPECKIT_CATALOG_URL`       | 覆盖扩展目录 URL | GitHub 托管的目录 |
| `GH_TOKEN` / `GITHUB_TOKEN` | 用于下载的 GitHub API token | 无 |

#### 示例: 使用自定义目录进行测试

```bash
# 指向本地或替代目录
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"

# 或使用暂存目录
export SPECKIT_CATALOG_URL="https://example.com/staging/catalog.json"
```

---

## 扩展目录

有关 Spec Kit 双目录系统如何工作的信息 (`catalog.json` vs `catalog.community.json`), 请参阅主 [扩展 README](README.md#扩展目录). 

## 组织目录自定义

### 为什么要自定义你的目录

组织自定义他们的 `catalog.json` 以:

- **控制可用扩展** - 精选团队可以安装哪些扩展
- **托管私有扩展** - 不应公开的内部工具
- **合规性自定义** - 满足安全/审计要求
- **支持离线环境** - 在没有互联网访问的情况下工作

### 设置自定义目录

#### 1. 创建你的目录文件

创建一个包含你的扩展的 `catalog.json` 文件:

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-02-03T00:00:00Z",
  "catalog_url": "https://your-org.com/spec-kit/catalog.json",
  "extensions": {
    "jira": {
      "name": "Jira Integration",
      "id": "jira",
      "description": "从 spec-kit 制品创建 Jira issue",
      "author": "Your Organization",
      "version": "2.1.0",
      "download_url": "https://github.com/your-org/spec-kit-jira/archive/refs/tags/v2.1.0.zip",
      "repository": "https://github.com/your-org/spec-kit-jira",
      "license": "MIT",
      "requires": {
        "speckit_version": ">=0.1.0",
        "tools": [
          {"name": "atlassian-mcp-server", "required": true}
        ]
      },
      "provides": {
        "commands": 3,
        "hooks": 1
      },
      "tags": ["jira", "atlassian", "issue-tracking"],
      "verified": true
    },
    "internal-tool": {
      "name": "Internal Tool Integration",
      "id": "internal-tool",
      "description": "连接到内部公司系统",
      "author": "Your Organization",
      "version": "1.0.0",
      "download_url": "https://internal.your-org.com/extensions/internal-tool-1.0.0.zip",
      "repository": "https://github.internal.your-org.com/spec-kit-internal",
      "license": "Proprietary",
      "requires": {
        "speckit_version": ">=0.1.0"
      },
      "provides": {
        "commands": 2
      },
      "tags": ["internal", "proprietary"],
      "verified": true
    }
  }
}
```

#### 2. 托管目录

托管目录的选项:

| 方法 | URL 示例 | 用例 |
| ---- | -------- | ---- |
| GitHub Pages | `https://your-org.github.io/spec-kit-catalog/catalog.json` | 公开或组织可见 |
| 内部 Web 服务器 | `https://internal.company.com/spec-kit/catalog.json` | 企业网络 |
| S3/云存储 | `https://s3.amazonaws.com/your-bucket/catalog.json` | 云托管团队 |
| 本地文件服务器 | `http://localhost:8000/catalog.json` | 开发/测试 |

**安全要求**: URL 必须使用 HTTPS (测试用的 `localhost` 除外). 

#### 3. 配置你的环境

##### 选项 A: 环境变量 (推荐用于 CI/CD)

```bash
# 在 ~/.bashrc, ~/.zshrc 或 CI 管道中
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
```

##### 选项 B: 每项目配置

创建 `.env` 或在运行 spec-kit 命令前在 shell 中设置:

```bash
SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json" specify extension search
```

#### 4. 验证配置

```bash
# 搜索现在应该显示你目录中的扩展
specify extension search

# 从你的目录安装
specify extension add jira
```

### 目录 JSON Schema

每个扩展条目的必需字段:

| 字段 | 类型 | 必需 | 描述 |
| ---- | ---- | ---- | ---- |
| `name` | string | 是 | 人类可读的名称 |
| `id` | string | 是 | 唯一标识符 (小写, 连字符) |
| `version` | string | 是 | 语义版本 (X.Y.Z) |
| `download_url` | string | 是 | ZIP 归档的 URL |
| `repository` | string | 是 | 源代码 URL |
| `description` | string | 否 | 简短描述 |
| `author` | string | 否 | 作者/组织 |
| `license` | string | 否 | SPDX 许可证标识符 |
| `requires.speckit_version` | string | 否 | 版本约束 |
| `requires.tools` | array | 否 | 必需的外部工具 |
| `provides.commands` | number | 否 | 命令数量 |
| `provides.hooks` | number | 否 | 钩子数量 |
| `tags` | array | 否 | 搜索标签 |
| `verified` | boolean | 否 | 验证状态 |

### 用例

#### 私有/内部扩展

托管与内部系统集成的专有扩展:

```json
{
  "internal-auth": {
    "name": "Internal SSO Integration",
    "download_url": "https://artifactory.company.com/spec-kit/internal-auth-1.0.0.zip",
    "verified": true
  }
}
```

#### 精选团队目录

限制团队可以安装哪些扩展:

```json
{
  "extensions": {
    "jira": { "..." },
    "github": { "..." }
  }
}
```

只有 `jira` 和 `github` 会出现在 `specify extension search` 中. 

#### 离线环境

对于没有互联网访问的网络:

1. 下载扩展 ZIP 到内部文件服务器
2. 创建指向内部 URL 的目录
3. 在内部 Web 服务器上托管目录

```json
{
  "jira": {
    "download_url": "https://files.internal/spec-kit/jira-2.1.0.zip"
  }
}
```

#### 开发/测试

在发布前测试新扩展:

```bash
# 启动本地服务器
python -m http.server 8000 --directory ./my-catalog/

# 将 spec-kit 指向本地目录
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"

# 测试安装
specify extension add my-new-extension
```

### 与直接安装结合使用

你仍然可以使用 `--from` 安装不在你目录中的扩展:

```bash
# 从目录
specify extension add jira

# 直接 URL (绕过目录)
specify extension add --from https://github.com/someone/spec-kit-ext/archive/v1.0.0.zip

# 本地开发
specify extension add --dev /path/to/extension
```

**注意**: 直接 URL 安装会显示安全警告, 因为扩展不是来自你配置的目录. 

---

## 故障排除

### 找不到扩展

**错误**: `Extension 'jira' not found in catalog`

**解决方案**:

1. 检查拼写: `specify extension search jira`
2. 刷新目录: `specify extension search --help`
3. 检查互联网连接
4. 扩展可能尚未发布

### 找不到配置

**错误**: `Jira configuration not found`

**解决方案**:

1. 检查扩展是否已安装: `specify extension list`
2. 从模板创建配置:

   ```bash
   cp .specify/extensions/jira/jira-config.template.yml \
      .specify/extensions/jira/jira-config.yml
   ```

3. 重新安装扩展: `specify extension remove jira && specify extension add jira`

### 命令不可用

**问题**: 扩展命令没有出现在 AI 代理中

**解决方案**:

1. 检查扩展是否已启用: `specify extension list`
2. 重启 AI 代理 (Claude Code)
3. 检查命令文件是否存在:

   ```bash
   ls .claude/commands/speckit.jira.*.md
   ```

4. 重新安装扩展

### 版本不兼容

**错误**: `Extension requires spec-kit >=0.2.0, but you have 0.1.0`

**解决方案**:

1. 升级 spec-kit:

   ```bash
   uv tool upgrade specify-cli
   ```

2. 安装旧版本的扩展:

   ```bash
   specify extension add --from https://github.com/org/ext/archive/v1.0.0.zip
   ```

### MCP 工具不可用

**错误**: `Tool 'jira-mcp-server/epic_create' not found`

**解决方案**:

1. 检查 MCP server 是否已安装
2. 检查 AI 代理 MCP 配置
3. 重启 AI 代理
4. 检查扩展要求: `specify extension info jira`

### 权限被拒绝

**错误**: 访问 Jira 时 `Permission denied`

**解决方案**:

1. 检查 MCP server 配置中的 Jira 凭据
2. 验证 Jira 中的项目权限
3. 独立测试 MCP server 连接

---

## 最佳实践

### 1. 版本控制

**要提交**:

- `.specify/extensions.yml` (项目扩展配置)
- `.specify/extensions/*/jira-config.yml` (项目配置)

**不要提交**:

- `.specify/extensions/.cache/` (目录缓存)
- `.specify/extensions/.backup/` (配置备份)
- `.specify/extensions/*/*.local.yml` (本地覆盖)
- `.specify/extensions/.registry` (安装状态)

添加到 `.gitignore`:

```gitignore
.specify/extensions/.cache/
.specify/extensions/.backup/
.specify/extensions/*/*.local.yml
.specify/extensions/.registry
```

### 2. 团队工作流程

**对于团队**:

1. 商定使用哪些扩展
2. 提交扩展配置
3. 在 README 中记录扩展使用
4. 一起保持扩展更新

**示例 README 部分**:

```markdown
## 扩展

此项目使用:
- **jira** (v1.0.0) - Jira 集成
  - 配置: `.specify/extensions/jira/jira-config.yml`
  - 需要: jira-mcp-server

安装: `specify extension add jira`
```

### 3. 本地开发

使用本地配置进行开发:

```yaml
# .specify/extensions/jira/jira-config.local.yml
project:
  key: "DEVTEST"  # 你的测试项目

defaults:
  task:
    custom_fields:
      customfield_10002: 1  # 测试用较低的 story points
```

### 4. 环境特定配置

为 CI/CD 使用环境变量:

```bash
# .github/workflows/deploy.yml
env:
  SPECKIT_JIRA_PROJECT_KEY: ${{ secrets.JIRA_PROJECT }}

- name: Create Jira Issues
  run: specify extension add jira && ...
```

### 5. 扩展更新

**定期检查更新**:

```bash
# 每周或主要发布前
specify extension update
```

**固定版本以保持稳定性**:

```yaml
# .specify/extensions.yml
installed:
  - id: jira
    version: "1.0.0"  # 固定到特定版本
```

### 6. 最小化扩展

只安装你积极使用的扩展:

- 减少复杂性
- 更快的命令加载
- 更少的配置

### 7. 文档

在项目中记录扩展使用:

```markdown
# PROJECT.md

## 使用 Jira

创建任务后, 同步到 Jira:
1. 运行 `/speckit.tasks` 生成任务
2. 运行 `/speckit.jira.specstoissues` 创建 Jira issue
3. 运行 `/speckit.jira.sync-status` 更新状态
```

---

## 常见问题

### Q: 我可以同时使用多个扩展吗?

**A**: 可以! 扩展被设计为可以一起工作. 根据需要安装任意数量. 

### Q: 扩展会减慢 spec-kit 吗?

**A**: 不会. 扩展按需加载, 且仅在使用其命令时加载. 

### Q: 我可以创建私有扩展吗?

**A**: 可以. 使用 `--dev` 或 `--from` 安装并保持私有. 公开目录提交是可选的. 

### Q: 我如何知道扩展是否安全?

**A**: 查找 ✓ Verified 徽章. 已验证的扩展由维护者审核. 安装前始终审核扩展代码. 

### Q: 扩展可以修改 spec-kit 核心吗?

**A**: 不可以. 扩展只能添加命令和钩子. 它们不能修改核心功能. 

### Q: 如果两个扩展有相同的命令名怎么办?

**A**: 扩展使用命名空间命令 (`speckit.{extension}.{command}`), 所以冲突非常罕见. 扩展系统会在发生冲突时警告你. 

### Q: 我可以为现有扩展做贡献吗?

**A**: 可以! 大多数扩展是开源的. 在 `specify extension info {extension}` 中查看仓库链接. 

### Q: 如何报告扩展 bug?

**A**: 前往扩展的仓库 (在 `specify extension info` 中显示) 并创建 issue. 

### Q: 扩展可以离线工作吗?

**A**: 一旦安装, 扩展可以离线工作. 但是, 某些扩展可能需要互联网才能实现其功能 (例如 Jira 需要 Jira API 访问). 

### Q: 如何备份我的扩展配置?

**A**: 扩展配置在 `.specify/extensions/{extension}/` 中. 备份此目录或将配置提交到 git. 

---

## 支持

- **扩展问题**: 报告到扩展仓库 (参见 `specify extension info`)
- **Spec Kit 问题**: <https://github.com/statsperform/spec-kit/issues>
- **扩展目录**: <https://github.com/statsperform/spec-kit/tree/main/extensions>
- **文档**: 参见 EXTENSION-DEVELOPMENT-GUIDE.md 和 EXTENSION-PUBLISHING-GUIDE.md

---

*最后更新: 2026-01-28*
*Spec Kit 版本: 0.1.0*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

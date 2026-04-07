# 扩展用户指南

使用 Spec Kit 扩展增强工作流的完整指南。

## 目录

1. [简介](#简介)
2. [入门](#入门)
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

扩展是模块化的包, 可以为 Spec Kit 添加新命令和功能, 而不会膨胀核心框架。它们允许你:

- **集成**外部工具 (Jira, Linear, GitHub 等)
- **自动化**重复性任务(通过钩子)
- **自定义**团队工作流
- **跨项目**共享解决方案

### 为什么使用扩展?

- **精简核心**: 保持 spec-kit 轻量和专注
- **可选功能**: 只安装你需要的内容
- **社区驱动**: 任何人都可以创建和分享扩展
- **版本控制**: 扩展独立版本控制

---

## 入门

### 先决条件

- Spec Kit 版本 0.1.0 或更高
- 一个 spec-kit 项目 (包含 `.specify/` 文件夹的目录)

### 检查版本

```bash
specify-cn version
# 应显示 0.1.0 或更高
```

### 第一个扩展

以安装 Jira 扩展为例:

```bash
# 1. 搜索扩展
specify-cn extension search jira

# 2. 获取详细信息
specify-cn extension info jira

# 3. 安装
specify-cn extension add jira

# 4. 配置
vim .specify/extensions/jira/jira-config.yml

# 5. 使用
# (命令现在在 Claude Code 中可用)
/speckit.jira.specstoissues
```

---

## 查找扩展

`specify-cn extension search` 同时搜索**所有活跃目录**, 默认包含社区目录。结果标注了源目录和安装状态。

### 浏览所有扩展

```bash
specify-cn extension search
```

显示所有活跃目录中的所有扩展 (默认包含默认目录和社区目录)。

### 按关键词搜索

```bash
# 搜索 "jira"
specify-cn extension search jira

# 搜索 "issue tracking"
specify-cn extension search issue
```

### 按标签过滤

```bash
# 查找所有 issue-tracking 扩展
specify-cn extension search --tag issue-tracking

# 查找所有 Atlassian 工具
specify-cn extension search --tag atlassian
```

### 按作者过滤

```bash
# Stats Perform 的扩展
specify-cn extension search --author "Stats Perform"
```

### 仅显示已验证的扩展

```bash
# 仅显示已验证的扩展
specify-cn extension search --verified
```

### 获取扩展详情

```bash
# 详细信息
specify-cn extension info jira
```

显示:

- 描述
- 要求
- 提供的命令
- 可用的钩子
- 链接 (文档、仓库、更新日志)
- 安装状态

---

## 安装扩展

### 从目录安装

```bash
# 按名称 (从目录)
specify-cn extension add jira
```

这将:

1. 从 GitHub 下载扩展
2. 验证清单
3. 检查与你 spec-kit 版本的兼容性
4. 安装到 `.specify/extensions/jira/`
5. 注册命令到你的 AI 代理
6. 创建配置模板

### 从 URL 安装

```bash
# 从 GitHub Release
specify-cn extension add <extension-name> --from https://github.com/org/spec-kit-ext/archive/refs/tags/v1.0.0.zip
```

### 从本地目录安装 (开发)

```bash
# 用于测试或开发
specify-cn extension add --dev /path/to/extension
```

### 安装输出

```text
✓ Extension installed successfully!

Jira Integration (v1.0.0)
  Create Jira Epics, Stories, and Issues from spec-kit artifacts

Provided commands:
  • speckit.jira.specstoissues - Create Jira hierarchy from spec and tasks
  • speckit.jira.discover-fields - Discover Jira custom fields for configuration
  • speckit.jira.sync-status - Sync task completion status to Jira

⚠  Configuration may be required
   Check: .specify/extensions/jira/
```

### 自动代理技能注册

如果你的项目使用 `--ai-skills` 初始化, 扩展命令在安装期间会**自动注册为代理技能**。这确保使用 [agentskills.io](https://agentskills.io) 技能规范的代理可以发现这些扩展。

```text
✓ Extension installed successfully!

Jira Integration (v1.0.0)
  ...

✓ 3 agent skill(s) auto-registered
```

当扩展被移除时, 其对应的技能也会自动清理。手动自定义的预存技能永远不会被覆盖。

---

## 使用扩展

### 使用扩展命令

扩展添加的命令会出现在你的 AI 代理 (Claude Code) 中:

```text
# 在 Claude Code 中
> /speckit.jira.specstoissues

# 或使用命名空间别名 (如果提供)
> /speckit.jira.sync
```

### 扩展配置

大多数扩展需要配置:

```bash
# 1. 找到配置文件
ls .specify/extensions/jira/

# 2. 从模板复制到配置
cp .specify/extensions/jira/jira-config.template.yml \
   .specify/extensions/jira/jira-config.yml

# 3. 编辑配置
vim .specify/extensions/jira/jira-config.yml

# 4. 使用扩展
# (命令现在将使用你的配置)
```

### 扩展钩子

某些扩展提供在核心命令后执行的钩子:

**示例**: Jira 扩展挂钩到 `/speckit.tasks`

```text
# 运行核心命令
> /speckit.tasks

# 输出包含:
## Extension Hooks

**Optional Hook**: jira
Command: `/speckit.jira.specstoissues`
Description: Automatically create Jira hierarchy after task generation

Prompt: Create Jira issues from tasks?
To execute: `/speckit.jira.specstoissues`
```

然后你可以选择运行钩子或跳过。

---

## 管理扩展

### 列出已安装的扩展

```bash
specify-cn extension list
```

输出:

```text
Installed Extensions:

  ✓ Jira Integration (v1.0.0)
     Create Jira Epics, Stories, and Issues from spec-kit artifacts
     Commands: 3 | Hooks: 1 | Status: Enabled
```

### 更新扩展

```bash
# 检查更新 (所有扩展)
specify-cn extension update

# 更新特定扩展
specify-cn extension update jira
```

输出:

```text
🔄 Checking for updates...

Updates available:

  • jira: 1.0.0 → 1.1.0

Update these extensions? [y/N]:
```

### 临时禁用扩展

```bash
# 禁用但不移除
specify-cn extension disable jira

✓ Extension 'jira' disabled

命令将不再可用。钩子不会执行。
重新启用: specify-cn extension enable jira
```

### 重新启用扩展

```bash
specify-cn extension enable jira

✓ Extension 'jira' enabled
```

### 移除扩展

```bash
# 移除扩展 (带确认)
specify-cn extension remove jira

# 移除时保留配置
specify-cn extension remove jira --keep-config

# 强制移除 (无确认)
specify-cn extension remove jira --force
```

---

## 配置

### 配置文件

扩展可以有多个配置文件:

```text
.specify/extensions/jira/
├── jira-config.yml           # 主配置 (版本控制)
├── jira-config.local.yml     # 本地覆盖 (gitignored)
└── jira-config.template.yml  # 模板 (参考)
```

### 配置层

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
  key: "MYTEST"  # Override for local development
```

**环境变量**:

```bash
export SPECKIT_JIRA_PROJECT_KEY="DEVTEST"
```

最终解析的配置使用来自环境变量的 `DEVTEST`。

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
# 可用事件: before_specify, after_specify, before_plan, after_plan,
#           before_tasks, after_tasks, before_implement, after_implement
# 计划中 (尚未接入核心模板): before_commit, after_commit
hooks:
  after_tasks:
    - extension: jira
      command: speckit.jira.specstoissues
      enabled: true
      optional: true
      prompt: "Create Jira issues from tasks?"
```

### 核心环境变量

除了扩展特定的环境变量 (`SPECKIT_{EXT_ID}_*`), spec-kit 还支持核心环境变量:

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `SPECKIT_CATALOG_URL`       | 使用单个 URL 覆盖整个目录栈 (向后兼容) | 内置默认栈 |
| `GH_TOKEN` / `GITHUB_TOKEN` | GitHub API 令牌用于下载 | None |

#### 示例: 使用自定义目录进行测试

```bash
# 指向本地或替代目录 (替换整个栈)
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"

# 或使用预发布目录
export SPECKIT_CATALOG_URL="https://example.com/staging/catalog.json"
```

---

## 扩展目录

Spec Kit 使用**目录栈** - 一个同时搜索的有序目录列表。默认激活两个目录:

| 优先级 | 目录 | 允许安装 | 用途 |
|----------|---------|-----------------|---------|
| 1 | `catalog.json` (默认) | ✅ 是 | 可安装的策划扩展 |
| 2 | `catalog.community.json` (社区) | ❌ 否 (仅发现) | 浏览社区扩展 |

### 列出活跃目录

```bash
specify-cn extension catalog list
```

### 通过 CLI 管理目录

你可以使用 `--help` 查看主要的目录管理命令:

```text
specify-cn extension catalog --help

 Usage: specify-cn extension catalog [OPTIONS] COMMAND [ARGS]...

 Manage extension catalogs
╭─ Options ────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                      │
╰──────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────╮
│ list     List all active extension catalogs.                                     │
│ add      Add a catalog to .specify/extension-catalogs.yml.                       │
│ remove   Remove a catalog from .specify/extension-catalogs.yml.                  │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

### 添加目录 (项目级)

```bash
# 添加允许安装的内部目录
specify-cn extension catalog add \
  --name "internal" \
  --priority 2 \
  --install-allowed \
  https://internal.company.com/spec-kit/catalog.json

# 添加仅发现目录
specify-cn extension catalog add \
  --name "partner" \
  --priority 5 \
  https://partner.example.com/spec-kit/catalog.json
```

这会创建或更新 `.specify/extension-catalogs.yml`。

### 移除目录

```bash
specify-cn extension catalog remove internal
```

### 手动配置文件

你也可以直接编辑 `.specify/extension-catalogs.yml`:

```yaml
catalogs:
  - name: "default"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json"
    priority: 1
    install_allowed: true
    description: "Built-in catalog of installable extensions"

  - name: "internal"
    url: "https://internal.company.com/spec-kit/catalog.json"
    priority: 2
    install_allowed: true
    description: "Internal company extensions"

  - name: "community"
    url: "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json"
    priority: 3
    install_allowed: false
    description: "Community-contributed extensions (discovery only)"
```

用户级别的等效文件位于 `~/.specify/extension-catalogs.yml`。当项目级配置包含一个或多个目录条目时, 它完全优先。空的 `catalogs: []` 列表会回退到内置默认值。

## 组织目录自定义

### 为什么自定义你的目录

组织自定义目录以:

- **控制可用扩展** - 策划团队可以安装的扩展
- **托管私有扩展** - 不应公开的内部工具
- **合规性自定义** - 满足安全/审计要求
- **支持离线环境** - 在无网络访问的情况下工作

### 设置自定义目录

#### 1. 创建你的目录文件

创建包含你扩展的 `catalog.json` 文件:

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-02-03T00:00:00Z",
  "catalog_url": "https://your-org.com/spec-kit/catalog.json",
  "extensions": {
    "jira": {
      "name": "Jira Integration",
      "id": "jira",
      "description": "Create Jira issues from spec-kit artifacts",
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
      "description": "Connect to internal company systems",
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

| 方式 | URL 示例 | 使用场景 |
| ------ | ----------- | -------- |
| GitHub Pages | `https://your-org.github.io/spec-kit-catalog/catalog.json` | 公开或组织可见 |
| 内部 Web 服务器 | `https://internal.company.com/spec-kit/catalog.json` | 企业网络 |
| S3/云存储 | `https://s3.amazonaws.com/your-bucket/catalog.json` | 云端团队 |
| 本地文件服务器 | `http://localhost:8000/catalog.json` | 开发/测试 |

**安全要求**: URL 必须使用 HTTPS (测试用的 `localhost` 除外)。

#### 3. 配置你的环境

##### 方式 A: 目录栈配置文件 (推荐)

在项目中的 `.specify/extension-catalogs.yml` 中添加:

```yaml
catalogs:
  - name: "my-org"
    url: "https://your-org.com/spec-kit/catalog.json"
    priority: 1
    install_allowed: true
```

或使用 CLI:

```bash
specify-cn extension catalog add \
  --name "my-org" \
  --install-allowed \
  https://your-org.com/spec-kit/catalog.json
```

##### 方式 B: 环境变量 (推荐用于 CI/CD, 单目录)

```bash
# 在 ~/.bashrc, ~/.zshrc 或 CI 管道中
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
```

#### 4. 验证配置

```bash
# 列出活跃目录
specify-cn extension catalog list

# 搜索应该显示你目录中的扩展
specify-cn extension search

# 从你的目录安装
specify-cn extension add jira
```

### 目录 JSON 模式

每个扩展条目的必填字段:

| 字段 | 类型 | 必填 | 描述 |
| ----- | ---- | -------- | ----------- |
| `name` | string | 是 | 人类可读名称 |
| `id` | string | 是 | 唯一标识符 (小写, 连字符) |
| `version` | string | 是 | 语义化版本 (X.Y.Z) |
| `download_url` | string | 是 | ZIP 归档 URL |
| `repository` | string | 是 | 源代码 URL |
| `description` | string | 否 | 简短描述 |
| `author` | string | 否 | 作者/组织 |
| `license` | string | 否 | SPDX 许可证标识符 |
| `requires.speckit_version` | string | 否 | 版本约束 |
| `requires.tools` | array | 否 | 所需的外部工具 |
| `provides.commands` | number | 否 | 命令数量 |
| `provides.hooks` | number | 否 | 钩子数量 |
| `tags` | array | 否 | 搜索标签 |
| `verified` | boolean | 否 | 验证状态 |

### 使用场景

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

#### 策划的团队目录

限制团队可以安装的扩展:

```json
{
  "extensions": {
    "jira": { "..." },
    "github": { "..." }
  }
}
```

只有 `jira` 和 `github` 会出现在 `specify-cn extension search` 中。

#### 离线环境

对于没有网络访问的环境:

1. 将扩展 ZIP 下载到内部文件服务器
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

# 指定 spec-kit 使用本地目录
export SPECKIT_CATALOG_URL="http://localhost:8000/catalog.json"

# 测试安装
specify-cn extension add my-new-extension
```

### 结合直接安装

你仍然可以使用 `--from` 安装不在你目录中的扩展:

```bash
# 从目录
specify-cn extension add jira

# 直接 URL (绕过目录)
specify-cn extension add <extension-name> --from https://github.com/someone/spec-kit-ext/archive/v1.0.0.zip

# 本地开发
specify-cn extension add --dev /path/to/extension
```

**注意**: 直接 URL 安装会显示安全警告, 因为该扩展不是来自你配置的目录。

---

## 故障排除

### 找不到扩展

**错误**: `Extension 'jira' not found in catalog`

**解决方案**:

1. 检查拼写: `specify-cn extension search jira`
2. 刷新目录: `specify-cn extension search --help`
3. 检查网络连接
4. 扩展可能尚未发布

### 找不到配置

**错误**: `Jira configuration not found`

**解决方案**:

1. 检查扩展是否已安装: `specify-cn extension list`
2. 从模板创建配置:

   ```bash
   cp .specify/extensions/jira/jira-config.template.yml \
      .specify/extensions/jira/jira-config.yml
   ```

3. 重新安装扩展: `specify-cn extension remove jira && specify-cn extension add jira`

### 命令不可用

**问题**: 扩展命令没有出现在 AI 代理中

**解决方案**:

1. 检查扩展是否已启用: `specify-cn extension list`
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
   uv tool upgrade specify-cn-cli
   ```

2. 安装旧版本的扩展:

   ```bash
   specify-cn extension add <extension-name> --from https://github.com/org/ext/archive/v1.0.0.zip
   ```

### MCP 工具不可用

**错误**: `Tool 'jira-mcp-server/epic_create' not found`

**解决方案**:

1. 检查 MCP 服务器是否已安装
2. 检查 AI 代理的 MCP 配置
3. 重启 AI 代理
4. 检查扩展要求: `specify-cn extension info jira`

### 权限被拒绝

**错误**: `Permission denied` 访问 Jira 时

**解决方案**:

1. 检查 MCP 服务器配置中的 Jira 凭据
2. 验证 Jira 中的项目权限
3. 独立测试 MCP 服务器连接

---

## 最佳实践

### 1. 版本控制

**应该提交**:

- `.specify/extensions.yml` (项目扩展配置)
- `.specify/extensions/*/jira-config.yml` (项目配置)

**不应提交**:

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

### 2. 团队工作流

**适用于团队**:

1. 约定使用的扩展
2. 提交扩展配置
3. 在 README 中记录扩展用法
4. 共同保持扩展更新

**示例 README 部分**:

```markdown
## Extensions

This project uses:
- **jira** (v1.0.0) - Jira integration
  - Config: `.specify/extensions/jira/jira-config.yml`
  - Requires: jira-mcp-server

To install: `specify-cn extension add jira`
```

### 3. 本地开发

使用本地配置进行开发:

```yaml
# .specify/extensions/jira/jira-config.local.yml
project:
  key: "DEVTEST"  # Your test project

defaults:
  task:
    custom_fields:
      customfield_10002: 1  # Lower story points for testing
```

### 4. 环境特定配置

在 CI/CD 中使用环境变量:

```bash
# .github/workflows/deploy.yml
env:
  SPECKIT_JIRA_PROJECT_KEY: ${{ secrets.JIRA_PROJECT }}

- name: Create Jira Issues
  run: specify-cn extension add jira && ...
```

### 5. 扩展更新

**定期检查更新**:

```bash
# 每周或重大发布前
specify-cn extension update
```

**固定版本以保持稳定性**:

```yaml
# .specify/extensions.yml
installed:
  - id: jira
    version: "1.0.0"  # Pin to specific version
```

### 6. 精简扩展

只安装你实际使用的扩展:

- 减少复杂性
- 更快的命令加载
- 更少的配置

### 7. 文档

在项目中记录扩展用法:

```markdown
# PROJECT.md

## Working with Jira

After creating tasks, sync to Jira:
1. Run `/speckit.tasks` to generate tasks
2. Run `/speckit.jira.specstoissues` to create Jira issues
3. Run `/speckit.jira.sync-status` to update status
```

---

## FAQ

### Q: 我可以同时使用多个扩展吗?

**A**: 可以! 扩展设计为协同工作。安装你需要的任意数量。

### Q: 扩展会拖慢 spec-kit 吗?

**A**: 不会。扩展按需加载, 只在使用其命令时才加载。

### Q: 我可以创建私有扩展吗?

**A**: 可以。使用 `--dev` 或 `--from` 安装并保持私有。公共目录提交是可选的。

### Q: 我如何知道扩展是否安全?

**A**: 查找 ✓ Verified 标志。已验证的扩展由维护者审查。安装前务必审查扩展代码。

### Q: 扩展可以修改 spec-kit 核心吗?

**A**: 不可以。扩展只能添加命令和钩子。它们不能修改核心功能。

### Q: 如果两个扩展有相同的命令名怎么办?

**A**: 扩展使用命名空间命令 (`speckit.{extension}.{command}`), 所以冲突非常罕见。扩展系统会在冲突发生时发出警告。

### Q: 我可以为现有扩展做贡献吗?

**A**: 可以! 大多数扩展都是开源的。查看 `specify-cn extension info {extension}` 中的仓库链接。

### Q: 如何报告扩展缺陷?

**A**: 前往扩展的仓库 (在 `specify-cn extension info` 中显示) 并创建 Issue。

### Q: 扩展可以离线使用吗?

**A**: 安装后, 扩展可以离线使用。但某些扩展可能需要网络连接才能实现其功能 (如 Jira 需要 Jira API 访问)。

### Q: 如何备份我的扩展配置?

**A**: 扩展配置位于 `.specify/extensions/{extension}/`。备份此目录或将配置提交到 Git。

---

## 支持

- **扩展问题**: 报告到扩展仓库 (参见 `specify-cn extension info`)
- **Spec Kit 问题**: <https://github.com/Linfee/spec-kit-cn/issues>
- **扩展目录**: <https://github.com/Linfee/spec-kit-cn/tree/main/extensions>
- **文档**: 参见 EXTENSION-DEVELOPMENT-GUIDE.md 和 EXTENSION-PUBLISHING-GUIDE.md

---

*最后更新: 2026-01-28*
*Spec Kit 版本: 0.1.0*

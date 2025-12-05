# 快速开始指南

本指南将帮助你使用 Spec Kit 开始规范驱动开发.

> [!NOTE]
> 所有自动化脚本现在都提供 Bash (`.sh`) 和 PowerShell (`.ps1`) 两种版本. `specify-cn` CLI 会根据操作系统自动选择, 除非你传递 `--script sh|ps` 参数.

## 6 步流程

> [!TIP]
> **上下文感知**: Spec Kit 命令会根据你当前的 Git 分支（例如 `001-feature-name`）自动检测活跃的功能. 要在不同规范之间切换, 只需切换 Git 分支.

### 步骤 1: 安装 Specify CN

**在终端中**, 运行 `specify-cn` CLI 命令来初始化你的项目:

```bash
# 创建新项目目录
uvx --from git+https://github.com/linfee/spec-kit-cn.git specify-cn init <PROJECT_NAME>

# 或在当前目录初始化
uvx --from git+https://github.com/linfee/spec-kit-cn.git specify-cn init .
```

显式选择脚本类型（可选）:

```bash
uvx --from git+https://github.com/linfee/spec-kit-cn.git specify-cn init <PROJECT_NAME> --script ps  # 强制使用 PowerShell
uvx --from git+https://github.com/linfee/spec-kit-cn.git specify-cn init <PROJECT_NAME> --script sh  # 强制使用 POSIX shell
```

### 步骤 2: 定义你的章程

**在你的 AI Agent 聊天界面中**, 使用 `/speckit.constitution` 斜杠命令来为你的项目建立核心规则和原则. 你应该提供项目的具体原则作为参数.

```markdown
constitution 本项目遵循"库优先"方法. 所有功能必须首先作为独立库实现. 我们严格使用 TDD. 我们偏好函数式编程模式.
```

### 步骤 3: 创建规范

**在聊天中**, 使用 `/speckit.specify` 斜杠命令来描述你想要构建的内容. 重点关注**做什么**和**为什么**, 而不是技术栈.

```markdown
/speckit.specify 构建一个可以帮助我将照片整理到不同相册中的应用程序. 相册按日期分组, 可以通过在主页上拖拽来重新组织. 相册不会嵌套在其他相册中. 在每个相册内, 照片以瓦片式界面预览.
```

### 步骤 4: 优化规范

**在聊天中**, 使用 `/speckit.clarify` 斜杠命令来识别和解决规范中的歧义. 你可以提供具体的关注领域作为参数.

```bash
clarify 重点关注安全性和性能要求.
```

### 步骤 5: 创建技术实施计划

**在聊天中**, 使用 `/speckit.plan` 斜杠命令来提供你的技术栈和架构选择.

```markdown
plan 应用程序使用 Vite 和最少数量的库. 尽可能使用纯 HTML、CSS 和 JavaScript. 图片不会上传到任何地方, 元数据存储在本地 SQLite 数据库中.
```

### 步骤 6: 分解并实施

**在聊天中**, 使用 `/speckit.tasks` 斜杠命令来创建可操作的任务列表.

```markdown
tasks
```

可选地, 使用 `/speckit.analyze` 验证计划:

```markdown
analyze
```

然后, 使用 `/speckit.implement` 斜杠命令来执行计划.

```markdown
implement
```

## 详细示例: 构建 Taskify

以下是构建团队生产力平台的完整示例:

### 步骤 1: 定义章程

初始化项目的章程以设置基本规则:

```markdown
constitution Taskify 是一个"安全优先"的应用程序. 所有用户输入必须经过验证. 我们使用微服务架构. 代码必须完全文档化.
```

### 步骤 2: 使用 `specify` 定义需求

```text
开发 Taskify, 一个团队生产力平台. 它应该允许用户创建项目、添加团队成员、
分配任务、评论以及以看板风格在板块之间移动任务. 在这个功能的初始阶段,
我们称之为"创建 Taskify", 我们将有多个用户, 但这些用户将提前声明、预定义.
我想要五个用户, 分为两个不同类别: 一个产品经理和四个工程师. 让我们创建三个
不同的示例项目. 让我们为每个任务的状态设置标准的看板列, 如"待办"、
"进行中"、"审核中"和"已完成". 这个应用程序将没有登录功能, 因为这只是
确保我们基本功能设置好的第一个测试.
```

### 步骤 3: 优化规范

使用 `clarify` 命令交互式地解决规范中的任何歧义. 你也可以提供你想要确保包含的具体细节.

```bash
clarify 我想澄清任务卡片的详细信息. 对于 UI 中的任务卡片, 你应该能够更改任务在看板工作板的不同列之间的当前状态. 你应该能够为特定卡片留下无限数量的评论. 你应该能够从该任务卡片中分配一个有效用户.
```

你可以继续使用 `clarify` 优化规范的更多细节:

```bash
clarify 当你首次启动 Taskify 时, 它会为你提供五个用户供你选择. 不需要密码. 当你点击用户时, 你进入主视图, 显示项目列表. 当你点击项目时, 你会打开该项目的看板. 你将看到这些列. 你将能够在不同列之间来回拖放卡片. 你将看到分配给你(当前登录用户)的卡片与其他卡片颜色不同, 这样你就可以快速看到你的卡片. 你可以编辑你所做的任何评论, 但不能编辑其他人所做的评论. 你可以删除你所做的任何评论, 但不能删除其他人所做的评论.
```

### 步骤 4: 验证规范

使用 `checklist` 命令验证规范清单:

```bash
checklist
```

### 步骤 5: 使用 `plan` 生成技术计划

具体说明你的技术栈和技术要求:

```bash
plan 我们将使用 .NET Aspire 生成这个, 使用 Postgres 作为数据库. 前端应该使用 Blazor server, 具有拖拽式任务板和实时更新功能. 应该创建一个 REST API, 包含项目 API、任务 API 和通知 API.
```

### 步骤 6: 验证并实施

让你的 AI 代理使用 `analyze` 审计实施计划:

```bash
analyze
```

最后, 实施解决方案:

```bash
implement
```

## 关键原则

- **明确说明**你要构建什么以及为什么
- **在规范阶段不要关注技术栈**
- **在实施前迭代和优化**你的规范
- **在编码开始前验证**计划
- **让 AI 代理处理**实施细节

## 下一步

- 阅读[完整的方法论](../spec-driven.md)以获取深入指导
- 在仓库中查看[更多示例](../templates)
- 在 GitHub 上探索[源代码](https://github.com/linfee/spec-kit-cn)

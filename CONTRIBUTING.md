# 为 Spec Kit CN 做贡献

你好! 我们很高兴你愿意为 Spec Kit CN 做出贡献. 本项目的贡献内容根据[项目开源许可证](LICENSE)向公众发布.

请注意, 本项目随[贡献者行为准则](CODE_OF_CONDUCT.md)一起发布. 参与本项目即表示你同意遵守其条款.

## 运行和测试代码的先决条件

这些是在提交拉取请求(PR)过程中, 能够在本地测试你的更改所需的一次性安装.

1. 安装 [Python 3.11+](https://www.python.org/downloads/)
1. 安装 [uv](https://docs.astral.sh/uv/) 用于包管理
1. 安装 [Git](https://git-scm.com/downloads)
1. 准备一个可用的 [AI 编码代理](README.md#-supported-ai-agents)

<details>
<summary><b>💡 如果你使用 <code>VSCode</code> 或 <code>GitHub Codespaces</code> 作为 IDE 的提示</b></summary>

<br>

只要你的机器上安装了 [Docker](https://docker.com)，你就可以通过这个 [VSCode 扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) 利用 [Dev Containers](https://containers.dev)，轻松设置你的开发环境。由于项目根目录中的 `.devcontainer/devcontainer.json` 文件，上述工具已经预先安装和配置。

为此，只需：

- 检出仓库
- 使用 VSCode 打开
- 打开 [命令面板](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) 并选择 "Dev Containers: Open Folder in Container..."

在 [GitHub Codespaces](https://github.com/features/codespaces) 上更简单，因为它在打开 codespace 时自动利用 `.devcontainer/devcontainer.json`。

</details>

## 提交拉取请求

>[!NOTE]
>如果你的拉取请求引入了对 CLI 或仓库其他部分工作产生实质性影响的大型更改(例如, 引入新模板、参数或其他重大更改), 请确保该更改已**经过项目维护者的讨论和同意**. 未经事先对话和同意的大型更改拉取请求将被关闭.

1. Fork 并克隆仓库
1. 配置和安装依赖项: `uv sync`
1. 确保 CLI 在你的机器上正常工作: `uv run specify-cn --help`
1. 创建新分支: `git checkout -b my-branch-name`
1. 进行更改, 添加测试, 并确保一切仍然正常工作
1. 如果相关, 使用示例项目测试 CLI 功能
1. 推送到你的 fork 并提交拉取请求
1. 等待你的拉取请求被审查和合并.

以下是一些可以增加你的拉取请求被接受几率的方法: 

- 遵循项目的编码规范.
- 为新功能编写测试.
- 如果你的更改影响用户可见的功能, 请更新文档(`README.md`、`spec-driven.md`).
- 尽可能保持你的更改专注. 如果你想进行多个相互不依赖的更改, 考虑将它们作为单独的拉取请求提交.
- 编写[良好的提交消息](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
- 使用 Spec-Driven Development 工作流测试你的更改以确保兼容性.

## 开发工作流

在处理 spec-kit 时:

1. 在你选择的编码代理中使用 `specify-cn` CLI 命令(`/speckit.specify`、`/speckit.plan`、`/speckit.tasks`)测试更改
2. 验证 `templates/` 目录中的模板是否正常工作
3. 测试 `scripts/` 目录中的脚本功能
4. 如果进行了重大的流程更改, 确保更新内存文件(`memory/constitution.md`)

### 本地测试模板和命令更改

运行 `uv run specify-cn init` 会拉取已发布的包，这些包不包括你的本地更改。
要在本地测试你的模板、命令和其他更改，请按照以下步骤操作：

1. **创建发布包**

   运行以下命令生成本地包：
   ```
   ./.github/workflows/scripts/create-release-packages.sh v1.0.0
   ```

2. **将相关包复制到你的测试项目**

   ```
   cp -r .genreleases/sdd-copilot-package-sh/. <path-to-test-project>/
   ```

3. **打开并测试代理**

   导航到你的测试项目文件夹并打开代理来验证你的实现。

## Spec Kit 中的 AI 贡献

> [!IMPORTANT]
>
> 如果你使用**任何类型的 AI 辅助**为 Spec Kit 做出贡献, 
> 必须在拉取请求或 issue 中披露.

我们欢迎并鼓励使用 AI 工具来帮助改进 Spec Kit! 许多有价值的贡献都通过 AI 辅助进行了代码生成、问题检测和功能定义的增强.

也就是说, 如果你在为 Spec Kit 做贡献时使用任何类型的 AI 辅助(例如, 代理、ChatGPT), 
**必须在拉取请求或 issue 中披露这一点**, 同时说明使用 AI 辅助的程度(例如, 文档注释 vs 代码生成).

如果你的 PR 响应或评论是由 AI 生成的, 也要披露这一点.

作为例外, 琐碎的间距或拼写错误修复不需要披露, 只要更改仅限于代码的小部分或短语.

披露示例: 

> 此 PR 主要由 GitHub Copilot 编写.

或者更详细的披露: 

> 我咨询了 ChatGPT 来理解代码库, 但解决方案
> 完全由我手动编写.

不披露这一点首先对拉取请求另一端的人类操作员是不礼貌的, 但也使得难以确定
对贡献应用多少审查力度.

在一个完美的世界里, AI 辅助会产生比任何人类同等或更高质量的工作. 那不是我们今天生活的世界, 在大多数情况下
在没有人类监督或专业知识的循环中, 它生成无法合理维护或演进的代码.

### 我们在寻找什么

提交 AI 辅助贡献时, 请确保它们包括: 

- **明确披露 AI 使用** - 你对 AI 使用透明, 并说明你在贡献中使用它的程度
- **人类理解和测试** - 你亲自测试了更改并理解它们的作用
- **明确的理由** - 你可以解释为什么需要更改以及它如何适应 Spec Kit 的目标
- **具体证据** - 包括展示改进的测试用例、场景或示例
- **你自己的分析** - 分享你对端到端开发体验的想法

### 我们会关闭的内容

我们保留关闭看起来是以下内容的贡献的权利: 

- 未经验证提交的未测试更改
- 不解决特定 Spec Kit 需求的通用建议
- 显示没有人类审查或理解的大批量提交

### 成功指南

关键是证明你理解并验证了你提议的更改. 如果维护者可以轻易看出贡献完全由 AI 生成而没有人类输入或测试, 它在提交前可能需要更多工作.

持续提交低质量 AI 生成更改的贡献者可能会被维护者自行决定限制进一步贡献.

请尊重维护者并披露 AI 辅助.

## 资源

- [Spec-Driven Development 方法论](./spec-driven.md)
- [如何为开源做贡献](https://opensource.guide/how-to-contribute/)
- [使用拉取请求](https://help.github.com/articles/about-pull-requests/)
- [GitHub 帮助](https://help.github.com)

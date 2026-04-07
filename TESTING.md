# 测试指南

本文档是 [`CONTRIBUTING.md`](./CONTRIBUTING.md) 的详细测试配套文档.

它的用途有三:

1. 在手动测试前运行快速自动化检查,
2. 通过 AI 代理手动测试受影响的斜杠命令, 以及
3. 以 PR 友好的格式捕获结果.

任何影响斜杠命令行为的更改都需要通过 AI 代理手动测试该命令, 并在 PR 中提交结果.

## 推荐顺序

1. **同步你的环境** — 安装项目和测试依赖.
2. **运行聚焦的自动化检查** — 特别是针对打包, 脚手架, 代理配置和生成文件变更.
3. **运行手动代理测试** — 针对所有受影响的斜杠命令.
4. **将结果粘贴到你的 PR 中** — 同时包含命令选择理由和手动测试结果.

## 快速自动化检查

当你的更改影响打包, 脚手架, 模板, 发布制品或代理连接时, 在手动测试前运行这些检查.

### 环境设置

```bash
cd <spec-kit-repo>
uv sync --extra test
source .venv/bin/activate  # Windows (CMD): .venv\Scripts\activate  |  (PowerShell): .venv\Scripts\Activate.ps1
```

### 生成的包结构和内容

```bash
uv run python -m pytest tests/test_core_pack_scaffold.py -q
```

这会验证 CI 风格打包所依赖的生成文件, 包括目录布局, 文件名, frontmatter/TOML 有效性, 占位符替换, `.specify/` 路径重写以及与 `create-release-packages.sh` 的一致性.

### 代理配置和发布连接一致性

```bash
uv run python -m pytest tests/test_agent_config_consistency.py -q
```

当你更改代理元数据, 发布脚本, 上下文更新脚本或制品命名时运行此命令.

### 可选的单代理打包抽查

```bash
AGENTS=copilot SCRIPTS=sh ./.github/workflows/scripts/create-release-packages.sh v1.0.0
```

当你想查看一个代理/脚本组合的确切打包输出时, 检查 `.genreleases/sdd-copilot-package-sh/` 和 `.genreleases/` 中匹配的 ZIP 文件.

## 手动测试流程

1. **识别受影响的命令** — 使用下面的[提示](#确定需要运行的测试)让你的代理分析更改的文件并确定哪些命令需要测试.
2. **设置测试项目** — 从你的本地分支搭建(参见[设置](#设置)).
3. **运行每个受影响的命令** — 在你的代理中调用它, 验证它成功完成, 并确认它产生预期的输出(创建的文件, 执行的脚本, 填充的制品).
4. **先运行先决条件** — 依赖于先前命令的命令(例如, `/speckit.tasks` 需要 `/speckit.plan`, 后者又需要 `/speckit.specify`)必须按顺序运行.
5. **报告结果** — 将[报告模板](#报告结果)粘贴到你的 PR 中, 包含每个测试命令的通过/失败状态.

## 设置

```bash
# 从本地分支安装项目和测试依赖
cd <spec-kit-repo>
uv sync --extra test
source .venv/bin/activate  # Windows (CMD): .venv\Scripts\activate  |  (PowerShell): .venv\Scripts\Activate.ps1
uv pip install -e .
# 确保此环境中的 `specify-cn` 二进制文件指向你的工作树, 以便代理运行你正在测试的分支.

# 使用本地更改初始化测试项目
uv run specify-cn init /tmp/speckit-test --ai <agent> --offline
cd /tmp/speckit-test

# 在你的代理中打开
```

如果你正在测试打包输出而不是实时源代码树, 请先按照 [`CONTRIBUTING.md`](./CONTRIBUTING.md) 中的说明创建本地发布包.

## 报告结果

将此模板粘贴到你的 PR 中:

~~~markdown
## 手动测试结果

**代理**: [例如, VS Code 中的 GitHub Copilot]  |  **操作系统/Shell**: [例如, macOS/zsh]

| 测试的命令 | 备注 |
|------------|------|
| `/speckit.command` | |
~~~

## 确定需要运行的测试

将此提示复制到你的代理中. 在你的 PR 中包含代理的响应(选择的测试和映射的简要说明).

~~~text
阅读 TESTING.md, 然后运行 `git diff --name-only main` 获取我更改的文件.
对于每个更改的文件, 通过阅读 templates/commands/ 中的命令模板来确定它影响哪些斜杠命令,
以了解每个命令调用了什么. 使用以下映射规则:

- templates/commands/X.md → 它定义的命令
- scripts/bash/Y.sh 或 scripts/powershell/Y.ps1 → 调用该脚本的每个命令(在 templates/commands/ 中搜索脚本名称).
  还要检查传递依赖: 如果更改的脚本被其他脚本 source(例如, common.sh 被 create-new-feature.sh, check-prerequisites.sh,
  setup-plan.sh, update-agent-context.sh source), 那么调用这些下游脚本的每个命令也受影响
- templates/Z-template.md → 在执行期间消费该模板的每个命令
- src/specify_cli/*.py → CLI 命令(`specify init`, `specify check`, `specify extension *`, `specify preset *`);
  测试受影响的 CLI 命令, 对于 init/脚手架更改, 至少测试 /speckit.specify
- extensions/X/commands/* → 它定义的扩展命令
- extensions/X/scripts/* → 调用该脚本的每个扩展命令
- extensions/X/extension.yml 或 config-template.yml → 该扩展中的每个命令.
  还要检查清单是否定义了钩子(查找 `hooks:` 条目, 如 `before_specify`, `after_implement` 等) —
  如果是, 这些钩子附加到的核心命令也受影响
- presets/*/* → 通过 `specify-cn init` 测试预设脚手架
- pyproject.toml → 打包/捆绑; 测试 `specify-cn init` 并验证捆绑的资产

包含先决条件测试(例如, T5 需要 T3, T3 需要 T1).

以以下格式输出:

### 测试选择理由

| 更改的文件 | 影响 | 测试 | 原因 |
|---|---|---|---|
| (路径) | (命令) | T# | (原因) |

### 必需的测试

按顺序编号每个测试(T1, T2, ...). 先列出先决条件测试.

- T1: /speckit.command — (原因)
- T2: /speckit.command — (原因)
~~~

---
name: release-post-verify
description: 在临时目录中用 uvx 或 uv tool run 安装 specify-cn 的 main 分支最新提交，对源码声明支持的 agent 执行 init，并校验版本、中文化、模板完整性、agent 文件落点与 ai-skills 安装结果。用于本地发布后验收。
disable-model-invocation: true
---

# 发布后本地验收

这个 skill 只用于手动触发，不应自动执行。

## 目标

验证 `specify-cn` 的 `main` 分支最新提交是否满足以下条件：

1. 安装到的是目标最新版
2. CLI 输出仍然是中文
3. 对全部支持的 agent 都能成功执行 `init`
4. `.specify/templates`、`.specify/memory`、脚本目录完整
5. agent 命令/工作流/提示文件落在正确位置
6. `--ai-skills` 模式下，skills 安装在正确位置且内容基本正确

## 使用方式

默认全量执行：

```bash
python3 .claude/skills/release-post-verify/validate_release_post.py
```

常用变体：

```bash
# 仅跑部分 agent
python3 .claude/skills/release-post-verify/validate_release_post.py --agents claude copilot q

# 保留临时目录
python3 .claude/skills/release-post-verify/validate_release_post.py --keep-temp

# 跳过 ai-skills 或 PowerShell 抽样
python3 .claude/skills/release-post-verify/validate_release_post.py --skip-ai-skills --skip-ps-sample
```

## 执行要求

1. 先读取脚本输出，不要手工猜测 agent 列表；脚本会从仓库源码中的 `AGENT_CONFIG` 动态取值。
2. 必须通过远端 `main` 分支最新提交运行，禁止回退到本地源码、本地 wheel 或当前工作区环境：
   - 首选 `uvx --isolated --from git+https://github.com/linfee/spec-kit-cn@main specify-cn`
   - 失败时再尝试 `uv tool run --isolated --from git+https://github.com/linfee/spec-kit-cn@main specify-cn`
   - 任何情况下都不能使用 `uv run specify-cn`、本地 editable 安装、仓库内 wheel 文件或本地路径依赖代替发布包
3. 脚本会优先复用现有 `GH_TOKEN` / `GITHUB_TOKEN`，否则尝试读取 `gh auth token`，并自动传给需要访问 GitHub API 的命令。
4. 所有初始化必须在临时目录进行，不要把验证产物写回仓库。
5. 默认应跑完整轮，即使某个 agent 失败，也继续其余 agent，最后统一汇总。
6. 若脚本返回非零退出码，不要宣称验证通过；先根据报告定位失败项。

## 输出解读

脚本会输出：

- 使用的 runner
- 目标版本
- 临时目录位置
- JSON 报告路径
- 每个 agent 的 `normal-init` / `ai-skills-init` / `powershell-sample` 状态

如果失败，临时目录会自动保留，便于继续排查。

## 完成时的回复要求

完成后只给用户简短结论，至少包含：

1. 是否通过
2. 失败的 agent 或失败类别
3. 临时目录或报告路径（若失败）

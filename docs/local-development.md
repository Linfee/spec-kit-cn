# 本地开发指南

本指南展示如何在本地对 `specify-cn` CLI 进行迭代开发, 无需先发布版本或提交到 `main` 分支.

> 脚本现在同时提供 Bash(`.sh`)和 PowerShell(`.ps1`)两种变体. CLI 会根据操作系统自动选择, 除非你传递 `--script sh|ps` 参数.

## 1. 克隆和切换分支

```bash
git clone https://github.com/linfee/spec-kit-cn.git
cd spec-kit-cn
# 在功能分支上工作
git checkout -b your-feature-branch
```

## 2. 直接运行 CLI(最快的反馈)

你可以通过模块入口点执行 CLI, 无需安装任何东西: 

```bash
# 从仓库根目录
python -m src.specify_cli --help
python -m src.specify_cli init demo-project --ai claude --ignore-agent-tools --script sh
```

如果你更喜欢调用脚本文件的方式(使用 shebang): 

```bash
python src/specify_cli/__init__.py init demo-project --script ps
```

## 3. 使用可编辑安装(隔离环境)

使用 `uv` 创建隔离环境, 这样依赖项的解析方式与最终用户完全一致: 

```bash
# 创建并激活虚拟环境(uv 自动管理 .venv)
uv venv
source .venv/bin/activate  # 或在 Windows 上: .venv\\Scripts\\activate

# 以可编辑模式安装项目
uv pip install -e .

# 现在 'specify-cn' 入口点可用
specify-cn --help
```

由于是可编辑模式, 代码编辑后重新运行无需重新安装.

## 4. 使用 uvx 直接从 Git(当前分支)调用

`uvx` 可以从本地路径(或 Git 引用)运行, 以模拟用户流程: 

```bash
uvx --from . specify-cn init demo-uvx --ai copilot --ignore-agent-tools --script sh
```

你也可以将 uvx 指向特定分支而无需合并: 

```bash
# 首先推送你的工作分支
git push origin your-feature-branch
uvx --from git+https://github.com/linfee/spec-kit-cn.git@your-feature-branch specify-cn init demo-branch-test --script ps
```

### 4a. 绝对路径 uvx(从任何位置运行)

如果你在其他目录中, 使用绝对路径代替 `.`: 

```bash
uvx --from /path/to/spec-kit-cn specify-cn --help
uvx --from /path/to/spec-kit-cn specify-cn init demo-anywhere --ai copilot --ignore-agent-tools --script sh
```

为方便起见, 设置环境变量: 
```bash
export SPEC_KIT_CN_SRC=/path/to/spec-kit-cn
uvx --from "$SPEC_KIT_CN_SRC" specify-cn init demo-env --ai copilot --ignore-agent-tools --script ps
```

(可选)定义 shell 函数: 
```bash
specify-cn-dev() { uvx --from /path/to/spec-kit-cn specify-cn "$@"; }
# 然后
specify-cn-dev --help
```

## 5. 测试脚本权限逻辑

运行 `init` 后, 检查 shell 脚本在 POSIX 系统上是否可执行: 

```bash
ls -l scripts | grep .sh
# 期望所有者执行位(例如 -rwxr-xr-x)
```
在 Windows 上你将改用 `.ps1` 脚本(不需要 chmod).

## 6. 运行 Lint / 基本检查(添加你自己的)

目前没有捆绑强制性的 lint 配置, 但你可以快速检查可导入性: 
```bash
python -c "import specify_cli; print('Import OK')"
```

## 7. 本地构建 Wheel(可选)

在发布前验证打包: 

```bash
uv build
ls dist/
```
如果需要, 将构建的制品安装到新的临时环境中.

## 8. 使用临时工作区

在脏目录中测试 `init --here` 时, 创建临时工作区: 

```bash
mkdir /tmp/spec-test && cd /tmp/spec-test
python -m src.specify_cli init --here --ai claude --ignore-agent-tools --script sh  # 如果仓库复制到这里
```
或者如果你想要更轻量的沙箱, 只复制修改后的 CLI 部分.

## 9. 调试网络 / TLS 跳过

如果在实验时需要绕过 TLS 验证: 

```bash
specify-cn check --skip-tls
specify-cn init demo --skip-tls --ai gemini --ignore-agent-tools --script ps
```
(仅用于本地实验. )

## 10. 快速编辑循环总结

| 操作 | 命令 |
|------|------|
| 直接运行 CLI | `python -m src.specify_cli --help` |
| 可编辑安装 | `uv pip install -e .` 然后 `specify-cn ...` |
| 本地 uvx 运行(仓库根目录) | `uvx --from . specify-cn ...` |
| 本地 uvx 运行(绝对路径) | `uvx --from /path/to/spec-kit-cn specify-cn ...` |
| Git 分支 uvx | `uvx --from git+URL@branch specify-cn ...` |
| 构建 wheel | `uv build` |

## 11. 清理

快速删除构建制品 / 虚拟环境: 
```bash
rm -rf .venv dist build *.egg-info
```

## 12. 常见问题

| 症状 | 修复方法 |
|------|----------|
| `ModuleNotFoundError: typer` | 运行 `uv pip install -e .` |
| 脚本不可执行(Linux) | 重新运行 init 或 `chmod +x scripts/*.sh` |
| Git 步骤被跳过 | 你传递了 `--no-git` 或未安装 Git |
| 下载了错误的脚本类型 | 明确传递 `--script sh` 或 `--script ps` |
| 企业网络上的 TLS 错误 | 尝试 `--skip-tls`(不用于生产环境) |

## 13. 下一步

- 更新文档并使用你修改后的 CLI 运行快速入门
- 满意后打开 PR
- (可选)更改合并到 `main` 后标记发布版本

# 预设 (Presets)

预设 (Presets) 是 Spec Kit 的可堆叠、按优先级排序的模板和命令覆盖集合. 它们让你可以自定义规范驱动开发工作流产生的制品 (规范、计划、任务、清单、章程) 以及引导 LLM 创建这些制品的命令, 而无需 fork 或修改核心文件.

## 工作原理

当 Spec Kit 需要一个模板 (例如 `spec-template`) 时, 它会按照解析栈的顺序查找:

1. `.specify/templates/overrides/` — 项目级的一次性覆盖
2. `.specify/presets/<preset-id>/templates/` — 已安装的预设 (按优先级排序)
3. `.specify/extensions/<ext-id>/templates/` — 扩展提供的模板
4. `.specify/templates/` — Spec Kit 附带的核心模板

如果没有安装任何预设, 则使用核心模板, 这与预设功能出现之前的行为完全一致.

模板解析在**运行时**进行 — 虽然预设文件在安装时会被复制到 `.specify/presets/<id>/`, 但 Spec Kit 在每次模板查找时都会遍历解析栈, 而不是将模板合并到单个位置.

有关详细的解析和命令注册流程, 请参阅 [ARCHITECTURE.md](ARCHITECTURE.md).

## 命令覆盖

预设还可以覆盖引导 SDD 工作流的命令. 模板定义了*生成什么* (规范、计划、章程); 命令定义了 LLM *如何生成*它们 (分步指令).

与模板不同, 命令覆盖在**安装时**应用. 当预设包含 `type: "command"` 条目时, 命令会以正确的格式 (Markdown 或 TOML, 带有适当的参数占位符) 注册到所有检测到的代理目录 (`.claude/commands/`, `.gemini/commands/` 等) 中. 当预设被移除时, 已注册的命令也会被清理.

## 快速开始

```bash
# 搜索可用预设
specify-cn preset search

# 从目录安装预设
specify-cn preset add healthcare-compliance

# 从本地目录安装 (用于开发)
specify-cn preset add --dev ./my-preset

# 安装时指定优先级 (数值越小 = 优先级越高)
specify-cn preset add healthcare-compliance --priority 5

# 列出已安装的预设
specify-cn preset list

# 查看某个模板名称解析到哪个文件
specify-cn preset resolve spec-template

# 获取预设的详细信息
specify-cn preset info healthcare-compliance

# 移除预设
specify-cn preset remove healthcare-compliance
```

## 堆叠预设

可以同时安装多个预设. `--priority` 标志控制当两个预设提供相同模板时哪个优先 (数值越小 = 优先级越高):

```bash
specify-cn preset add enterprise-safe --priority 10      # 基础层
specify-cn preset add healthcare-compliance --priority 5  # 覆盖 enterprise-safe
specify-cn preset add pm-workflow --priority 1            # 覆盖所有
```

预设是**覆盖**关系, 不会合并. 如果两个预设都提供了 `spec-template`, 则优先级数值最低的那个完全生效.

## 目录管理

预设通过目录 (Catalog) 进行发现. 默认情况下, Spec Kit 使用官方目录和社区目录:

> [!NOTE]
> 社区预设由各自的作者独立创建和维护. GitHub 和 Spec Kit 维护者可能会审查向社区目录添加条目的 pull request, 以确保格式、目录结构或策略合规性, 但他们**不审查、审计、认可或支持预设代码本身**. 安装前请审查预设源代码, 并自行承担使用风险.

```bash
# 列出活跃的目录
specify-cn preset catalog list

# 添加自定义目录
specify-cn preset catalog add https://example.com/catalog.json --name my-org --install-allowed

# 移除目录
specify-cn preset catalog remove my-org
```

## 创建预设

请参阅 [scaffold/](scaffold/) 获取可用于创建自定义预设的脚手架.

1. 将 `scaffold/` 复制到一个新目录
2. 编辑 `preset.yml` 填写你的预设元数据
3. 在 `templates/` 中添加或替换模板
4. 使用 `specify-cn preset add --dev .` 在本地测试
5. 使用 `specify-cn preset resolve spec-template` 验证

## 环境变量

| 变量 | 说明 |
|------|------|
| `SPECKIT_PRESET_CATALOG_URL` | 覆盖目录 URL (替换所有默认值) |

## 配置文件

| 文件 | 范围 | 说明 |
|------|------|------|
| `.specify/preset-catalogs.yml` | 项目 | 此项目的自定义目录栈 |
| `~/.specify/preset-catalogs.yml` | 用户 | 所有项目的自定义目录栈 |

## 未来展望

以下增强功能正在考虑用于未来版本:

- **组合策略** — 允许预设为每个模板声明 `strategy`, 而不是默认的 `replace`:

  | 类型 | `replace` | `prepend` | `append` | `wrap` |
  |------|-----------|-----------|----------|--------|
  | **template** | ✓ (默认) | ✓ | ✓ | ✓ |
  | **command** | ✓ (默认) | ✓ | ✓ | ✓ |
  | **script** | ✓ (默认) | — | — | ✓ |

  对于制品和命令 (它们是 LLM 指令), `wrap` 会使用 `{CORE_TEMPLATE}` 占位符在核心模板前后注入预设内容. 对于脚本, `wrap` 会通过 `$CORE_SCRIPT` 变量在核心脚本前后运行自定义逻辑.
- **脚本覆盖** — 允许预设提供核心脚本的替代版本 (例如 `create-new-feature.sh`) 以自定义工作流. `strategy: "wrap"` 选项可以让预设在不完全替换核心脚本的情况下, 在其前后运行自定义逻辑.

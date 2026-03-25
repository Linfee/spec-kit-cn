# Presets(预设)

Presets 是 Spec Kit 的可堆叠, 按优先级排序的模板和命令覆盖集合. 它们让你可以自定义规范驱动开发工作流产生的制品(specs, plans, tasks, checklists, constitutions)以及指导 LLM 创建它们的命令 — 而无需分叉或修改核心文件.

## 工作原理

当 Spec Kit 需要模板(例如 `spec-template`)时, 它会遍历一个解析栈:

1. `.specify/templates/overrides/` — 项目本地的一次性覆盖
2. `.specify/presets/<preset-id>/templates/` — 已安装的 presets(按优先级排序)
3. `.specify/extensions/<ext-id>/templates/` — 扩展提供的模板
4. `.specify/templates/` — Spec Kit 附带的核心模板

如果没有安装 preset, 则使用核心模板 — 与 presets 存在之前的行为完全相同.

模板解析发生在**运行时** — 尽管 preset 文件在安装期间被复制到 `.specify/presets/<id>/` 中, Spec Kit 在每次模板查找时遍历解析栈, 而不是将模板合并到单个位置.

有关详细的解析和命令注册流程, 请参阅 [ARCHITECTURE.md](ARCHITECTURE.md).

## 命令覆盖

Presets 还可以覆盖指导 SDD 工作流的命令. 模板定义*生产什么*(specs, plans, constitutions); 命令定义 LLM *如何*生产它们(分步说明).

与模板不同, 命令覆盖在**安装时**应用. 当 preset 包含 `type: "command"` 条目时, 命令会以正确的格式(带有适当参数占位符的 Markdown 或 TOML)注册到所有检测到的代理目录(`.claude/commands/`, `.gemini/commands/` 等)中. 当 preset 被移除时, 已注册的命令会被清理.

## 快速开始

```bash
# 搜索可用的 presets
specify-cn preset search

# 从目录安装 preset
specify-cn preset add healthcare-compliance

# 从本地目录安装(用于开发)
specify-cn preset add --dev ./my-preset

# 使用特定优先级安装(数字越小 = 优先级越高)
specify-cn preset add healthcare-compliance --priority 5

# 列出已安装的 presets
specify-cn preset list

# 查看模板名称解析到哪个模板
specify-cn preset resolve spec-template

# 获取 preset 的详细信息
specify-cn preset info healthcare-compliance

# 移除 preset
specify-cn preset remove healthcare-compliance
```

## 堆叠 Presets

多个 presets 可以同时安装. `--priority` 标志控制当两个 presets 提供相同模板时哪个获胜(数字越小 = 优先级越高):

```bash
specify-cn preset add enterprise-safe --priority 10      # 基础层
specify-cn preset add healthcare-compliance --priority 5  # 覆盖 enterprise-safe
specify-cn preset add pm-workflow --priority 1            # 覆盖所有
```

Presets **覆盖**, 它们不合并. 如果两个 presets 都提供 `spec-template`, 优先级数字最低的那个完全获胜.

## 目录管理

Presets 通过目录发现. 默认情况下, Spec Kit 使用官方和社区目录:

```bash
# 列出活跃的目录
specify-cn preset catalog list

# 添加自定义目录
specify-cn preset catalog add https://example.com/catalog.json --name my-org --install-allowed

# 移除目录
specify-cn preset catalog remove my-org
```

## 创建 Preset

请参阅 [scaffold/](scaffold/) 获取可用于创建自己 preset 的脚手架.

1. 将 `scaffold/` 复制到新目录
2. 使用 preset 的元数据编辑 `preset.yml`
3. 在 `templates/` 中添加或替换模板
4. 使用 `specify-cn preset add --dev .` 在本地测试
5. 使用 `specify-cn preset resolve spec-template` 验证

## 环境变量

| 变量 | 描述 |
|------|------|
| `SPECKIT_PRESET_CATALOG_URL` | 覆盖目录 URL(替换所有默认值) |

## 配置文件

| 文件 | 范围 | 描述 |
|------|------|------|
| `.specify/preset-catalogs.yml` | 项目 | 此项目的自定义目录栈 |
| `~/.specify/preset-catalogs.yml` | 用户 | 所有项目的自定义目录栈 |

## 未来考虑

以下增强功能正在考虑用于未来版本:

- **组合策略** — 允许 presets 为每个模板声明 `strategy` 而不是默认的 `replace`:

  | 类型 | `replace` | `prepend` | `append` | `wrap` |
  |------|-----------|-----------|----------|--------|
  | **template** | ✓ (默认) | ✓ | ✓ | ✓ |
  | **command** | ✓ (默认) | ✓ | ✓ | ✓ |
  | **script** | ✓ (默认) | — | — | ✓ |

  对于制品和命令(它们是 LLM 指令), `wrap` 将使用 `{CORE_TEMPLATE}` 占位符在核心模板之前和之后注入 preset 内容. 对于脚本, `wrap` 将通过 `$CORE_SCRIPT` 变量在核心脚本之前/之后运行自定义逻辑.
- **脚本覆盖** — 使 presets 能够提供核心脚本的替代版本(例如 `create-new-feature.sh`)以进行工作流自定义. `strategy: "wrap"` 选项可以允许 presets 在核心脚本之前/之后运行自定义逻辑, 而无需完全替换它.

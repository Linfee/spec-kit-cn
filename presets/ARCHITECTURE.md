# Preset 系统架构

本文档描述 preset 系统的内部架构 — 模板解析, 命令注册和目录管理在底层是如何工作的.

有关使用说明, 请参阅 [README.md](README.md).

## 模板解析

当 Spec Kit 需要模板(例如 `spec-template`)时, `PresetResolver` 遍历优先级栈并返回第一个匹配项:

```mermaid
flowchart TD
    A["resolve_template('spec-template')"] --> B{覆盖存在?}
    B -- 是 --> C[".specify/templates/overrides/spec-template.md"]
    B -- 否 --> D{Preset 提供?}
    D -- 是 --> E[".specify/presets/‹preset-id›/templates/spec-template.md"]
    D -- 否 --> F{扩展提供?}
    F -- 是 --> G[".specify/extensions/‹ext-id›/templates/spec-template.md"]
    F -- 否 --> H[".specify/templates/spec-template.md"]

    E -- "多个 presets?" --> I["优先级数字最低的获胜"]
    I --> E

    style C fill:#4caf50,color:#fff
    style E fill:#2196f3,color:#fff
    style G fill:#ff9800,color:#fff
    style H fill:#9e9e9e,color:#fff
```

| 优先级 | 来源 | 路径 | 使用场景 |
|--------|------|------|----------|
| 1 (最高) | 覆盖 | `.specify/templates/overrides/` | 一次性项目本地调整 |
| 2 | Preset | `.specify/presets/<id>/templates/` | 可共享, 可堆叠的自定义 |
| 3 | 扩展 | `.specify/extensions/<id>/templates/` | 扩展提供的模板 |
| 4 (最低) | 核心 | `.specify/templates/` | 附带的默认值 |

当安装了多个 presets 时, 它们按 `priority` 字段排序(数字越小 = 优先级越高). 这是通过 `specify-cn preset add` 上的 `--priority` 设置的.

解析被实现了三次以确保一致性:
- **Python**: `src/specify_cli/presets.py` 中的 `PresetResolver`
- **Bash**: `scripts/bash/common.sh` 中的 `resolve_template()`
- **PowerShell**: `scripts/powershell/common.ps1` 中的 `Resolve-Template`

## 命令注册

当安装带有 `type: "command"` 条目的 preset 时, `PresetManager` 使用 `src/specify_cli/agents.py` 中的共享 `CommandRegistrar` 将它们注册到所有检测到的代理目录.

```mermaid
flowchart TD
    A["specify-cn preset add my-preset"] --> B{Preset 有 type: command?}
    B -- 否 --> Z["完成(仅模板)"]
    B -- 是 --> C{扩展命令?}
    C -- "speckit.myext.cmd\n(3+ 点段)" --> D{扩展已安装?}
    D -- 否 --> E["跳过(扩展未激活)"]
    D -- 是 --> F["注册命令"]
    C -- "speckit.specify\n(核心命令)" --> F
    F --> G["检测代理目录"]
    G --> H[".claude/commands/"]
    G --> I[".gemini/commands/"]
    G --> J[".github/agents/"]
    G --> K["... (17+ 代理)"]
    H --> L["写入 .md (Markdown 格式)"]
    I --> M["写入 .toml (TOML 格式)"]
    J --> N["写入 .agent.md + .prompt.md"]

    style E fill:#ff5722,color:#fff
    style L fill:#4caf50,color:#fff
    style M fill:#4caf50,color:#fff
    style N fill:#4caf50,color:#fff
```

### 扩展安全检查

命令名称遵循模式 `speckit.<ext-id>.<cmd-name>`. 当命令有 3+ 个点段时, 系统提取扩展 ID 并检查 `.specify/extensions/<ext-id>/` 是否存在. 如果扩展未安装, 命令会被跳过 — 防止引用不存在扩展的孤立文件.

核心命令(例如 `speckit.specify`, 只有 2 个段)总是会被注册.

### 代理格式渲染

`CommandRegistrar` 为每个代理以不同方式渲染命令:

| 代理 | 格式 | 扩展名 | 参数占位符 |
|------|------|--------|------------|
| Claude, Cursor, opencode, Windsurf 等 | Markdown | `.md` | `$ARGUMENTS` |
| Copilot | Markdown | `.agent.md` + `.prompt.md` | `$ARGUMENTS` |
| Gemini, Qwen, Tabnine | TOML | `.toml` | `{{args}}` |

### 移除时清理

当调用 `specify-cn preset remove` 时, 已注册的命令从注册表元数据中读取, 相应的文件从每个代理目录中删除, 包括 Copilot 的配套 `.prompt.md` 文件.

## 目录系统

```mermaid
flowchart TD
    A["specify-cn preset search"] --> B["PresetCatalog.get_active_catalogs()"]
    B --> C{SPECKIT_PRESET_CATALOG_URL 已设置?}
    C -- 是 --> D["单个自定义目录"]
    C -- 否 --> E{.specify/preset-catalogs.yml 存在?}
    E -- 是 --> F["项目级目录栈"]
    E -- 否 --> G{"~/.specify/preset-catalogs.yml 存在?"}
    G -- 是 --> H["用户级目录栈"]
    G -- 否 --> I["内置默认值"]
    I --> J["default(允许安装)"]
    I --> K["community(仅发现)"]

    style D fill:#ff9800,color:#fff
    style F fill:#2196f3,color:#fff
    style H fill:#2196f3,color:#fff
    style J fill:#4caf50,color:#fff
    style K fill:#9e9e9e,color:#fff
```

目录以 1 小时缓存获取(每个 URL, SHA256 哈希缓存文件). 每个目录条目有一个 `priority`(用于合并排序)和 `install_allowed` 标志.

## 仓库布局

```
presets/
├── ARCHITECTURE.md                         # 本文件
├── PUBLISHING.md                           # 提交 presets 到目录的指南
├── README.md                               # 用户指南
├── catalog.json                            # 官方 preset 目录
├── catalog.community.json                  # 社区 preset 目录
├── scaffold/                               # 创建新 presets 的脚手架
│   ├── preset.yml                          # 示例清单
│   ├── README.md                           # 自定义脚手架的指南
│   ├── commands/
│   │   ├── speckit.specify.md              # 核心命令覆盖示例
│   │   └── speckit.myext.myextcmd.md       # 扩展命令覆盖示例
│   └── templates/
│       ├── spec-template.md                # 核心模板覆盖示例
│       └── myext-template.md               # 扩展模板覆盖示例
└── self-test/                              # 自测 preset(覆盖所有核心模板)
    ├── preset.yml
    ├── commands/
    │   └── speckit.specify.md
    └── templates/
        ├── spec-template.md
        ├── plan-template.md
        ├── tasks-template.md
        ├── checklist-template.md
        ├── constitution-template.md
        └── agent-file-template.md
```

## 模块结构

```
src/specify_cli/
├── agents.py       # CommandRegistrar — 将命令文件写入代理目录的
│                    #   共享基础设施
├── presets.py       # PresetManifest, PresetRegistry, PresetManager,
│                    #   PresetCatalog, PresetCatalogEntry, PresetResolver
└── __init__.py      # CLI 命令: specify-cn preset list/add/remove/search/
                     #   resolve/info, specify-cn preset catalog list/add/remove
```

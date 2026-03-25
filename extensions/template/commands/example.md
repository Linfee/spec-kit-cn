---
description: "演示扩展功能的示例命令"
# 自定义: 列出此命令使用的 MCP 工具
tools:
  - 'example-mcp-server/example_tool'
---

# 示例命令

<!-- 自定义: 用你的命令文档替换整个文件 -->

这是一个示例命令，用于演示如何为 Spec Kit 扩展创建命令。

## 用途

描述此命令的作用以及适用场景。

## 先决条件

列出使用此命令前的要求：

1. 先决条件 1（例如 “MCP server configured”）
2. 先决条件 2（例如 “Configuration file exists”）
3. 先决条件 3（例如 “Valid API credentials”）

## 用户输入

$ARGUMENTS

## 步骤

### 步骤 1：加载配置

<!-- 自定义: 替换为你的实际步骤 -->

从项目中加载扩展配置：

```bash
config_file=".specify/extensions/my-extension/my-extension-config.yml"

if [ ! -f "$config_file" ]; then
  echo "❌ Error: Configuration not found at $config_file"
  echo "Run 'specify extension add my-extension' to install and configure"
  exit 1
fi

# Read configuration values
setting_value=$(yq eval '.settings.key' "$config_file")

# Apply environment variable overrides
setting_value="${SPECKIT_MY_EXTENSION_KEY:-$setting_value}"

# Validate configuration
if [ -z "$setting_value" ]; then
  echo "❌ Error: Configuration value not set"
  echo "Edit $config_file and set 'settings.key'"
  exit 1
fi

echo "📋 Configuration loaded: $setting_value"
```

### 步骤 2：执行主要操作

<!-- 自定义: 替换为你的命令逻辑 -->

描述此步骤要做什么：

使用 MCP 工具执行主要操作：

- Tool: example-mcp-server example_tool
- Parameters: { "key": "$setting_value" }

这会调用 MCP server 工具来执行操作。

### 步骤 3：处理结果

<!-- 自定义: 根据需要添加更多步骤 -->

处理结果并输出：

```bash
echo ""
echo "✅ Command completed successfully!"
echo ""
echo "Results:"
echo "  • Item 1: Value"
echo "  • Item 2: Value"
echo ""
```

### 步骤 4：保存输出（可选）

如果需要将结果保存到文件：

```bash
output_file=".specify/my-extension-output.json"

cat > "$output_file" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "setting": "$setting_value",
  "results": []
}
EOF

echo "💾 Output saved to $output_file"
```

## 配置参考

<!-- 自定义: 文档化配置选项 -->

此命令使用 `my-extension-config.yml` 中的以下配置：

- **settings.key**: 此设置的用途说明
  - Type: string
  - Required: Yes
  - Example: `"example-value"`

- **settings.another_key**: 另一个设置的说明
  - Type: boolean
  - Required: No
  - Default: `false`
  - Example: `true`

## 环境变量

<!-- 自定义: 文档化环境变量覆盖 -->

可以使用环境变量覆盖配置：

- `SPECKIT_MY_EXTENSION_KEY` - 覆盖 `settings.key`
- `SPECKIT_MY_EXTENSION_ANOTHER_KEY` - 覆盖 `settings.another_key`

示例：
```bash
export SPECKIT_MY_EXTENSION_KEY="override-value"
```

## 故障排除

<!-- 自定义: 添加常见问题和解决方案 -->

### “Configuration not found”

**解决方案**: 安装扩展并创建配置：
```bash
specify extension add my-extension
cp .specify/extensions/my-extension/config-template.yml \
   .specify/extensions/my-extension/my-extension-config.yml
```

### “MCP tool not available”

**解决方案**: 确保 MCP server 已在你的 AI 代理设置中配置。

### “Permission denied”

**解决方案**: 检查外部服务中的凭据和权限。

## 说明

<!-- 自定义: 添加有用的说明和提示 -->

- 此命令需要与外部服务保持活动连接
- 结果会被缓存以提升性能
- 重新运行命令以刷新数据

## 示例

<!-- 自定义: 添加使用示例 -->

### 示例 1：基本用法

```bash
# Run with default configuration
>
> /speckit.my-extension.example
```

### 示例 2：使用环境变量覆盖

```bash
# Override configuration with environment variable
export SPECKIT_MY_EXTENSION_KEY="custom-value"
> /speckit.my-extension.example
```

### 示例 3：在核心命令之后执行

```bash
# Use as part of a workflow
>
> /speckit.tasks
> /speckit.my-extension.example
```

---

*更多信息，请参阅扩展 README，或运行 `specify extension info my-extension`*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

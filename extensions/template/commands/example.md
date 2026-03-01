---
description: "Example command that demonstrates extension functionality"
# 自定义: 列出此命令使用的 MCP 工具
tools:
  - 'example-mcp-server/example_tool'
---

# Example Command

<!-- 自定义: 用你的命令文档替换整个文件 -->

这是演示如何为 Spec Kit 扩展创建命令的示例命令. 

## 用途

描述此命令做什么以及何时使用它. 

## 先决条件

使用此命令前列出要求:

1. 先决条件 1 (如 "MCP server configured")
2. 先决条件 2 (如 "Configuration file exists")
3. 先决条件 3 (如 "Valid API credentials")

## User Input

$ARGUMENTS

## Steps

### Step 1: Load Configuration

<!-- 自定义: 替换为你的实际步骤 -->

从项目加载扩展配置:

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

### Step 2: Perform Main Action

<!-- 自定义: 替换为你的命令逻辑 -->

描述此步骤做什么:

Use MCP tools to perform the main action:

- Tool: example-mcp-server example_tool
- Parameters: { "key": "$setting_value" }

This calls the MCP server tool to execute the operation.

### Step 3: Process Results

<!-- 自定义: 根据需要添加更多步骤 -->

处理结果并提供输出:

```bash
echo ""
echo "✅ Command completed successfully!"
echo ""
echo "Results:"
echo "  • Item 1: Value"
echo "  • Item 2: Value"
echo ""
```

### Step 4: Save Output (Optional)

如果需要将结果保存到文件:

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

## Configuration Reference

<!-- 自定义: 文档化配置选项 -->

此命令使用 `my-extension-config.yml` 中的以下配置:

- **settings.key**: 此设置做什么的描述
  - Type: string
  - Required: Yes
  - Example: `"example-value"`

- **settings.another_key**: 另一个设置的描述
  - Type: boolean
  - Required: No
  - Default: `false`
  - Example: `true`

## Environment Variables

<!-- 自定义: 文档化环境变量覆盖 -->

配置可以用环境变量覆盖:

- `SPECKIT_MY_EXTENSION_KEY` - 覆盖 `settings.key`
- `SPECKIT_MY_EXTENSION_ANOTHER_KEY` - 覆盖 `settings.another_key`

示例:
```bash
export SPECKIT_MY_EXTENSION_KEY="override-value"
```

## Troubleshooting

<!-- 自定义: 添加常见问题和解决方案 -->

### "Configuration not found"

**解决方案**: 安装扩展并创建配置:
```bash
specify extension add my-extension
cp .specify/extensions/my-extension/config-template.yml \
   .specify/extensions/my-extension/my-extension-config.yml
```

### "MCP tool not available"

**解决方案**: 确保 MCP server 在你的 AI 代理设置中已配置. 

### "Permission denied"

**解决方案**: 检查外部服务中的凭据和权限. 

## Notes

<!-- 自定义: 添加有用的注释和提示 -->

- 此命令需要与外部服务的活动连接
- 结果会被缓存以提高性能
- 重新运行命令以刷新数据

## Examples

<!-- 自定义: 添加使用示例 -->

### Example 1: Basic Usage

```bash
# Run with default configuration
>
> /speckit.my-extension.example
```

### Example 2: With Environment Override

```bash
# Override configuration with environment variable
export SPECKIT_MY_EXTENSION_KEY="custom-value"
> /speckit.my-extension.example
```

### Example 3: After Core Command

```bash
# Use as part of a workflow
>
> /speckit.tasks
> /speckit.my-extension.example
```

---

*更多信息, 请参阅扩展 README 或运行 `specify extension info my-extension`*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

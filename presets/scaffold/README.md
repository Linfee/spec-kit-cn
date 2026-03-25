# 我的预设

这是一个 Spec Kit 的自定义预设。复制此目录并按需修改，即可创建你自己的预设。

## 包含的模板

| 模板 | 类型 | 说明 |
|------|------|------|
| `spec-template` | `template` | 自定义功能规范模板（覆盖核心和扩展） |
| `myext-template` | `template` | 对 myext 扩展报告模板的覆盖 |
| `speckit.specify` | `command` | 自定义规范命令（覆盖核心） |
| `speckit.myext.myextcmd` | `command` | 对 myext 扩展 `myextcmd` 命令的覆盖 |

## 开发

1. 复制此目录：`cp -r presets/scaffold my-preset`
2. 编辑 `preset.yml` —— 设置预设的 ID、名称、描述和模板
3. 在 `templates/` 中添加或修改模板
4. 本地测试：`specify-cn preset add --dev ./my-preset`
5. 验证解析结果：`specify-cn preset resolve spec-template`
6. 测试完成后移除：`specify-cn preset remove my-preset`

## 清单参考（`preset.yml`）

必填字段：

- `schema_version` —— 始终为 `"1.0"`
- `preset.id` —— 使用带连字符的小写字母数字
- `preset.name` —— 人类可读名称
- `preset.version` —— 语义化版本（例如 `1.0.0`）
- `preset.description` —— 简短描述
- `requires.speckit_version` —— 版本约束（例如 `>=0.1.0`）
- `provides.templates` —— 模板列表，包含 `type`、`name` 和 `file`

## 模板类型

- **`template`** —— 文档脚手架（`spec-template.md`、`plan-template.md`、`tasks-template.md` 等）
- **`command`** —— AI 代理工作流提示词（例如 `speckit.specify`、`speckit.plan`）
- **`script`** —— 自定义脚本（保留供未来使用）

## 发布

提交到目录的详细说明，请参阅[预设发布指南](../PUBLISHING.md)。

## 许可证

MIT

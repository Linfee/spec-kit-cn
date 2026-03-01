# 示例: 扩展 README

这是自定义后扩展 README 应该是什么样子的示例. 
**删除此文件并用类似这样的内容替换 README.md. **

---

# My Extension

<!-- 自定义: 替换为你的扩展描述 -->

简要描述你的扩展做什么以及为什么有用. 

## 功能

<!-- 自定义: 列出关键功能 -->

- 功能 1: 描述
- 功能 2: 描述
- 功能 3: 描述

## 安装

```bash
# 从目录安装
specify extension add my-extension

# 或从本地开发目录安装
specify extension add --dev /path/to/my-extension
```

## 配置

1. 创建配置文件:

   ```bash
   cp .specify/extensions/my-extension/config-template.yml \
      .specify/extensions/my-extension/my-extension-config.yml
   ```

2. 编辑配置:

   ```bash
   vim .specify/extensions/my-extension/my-extension-config.yml
   ```

3. 设置必需的值:
   <!-- 自定义: 列出必需的配置 -->
   ```yaml
   connection:
     url: "https://api.example.com"
     api_key: "your-api-key"

   project:
     id: "your-project-id"
   ```

## 使用

<!-- 自定义: 添加使用示例 -->

### 命令: example

描述此命令做什么. 

```bash
# 在 Claude Code 中
> /speckit.my-extension.example
```

**先决条件**:

- 先决条件 1
- 先决条件 2

**输出**:

- 此命令产生什么
- 结果保存在哪里

## 配置参考

<!-- 自定义: 文档化所有配置选项 -->

### 连接设置

| 设置 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `connection.url` | string | 是 | API 端点 URL |
| `connection.api_key` | string | 是 | API 认证密钥 |

### 项目设置

| 设置 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `project.id` | string | 是 | 项目标识符 |
| `project.workspace` | string | 否 | 工作区或组织 |

## 环境变量

使用环境变量覆盖配置:

```bash
# 覆盖连接设置
export SPECKIT_MY_EXTENSION_CONNECTION_URL="https://custom-api.com"
export SPECKIT_MY_EXTENSION_CONNECTION_API_KEY="custom-key"
```

## 示例

<!-- 自定义: 添加真实世界示例 -->

### 示例 1: 基本工作流程

```bash
# 步骤 1: 创建规范
> /speckit.spec

# 步骤 2: 生成任务
> /speckit.tasks

# 步骤 3: 使用扩展
> /speckit.my-extension.example
```

## 故障排除

<!-- 自定义: 添加常见问题 -->

### 问题: 找不到配置

**解决方案**: 从模板创建配置 (参见配置部分)

### 问题: 命令不可用

**解决方案**:

1. 检查扩展是否已安装: `specify extension list`
2. 重启 AI 代理
3. 重新安装扩展

## 许可证

MIT License - 参见 LICENSE 文件

## 支持

- **问题**: <https://github.com/your-org/spec-kit-my-extension/issues>
- **Spec Kit 文档**: <https://github.com/statsperform/spec-kit>

## 变更日志

参见 [CHANGELOG.md](CHANGELOG.md) 了解版本历史. 

---

*扩展版本: 1.0.0*
*Spec Kit: >=0.1.0*
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

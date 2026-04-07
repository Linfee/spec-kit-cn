# Spec Kit 扩展

[Spec Kit](https://github.com/Linfee/spec-kit-cn) 的扩展系统 - 无需膨胀核心框架即可添加新功能。

## 扩展目录

Spec Kit 提供两种不同用途的目录文件:

### 你的目录 (`catalog.json`)

- **用途**: Spec Kit CLI 使用的默认上游扩展目录
- **默认状态**: 上游项目中默认为空 - 你或你的组织在分叉/副本中填充受信任的扩展
- **位置(上游)**: GitHub 托管的 spec-kit 仓库中的 `extensions/catalog.json`
- **CLI 默认值**: `specify-cn extension` 命令默认使用上游目录 URL, 除非被覆盖
- **组织目录**: 将 `SPECKIT_CATALOG_URL` 指向你组织的分叉或托管的目录 JSON, 以替代上游默认值
- **自定义**: 从社区目录复制条目到你的组织目录, 或直接添加你自己的扩展

**示例覆盖:**
```bash
# 用你组织的目录覆盖默认的上游目录
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
specify-cn extension search  # 现在使用你组织的目录而不是上游默认值
```

### 社区参考目录 (`catalog.community.json`)

> [!NOTE]
> 社区扩展由各自的作者独立创建和维护。GitHub 和 Spec Kit 维护者可能会审查添加到社区目录条目的 Pull Request, 以检查格式、目录结构或策略合规性, 但他们**不会审查、审计、认可或支持扩展代码本身**。社区扩展网站也是第三方资源。在安装前请审查扩展源代码, 使用时请自行判断。

- **用途**: 浏览可用的社区贡献扩展
- **状态**: 活跃 - 包含社区提交的扩展
- **位置**: `extensions/catalog.community.json`
- **用法**: 用于发现可用扩展的参考目录
- **提交**: 通过 Pull Request 开放社区贡献

**工作原理:**

## 提供扩展

你控制团队能发现和安装哪些扩展:

### 方式 1: 策划目录(推荐用于组织)

用已批准的扩展填充你的 `catalog.json`:

1. **发现**来自各种来源的扩展:
   - 浏览 `catalog.community.json` 中的社区扩展
   - 在你组织的仓库中查找私有/内部扩展
   - 发现来自受信任第三方的扩展
2. **审查**扩展, 选择你想要提供的扩展
3. **添加**这些扩展条目到你自己的 `catalog.json`
4. **团队成员**现在可以发现并安装它们:
   - `specify-cn extension search` 显示你策划的目录
   - `specify-cn extension add <name>` 从你的目录安装

**优势**: 完全控制可用扩展, 团队一致性, 组织审批工作流

**示例**: 从 `catalog.community.json` 复制条目到你的 `catalog.json`, 然后你的团队就可以按名称发现并安装它。

### 方式 2: 直接 URL(适用于临时使用)

跳过目录策划 - 团队成员直接使用 URL 安装:

```bash
specify-cn extension add <extension-name> --from https://github.com/org/spec-kit-ext/archive/refs/tags/v1.0.0.zip
```

**优势**: 快速适用于一次性测试或私有扩展

**权衡**: 通过这种方式安装的扩展不会出现在 `specify-cn extension search` 中供其他团队成员使用, 除非你也把它们添加到你的 `catalog.json`。

## 可用社区扩展

> [!NOTE]
> 社区扩展由各自的作者独立创建和维护。GitHub 和 Spec Kit 维护者可能会审查添加到社区目录条目的 Pull Request, 以检查格式、目录结构或策略合规性, 但他们**不会审查、审计、认可或支持扩展代码本身**。社区扩展网站也是第三方资源。在安装前请审查扩展源代码, 使用时请自行判断。

🔍 **在[社区扩展网站](https://speckit-community.github.io/extensions/)上浏览和搜索社区扩展。**

参见主 README 中的[社区扩展](../README.md#-community-extensions)部分, 获取可用社区贡献扩展的完整列表。

原始目录数据请参见 [`catalog.community.json`](catalog.community.json)。


## 添加你的扩展

### 提交流程

将你的扩展添加到社区目录:

1. 按照[扩展开发指南](EXTENSION-DEVELOPMENT-GUIDE.md)**准备你的扩展**
2. **创建 GitHub Release** 用于你的扩展
3. **提交 Pull Request**, 需要:
   - 将你的扩展添加到 `extensions/catalog.community.json`
   - 在此 README 的可用扩展表中更新你的扩展信息
4. **等待审查** - 维护者将审查并在满足条件时合并

详细步骤说明请参见[扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md)。

### 提交检查清单

提交前请确保:

- ✅ 有效的 `extension.yml` 清单
- ✅ 包含安装和使用说明的完整 README
- ✅ 包含 LICENSE 文件
- ✅ 创建了带有语义化版本号的 GitHub Release(如 v1.0.0)
- ✅ 在真实项目中测试过扩展
- ✅ 所有命令按文档说明正常工作

## 安装扩展

扩展可用后(在你的目录中或通过直接 URL), 安装它们:

```bash
# 从你策划的目录(按名称)
specify-cn extension search                  # 查看你的目录中的内容
specify-cn extension add <extension-name>    # 按名称安装

# 从 URL 直接安装(绕过目录)
specify-cn extension add <extension-name> --from https://github.com/<org>/<repo>/archive/refs/tags/<version>.zip

# 列出已安装的扩展
specify-cn extension list
```

更多信息请参见[扩展用户指南](EXTENSION-USER-GUIDE.md)。

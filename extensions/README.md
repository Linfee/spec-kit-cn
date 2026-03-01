# Spec Kit 扩展系统

[Spec Kit](https://github.com/github/spec-kit) 的扩展系统 - 无需膨胀核心框架即可添加新功能. 

## 扩展目录

Spec Kit 提供两个不同用途的目录文件:

### 你的目录 (`catalog.json`)

- **用途**: Spec Kit CLI 使用的默认上游扩展目录
- **默认状态**: 在上游项目中默认为空 - 你或你的组织填充一个分支/副本, 包含你信任的扩展
- **位置 (上游)**: GitHub 托管的 spec-kit 仓库中的 `extensions/catalog.json`
- **CLI 默认值**: `specify extension` 命令默认使用上游目录 URL, 除非被覆盖
- **组织目录**: 将 `SPECKIT_CATALOG_URL` 指向你组织的分支或托管的目录 JSON 来替代上游默认值
- **自定义**: 从社区目录复制条目到你的组织目录, 或直接添加你自己的扩展

**示例覆盖:**
```bash
# 用你组织的目录覆盖默认的上游目录
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
specify extension search  # 现在使用你组织的目录而不是上游默认值
```

### 社区参考目录 (`catalog.community.json`)

- **用途**: 浏览可用的社区贡献扩展
- **状态**: 活跃 - 包含社区提交的扩展
- **位置**: `extensions/catalog.community.json`
- **用法**: 用于发现可用扩展的参考目录
- **提交**: 通过 Pull Request 开放社区贡献

**工作原理:**

## 使扩展可用

你可以控制团队成员可以发现和安装哪些扩展:

### 选项 1: 精选目录 (推荐用于组织)

用已批准的扩展填充你的 `catalog.json`:

1. **发现** 来自各种来源的扩展:
   - 浏览 `catalog.community.json` 中的社区扩展
   - 在你组织的仓库中查找私有/内部扩展
   - 从可信的第三方发现扩展
2. **审查** 扩展并选择你想要提供的扩展
3. **添加** 这些扩展条目到你自己的 `catalog.json`
4. **团队成员** 现在可以发现并安装它们:
   - `specify extension search` 显示你的精选目录
   - `specify extension add <name>` 从你的目录安装

**优势**: 完全控制可用扩展, 团队一致性, 组织审批流程

**示例**: 从 `catalog.community.json` 复制一个条目到你的 `catalog.json`, 然后你的团队就可以发现并按名称安装它. 

### 选项 2: 直接 URL (用于临时使用)

跳过目录管理 - 团队成员直接使用 URL 安装:

```bash
specify extension add --from https://github.com/org/spec-kit-ext/archive/refs/tags/v1.0.0.zip
```

**优势**: 适合一次性测试或私有扩展

**权衡**: 以这种方式安装的扩展不会出现在其他团队成员的 `specify extension search` 中, 除非你也把它们添加到你的 `catalog.json`. 

## 可用的社区扩展

以下社区贡献的扩展可在 [`catalog.community.json`](catalog.community.json) 中找到:

| 扩展 | 用途 | URL |
|------|------|-----|
| V-Model Extension Pack | 强制执行 V-Model 配对生成开发规范和测试规范, 具有完整的可追溯性 | [spec-kit-v-model](https://github.com/leocamello/spec-kit-v-model) |
| Cleanup Extension | 实施后质量门禁, 审查变更, 修复小问题 (scout rule), 为中等问题创建任务, 为大问题生成分析 | [spec-kit-cleanup](https://github.com/dsrednicki/spec-kit-cleanup) |

## 添加你的扩展

### 提交流程

要将你的扩展添加到社区目录:

1. **准备你的扩展**, 遵循 [扩展开发指南](EXTENSION-DEVELOPMENT-GUIDE.md)
2. **创建 GitHub release** 为你的扩展
3. **提交 Pull Request**:
   - 将你的扩展添加到 `extensions/catalog.community.json`
   - 在可用扩展表中更新此 README
4. **等待审核** - 维护者将审核并在满足条件时合并

详细步骤请参阅 [扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md). 

### 提交清单

提交前, 请确保:

- ✅ 有效的 `extension.yml` 清单
- ✅ 完整的 README, 包含安装和使用说明
- ✅ 包含 LICENSE 文件
- ✅ 创建了带有语义版本号的 GitHub release (如 v1.0.0)
- ✅ 在真实项目上测试过扩展
- ✅ 所有命令按文档工作

## 安装扩展

一旦扩展可用（在你的目录中或通过直接 URL）, 安装它们:

```bash
# 从你的精选目录 (按名称)
specify extension search                  # 查看目录中的内容
specify extension add <extension-name>    # 按名称安装

# 直接从 URL (绕过目录)
specify extension add --from https://github.com/<org>/<repo>/archive/refs/tags/<version>.zip

# 列出已安装的扩展
specify extension list
```

更多信息请参阅 [扩展用户指南](EXTENSION-USER-GUIDE.md). 
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

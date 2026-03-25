# Spec Kit Extensions(扩展)

[Spec Kit](https://github.com/github/spec-kit) 的扩展系统 — 在不膨胀核心框架的情况下添加新功能.

## 扩展目录

Spec Kit 提供两个具有不同用途的目录文件:

### 你的目录(`catalog.json`)

- **用途**: Spec Kit CLI 使用的默认上游扩展目录
- **默认状态**: 上游项目中设计为空 — 你或你的组织用你信任的扩展填充分叉/副本
- **位置(上游)**: GitHub 托管的 spec-kit 仓库中的 `extensions/catalog.json`
- **CLI 默认**: `specify-cn extension` 命令默认使用上游目录 URL, 除非被覆盖
- **组织目录**: 将 `SPECKIT_CATALOG_URL` 指向你组织的分叉或托管的目录 JSON, 以使用它代替上游默认值
- **自定义**: 从社区目录复制条目到你的组织目录, 或直接添加你自己的扩展

**示例覆盖:**
```bash
# 用你组织的目录覆盖默认上游目录
export SPECKIT_CATALOG_URL="https://your-org.com/spec-kit/catalog.json"
specify-cn extension search  # 现在使用你组织的目录而不是上游默认值
```

### 社区参考目录(`catalog.community.json`)

- **用途**: 浏览可用的社区贡献扩展
- **状态**: 活跃 — 包含社区提交的扩展
- **位置**: `extensions/catalog.community.json`
- **用法**: 用于发现可用扩展的参考目录
- **提交**: 通过 Pull Request 开放社区贡献

**工作原理:**

## 使扩展可用

你控制你的团队可以发现和安装哪些扩展:

### 选项 1: 策划目录(推荐给组织)

用已批准的扩展填充你的 `catalog.json`:

1. **发现** 来自各种来源的扩展:
   - 浏览 `catalog.community.json` 中的社区扩展
   - 在你组织的仓库中查找私有/内部扩展
   - 从受信任的第三方发现扩展
2. **审查** 扩展并选择你想让哪些可用
3. **添加** 这些扩展条目到你自己的 `catalog.json`
4. **团队成员** 现在可以发现并安装它们:
   - `specify-cn extension search` 显示你策划的目录
   - `specify-cn extension add <name>` 从你的目录安装

**好处**: 完全控制可用扩展, 团队一致性, 组织审批流程

**示例**: 从 `catalog.community.json` 复制条目到你的 `catalog.json`, 然后你的团队可以按名称发现并安装它.

### 选项 2: 直接 URL(用于临时使用)

跳过目录策划 — 团队成员使用 URL 直接安装:

```bash
specify-cn extension add --from https://github.com/org/spec-kit-ext/archive/refs/tags/v1.0.0.zip
```

**好处**: 快速用于一次性测试或私有扩展

**权衡**: 除非你也把它们添加到 `catalog.json`, 否则以这种方式安装的扩展不会出现在其他团队成员的 `specify-cn extension search` 中.

## 可用的社区扩展

[`catalog.community.json`](catalog.community.json) 中提供以下社区贡献的扩展:

**类别:** `docs` — 读取, 验证或生成规范制品 · `code` — 审查, 验证或修改源代码 · `process` — 跨阶段编排工作流 · `integration` — 与外部平台同步 · `visibility` — 报告项目健康或进度

**效果:** `Read-only` — 生成报告而不修改文件 · `Read+Write` — 修改文件, 创建制品或更新规范

| 扩展 | 用途 | 类别 | 效果 | URL |
|------|------|------|------|-----|
| Archive Extension | 将已合并的功能归档到主项目内存中. | `docs` | Read+Write | [spec-kit-archive](https://github.com/stn1slv/spec-kit-archive) |
| Azure DevOps Integration | 使用 OAuth 身份验证将用户故事和任务同步到 Azure DevOps 工作项 | `integration` | Read+Write | [spec-kit-azure-devops](https://github.com/pragya247/spec-kit-azure-devops) |
| Cleanup Extension | 实施后质量关卡, 审查更改, 修复小问题(侦察规则), 为中等问题创建任务, 并为大型问题生成分析 | `code` | Read+Write | [spec-kit-cleanup](https://github.com/dsrednicki/spec-kit-cleanup) |
| Cognitive Squad | 多代理认知系统, 采用三元模型: 理解, 内化, 应用 — 具有质量关卡, 反向传播验证和自我修复 | `docs` | Read+Write | [cognitive-squad](https://github.com/Testimonial/cognitive-squad) |
| Conduct Extension | 通过子代理委托编排 spec-kit 阶段以减少上下文污染. | `process` | Read+Write | [spec-kit-conduct-ext](https://github.com/twbrandon7/spec-kit-conduct-ext) |
| DocGuard — CDD Enforcement | 规范驱动开发强制执行. 通过自动化检查, AI 驱动的工作流和 spec-kit 钩子验证, 评分和追踪项目文档. 零 NPM 运行时依赖. | `docs` | Read+Write | [spec-kit-docguard](https://github.com/raccioly/docguard) |
| Fleet Orchestrator | 在所有 SpecKit 阶段中通过人工关卡编排完整功能生命周期 | `process` | Read+Write | [spec-kit-fleet](https://github.com/sharathsatish/spec-kit-fleet) |
| Iterate | 使用两阶段定义和应用工作流迭代规范文档 — 在实施中途完善规范并直接回到构建 | `docs` | Read+Write | [spec-kit-iterate](https://github.com/imviancagrace/spec-kit-iterate) |
| Jira Integration | 从 spec-kit 规范和任务分解创建 Jira Epic, Story 和 Issue, 具有可配置的层次结构和自定义字段支持 | `integration` | Read+Write | [spec-kit-jira](https://github.com/mbachorik/spec-kit-jira) |
| Learning Extension | 从实施中生成教育指南, 并通过指导上下文增强说明 | `docs` | Read+Write | [spec-kit-learn](https://github.com/imviancagrace/spec-kit-learn) |
| Project Health Check | 诊断 Spec Kit 项目并报告结构, 代理, 功能, 脚本, 扩展和 git 方面的健康问题 | `visibility` | Read-only | [spec-kit-doctor](https://github.com/KhawarHabibKhan/spec-kit-doctor) |
| Project Status | 显示当前 SDD 工作流进度 — 活跃功能, 制品状态, 任务完成情况, 工作流阶段和扩展摘要 | `visibility` | Read-only | [spec-kit-status](https://github.com/KhawarHabibKhan/spec-kit-status) |
| Ralph Loop | 使用 AI 代理 CLI 的自主实施循环 | `code` | Read+Write | [spec-kit-ralph](https://github.com/Rubiss/spec-kit-ralph) |
| Reconcile Extension | 通过外科手术式更新功能制品来协调实施偏差. | `docs` | Read+Write | [spec-kit-reconcile](https://github.com/stn1slv/spec-kit-reconcile) |
| Retrospective Extension | 实施后回顾, 包含规范遵守评分, 偏差分析和人工关卡的规范更新 | `docs` | Read+Write | [spec-kit-retrospective](https://github.com/emi-dm/spec-kit-retrospective) |
| Review Extension | 实施后全面代码审查, 使用专门的代理进行代码质量, 注释, 测试, 错误处理, 类型设计和简化 | `code` | Read-only | [spec-kit-review](https://github.com/ismaelJimenez/spec-kit-review) |
| SDD Utilities | 恢复中断的工作流, 验证项目健康, 并验证规范到任务的追溯性 | `process` | Read+Write | [speckit-utils](https://github.com/mvanhorn/speckit-utils) |
| Spec Sync | 检测并解决规范与实施之间的偏差. AI 辅助解决方案, 需人工批准 | `docs` | Read+Write | [spec-kit-sync](https://github.com/bgervin/spec-kit-sync) |
| Understanding | 自动化需求质量分析 — 基于 IEEE/ISO 标准的 31 个确定性指标, 带有实验性能量模糊检测 | `docs` | Read-only | [understanding](https://github.com/Testimonial/understanding) |
| V-Model Extension Pack | 强制执行 V 模型成对生成开发规范和测试规范, 具有完整的追溯性 | `docs` | Read+Write | [spec-kit-v-model](https://github.com/leocamello/spec-kit-v-model) |
| Verify Extension | 实施后质量关卡, 根据规范制品验证已实施的代码 | `code` | Read-only | [spec-kit-verify](https://github.com/ismaelJimenez/spec-kit-verify) |
| Verify Tasks Extension | 检测虚假完成: tasks.md 中标记为 [X] 但没有实际实施的任务 | `code` | Read-only | [spec-kit-verify-tasks](https://github.com/datastone-inc/spec-kit-verify-tasks) |


## 添加你的扩展

### 提交流程

要将你的扩展添加到社区目录:

1. **准备你的扩展**, 遵循 [扩展开发指南](EXTENSION-DEVELOPMENT-GUIDE.md)
2. **为你的扩展创建 GitHub release**
3. **提交 Pull Request**, 需要:
   - 将你的扩展添加到 `extensions/catalog.community.json`
   - 在此 README 的可用扩展表中更新你的扩展
4. **等待审查** - 维护者将审查并在满足条件时合并

有关详细的分步说明, 请参阅 [扩展发布指南](EXTENSION-PUBLISHING-GUIDE.md).

### 提交清单

提交前, 确保:

- ✅ 有效的 `extension.yml` 清单
- ✅ 带有安装和使用说明的完整 README
- ✅ 包含 LICENSE 文件
- ✅ 使用语义版本(例如 v1.0.0)创建的 GitHub release
- ✅ 在真实项目上测试过的扩展
- ✅ 所有命令按文档工作

## 安装扩展

一旦扩展可用(在你的目录中或通过直接 URL), 安装它们:

```bash
# 从你策划的目录(按名称)
specify-cn extension search                  # 查看目录中的内容
specify-cn extension add <extension-name>    # 按名称安装

# 直接从 URL(绕过目录)
specify-cn extension add --from https://github.com/<org>/<repo>/archive/refs/tags/<version>.zip

# 列出已安装的扩展
specify-cn extension list
```

有关更多信息, 请参阅 [扩展用户指南](EXTENSION-USER-GUIDE.md).

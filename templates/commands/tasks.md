---
description: 基于可用的设计制品, 为功能生成可操作的、按依赖关系排序的 tasks.md.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入（如果不为空）。

## 执行前检查

**检查扩展钩子（任务生成前）**:
- 检查项目根目录下是否存在 `.specify/extensions.yml`
- 如果存在，读取该文件并查找 `hooks.before_tasks` 键下的条目
- 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续
- 过滤掉 `enabled` 显式为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子的 `condition` 表达式:
  - 如果钩子没有 `condition` 字段，或为 null/空，则将钩子视为可执行
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，将条件评估留给 HookExecutor 实现
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容:
  - **可选钩子** (`optional: true`):
    ```
    ## 扩展钩子

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必选钩子** (`optional: false`):
    ```
    ## 扩展钩子

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，静默跳过

## 大纲

1. **设置**: 从仓库根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须是绝对路径。对于参数中的单引号（如 "I'm Groot"），使用转义语法: 例如 'I'\''m Groot'（或尽可能使用双引号: "I'm Groot"）。

2. **加载设计文档**: 从 FEATURE_DIR 读取:
   - **必需**: plan.md（技术栈、库、结构），spec.md（带优先级的用户故事）
   - **可选**: data-model.md（实体），contracts/（接口契约），research.md（决策），quickstart.md（测试场景）
   - 注意: 不是所有项目都有所有文档。根据可用的文档生成任务。

3. **执行任务生成工作流**:
   - 加载 plan.md 并提取技术栈、库、项目结构
   - 加载 spec.md 并提取用户故事及其优先级（P1, P2, P3 等）
   - 如果存在 data-model.md: 提取实体并映射到用户故事
   - 如果存在 contracts/: 将接口契约映射到用户故事
   - 如果存在 research.md: 提取用于设置任务的决策
   - 按用户故事组织任务生成（见下方任务生成规则）
   - 生成依赖关系图，显示用户故事完成顺序
   - 为每个用户故事创建并行执行示例
   - 验证任务完整性（每个用户故事都有所需的所有任务，可独立测试）

4. **生成 tasks.md**: 使用 `templates/tasks-template.md` 作为结构，填充以下内容:
   - 从 plan.md 获取正确的功能名称
   - Phase 1: 设置任务（项目初始化）
   - Phase 2: 基础任务（所有用户故事的阻塞性前置条件）
   - Phase 3+: 每个用户故事一个阶段（按 spec.md 中的优先级顺序）
   - 每个阶段包括: 故事目标、独立测试标准、测试（如有请求）、实现任务
   - 最终阶段: 收尾与横切关注点
   - 所有任务必须遵循严格的清单格式（见下方任务生成规则）
   - 每个任务的清晰文件路径
   - 显示故事完成顺序的依赖关系部分
   - 每个故事的并行执行示例
   - 实现策略部分（MVP 优先，增量交付）

5. **报告**: 输出生成的 tasks.md 路径和摘要:
   - 总任务数
   - 每个用户故事的任务数
   - 识别出的并行执行机会
   - 每个故事的独立测试标准
   - 建议的 MVP 范围（通常仅用户故事 1）
   - 格式验证: 确认所有任务都遵循清单格式（复选框、ID、标签、文件路径）

6. **检查扩展钩子**: tasks.md 生成后，检查项目根目录下是否存在 `.specify/extensions.yml`。
   - 如果存在，读取该文件并查找 `hooks.after_tasks` 键下的条目
   - 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续
   - 过滤掉 `enabled` 显式为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用
   - 对于每个剩余的钩子，**不要**尝试解释或评估钩子的 `condition` 表达式:
     - 如果钩子没有 `condition` 字段，或为 null/空，则将钩子视为可执行
     - 如果钩子定义了非空的 `condition`，则跳过该钩子，将条件评估留给 HookExecutor 实现
   - 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容:
     - **可选钩子** (`optional: true`):
       ```
       ## 扩展钩子

       **Optional Hook**: {extension}
       Command: `/{command}`
       Description: {description}

       Prompt: {prompt}
       To execute: `/{command}`
       ```
     - **必选钩子** (`optional: false`):
       ```
       ## 扩展钩子

       **Automatic Hook**: {extension}
       Executing: `/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - 如果没有注册钩子或 `.specify/extensions.yml` 不存在，静默跳过

任务生成上下文: {ARGS}

tasks.md 应该可以立即执行 - 每个任务必须足够具体，以便 LLM 无需额外上下文即可完成。

## 任务生成规则

**关键**: 任务必须按用户故事组织，以实现独立实现和测试。

**测试是可选的**: 仅在功能规范中明确请求或用户请求 TDD 方法时才生成测试任务。

### 清单格式（必需）

每个任务必须严格遵循此格式:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**格式组件**:

1. **复选框**: 始终以 `- [ ]` 开头（markdown 复选框）
2. **任务 ID**: 按执行顺序的序号（T001, T002, T003...）
3. **[P] 标记**: 仅在任务可并行化时包含（不同文件，不依赖于未完成的任务）
4. **[Story] 标签**: 仅用户故事阶段任务需要
   - 格式: [US1], [US2], [US3] 等（映射到 spec.md 中的用户故事）
   - 设置阶段: 无故事标签
   - 基础阶段: 无故事标签
   - 用户故事阶段: 必须有故事标签
   - 收尾阶段: 无故事标签
5. **描述**: 带有确切文件路径的清晰操作

**示例**:

- ✅ 正确: `- [ ] T001 Create project structure per implementation plan`
- ✅ 正确: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误: `- [ ] Create User model`（缺少 ID 和故事标签）
- ❌ 错误: `T001 [US1] Create model`（缺少复选框）
- ❌ 错误: `- [ ] [US1] Create User model`（缺少任务 ID）
- ❌ 错误: `- [ ] T001 [US1] Create model`（缺少文件路径）

### 任务组织

1. **从用户故事（spec.md）** - 主要组织方式:
   - 每个用户故事（P1, P2, P3...）获得自己的阶段
   - 将所有相关组件映射到其故事:
     - 该故事所需的模型
     - 该故事所需的服务
     - 该故事所需的接口/UI
     - 如有测试请求: 该故事特定的测试
   - 标记故事依赖关系（大多数故事应该是独立的）

2. **从契约**:
   - 将每个接口契约 → 映射到它服务的用户故事
   - 如有测试请求: 每个接口契约 → 在该故事阶段实现之前的契约测试任务 [P]

3. **从数据模型**:
   - 将每个实体映射到需要它的用户故事
   - 如果实体服务于多个故事: 放入最早的故事或设置阶段
   - 关系 → 适当故事阶段的服务层任务

4. **从设置/基础设施**:
   - 共享基础设施 → 设置阶段（Phase 1）
   - 基础/阻塞任务 → 基础阶段（Phase 2）
   - 特定于故事的设置 → 在该故事的阶段内

### 阶段结构

- **Phase 1**: 设置（项目初始化）
- **Phase 2**: 基础（阻塞性前置条件 - 必须在用户故事之前完成）
- **Phase 3+**: 用户故事按优先级顺序（P1, P2, P3...）
  - 在每个故事内: 测试（如有请求）→ 模型 → 服务 → 端点 → 集成
  - 每个阶段应该是一个完整、可独立测试的增量
- **最终阶段**: 收尾与横切关注点

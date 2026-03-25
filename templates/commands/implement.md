---
description: 通过处理并执行 tasks.md 中定义的所有任务来执行实施计划
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前, 你**必须**考虑用户输入(如果非空).

## 执行前检查

**检查扩展钩子(实现前)**:
- 检查项目根目录下是否存在 `.specify/extensions.yml`
- 如果存在, 读取该文件并查找 `hooks.before_implement` 键下的条目
- 如果 YAML 无法解析或无效, 静默跳过钩子检查并正常继续
- 过滤掉 `enabled` 显式为 `false` 的钩子. 没有 `enabled` 字段的钩子默认视为已启用.
- 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
  - 如果钩子没有 `condition` 字段, 或该字段为 null/空, 则将钩子视为可执行
  - 如果钩子定义了非空的 `condition`, 则跳过该钩子, 将条件评估留给 HookExecutor 实现
- 对于每个可执行的钩子, 根据其 `optional` 标志输出以下内容:
  - **可选钩子** (`optional: true`):
    ```
    ## 扩展钩子

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **强制钩子** (`optional: false`):
    ```
    ## 扩展钩子

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在, 静默跳过

## 执行大纲

1. 从仓库根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表. 所有路径必须是绝对路径. 对于参数中的单引号(如 "I'm Groot"), 使用转义语法: 例如 'I'\''m Groot' (或者尽可能使用双引号: "I'm Groot").

2. **检查清单状态**(如果 FEATURE_DIR/checklists/ 存在):
   - 扫描 checklists/ 目录中的所有清单文件
   - 对于每个清单, 统计:
     - 总项目数: 匹配 `- [ ]` 或 `- [X]` 或 `- [x]` 的所有行
     - 已完成项目: 匹配 `- [X]` 或 `- [x]` 的行
     - 未完成项目: 匹配 `- [ ]` 的行
   - 创建状态表:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - 计算整体状态:
     - **PASS**: 所有清单的未完成项目数均为 0
     - **FAIL**: 一个或多个清单存在未完成项目

   - **如果任何清单未完成**:
     - 显示包含未完成项目数量的表格
     - **停止**并询问: "部分清单尚未完成. 你是否仍要继续实现? (yes/no)"
     - 等待用户响应后再继续
     - 如果用户说 "no"、"wait" 或 "stop", 停止执行
     - 如果用户说 "yes"、"proceed" 或 "continue", 继续到步骤 3

   - **如果所有清单都已完成**:
     - 显示表格, 表明所有清单都已通过
     - 自动继续到步骤 3

3. 加载并分析实现上下文:
   - **必需**: 读取 tasks.md 获取完整的任务列表和执行计划
   - **必需**: 读取 plan.md 获取技术栈、架构和文件结构
   - **如存在**: 读取 data-model.md 获取实体和关系
   - **如存在**: 读取 contracts/ 获取 API 规范和测试需求
   - **如存在**: 读取 research.md 获取技术决策和约束
   - **如存在**: 读取 quickstart.md 获取集成场景

4. **项目设置验证**:
   - **必需**: 根据实际项目设置创建/验证忽略文件:

   **检测与创建逻辑**:
   - 检查以下命令是否成功, 以确定仓库是否为 git 仓库(如果是, 则创建/验证 .gitignore):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - 检查是否存在 Dockerfile* 或 plan.md 中提到 Docker → 创建/验证 .dockerignore
   - 检查是否存在 .eslintrc* → 创建/验证 .eslintignore
   - 检查是否存在 eslint.config.* → 确保配置的 `ignores` 条目覆盖必要的模式
   - 检查是否存在 .prettierrc* → 创建/验证 .prettierignore
   - 检查是否存在 .npmrc 或 package.json → 创建/验证 .npmignore(如果要发布)
   - 检查是否存在 terraform 文件 (*.tf) → 创建/验证 .terraformignore
   - 检查是否需要 .helmignore(存在 helm charts) → 创建/验证 .helmignore

   **如果忽略文件已存在**: 验证其包含必要的模式, 仅追加缺失的关键模式
   **如果忽略文件缺失**: 为检测到的技术创建完整的模式集

   **按技术分类的通用模式**(来自 plan.md 技术栈):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `*.dll`, `autom4te.cache/`, `config.status`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **通用**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **工具专用模式**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. 解析 tasks.md 结构并提取:
   - **任务阶段**: Setup, Tests, Core, Integration, Polish
   - **任务依赖**: 顺序执行 vs 并行执行规则
   - **任务详情**: ID, 描述, 文件路径, 并行标记 [P]
   - **执行流程**: 顺序和依赖要求

6. 按照任务计划执行实现:
   - **逐阶段执行**: 完成每个阶段后再进入下一阶段
   - **遵守依赖**: 按顺序运行串行任务, 并行任务 [P] 可以同时运行
   - **遵循 TDD 方法**: 在相应的实现任务之前执行测试任务
   - **基于文件的协调**: 影响相同文件的任务必须按顺序运行
   - **验证检查点**: 在继续之前验证每个阶段的完成情况

7. 实现执行规则:
   - **先设置**: 初始化项目结构、依赖、配置
   - **先测试后代码**: 如果需要为契约、实体和集成场景编写测试
   - **核心开发**: 实现模型、服务、CLI 命令、端点
   - **集成工作**: 数据库连接、中间件、日志、外部服务
   - **完善和验证**: 单元测试、性能优化、文档

8. 进度跟踪和错误处理:
   - 在每个任务完成后报告进度
   - 如果任何非并行任务失败, 停止执行
   - 对于并行任务 [P], 继续执行成功的任务, 报告失败的任务
   - 提供带有调试上下文的清晰错误消息
   - 如果实现无法继续, 建议后续步骤
   - **重要**: 对于已完成的任务, 确保在 tasks 文件中将任务标记为 [X].

9. 完成验证:
   - 验证所有必需任务已完成
   - 检查实现的功能是否与原始规范匹配
   - 验证测试通过且覆盖率满足要求
   - 确认实现遵循技术计划
   - 报告最终状态及已完成工作摘要

注意: 此命令假设 tasks.md 中存在完整的任务分解. 如果任务不完整或缺失, 建议先运行 `/speckit.tasks` 重新生成任务列表.

10. **检查扩展钩子**: 完成验证后, 检查项目根目录下是否存在 `.specify/extensions.yml`.
    - 如果存在, 读取该文件并查找 `hooks.after_implement` 键下的条目
    - 如果 YAML 无法解析或无效, 静默跳过钩子检查并正常继续
    - 过滤掉 `enabled` 显式为 `false` 的钩子. 没有 `enabled` 字段的钩子默认视为已启用.
    - 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
      - 如果钩子没有 `condition` 字段, 或该字段为 null/空, 则将钩子视为可执行
      - 如果钩子定义了非空的 `condition`, 则跳过该钩子, 将条件评估留给 HookExecutor 实现
    - 对于每个可执行的钩子, 根据其 `optional` 标志输出以下内容:
      - **可选钩子** (`optional: true`):
        ```
        ## 扩展钩子

        **Optional Hook**: {extension}
        Command: `/{command}`
        Description: {description}

        Prompt: {prompt}
        To execute: `/{command}`
        ```
      - **强制钩子** (`optional: false`):
        ```
        ## 扩展钩子

        **Automatic Hook**: {extension}
        Executing: `/{command}`
        EXECUTE_COMMAND: {command}
        ```
    - 如果没有注册钩子或 `.specify/extensions.yml` 不存在, 静默跳过

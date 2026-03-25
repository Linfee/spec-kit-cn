---
description: 使用计划模板执行实施计划工作流, 生成设计制品.
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前, 你**必须**考虑用户输入(如果不为空)。

## 执行前检查

**检查扩展钩子(规划前)**:
- 检查项目根目录是否存在 `.specify/extensions.yml` 文件。
- 如果存在, 读取该文件并查找 `hooks.before_plan` 键下的条目
- 如果 YAML 无法解析或无效, 静默跳过钩子检查并正常继续
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
  - 如果钩子没有 `condition` 字段, 或者为 null/空, 则将钩子视为可执行
  - 如果钩子定义了非空的 `condition`, 则跳过该钩子并将条件评估留给 HookExecutor 实现
- 对于每个可执行的钩子, 根据其 `optional` 标志输出以下内容:
  - **可选钩子** (`optional: true`):
    ```
    ## 扩展钩子

    **可选前置钩子**: {extension}
    命令: `/{command}`
    描述: {description}

    提示: {prompt}
    执行方式: `/{command}`
    ```
  - **必需钩子** (`optional: false`):
    ```
    ## 扩展钩子

    **自动前置钩子**: {extension}
    正在执行: `/{command}`
    EXECUTE_COMMAND: {command}

    等待钩子命令的结果后再继续执行大纲。
    ```
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在, 静默跳过

## 大纲

1. **设置**: 从仓库根目录运行 `{SCRIPT}` 并解析 JSON 获取 FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH。对于参数中的单引号如 "I'm Groot", 使用转义语法: 例如 'I'\''m Groot' (或尽可能使用双引号: "I'm Groot")。

2. **加载上下文**: 读取 FEATURE_SPEC 和 `/memory/constitution.md`。加载 IMPL_PLAN 模板(已复制)。

3. **执行规划工作流**: 按照 IMPL_PLAN 模板中的结构:
   - 填写技术上下文(将未知项标记为 "NEEDS CLARIFICATION")
   - 从章程填写章程检查部分
   - 评估门控条件(如果违规且无正当理由则报 ERROR)
   - 阶段 0: 生成 research.md(解决所有 NEEDS CLARIFICATION)
   - 阶段 1: 生成 data-model.md, contracts/, quickstart.md
   - 阶段 1: 通过运行代理脚本更新代理上下文
   - 设计后重新评估章程检查

4. **停止并报告**: 命令在阶段 2 规划后结束。报告分支, IMPL_PLAN 路径和生成的制品。

5. **检查扩展钩子**: 报告后, 检查项目根目录是否存在 `.specify/extensions.yml` 文件。
   - 如果存在, 读取该文件并查找 `hooks.after_plan` 键下的条目
   - 如果 YAML 无法解析或无效, 静默跳过钩子检查并正常继续
   - 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
   - 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
     - 如果钩子没有 `condition` 字段, 或者为 null/空, 则将钩子视为可执行
     - 如果钩子定义了非空的 `condition`, 则跳过该钩子并将条件评估留给 HookExecutor 实现
   - 对于每个可执行的钩子, 根据其 `optional` 标志输出以下内容:
     - **可选钩子** (`optional: true`):
       ```
       ## 扩展钩子

       **可选钩子**: {extension}
       命令: `/{command}`
       描述: {description}

       提示: {prompt}
       执行方式: `/{command}`
       ```
     - **必需钩子** (`optional: false`):
       ```
       ## 扩展钩子

       **自动钩子**: {extension}
       正在执行: `/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - 如果没有注册钩子或 `.specify/extensions.yml` 不存在, 静默跳过

## 阶段

### 阶段 0: 大纲与研究

1. **从上方技术上下文中提取未知项**:
   - 对于每个 NEEDS CLARIFICATION → 研究任务
   - 对于每个依赖 → 最佳实践任务
   - 对于每个集成 → 模式任务

2. **生成并派发研究代理**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **在 `research.md` 中整合研究结果**, 使用以下格式:
   - Decision: [选择了什么]
   - Rationale: [为什么选择]
   - Alternatives considered: [还评估了哪些选项]

**输出**: 包含所有 NEEDS CLARIFICATION 已解决的 research.md

### 阶段 1: 设计与契约

**前提条件:** `research.md` 已完成

1. **从功能规范中提取实体** → `data-model.md`:
   - 实体名称, 字段, 关系
   - 来自需求的验证规则
   - 状态转换(如适用)

2. **定义接口契约**(如果项目有外部接口) → `/contracts/`:
   - 识别项目向用户或其他系统暴露的接口
   - 记录适合项目类型的契约格式
   - 示例: 库的公共 API, CLI 工具的命令模式, Web 服务的端点, 解析器的语法, 应用程序的 UI 契约
   - 如果项目纯内部使用(构建脚本, 一次性工具等), 则跳过

3. **代理上下文更新**:
   - 运行 `{AGENT_SCRIPT}`
   - 这些脚本检测当前使用的是哪个 AI 代理
   - 更新相应的代理专用上下文文件
   - 仅从当前计划中添加新技术
   - 保留标记之间的手动添加内容

**输出**: data-model.md, /contracts/*, quickstart.md, 代理专用文件

## 关键规则

- 使用绝对路径
- 门控失败或未解决的澄清项报 ERROR

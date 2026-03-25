---
description: 根据自然语言功能描述创建或更新功能规范。
handoffs:
  - label: 构建技术计划
    agent: speckit.plan
    prompt: 为规范创建计划。我正在使用...
  - label: 澄清规范需求
    agent: speckit.clarify
    prompt: 澄清规范需求
    send: true
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 "{ARGS}"
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前, 你**必须**考虑用户输入(如果不为空)。

## 执行前检查

**检查扩展钩子(规范创建前)**:
- 检查项目根目录下是否存在 `.specify/extensions.yml`
- 如果存在, 读取它并查找 `hooks.before_specify` 键下的条目
- 如果 YAML 无法解析或无效, 静默跳过钩子检查并继续正常执行
- 过滤掉 `enabled` 明确为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用
- 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
  - 如果钩子没有 `condition` 字段, 或者为 null/空, 将该钩子视为可执行
  - 如果钩子定义了非空的 `condition`, 跳过该钩子并将条件评估留给 HookExecutor 实现
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

## 大纲

用户在触发消息中 `/speckit.specify` 之后输入的文本**就是**功能描述。假设你在这个对话中始终可以获取到它, 即使下面 `{ARGS}` 字面上显示为空。除非用户提供了空命令, 否则不要要求用户重复输入。

根据该功能描述, 执行以下操作:

1. **生成简洁的短名称**(2-4 个单词)用于分支:
   - 分析功能描述并提取最有意义的关键词
   - 创建一个能捕捉功能本质的 2-4 个单词的短名称
   - 尽可能使用动名词格式(例如 "add-user-auth", "fix-payment-bug")
   - 保留技术术语和缩写(OAuth2, API, JWT 等)
   - 保持简洁但足够描述性, 以便一眼就能理解功能
   - 示例:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **创建功能分支**, 通过运行带有 `--short-name`(和 `--json`)的脚本来创建。在顺序模式下, **不要**传递 `--number` — 脚本会自动检测下一个可用编号。在时间戳模式下, 脚本会自动生成 `YYYYMMDD-HHMMSS` 前缀:

   **分支编号模式**: 在运行脚本之前, 检查 `.specify/init-options.json` 是否存在并读取 `branch_numbering` 值。
   - 如果是 `"timestamp"`, 在脚本调用中添加 `--timestamp`(Bash)或 `-Timestamp`(PowerShell)
   - 如果是 `"sequential"` 或不存在, 不添加任何额外标志(默认行为)

   - Bash 示例: `{SCRIPT} --json --short-name "user-auth" "Add user authentication"`
   - Bash(时间戳): `{SCRIPT} --json --timestamp --short-name "user-auth" "Add user authentication"`
   - PowerShell 示例: `{SCRIPT} -Json -ShortName "user-auth" "Add user authentication"`
   - PowerShell(时间戳): `{SCRIPT} -Json -Timestamp -ShortName "user-auth" "Add user authentication"`

   **重要**:
   - **不要**传递 `--number` — 脚本会自动确定正确的下一个编号
   - 始终包含 JSON 标志(Bash 用 `--json`, PowerShell 用 `-Json`), 以便输出可以被可靠地解析
   - 每个功能只能运行此脚本一次
   - JSON 会在终端中作为输出提供 — 始终参考它来获取你需要的实际内容
   - JSON 输出将包含 BRANCH_NAME 和 SPEC_FILE 路径
   - 对于参数中的单引号, 如 "I'm Groot", 使用转义语法: 例如 'I'\''m Groot'(或者尽可能使用双引号: "I'm Groot")

3. 加载 `templates/spec-template.md` 以了解所需的章节。

4. 按照此执行流程:

    1. 从输入解析用户描述
       如果为空: 错误 "No feature description provided"
    2. 从描述中提取关键概念
       识别: 参与者、操作、数据、约束
    3. 对于不明确的方面:
       - 根据上下文和行业标准进行合理推测
       - 仅在以下情况下使用 [NEEDS CLARIFICATION: 具体问题] 标记:
         - 该选择显著影响功能范围或用户体验
         - 存在多种合理的解释, 且有不同的影响
         - 不存在合理的默认值
       - **限制: 最多 3 个 [NEEDS CLARIFICATION] 标记**
       - 按影响优先级排序澄清: 范围 > 安全/隐私 > 用户体验 > 技术细节
    4. 填写用户场景和测试章节
       如果没有清晰的用户流程: 错误 "Cannot determine user scenarios"
    5. 生成功能需求
       每个需求必须是可测试的
       对未指定的细节使用合理的默认值(在假设章节中记录假设)
    6. 定义成功标准
       创建可衡量、与技术无关的结果
       包括定量指标(时间、性能、数量)和定性指标(用户满意度、任务完成率)
       每个标准必须可以在不了解实现细节的情况下进行验证
    7. 识别关键实体(如果涉及数据)
    8. 返回: 成功(规范已准备好进行规划)

5. 使用模板结构将规范写入 SPEC_FILE, 用从功能描述(参数)派生的具体细节替换占位符, 同时保留章节顺序和标题。

6. **规范质量验证**: 编写初始规范后, 根据质量标准进行验证:

   a. **创建规范质量清单**: 在 `FEATURE_DIR/checklists/requirements.md` 生成清单文件, 使用清单模板结构包含以下验证项:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: 在进入规划阶段之前验证规范的完整性和质量
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before `/speckit.clarify` or `/speckit.plan`
      ```

   b. **运行验证检查**: 根据每个清单项审查规范:
      - 对于每一项, 确定是通过还是失败
      - 记录发现的具体问题(引用相关规范章节)

   c. **处理验证结果**:

      - **如果所有项都通过**: 标记清单完成并继续第 7 步

      - **如果有项失败(不包括 [NEEDS CLARIFICATION])**:
        1. 列出失败的项和具体问题
        2. 更新规范以解决每个问题
        3. 重新运行验证直到所有项都通过(最多 3 次迭代)
        4. 如果 3 次迭代后仍有失败项, 在清单备注中记录剩余问题并警告用户

      - **如果仍有 [NEEDS CLARIFICATION] 标记**:
        1. 从规范中提取所有 [NEEDS CLARIFICATION: ...] 标记
        2. **限制检查**: 如果超过 3 个标记, 只保留 3 个最关键的(按范围/安全/用户体验影响排序), 对其余的进行合理推测
        3. 对于每个需要澄清的问题(最多 3 个), 以此格式向用户展示选项:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **关键 - 表格格式**: 确保 markdown 表格格式正确:
           - 使用一致的间距, 竖线对齐
           - 每个单元格的内容前后应有空格: `| Content |` 而不是 `|Content|`
           - 表头分隔符必须至少有 3 个破折号: `|--------|`
           - 测试表格在 markdown 预览中能正确渲染
        5. 按顺序编号问题(Q1, Q2, Q3 - 最多 3 个)
        6. 在等待响应之前一起展示所有问题
        7. 等待用户对所有问题的选择做出回应(例如, "Q1: A, Q2: Custom - [details], Q3: B")
        8. 通过用用户选择或提供的答案替换每个 [NEEDS CLARIFICATION] 标记来更新规范
        9. 在所有澄清问题解决后重新运行验证

   d. **更新清单**: 每次验证迭代后, 用当前的通过/失败状态更新清单文件

7. 报告完成情况, 包括分支名称、规范文件路径、清单结果, 以及准备好进入下一阶段(`/speckit.clarify` 或 `/speckit.plan`)。

8. **检查扩展钩子**: 报告完成后, 检查项目根目录下是否存在 `.specify/extensions.yml`。
   - 如果存在, 读取它并查找 `hooks.after_specify` 键下的条目
   - 如果 YAML 无法解析或无效, 静默跳过钩子检查并继续正常执行
   - 过滤掉 `enabled` 明确为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用
   - 对于每个剩余的钩子, **不要**尝试解释或评估钩子的 `condition` 表达式:
     - 如果钩子没有 `condition` 字段, 或者为 null/空, 将该钩子视为可执行
     - 如果钩子定义了非空的 `condition`, 跳过该钩子并将条件评估留给 HookExecutor 实现
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

**注意:** 脚本会创建并切换到新分支, 在写入之前初始化规范文件。

## 快速指南

- 关注用户需要**什么**以及**为什么**。
- 避免**如何**实现(不要涉及技术栈、API、代码结构)。
- 为业务相关方编写, 而不是开发人员。
- **不要**创建嵌入在规范中的任何清单。那将是一个单独的命令。

### 章节要求

- **必填章节**: 每个功能都必须完成
- **可选章节**: 仅在与功能相关时包含
- 当章节不适用时, 完全删除它(不要保留为 "N/A")

### AI 生成指南

从用户提示创建此规范时:

1. **进行合理推测**: 使用上下文、行业标准和常见模式来填补空白
2. **记录假设**: 在假设章节中记录合理的默认值
3. **限制澄清标记**: 最多 3 个 [NEEDS CLARIFICATION] 标记 - 仅用于以下关键决策:
   - 显著影响功能范围或用户体验
   - 存在多种合理的解释, 且有不同的影响
   - 缺乏任何合理的默认值
4. **按优先级排序澄清**: 范围 > 安全/隐私 > 用户体验 > 技术细节
5. **像测试人员一样思考**: 每个模糊的需求都应该无法通过"可测试且明确"的清单项
6. **常见需要澄清的领域**(仅在不存在合理默认值时):
   - 功能范围和边界(包括/排除特定用例)
   - 用户类型和权限(如果存在多种冲突的解释)
   - 安全/合规要求(当具有法律/财务重要性时)

**合理默认值示例**(不要询问这些):

- 数据保留: 该领域的行业标准做法
- 性能目标: 标准 Web/移动应用的预期, 除非另有说明
- 错误处理: 用户友好的消息和适当的回退
- 认证方式: Web 应用使用标准的基于会话或 OAuth2
- 集成模式: 使用适合项目的模式(Web 服务用 REST/GraphQL, 库用函数调用, 工具用 CLI 参数等)

### 成功标准指南

成功标准必须:

1. **可衡量**: 包含具体指标(时间、百分比、数量、比率)
2. **与技术无关**: 不提及框架、语言、数据库或工具
3. **以用户为中心**: 从用户/业务角度描述结果, 而不是系统内部
4. **可验证**: 可以在不知道实现细节的情况下进行测试/验证

**好的示例**:

- "用户可以在 3 分钟内完成结账"
- "系统支持 10,000 个并发用户"
- "95% 的搜索在 1 秒内返回结果"
- "任务完成率提高 40%"

**不好的示例**(以实现为中心):

- "API 响应时间在 200ms 以内"(太技术化, 使用"用户即时看到结果")
- "数据库可以处理 1000 TPS"(实现细节, 使用面向用户的指标)
- "React 组件高效渲染"(特定于框架)
- "Redis 缓存命中率高于 80%"(特定于技术)

---
description: 生成并执行符合 Conventional Commits 规范的标准化 Git 提交，自动添加智能体署名。
---

## 用户输入

```text
$ARGUMENTS
```

如果用户输入不为空，**必须**优先考虑用户输入的内容。

## 配置说明

以下配置可以修改以自定义提交行为：

### 提交类型

允许的提交类型（可修改此列表以添加/删除类型）：

| 类型 | 说明 | 表情 | 使用场景 |
|------|------|------|----------|
| feat | 新功能 | ✨ | 添加新功能时使用 |
| fix | Bug 修复 | 🐛 | 修复 Bug 时使用 |
| docs | 文档 | 📝 | 仅修改文档时使用 |
| style | 代码格式 | 💄 | 格式化代码，不影响功能 |
| refactor | 重构 | ♻️ | 代码重构，无新功能或修复 |
| test | 测试 | ✅ | 添加或更新测试 |
| chore | 杂务 | 🔧 | 构建过程、依赖更新等 |
| perf | 性能优化 | ⚡ | 性能改进 |
| ci | CI/CD | 👷 | CI 配置变更 |
| build | 构建 | 📦 | 构建系统变更 |

### 消息格式

- **subject_max_length**: 72（主题行最大长度）
- **body_max_line_length**: 100（正文每行最大长度）
- **require_scope**: false（是否必须指定作用域）
- **require_body**: false（是否必须填写正文）
- **use_emoji**: false（是否在主题行使用表情符号）

### 确认模式

- **default_mode**: auto
  - `auto`: 复杂变更（5+ 文件）时确认，简单变更直接提交
  - `confirm`: 始终等待确认
  - `skip`: 始终跳过确认

### 语言设置

- **default**: zh
  - `en`: 英文提交消息
  - `zh`: 中文提交消息

### 敏感文件模式

匹配以下模式的文件将触发警告：

```text
.env
.env.*
*.key
*.pem
*.p12
*secret*
*credential*
*password*
*token*
serviceAccountKey.json
id_rsa
id_dsa
```

---

## 执行流程

### 步骤 1: 解析命令参数

解析 `$ARGUMENTS` 提取选项：

| 选项 | 简写 | 类型 | 说明 |
|------|------|------|------|
| `--type` | `-t` | 字符串 | 提交类型（feat, fix, docs 等） |
| `--scope` | `-s` | 字符串 | 提交作用域（如 auth, api） |
| `--message` | `-m` | 字符串 | 自定义提交描述 |
| `--confirm` | - | 标志 | 强制确认模式 |
| `--no-confirm` | - | 标志 | 跳过确认 |
| `--dry-run` | - | 标志 | 仅预览，不执行提交 |
| `--amend` | - | 标志 | 修改上次提交 |

选项之后的剩余文本作为提交描述使用。

**使用示例**：
- `/speckit.commit` - 自动分析并提交
- `/speckit.commit --type feat` - 作为新功能提交
- `/speckit.commit --type fix --scope auth` - 作为 auth 模块的 Bug 修复提交
- `/speckit.commit --dry-run` - 仅预览不提交
- `/speckit.commit 添加用户登录功能` - 使用文本作为描述

### 步骤 2: 检查 Git 状态

1. **验证 Git 仓库**：
   ```bash
   git rev-parse --git-dir 2>/dev/null
   ```
   如果失败，显示错误："❌ **错误**：当前目录不是 Git 仓库。请在 Git 仓库内执行此命令。"

2. **检查变更**：
   ```bash
   git status --porcelain
   ```

3. **处理不同状态**：
   - 如果没有变更（输出为空）：显示 "❌ **没有可提交的变更**。请先使用 `git add` 暂存变更或进行一些修改。"
   - 如果只有未跟踪文件：询问用户是否要包含它们
   - 如果有已暂存的变更：仅处理已暂存的变更
   - 如果有未暂存的变更：使用 `git add -A` 暂存所有变更

4. **检查特殊 Git 状态**：
   ```bash
   git status
   ```
   - 如果处于 rebase/merge 状态：显示警告并建议先解决冲突

### 步骤 3: 检测敏感文件

1. **获取待提交的文件列表**：
   ```bash
   git diff --cached --name-only
   ```

2. **根据配置中定义的敏感模式检查每个文件**

3. **如果检测到敏感文件**：
   ```markdown
   ## ⚠️ 警告：检测到敏感文件

   以下文件匹配敏感模式：
   - `.env.local`（匹配：`.env.*`）
   - `secrets/api.key`（匹配：`*.key`）

   这些文件可能包含密钥或凭证。是否继续提交？
   ```

   等待用户确认后继续。如果用户拒绝，显示"提交已取消"并停止。

### 步骤 4: 分析变更

1. **获取详细差异**：
   ```bash
   git diff --cached --stat
   git diff --cached
   ```

2. **识别变更特征**：
   - 修改的文件类型（源代码、测试、文档、配置）
   - 变更性质（新增、修改、删除）
   - 影响的目录/模块

3. **自动推断提交类型**（如果未通过 `--type` 指定）：

   | 变更模式 | 推断类型 |
   |----------|----------|
   | `test/` 目录下的新文件或 `*.test.*`、`*.spec.*` | test |
   | 仅 `docs/` 目录或 `*.md` 文件的变更 | docs |
   | 仅 `package.json`、`pom.xml`、`build.gradle` 等 | chore |
   | `.github/workflows/`、`.gitlab-ci.yml` 的变更 | ci |
   | `src/` 下的新源文件 | feat |
   | 差异中包含 "fix"、"bug"、"error" 的修改文件 | fix |
   | 无新功能的代码变更 | refactor |
   | 默认 | feat |

4. **自动推断作用域**（如果未通过 `--scope` 指定）：
   - 提取变更文件的公共父目录
   - 如果变更在单个模块内，使用模块名称

### 步骤 5: 生成提交消息

根据配置部分的设置：

1. **构建主题行**：
   ```
   <类型>[(<作用域>)]: <描述>
   ```

   - 如果 `use_emoji` 为 true，添加表情前缀：`✨ feat(auth): 添加登录功能`
   - 确保主题长度 ≤ `subject_max_length`（72 字符）
   - 不以句号结尾
   - 使用祈使语气（添加、修复、更新，而非已添加、已修复、已更新）

2. **构建正文**（对于复杂变更）：
   - 总结变更内容和原因
   - 使用列表形式展示多个变更
   - 每行不超过 `body_max_line_length`（100 字符）

3. **添加智能体署名页脚**：
   ```
   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

4. **语言处理**：
   - 如果 `language.default` 为 `zh`：使用中文生成描述
   - 如果 `language.default` 为 `en`：使用英文生成描述

### 步骤 6: 验证消息

1. **检查主题长度**：
   - 如果 > 72 字符：截断或警告用户

2. **检查类型有效性**：
   - 如果类型不在允许列表中：显示错误并列出可用类型

3. **检查必填字段**：
   - 如果 `require_scope` 为 true 且没有作用域：提示输入作用域
   - 如果 `require_body` 为 true 且没有正文：生成正文

### 步骤 7: 显示预览

显示提交预览：

```markdown
## 提交预览

**类型**: feat
**作用域**: auth
**主题**: 添加用户登录功能

### 待提交文件 (3)
- `src/auth/login.ts`（新增）
- `src/auth/token.ts`（新增）
- `src/routes/auth.ts`（修改）

### 提交消息
```
feat(auth): 添加用户登录功能

实现基于 JWT 的用户认证：
- 添加登录接口
- 添加 token 验证中间件
- 添加刷新 token 接口

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
```

### 步骤 8: 处理确认

根据 `confirmation.default_mode` 和命令参数：

| 配置模式 | `--confirm` | `--no-confirm` | 行为 |
|----------|-------------|----------------|------|
| auto | - | - | 5+ 文件时确认，否则跳过 |
| auto | 是 | - | 等待确认 |
| auto | - | 是 | 跳过确认 |
| confirm | - | - | 等待确认 |
| confirm | - | 是 | 跳过确认 |
| skip | - | - | 跳过确认 |
| skip | 是 | - | 等待确认 |

如果指定了 `--dry-run`：显示预览后停止，不执行提交。

如果用户取消确认：显示"提交已取消"并停止。

### 步骤 9: 执行提交

1. **暂存变更**（如果尚未暂存）：
   ```bash
   git add -A
   ```

2. **创建提交**：
   ```bash
   git commit -m "<消息>"
   ```

   对于多行消息使用 HEREDOC：
   ```bash
   git commit -m "$(cat <<'EOF'
   feat(auth): 添加用户登录功能

   实现基于 JWT 的用户认证

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. **处理 --amend**：
   - 如果指定了 `--amend`：
     - 检查上次提交是否已推送：`git status` 显示 "Your branch is ahead"
     - 如果已推送到远程：显示需要强制推送的警告
     - 执行：`git commit --amend -m "<消息>"`

### 步骤 10: 显示结果

成功时：
```markdown
## ✅ 提交成功

**提交哈希**: `a1b2c3d`
**类型**: feat
**作用域**: auth
**主题**: 添加用户登录功能

### 变更摘要
- 3 个文件变更
- 150 行新增(+)
- 12 行删除(-)
```

失败时：
```markdown
## ❌ 提交失败

**错误**: <git 错误信息>

### 故障排除
- 使用 `git status` 检查冲突
- 确保有写入权限
- 尝试手动运行 `git add`
```

---

## 错误处理

| 错误 | 消息 | 建议 |
|------|------|------|
| 非 Git 仓库 | 当前目录不是 Git 仓库 | 请在 Git 仓库内运行 |
| 无变更 | 没有可提交的变更 | 请先使用 `git add` 暂存变更 |
| 无效类型 | 未知的提交类型: {type} | 请使用以下类型之一: feat, fix, docs, style, refactor, test, chore |
| 消息过长 | 主题超过 72 字符 | 请使用更简短的描述 |
| Git 命令失败 | Git 错误: {message} | 请检查 git status 并解决问题 |
| 修改已推送的提交 | 上次提交已推送到远程 | 修改后需使用 `git push --force`（谨慎使用！） |

---

## 使用示例

### 基本使用
```
/speckit.commit
```
自动分析变更、推断类型、生成消息并提交。

### 指定类型
```
/speckit.commit --type feat
```
作为新功能提交。

### 指定类型和作用域
```
/speckit.commit --type fix --scope auth
```
作为 auth 模块的 Bug 修复提交。

### 带描述
```
/speckit.commit --type feat 添加用户登录功能
```
使用提供的描述。

### 预览模式
```
/speckit.commit --dry-run
```
显示将要提交的内容，但不实际提交。

### 跳过确认
```
/speckit.commit --no-confirm
```
立即提交，不等待确认。

### 修改上次提交
```
/speckit.commit --amend
```
将当前变更合并到上次提交。

---

## 快速参考

| 命令 | 说明 |
|------|------|
| `/speckit.commit` | 自动分析并提交 |
| `/speckit.commit --type feat` | 指定为新功能 |
| `/speckit.commit --type fix` | 指定为 Bug 修复 |
| `/speckit.commit --scope auth` | 指定作用域 |
| `/speckit.commit --dry-run` | 预览不提交 |
| `/speckit.commit --no-confirm` | 跳过确认直接提交 |
| `/speckit.commit --amend` | 修改上次提交 |

### 提交类型速查

| 类型 | 用途 | 示例场景 |
|------|------|----------|
| `feat` | 新功能 | 添加登录页面 |
| `fix` | Bug 修复 | 修复密码验证错误 |
| `docs` | 文档 | 更新 README |
| `style` | 格式 | 调整代码缩进 |
| `refactor` | 重构 | 提取公共方法 |
| `test` | 测试 | 添加单元测试 |
| `chore` | 杂项 | 更新依赖版本 |
| `perf` | 性能 | 优化查询速度 |
| `ci` | CI/CD | 配置 GitHub Actions |
| `build` | 构建 | 修改 webpack 配置 |

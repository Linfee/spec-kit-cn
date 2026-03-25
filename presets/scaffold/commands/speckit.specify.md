---
description: "创建功能规范（预设覆盖）"
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 "{ARGS}"
---

## 用户输入

```text
$ARGUMENTS
```

根据上面的功能描述：

1. **通过运行脚本创建功能分支**：
   - Bash：`{SCRIPT} --json --short-name "<short-name>" "<description>"`
   - JSON 输出包含 `BRANCH_NAME` 和 `SPEC_FILE` 路径。

2. **读取 `spec-template`**，查看需要填写的章节。

3. **将规范写入 `SPEC_FILE`**，用用户描述中的细节替换各节中的占位符
   （概述、需求、验收标准）。

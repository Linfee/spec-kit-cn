---
description: "覆盖 myext 扩展的 myextcmd 命令"
---

<!-- 预设对 speckit.myext.myextcmd 的覆盖 -->

你正在使用 myext 扩展 `myextcmd` 命令的自定义版本。

执行此命令时：

1. 从 `$ARGUMENTS` 读取用户输入
2. 按照标准 `myextcmd` 工作流执行
3. 另外应用此预设提供的以下自定义：
   - 在继续前添加合规性检查
   - 在输出中包含审计追踪记录

> 自定义：将上面的说明替换为你自己的内容。
> 此文件覆盖 `myext` 扩展提供的命令。
> 安装此预设后，所有代理（Claude、Gemini、Copilot 等）
> 都会使用这个版本，而不是扩展原始版本。

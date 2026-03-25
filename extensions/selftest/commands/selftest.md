---
description: "验证目录中某个扩展的生命周期。"
---

# 扩展自测：`$ARGUMENTS`

此命令用于执行一次自测，模拟开发者使用 `$ARGUMENTS` 扩展时的完整体验。

## 目标

验证扩展 `$ARGUMENTS` 的端到端生命周期（发现、安装、注册）。
如果 `$ARGUMENTS` 为空，你必须提示用户提供扩展名称，例如：`/speckit.selftest.extension linear`。

## 步骤

### 步骤 1：验证目录发现

检查该扩展是否存在于 Spec Kit 目录中。
执行下面的命令，并验证它成功完成，且返回的扩展 ID 与 `$ARGUMENTS` 完全一致。如果命令失败，或 ID 与 `$ARGUMENTS` 不匹配，则测试失败。

```bash
specify extension info "$ARGUMENTS"
```

### 步骤 2：模拟安装

首先，尝试直接将该扩展添加到当前工作区配置中。如果目录将该扩展标记为 `install_allowed: false`（仅发现，不允许直接安装），那么此步骤**预期**会失败。

```bash
specify extension add "$ARGUMENTS"
```

随后，通过目录中的下载 URL 来模拟添加该扩展，这应当绕过限制。
从目录元数据中获取扩展的 `download_url`（例如通过目录信息命令或 UI），然后运行：

```bash
specify extension add "$ARGUMENTS" --from "<download_url>"
```

### 步骤 3：验证注册结果

当 `add` 命令完成后，通过检查项目配置来验证安装结果。
使用终端工具（如 `cat`）检查下面的文件是否包含 `$ARGUMENTS` 的注册记录。

```bash
cat .specify/extensions/.registry/$ARGUMENTS.json
```

### 步骤 4：输出验证报告

分析前面三个步骤的标准输出。
生成一种终端风格的测试输出格式，说明发现、安装和注册的结果，并直接返回给用户。

示例输出格式：
```text
============================= test session starts ==============================
collected 3 items

test_selftest_discovery.py::test_catalog_search [PASS/FAIL]
  Details: [Provide execution result of specify extension search]

test_selftest_installation.py::test_extension_add [PASS/FAIL]
  Details: [Provide execution result of specify extension add]

test_selftest_registration.py::test_config_verification [PASS/FAIL]
  Details: [Provide execution result of registry record verification]

============================== [X] passed in ... ==============================
```

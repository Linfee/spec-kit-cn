---
name: spec-kit-release
description: 按 spec-kit 对齐版本进行发布与重发的标准流程。用于需要发布本项目、重跑同版本发布、删除并重建同名 tag/release、校验 GitHub Actions 与 release 资产清单一致性的场景。
---

# Spec Kit 对齐发布流程

严格约束：版本号必须与 `spec-kit` 对齐，不允许自增自定义版本。

## 1) 确认目标版本

1. 从 `./spec-kit` 获取上游最新 tag（如 `v0.1.10`）。
2. 本项目发布版本必须使用同一个 tag。

## 2) 合并到主分支并校验

1. 若当前不在 `main`，先合并到 `main`。
2. 推送 `main` 前完成本地发布校验（项目已有脚本优先）：

```bash
bash tests/e2e/validate-release.sh
```

3. 校验通过后推送 `main`。

## 3) 首次发布（正常路径）

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

推送 tag 后应触发 `release.yml`。

## 4) 同版本重发（失败补救路径）

当同版本发布失败且必须保持版本不变时，按顺序执行：

1. 修复问题并合并到 `main`。
2. 删除远端 release（若存在）：

```bash
gh release delete vX.Y.Z --repo Linfee/spec-kit-cn --yes
```

3. 删除远端 tag（若存在）：

```bash
git push origin :refs/tags/vX.Y.Z
```

4. 删除本地 tag（若存在）：

```bash
git tag -d vX.Y.Z
```

5. 推送修复后的 `main`，重新打并推送同名 tag：

```bash
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 5) 发布后验收

1. GitHub Actions: `release.yml` 最新运行必须 `completed/success`。
2. Release 状态：非 draft、非 prerelease。
3. 资产清单：与 `github/spec-kit` 对应版本 release 资产列表一致（agent/script 组合一致）。

可用检查命令：

```bash
gh run list --repo Linfee/spec-kit-cn --workflow release.yml --limit 5
gh release view vX.Y.Z --repo Linfee/spec-kit-cn --json url,tagName,isDraft,isPrerelease
gh release view vX.Y.Z --repo Linfee/spec-kit-cn --json assets --jq '.assets[].name' | sort
gh release view vX.Y.Z --repo github/spec-kit --json assets --jq '.assets[].name' | sort
```

若资产命名仅版本前缀（`v`）策略不同，需确认组合与数量完全一致。

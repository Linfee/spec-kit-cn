# 扩展模板

用于创建 Spec Kit 扩展的入门模板. 

## 快速开始

1. **复制此模板**:

   ```bash
   cp -r extensions/template my-extension
   cd my-extension
   ```

2. **自定义 `extension.yml`**:
   - 更改扩展 ID, 名称, 描述
   - 更新作者和仓库
   - 定义你的命令

3. **创建命令**:
   - 在 `commands/` 目录中添加命令文件
   - 使用带有 YAML frontmatter 的 Markdown 格式

4. **创建配置模板**:
   - 定义配置选项
   - 文档化所有设置

5. **编写文档**:
   - 更新 README.md 包含使用说明
   - 添加示例

6. **本地测试**:

   ```bash
   cd /path/to/spec-kit-project
   specify extension add --dev /path/to/my-extension
   ```

7. **发布** (可选):
   - 创建 GitHub 仓库
   - 创建 release
   - 提交到目录 (参见 EXTENSION-PUBLISHING-GUIDE.md)

## 此模板中的文件

- `extension.yml` - 扩展清单 (自定义此文件)
- `config-template.yml` - 配置模板 (自定义此文件)
- `commands/example.md` - 示例命令 (替换此文件)
- `README.md` - 扩展文档 (替换此文件)
- `LICENSE` - MIT 许可证 (审核此文件)
- `CHANGELOG.md` - 版本历史 (更新此文件)
- `.gitignore` - Git 忽略规则

## 自定义清单

- [ ] 更新 `extension.yml` 包含你的扩展详情
- [ ] 将扩展 ID 更改为你的扩展名称
- [ ] 更新作者信息
- [ ] 定义你的命令
- [ ] 在 `commands/` 中创建命令文件
- [ ] 更新配置模板
- [ ] 编写包含使用说明的 README
- [ ] 添加示例
- [ ] 如需要更新 LICENSE
- [ ] 本地测试扩展
- [ ] 创建 git 仓库
- [ ] 创建第一个 release

## 需要帮助?

- **开发指南**: 参见 EXTENSION-DEVELOPMENT-GUIDE.md
- **API 参考**: 参见 EXTENSION-API-REFERENCE.md
- **发布指南**: 参见 EXTENSION-PUBLISHING-GUIDE.md
- **用户指南**: 参见 EXTENSION-USER-GUIDE.md

## 模板版本

- 版本: 1.0.0
- 最后更新: 2026-01-28
- 兼容 Spec Kit: >=0.1.0
STATS:comma=0,period=0,colon=0,semicolon=0,exclaim=0,question=0,dunhao=0

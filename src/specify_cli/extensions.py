"""
Spec Kit 扩展管理器

处理 Spec Kit 扩展的安装, 移除和管理. 
扩展是模块化的包, 可以在不增加核心框架臃肿的情况下
为 spec-kit 添加命令和功能. 
"""

import json
import hashlib
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import re

import yaml
from packaging import version as pkg_version
from packaging.specifiers import SpecifierSet, InvalidSpecifier


class ExtensionError(Exception):
    """扩展相关错误的基类异常. """
    pass


class ValidationError(ExtensionError):
    """当扩展清单验证失败时抛出. """
    pass


class CompatibilityError(ExtensionError):
    """当扩展与当前环境不兼容时抛出. """
    pass


class ExtensionManifest:
    """表示并验证扩展清单 (extension.yml). """

    SCHEMA_VERSION = "1.0"
    REQUIRED_FIELDS = ["schema_version", "extension", "requires", "provides"]

    def __init__(self, manifest_path: Path):
        """加载并验证扩展清单. 

        Args:
            manifest_path: extension.yml 文件的路径

        Raises:
            ValidationError: 如果清单无效
        """
        self.path = manifest_path
        self.data = self._load_yaml(manifest_path)
        self._validate()

    def _load_yaml(self, path: Path) -> dict:
        """安全加载 YAML 文件. """
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValidationError(f"{path} 中的 YAML 无效: {e}")
        except FileNotFoundError:
            raise ValidationError(f"未找到清单文件: {path}")

    def _validate(self):
        """验证清单结构和必填字段. """
        # 检查必填的顶级字段
        for field in self.REQUIRED_FIELDS:
            if field not in self.data:
                raise ValidationError(f"缺少必填字段: {field}")

        # 验证 schema 版本
        if self.data["schema_version"] != self.SCHEMA_VERSION:
            raise ValidationError(
                f"不支持的 schema 版本: {self.data['schema_version']} "
                f"(期望 {self.SCHEMA_VERSION})"
            )

        # 验证扩展元数据
        ext = self.data["extension"]
        for field in ["id", "name", "version", "description"]:
            if field not in ext:
                raise ValidationError(f"缺少 extension.{field}")

        # 验证扩展 ID 格式
        if not re.match(r'^[a-z0-9-]+$', ext["id"]):
            raise ValidationError(
                f"无效的扩展 ID '{ext['id']}': "
                "必须仅包含小写字母数字和连字符"
            )

        # 验证语义化版本
        try:
            pkg_version.Version(ext["version"])
        except pkg_version.InvalidVersion:
            raise ValidationError(f"无效的版本号: {ext['version']}")

        # 验证 requires 部分
        requires = self.data["requires"]
        if "speckit_version" not in requires:
            raise ValidationError("缺少 requires.speckit_version")

        # 验证 provides 部分
        provides = self.data["provides"]
        if "commands" not in provides or not provides["commands"]:
            raise ValidationError("扩展必须提供至少一个命令")

        # 验证命令
        for cmd in provides["commands"]:
            if "name" not in cmd or "file" not in cmd:
                raise ValidationError("命令缺少 'name' 或 'file'")

            # 验证命令名称格式
            if not re.match(r'^speckit\.[a-z0-9-]+\.[a-z0-9-]+$', cmd["name"]):
                raise ValidationError(
                    f"无效的命令名称 '{cmd['name']}': "
                    "必须遵循 'speckit.{extension}.{command}' 格式"
                )

    @property
    def id(self) -> str:
        """获取扩展 ID. """
        return self.data["extension"]["id"]

    @property
    def name(self) -> str:
        """获取扩展名称. """
        return self.data["extension"]["name"]

    @property
    def version(self) -> str:
        """获取扩展版本. """
        return self.data["extension"]["version"]

    @property
    def description(self) -> str:
        """获取扩展描述. """
        return self.data["extension"]["description"]

    @property
    def requires_speckit_version(self) -> str:
        """获取所需的 spec-kit 版本范围. """
        return self.data["requires"]["speckit_version"]

    @property
    def commands(self) -> List[Dict[str, Any]]:
        """获取提供的命令列表. """
        return self.data["provides"]["commands"]

    @property
    def hooks(self) -> Dict[str, Any]:
        """获取钩子定义. """
        return self.data.get("hooks", {})

    def get_hash(self) -> str:
        """计算清单文件的 SHA256 哈希值. """
        with open(self.path, 'rb') as f:
            return f"sha256:{hashlib.sha256(f.read()).hexdigest()}"


class ExtensionRegistry:
    """管理已安装扩展的注册表. """

    REGISTRY_FILE = ".registry"
    SCHEMA_VERSION = "1.0"

    def __init__(self, extensions_dir: Path):
        """初始化注册表. 

        Args:
            extensions_dir: .specify/extensions/ 目录的路径
        """
        self.extensions_dir = extensions_dir
        self.registry_path = extensions_dir / self.REGISTRY_FILE
        self.data = self._load()

    def _load(self) -> dict:
        """从磁盘加载注册表. """
        if not self.registry_path.exists():
            return {
                "schema_version": self.SCHEMA_VERSION,
                "extensions": {}
            }

        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 注册表损坏或丢失, 重新开始
            return {
                "schema_version": self.SCHEMA_VERSION,
                "extensions": {}
            }

    def _save(self):
        """保存注册表到磁盘. """
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add(self, extension_id: str, metadata: dict):
        """将扩展添加到注册表. 

        Args:
            extension_id: 扩展 ID
            metadata: 扩展元数据（版本, 来源等）
        """
        self.data["extensions"][extension_id] = {
            **metadata,
            "installed_at": datetime.now(timezone.utc).isoformat()
        }
        self._save()

    def remove(self, extension_id: str):
        """从注册表中移除扩展. 

        Args:
            extension_id: 扩展 ID
        """
        if extension_id in self.data["extensions"]:
            del self.data["extensions"][extension_id]
            self._save()

    def get(self, extension_id: str) -> Optional[dict]:
        """从注册表获取扩展元数据. 

        Args:
            extension_id: 扩展 ID

        Returns:
            扩展元数据, 如果未找到则返回 None
        """
        return self.data["extensions"].get(extension_id)

    def list(self) -> Dict[str, dict]:
        """获取所有已安装的扩展. 

        Returns:
            extension_id -> 元数据 的字典
        """
        return self.data["extensions"]

    def is_installed(self, extension_id: str) -> bool:
        """检查扩展是否已安装. 

        Args:
            extension_id: 扩展 ID

        Returns:
            如果扩展已安装则返回 True
        """
        return extension_id in self.data["extensions"]


class ExtensionManager:
    """管理扩展生命周期: 安装, 移除, 更新. """

    def __init__(self, project_root: Path):
        """初始化扩展管理器. 

        Args:
            project_root: 项目根目录的路径
        """
        self.project_root = project_root
        self.extensions_dir = project_root / ".specify" / "extensions"
        self.registry = ExtensionRegistry(self.extensions_dir)

    def check_compatibility(
        self,
        manifest: ExtensionManifest,
        speckit_version: str
    ) -> bool:
        """检查扩展是否与当前 spec-kit 版本兼容. 

        Args:
            manifest: 扩展清单
            speckit_version: 当前 spec-kit 版本

        Returns:
            如果兼容则返回 True

        Raises:
            CompatibilityError: 如果扩展不兼容
        """
        required = manifest.requires_speckit_version
        current = pkg_version.Version(speckit_version)

        # 解析版本说明符（例如 ">=0.1.0,<2.0.0"）
        try:
            specifier = SpecifierSet(required)
            if current not in specifier:
                raise CompatibilityError(
                    f"扩展需要 spec-kit {required}, "
                    f"但已安装 {speckit_version}. \n"
                    f"请使用以下命令升级 spec-kit: uv tool install specify-cn-cli --force"
                )
        except InvalidSpecifier:
            raise CompatibilityError(f"无效的版本说明符: {required}")

        return True

    def install_from_directory(
        self,
        source_dir: Path,
        speckit_version: str,
        register_commands: bool = True
    ) -> ExtensionManifest:
        """从本地目录安装扩展. 

        Args:
            source_dir: 扩展目录的路径
            speckit_version: 当前 spec-kit 版本
            register_commands: 如果为 True, 则向 AI 代理注册命令

        Returns:
            已安装的扩展清单

        Raises:
            ValidationError: 如果清单无效
            CompatibilityError: 如果扩展不兼容
        """
        # 加载并验证清单
        manifest_path = source_dir / "extension.yml"
        manifest = ExtensionManifest(manifest_path)

        # 检查兼容性
        self.check_compatibility(manifest, speckit_version)

        # 检查是否已安装
        if self.registry.is_installed(manifest.id):
            raise ExtensionError(
                f"扩展 '{manifest.id}' 已安装. "
                f"请先使用 'specify-cn extension remove {manifest.id}' 移除. "
            )

        # 安装扩展
        dest_dir = self.extensions_dir / manifest.id
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        shutil.copytree(source_dir, dest_dir)

        # 向 AI 代理注册命令
        registered_commands = {}
        if register_commands:
            registrar = CommandRegistrar()
            # 为所有检测到的代理注册
            registered_commands = registrar.register_commands_for_all_agents(
                manifest, dest_dir, self.project_root
            )

        # 注册钩子
        hook_executor = HookExecutor(self.project_root)
        hook_executor.register_hooks(manifest)

        # 更新注册表
        self.registry.add(manifest.id, {
            "version": manifest.version,
            "source": "local",
            "manifest_hash": manifest.get_hash(),
            "enabled": True,
            "registered_commands": registered_commands
        })

        return manifest

    def install_from_zip(
        self,
        zip_path: Path,
        speckit_version: str
    ) -> ExtensionManifest:
        """从 ZIP 文件安装扩展. 

        Args:
            zip_path: 扩展 ZIP 文件的路径
            speckit_version: 当前 spec-kit 版本

        Returns:
            已安装的扩展清单

        Raises:
            ValidationError: 如果清单无效
            CompatibilityError: 如果扩展不兼容
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # 安全解压 ZIP（防止 Zip Slip 攻击）
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 在解压任何内容之前先验证所有路径
                temp_path_resolved = temp_path.resolve()
                for member in zf.namelist():
                    member_path = (temp_path / member).resolve()
                    # 使用 is_relative_to 进行安全的路径包含检查
                    try:
                        member_path.relative_to(temp_path_resolved)
                    except ValueError:
                        raise ValidationError(
                            f"ZIP 归档中存在不安全的路径: {member}（潜在的路径遍历攻击）"
                        )
                # 所有路径验证通过后才解压
                zf.extractall(temp_path)

            # 查找扩展目录（可能是嵌套的）
            extension_dir = temp_path
            manifest_path = extension_dir / "extension.yml"

            # 检查清单是否在子目录中
            if not manifest_path.exists():
                subdirs = [d for d in temp_path.iterdir() if d.is_dir()]
                if len(subdirs) == 1:
                    extension_dir = subdirs[0]
                    manifest_path = extension_dir / "extension.yml"

            if not manifest_path.exists():
                raise ValidationError("ZIP 文件中未找到 extension.yml")

            # 从解压的目录安装
            return self.install_from_directory(extension_dir, speckit_version)

    def remove(self, extension_id: str, keep_config: bool = False) -> bool:
        """移除已安装的扩展. 

        Args:
            extension_id: 扩展 ID
            keep_config: 如果为 True, 则保留配置文件（不删除扩展目录）

        Returns:
            如果扩展被移除则返回 True
        """
        if not self.registry.is_installed(extension_id):
            return False

        # 在移除之前获取已注册的命令
        metadata = self.registry.get(extension_id)
        registered_commands = metadata.get("registered_commands", {})

        extension_dir = self.extensions_dir / extension_id

        # 从所有 AI 代理注销命令
        if registered_commands:
            registrar = CommandRegistrar()
            for agent_name, cmd_names in registered_commands.items():
                if agent_name not in registrar.AGENT_CONFIGS:
                    continue

                agent_config = registrar.AGENT_CONFIGS[agent_name]
                commands_dir = self.project_root / agent_config["dir"]

                for cmd_name in cmd_names:
                    cmd_file = commands_dir / f"{cmd_name}{agent_config['extension']}"
                    if cmd_file.exists():
                        cmd_file.unlink()

        if keep_config:
            # 保留配置文件, 仅移除非配置文件
            if extension_dir.exists():
                for child in extension_dir.iterdir():
                    # 保留顶层的 *-config.yml 和 *-config.local.yml 文件
                    if child.is_file() and (
                        child.name.endswith("-config.yml") or
                        child.name.endswith("-config.local.yml")
                    ):
                        continue
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
        else:
            # 删除前备份配置文件
            if extension_dir.exists():
                # 为每个扩展使用子目录以避免名称累积
                # （例如, 在重复移除/安装循环中出现 jira-jira-config.yml）
                backup_dir = self.extensions_dir / ".backup" / extension_id
                backup_dir.mkdir(parents=True, exist_ok=True)

                # 备份主配置和本地覆盖配置文件
                config_files = list(extension_dir.glob("*-config.yml")) + list(
                    extension_dir.glob("*-config.local.yml")
                )
                for config_file in config_files:
                    backup_path = backup_dir / config_file.name
                    shutil.copy2(config_file, backup_path)

            # 移除扩展目录
            if extension_dir.exists():
                shutil.rmtree(extension_dir)

        # 注销钩子
        hook_executor = HookExecutor(self.project_root)
        hook_executor.unregister_hooks(extension_id)

        # 更新注册表
        self.registry.remove(extension_id)

        return True

    def list_installed(self) -> List[Dict[str, Any]]:
        """列出所有已安装的扩展及其元数据. 

        Returns:
            扩展元数据字典列表
        """
        result = []

        for ext_id, metadata in self.registry.list().items():
            ext_dir = self.extensions_dir / ext_id
            manifest_path = ext_dir / "extension.yml"

            try:
                manifest = ExtensionManifest(manifest_path)
                result.append({
                    "id": ext_id,
                    "name": manifest.name,
                    "version": metadata["version"],
                    "description": manifest.description,
                    "enabled": metadata.get("enabled", True),
                    "installed_at": metadata.get("installed_at"),
                    "command_count": len(manifest.commands),
                    "hook_count": len(manifest.hooks)
                })
            except ValidationError:
                # 损坏的扩展
                result.append({
                    "id": ext_id,
                    "name": ext_id,
                    "version": metadata.get("version", "unknown"),
                    "description": "⚠️ 损坏的扩展",
                    "enabled": False,
                    "installed_at": metadata.get("installed_at"),
                    "command_count": 0,
                    "hook_count": 0
                })

        return result

    def get_extension(self, extension_id: str) -> Optional[ExtensionManifest]:
        """获取已安装扩展的清单. 

        Args:
            extension_id: 扩展 ID

        Returns:
            扩展清单, 如果未安装则返回 None
        """
        if not self.registry.is_installed(extension_id):
            return None

        ext_dir = self.extensions_dir / extension_id
        manifest_path = ext_dir / "extension.yml"

        try:
            return ExtensionManifest(manifest_path)
        except ValidationError:
            return None


def version_satisfies(current: str, required: str) -> bool:
    """检查当前版本是否满足所需的版本说明符. 

    Args:
        current: 当前版本（例如 "0.1.5"）
        required: 所需的版本说明符（例如 ">=0.1.0,<2.0.0"）

    Returns:
        如果版本满足要求则返回 True
    """
    try:
        current_ver = pkg_version.Version(current)
        specifier = SpecifierSet(required)
        return current_ver in specifier
    except (pkg_version.InvalidVersion, InvalidSpecifier):
        return False


class CommandRegistrar:
    """处理扩展命令在 AI 代理中的注册. """

    # 代理配置, 包含目录, 格式和参数占位符
    AGENT_CONFIGS = {
        "claude": {
            "dir": ".claude/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "gemini": {
            "dir": ".gemini/commands",
            "format": "toml",
            "args": "{{args}}",
            "extension": ".toml"
        },
        "copilot": {
            "dir": ".github/agents",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "cursor": {
            "dir": ".cursor/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "qwen": {
            "dir": ".qwen/commands",
            "format": "toml",
            "args": "{{args}}",
            "extension": ".toml"
        },
        "opencode": {
            "dir": ".opencode/command",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "windsurf": {
            "dir": ".windsurf/workflows",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "kilocode": {
            "dir": ".kilocode/rules",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "auggie": {
            "dir": ".augment/rules",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "roo": {
            "dir": ".roo/rules",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "codebuddy": {
            "dir": ".codebuddy/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "qodercli": {
            "dir": ".qoder/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "q": {
            "dir": ".amazonq/prompts",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "amp": {
            "dir": ".agents/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "shai": {
            "dir": ".shai/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        },
        "bob": {
            "dir": ".bob/commands",
            "format": "markdown",
            "args": "$ARGUMENTS",
            "extension": ".md"
        }
    }

    @staticmethod
    def parse_frontmatter(content: str) -> tuple[dict, str]:
        """从 Markdown 内容中解析 YAML frontmatter. 

        Args:
            content: 包含 YAML frontmatter 的 Markdown 内容

        Returns:
            (frontmatter_dict, body_content) 元组
        """
        if not content.startswith("---"):
            return {}, content

        # 查找第二个 ---
        end_marker = content.find("---", 3)
        if end_marker == -1:
            return {}, content

        frontmatter_str = content[3:end_marker].strip()
        body = content[end_marker + 3:].strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            frontmatter = {}

        return frontmatter, body

    @staticmethod
    def render_frontmatter(fm: dict) -> str:
        """将 frontmatter 字典渲染为 YAML. 

        Args:
            fm: Frontmatter 字典

        Returns:
            带分隔符的 YAML 格式 frontmatter
        """
        if not fm:
            return ""

        yaml_str = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---\n"

    def _adjust_script_paths(self, frontmatter: dict) -> dict:
        """将脚本路径从扩展相对路径调整为仓库相对路径. 

        Args:
            frontmatter: Frontmatter 字典

        Returns:
            调整路径后的 frontmatter
        """
        if "scripts" in frontmatter:
            for key in frontmatter["scripts"]:
                script_path = frontmatter["scripts"][key]
                if script_path.startswith("../../scripts/"):
                    frontmatter["scripts"][key] = f".specify/scripts/{script_path[14:]}"
        return frontmatter

    def _render_markdown_command(
        self,
        frontmatter: dict,
        body: str,
        ext_id: str
    ) -> str:
        """以 Markdown 格式渲染命令. 

        Args:
            frontmatter: 命令 frontmatter
            body: 命令正文内容
            ext_id: 扩展 ID

        Returns:
            格式化的 Markdown 命令文件内容
        """
        context_note = f"\n<!-- Extension: {ext_id} -->\n<!-- Config: .specify/extensions/{ext_id}/ -->\n"
        return self.render_frontmatter(frontmatter) + "\n" + context_note + body

    def _render_toml_command(
        self,
        frontmatter: dict,
        body: str,
        ext_id: str
    ) -> str:
        """以 TOML 格式渲染命令. 

        Args:
            frontmatter: 命令 frontmatter
            body: 命令正文内容
            ext_id: 扩展 ID

        Returns:
            格式化的 TOML 命令文件内容
        """
        # Gemini/Qwen 的 TOML 格式
        toml_lines = []

        # 如果存在描述则添加
        if "description" in frontmatter:
            # 转义描述中的引号
            desc = frontmatter["description"].replace('"', '\\"')
            toml_lines.append(f'description = "{desc}"')
            toml_lines.append("")

        # 以注释形式添加扩展上下文
        toml_lines.append(f"# Extension: {ext_id}")
        toml_lines.append(f"# Config: .specify/extensions/{ext_id}/")
        toml_lines.append("")

        # 添加提示内容
        toml_lines.append('prompt = """')
        toml_lines.append(body)
        toml_lines.append('"""')

        return "\n".join(toml_lines)

    def _convert_argument_placeholder(self, content: str, from_placeholder: str, to_placeholder: str) -> str:
        """转换参数占位符格式. 

        Args:
            content: 命令内容
            from_placeholder: 源占位符（例如 "$ARGUMENTS"）
            to_placeholder: 目标占位符（例如 "{{args}}"）

        Returns:
            转换占位符后的内容
        """
        return content.replace(from_placeholder, to_placeholder)

    def register_commands_for_agent(
        self,
        agent_name: str,
        manifest: ExtensionManifest,
        extension_dir: Path,
        project_root: Path
    ) -> List[str]:
        """为特定代理注册扩展命令. 

        Args:
            agent_name: 代理名称（claude, gemini, copilot 等）
            manifest: 扩展清单
            extension_dir: 扩展目录的路径
            project_root: 项目根目录的路径

        Returns:
            已注册的命令名称列表

        Raises:
            ExtensionError: 如果不支持该代理
        """
        if agent_name not in self.AGENT_CONFIGS:
            raise ExtensionError(f"不支持的代理: {agent_name}")

        agent_config = self.AGENT_CONFIGS[agent_name]
        commands_dir = project_root / agent_config["dir"]
        commands_dir.mkdir(parents=True, exist_ok=True)

        registered = []

        for cmd_info in manifest.commands:
            cmd_name = cmd_info["name"]
            cmd_file = cmd_info["file"]

            # 读取源命令文件
            source_file = extension_dir / cmd_file
            if not source_file.exists():
                continue

            content = source_file.read_text()
            frontmatter, body = self.parse_frontmatter(content)

            # 调整脚本路径
            frontmatter = self._adjust_script_paths(frontmatter)

            # 转换参数占位符
            body = self._convert_argument_placeholder(
                body, "$ARGUMENTS", agent_config["args"]
            )

            # 以代理特定格式渲染
            if agent_config["format"] == "markdown":
                output = self._render_markdown_command(frontmatter, body, manifest.id)
            elif agent_config["format"] == "toml":
                output = self._render_toml_command(frontmatter, body, manifest.id)
            else:
                raise ExtensionError(f"不支持的格式: {agent_config['format']}")

            # 写入命令文件
            dest_file = commands_dir / f"{cmd_name}{agent_config['extension']}"
            dest_file.write_text(output)

            registered.append(cmd_name)

            # 注册别名
            for alias in cmd_info.get("aliases", []):
                alias_file = commands_dir / f"{alias}{agent_config['extension']}"
                alias_file.write_text(output)
                registered.append(alias)

        return registered

    def register_commands_for_all_agents(
        self,
        manifest: ExtensionManifest,
        extension_dir: Path,
        project_root: Path
    ) -> Dict[str, List[str]]:
        """为所有检测到的代理注册扩展命令. 

        Args:
            manifest: 扩展清单
            extension_dir: 扩展目录的路径
            project_root: 项目根目录的路径

        Returns:
            代理名称到已注册命令列表的映射字典
        """
        results = {}

        # 检测项目中存在哪些代理
        for agent_name, agent_config in self.AGENT_CONFIGS.items():
            agent_dir = project_root / agent_config["dir"].split("/")[0]

            # 如果代理目录存在则注册
            if agent_dir.exists():
                try:
                    registered = self.register_commands_for_agent(
                        agent_name, manifest, extension_dir, project_root
                    )
                    if registered:
                        results[agent_name] = registered
                except ExtensionError:
                    # 出错时跳过该代理
                    continue

        return results

    def register_commands_for_claude(
        self,
        manifest: ExtensionManifest,
        extension_dir: Path,
        project_root: Path
    ) -> List[str]:
        """为 Claude Code 代理注册扩展命令. 

        Args:
            manifest: 扩展清单
            extension_dir: 扩展目录的路径
            project_root: 项目根目录的路径

        Returns:
            已注册的命令名称列表
        """
        return self.register_commands_for_agent("claude", manifest, extension_dir, project_root)


class ExtensionCatalog:
    """管理扩展目录的获取, 缓存和搜索. """

    DEFAULT_CATALOG_URL = "https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json"
    CACHE_DURATION = 3600  # 1 小时（以秒为单位）

    def __init__(self, project_root: Path):
        """初始化扩展目录管理器. 

        Args:
            project_root: spec-kit 项目的根目录
        """
        self.project_root = project_root
        self.extensions_dir = project_root / ".specify" / "extensions"
        self.cache_dir = self.extensions_dir / ".cache"
        self.cache_file = self.cache_dir / "catalog.json"
        self.cache_metadata_file = self.cache_dir / "catalog-metadata.json"

    def get_catalog_url(self) -> str:
        """从配置获取目录 URL 或使用默认值. 

        按以下顺序检查:
        1. SPECKIT_CATALOG_URL 环境变量
        2. 默认目录 URL

        Returns:
            获取目录的 URL

        Raises:
            ValidationError: 如果自定义 URL 无效（非 HTTPS）
        """
        import os
        import sys
        from urllib.parse import urlparse

        # 环境变量覆盖（用于测试）
        if env_value := os.environ.get("SPECKIT_CATALOG_URL"):
            catalog_url = env_value.strip()
            parsed = urlparse(catalog_url)

            # 出于安全考虑要求 HTTPS（防止中间人攻击）
            # 允许 http://localhost 用于本地开发/测试
            is_localhost = parsed.hostname in ("localhost", "127.0.0.1", "::1")
            if parsed.scheme != "https" and not (parsed.scheme == "http" and is_localhost):
                raise ValidationError(
                    f"无效的 SPECKIT_CATALOG_URL: 必须使用 HTTPS（当前为 {parsed.scheme}://）. "
                    "仅 localhost 允许使用 HTTP. "
                )

            if not parsed.netloc:
                raise ValidationError(
                    "无效的 SPECKIT_CATALOG_URL: 必须是包含主机的有效 URL. "
                )

            # 当使用非默认目录时警告用户（每个实例仅一次）
            if catalog_url != self.DEFAULT_CATALOG_URL:
                if not getattr(self, "_non_default_catalog_warning_shown", False):
                    print(
                        "警告: 正在使用非默认扩展目录. "
                        "请仅使用您信任的来源的目录. ",
                        file=sys.stderr,
                    )
                    self._non_default_catalog_warning_shown = True

            return catalog_url

        # TODO: 支持来自 .specify/extension-catalogs.yml 的自定义目录
        return self.DEFAULT_CATALOG_URL

    def is_cache_valid(self) -> bool:
        """检查缓存的目录是否仍然有效. 

        Returns:
            如果缓存存在且在缓存有效期内则返回 True
        """
        if not self.cache_file.exists() or not self.cache_metadata_file.exists():
            return False

        try:
            metadata = json.loads(self.cache_metadata_file.read_text())
            cached_at = datetime.fromisoformat(metadata.get("cached_at", ""))
            age_seconds = (datetime.now(timezone.utc) - cached_at).total_seconds()
            return age_seconds < self.CACHE_DURATION
        except (json.JSONDecodeError, ValueError, KeyError):
            return False

    def fetch_catalog(self, force_refresh: bool = False) -> Dict[str, Any]:
        """从 URL 或缓存获取扩展目录. 

        Args:
            force_refresh: 如果为 True, 则绕过缓存从网络获取

        Returns:
            目录数据字典

        Raises:
            ExtensionError: 如果无法获取目录
        """
        # 除非强制刷新, 否则先检查缓存
        if not force_refresh and self.is_cache_valid():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                pass  # 继续从网络获取

        # 从网络获取
        catalog_url = self.get_catalog_url()

        try:
            import urllib.request
            import urllib.error

            with urllib.request.urlopen(catalog_url, timeout=10) as response:
                catalog_data = json.loads(response.read())

            # 验证目录结构
            if "schema_version" not in catalog_data or "extensions" not in catalog_data:
                raise ExtensionError("无效的目录格式")

            # 保存到缓存
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(catalog_data, indent=2))

            # 保存缓存元数据
            metadata = {
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "catalog_url": catalog_url,
            }
            self.cache_metadata_file.write_text(json.dumps(metadata, indent=2))

            return catalog_data

        except urllib.error.URLError as e:
            raise ExtensionError(f"从 {catalog_url} 获取目录失败: {e}")
        except json.JSONDecodeError as e:
            raise ExtensionError(f"目录中的 JSON 无效: {e}")

    def search(
        self,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        verified_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """在目录中搜索扩展. 

        Args:
            query: 搜索查询（搜索名称, 描述, 标签）
            tag: 按特定标签过滤
            author: 按作者名称过滤
            verified_only: 如果为 True, 则仅显示已验证的扩展

        Returns:
            匹配的扩展元数据列表
        """
        catalog = self.fetch_catalog()
        extensions = catalog.get("extensions", {})

        results = []

        for ext_id, ext_data in extensions.items():
            # 应用过滤器
            if verified_only and not ext_data.get("verified", False):
                continue

            if author and ext_data.get("author", "").lower() != author.lower():
                continue

            if tag and tag.lower() not in [t.lower() for t in ext_data.get("tags", [])]:
                continue

            if query:
                # 在名称, 描述和标签中搜索
                query_lower = query.lower()
                searchable_text = " ".join(
                    [
                        ext_data.get("name", ""),
                        ext_data.get("description", ""),
                        ext_id,
                    ]
                    + ext_data.get("tags", [])
                ).lower()

                if query_lower not in searchable_text:
                    continue

            results.append({"id": ext_id, **ext_data})

        return results

    def get_extension_info(self, extension_id: str) -> Optional[Dict[str, Any]]:
        """获取特定扩展的详细信息. 

        Args:
            extension_id: 扩展 ID

        Returns:
            扩展元数据, 如果未找到则返回 None
        """
        catalog = self.fetch_catalog()
        extensions = catalog.get("extensions", {})

        if extension_id in extensions:
            return {"id": extension_id, **extensions[extension_id]}

        return None

    def download_extension(self, extension_id: str, target_dir: Optional[Path] = None) -> Path:
        """从目录下载扩展 ZIP 文件. 

        Args:
            extension_id: 要下载的扩展 ID
            target_dir: 保存 ZIP 文件的目录（默认为临时目录）

        Returns:
            下载的 ZIP 文件路径

        Raises:
            ExtensionError: 如果扩展未找到或下载失败
        """
        import urllib.request
        import urllib.error

        # 从目录获取扩展信息
        ext_info = self.get_extension_info(extension_id)
        if not ext_info:
            raise ExtensionError(f"在目录中未找到扩展 '{extension_id}'")

        download_url = ext_info.get("download_url")
        if not download_url:
            raise ExtensionError(f"扩展 '{extension_id}' 没有下载 URL")

        # 验证下载 URL 需要 HTTPS（防止中间人攻击）
        from urllib.parse import urlparse
        parsed = urlparse(download_url)
        is_localhost = parsed.hostname in ("localhost", "127.0.0.1", "::1")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and is_localhost):
            raise ExtensionError(
                f"扩展下载 URL 必须使用 HTTPS: {download_url}"
            )

        # 确定目标路径
        if target_dir is None:
            target_dir = self.cache_dir / "downloads"
        target_dir.mkdir(parents=True, exist_ok=True)

        version = ext_info.get("version", "unknown")
        zip_filename = f"{extension_id}-{version}.zip"
        zip_path = target_dir / zip_filename

        # 下载 ZIP 文件
        try:
            with urllib.request.urlopen(download_url, timeout=60) as response:
                zip_data = response.read()

            zip_path.write_bytes(zip_data)
            return zip_path

        except urllib.error.URLError as e:
            raise ExtensionError(f"从 {download_url} 下载扩展失败: {e}")
        except IOError as e:
            raise ExtensionError(f"保存扩展 ZIP 失败: {e}")

    def clear_cache(self):
        """清除目录缓存. """
        if self.cache_file.exists():
            self.cache_file.unlink()
        if self.cache_metadata_file.exists():
            self.cache_metadata_file.unlink()


class ConfigManager:
    """管理扩展的分层配置. 

    配置层级（按优先级从低到高排序）:
    1. 默认值（来自 extension.yml）
    2. 项目配置（.specify/extensions/{ext-id}/{ext-id}-config.yml）
    3. 本地配置（.specify/extensions/{ext-id}/local-config.yml）- gitignored
    4. 环境变量（SPECKIT_{EXT_ID}_{KEY}）
    """

    def __init__(self, project_root: Path, extension_id: str):
        """为扩展初始化配置管理器. 

        Args:
            project_root: spec-kit 项目的根目录
            extension_id: 扩展 ID
        """
        self.project_root = project_root
        self.extension_id = extension_id
        self.extension_dir = project_root / ".specify" / "extensions" / extension_id

    def _load_yaml_config(self, file_path: Path) -> Dict[str, Any]:
        """从 YAML 文件加载配置. 

        Args:
            file_path: YAML 文件的路径

        Returns:
            配置字典
        """
        if not file_path.exists():
            return {}

        try:
            return yaml.safe_load(file_path.read_text()) or {}
        except (yaml.YAMLError, OSError):
            return {}

    def _get_extension_defaults(self) -> Dict[str, Any]:
        """从扩展清单获取默认配置. 

        Returns:
            默认配置字典
        """
        manifest_path = self.extension_dir / "extension.yml"
        if not manifest_path.exists():
            return {}

        manifest_data = self._load_yaml_config(manifest_path)
        return manifest_data.get("config", {}).get("defaults", {})

    def _get_project_config(self) -> Dict[str, Any]:
        """获取项目级配置. 

        Returns:
            项目配置字典
        """
        config_file = self.extension_dir / f"{self.extension_id}-config.yml"
        return self._load_yaml_config(config_file)

    def _get_local_config(self) -> Dict[str, Any]:
        """获取本地配置（gitignored, 机器特定）. 

        Returns:
            本地配置字典
        """
        config_file = self.extension_dir / "local-config.yml"
        return self._load_yaml_config(config_file)

    def _get_env_config(self) -> Dict[str, Any]:
        """从环境变量获取配置. 

        环境变量遵循以下模式:
        SPECKIT_{EXT_ID}_{SECTION}_{KEY}

        例如:
        - SPECKIT_JIRA_CONNECTION_URL
        - SPECKIT_JIRA_PROJECT_KEY

        Returns:
            来自环境变量的配置字典
        """
        import os

        env_config = {}
        ext_id_upper = self.extension_id.replace("-", "_").upper()
        prefix = f"SPECKIT_{ext_id_upper}_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            # 移除前缀并拆分为多个部分
            config_path = key[len(prefix):].lower().split("_")

            # 构建嵌套字典
            current = env_config
            for part in config_path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # 设置最终值
            current[config_path[-1]] = value

        return env_config

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并两个配置字典. 

        Args:
            base: 基础配置
            override: 要合并到上面的配置

        Returns:
            合并后的配置
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 嵌套字典的递归合并
                result[key] = self._merge_configs(result[key], value)
            else:
                # 覆盖值
                result[key] = value

        return result

    def get_config(self) -> Dict[str, Any]:
        """获取扩展的最终合并配置. 

        按以下顺序合并配置层级:
        defaults -> project -> local -> env

        Returns:
            最终合并的配置字典
        """
        # 从默认值开始
        config = self._get_extension_defaults()

        # 合并项目配置
        config = self._merge_configs(config, self._get_project_config())

        # 合并本地配置
        config = self._merge_configs(config, self._get_local_config())

        # 合并环境变量配置
        config = self._merge_configs(config, self._get_env_config())

        return config

    def get_value(self, key_path: str, default: Any = None) -> Any:
        """通过点符号路径获取特定的配置值. 

        Args:
            key_path: 配置值的点分隔路径（例如 "connection.url"）
            default: 如果未找到键则使用的默认值

        Returns:
            配置值或默认值

        Example:
            >>> config = ConfigManager(project_root, "jira")
            >>> url = config.get_value("connection.url")
            >>> timeout = config.get_value("connection.timeout", 30)
        """
        config = self.get_config()
        keys = key_path.split(".")

        current = config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current

    def has_value(self, key_path: str) -> bool:
        """检查配置值是否存在. 

        Args:
            key_path: 配置值的点分隔路径

        Returns:
            如果值存在（即使为 None）则返回 True, 否则返回 False
        """
        config = self.get_config()
        keys = key_path.split(".")

        current = config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]

        return True


class HookExecutor:
    """管理扩展钩子的执行. """

    def __init__(self, project_root: Path):
        """初始化钩子执行器. 

        Args:
            project_root: spec-kit 项目的根目录
        """
        self.project_root = project_root
        self.extensions_dir = project_root / ".specify" / "extensions"
        self.config_file = project_root / ".specify" / "extensions.yml"

    def get_project_config(self) -> Dict[str, Any]:
        """加载项目级扩展配置. 

        Returns:
            扩展配置字典
        """
        if not self.config_file.exists():
            return {
                "installed": [],
                "settings": {"auto_execute_hooks": True},
                "hooks": {},
            }

        try:
            return yaml.safe_load(self.config_file.read_text()) or {}
        except (yaml.YAMLError, OSError):
            return {
                "installed": [],
                "settings": {"auto_execute_hooks": True},
                "hooks": {},
            }

    def save_project_config(self, config: Dict[str, Any]):
        """保存项目级扩展配置. 

        Args:
            config: 要保存的配置字典
        """
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            yaml.dump(config, default_flow_style=False, sort_keys=False)
        )

    def register_hooks(self, manifest: ExtensionManifest):
        """在项目配置中注册扩展钩子. 

        Args:
            manifest: 包含要注册钩子的扩展清单
        """
        if not hasattr(manifest, "hooks") or not manifest.hooks:
            return

        config = self.get_project_config()

        # 确保钩子字典存在
        if "hooks" not in config:
            config["hooks"] = {}

        # 注册每个钩子
        for hook_name, hook_config in manifest.hooks.items():
            if hook_name not in config["hooks"]:
                config["hooks"][hook_name] = []

            # 添加钩子条目
            hook_entry = {
                "extension": manifest.id,
                "command": hook_config.get("command"),
                "enabled": True,
                "optional": hook_config.get("optional", True),
                "prompt": hook_config.get(
                    "prompt", f"执行 {hook_config.get('command')}?"
                ),
                "description": hook_config.get("description", ""),
                "condition": hook_config.get("condition"),
            }

            # 检查是否已注册
            existing = [
                h
                for h in config["hooks"][hook_name]
                if h.get("extension") == manifest.id
            ]

            if not existing:
                config["hooks"][hook_name].append(hook_entry)
            else:
                # 更新现有条目
                for i, h in enumerate(config["hooks"][hook_name]):
                    if h.get("extension") == manifest.id:
                        config["hooks"][hook_name][i] = hook_entry

        self.save_project_config(config)

    def unregister_hooks(self, extension_id: str):
        """从项目配置中移除扩展钩子. 

        Args:
            extension_id: 要注销的扩展 ID
        """
        config = self.get_project_config()

        if "hooks" not in config:
            return

        # 移除此扩展的钩子
        for hook_name in config["hooks"]:
            config["hooks"][hook_name] = [
                h
                for h in config["hooks"][hook_name]
                if h.get("extension") != extension_id
            ]

        # 清理空的钩子数组
        config["hooks"] = {
            name: hooks for name, hooks in config["hooks"].items() if hooks
        }

        self.save_project_config(config)

    def get_hooks_for_event(self, event_name: str) -> List[Dict[str, Any]]:
        """获取特定事件的所有已注册钩子. 

        Args:
            event_name: 事件名称（例如 'after_tasks'）

        Returns:
            钩子配置列表
        """
        config = self.get_project_config()
        hooks = config.get("hooks", {}).get(event_name, [])

        # 仅过滤启用的钩子
        return [h for h in hooks if h.get("enabled", True)]

    def should_execute_hook(self, hook: Dict[str, Any]) -> bool:
        """根据条件判断是否应执行钩子. 

        Args:
            hook: 钩子配置

        Returns:
            如果应执行钩子则返回 True, 否则返回 False
        """
        condition = hook.get("condition")

        if not condition:
            return True

        # 解析并评估条件
        try:
            return self._evaluate_condition(condition, hook.get("extension"))
        except Exception:
            # 如果条件评估失败, 默认不执行
            return False

    def _evaluate_condition(self, condition: str, extension_id: Optional[str]) -> bool:
        """评估钩子条件表达式. 

        支持的条件模式:
        - "config.key.path is set" - 检查配置值是否存在
        - "config.key.path == 'value'" - 检查配置是否等于值
        - "config.key.path != 'value'" - 检查配置是否不等于值
        - "env.VAR_NAME is set" - 检查环境变量是否存在
        - "env.VAR_NAME == 'value'" - 检查环境变量是否等于值

        Args:
            condition: 条件表达式字符串
            extension_id: 用于配置查找的扩展 ID

        Returns:
            如果满足条件则返回 True, 否则返回 False
        """
        import os

        condition = condition.strip()

        # 模式: "config.key.path is set"
        if match := re.match(r'config\.([a-z0-9_.]+)\s+is\s+set', condition, re.IGNORECASE):
            key_path = match.group(1)
            if not extension_id:
                return False

            config_manager = ConfigManager(self.project_root, extension_id)
            return config_manager.has_value(key_path)

        # 模式: "config.key.path == 'value'" 或 "config.key.path != 'value'"
        if match := re.match(r'config\.([a-z0-9_.]+)\s*(==|!=)\s*["\']([^"\']+)["\']', condition, re.IGNORECASE):
            key_path = match.group(1)
            operator = match.group(2)
            expected_value = match.group(3)

            if not extension_id:
                return False

            config_manager = ConfigManager(self.project_root, extension_id)
            actual_value = config_manager.get_value(key_path)

            # 将布尔值规范化为小写以进行比较
            # (YAML True/False 与条件字符串 'true'/'false')
            if isinstance(actual_value, bool):
                normalized_value = "true" if actual_value else "false"
            else:
                normalized_value = str(actual_value)

            if operator == "==":
                return normalized_value == expected_value
            else:  # !=
                return normalized_value != expected_value

        # 模式: "env.VAR_NAME is set"
        if match := re.match(r'env\.([A-Z0-9_]+)\s+is\s+set', condition, re.IGNORECASE):
            var_name = match.group(1).upper()
            return var_name in os.environ

        # 模式: "env.VAR_NAME == 'value'" 或 "env.VAR_NAME != 'value'"
        if match := re.match(r'env\.([A-Z0-9_]+)\s*(==|!=)\s*["\']([^"\']+)["\']', condition, re.IGNORECASE):
            var_name = match.group(1).upper()
            operator = match.group(2)
            expected_value = match.group(3)

            actual_value = os.environ.get(var_name, "")

            if operator == "==":
                return actual_value == expected_value
            else:  # !=
                return actual_value != expected_value

        # 未知条件格式, 为安全起见默认为 False
        return False

    def format_hook_message(
        self, event_name: str, hooks: List[Dict[str, Any]]
    ) -> str:
        """格式化钩子执行消息以便在命令输出中显示. 

        Args:
            event_name: 事件名称
            hooks: 要执行的钩子列表

        Returns:
            格式化的消息字符串
        """
        if not hooks:
            return ""

        lines = ["\n## 扩展钩子\n"]
        lines.append(f"事件 '{event_name}' 可用的钩子:\n")

        for hook in hooks:
            extension = hook.get("extension")
            command = hook.get("command")
            optional = hook.get("optional", True)
            prompt = hook.get("prompt", "")
            description = hook.get("description", "")

            if optional:
                lines.append(f"\n**可选钩子**: {extension}")
                lines.append(f"命令: `/{command}`")
                if description:
                    lines.append(f"描述: {description}")
                lines.append(f"\n提示: {prompt}")
                lines.append(f"执行方式: `/{command}`")
            else:
                lines.append(f"\n**自动钩子**: {extension}")
                lines.append(f"正在执行: `/{command}`")
                lines.append(f"EXECUTE_COMMAND: {command}")

        return "\n".join(lines)

    def check_hooks_for_event(self, event_name: str) -> Dict[str, Any]:
        """检查为特定事件注册的钩子. 

        此方法设计为核心命令完成后由 AI 代理调用. 

        Args:
            event_name: 事件名称（例如 'after_spec', 'after_tasks'）

        Returns:
            包含钩子信息的字典:
            - has_hooks: bool - 是否存在此事件的钩子
            - hooks: List[Dict] - 钩子列表（已应用条件评估）
            - message: str - 格式化的显示消息
        """
        hooks = self.get_hooks_for_event(event_name)

        if not hooks:
            return {
                "has_hooks": False,
                "hooks": [],
                "message": ""
            }

        # 按条件过滤钩子
        executable_hooks = []
        for hook in hooks:
            if self.should_execute_hook(hook):
                executable_hooks.append(hook)

        if not executable_hooks:
            return {
                "has_hooks": False,
                "hooks": [],
                "message": f"# 事件 '{event_name}' 没有可执行的钩子（条件未满足）"
            }

        return {
            "has_hooks": True,
            "hooks": executable_hooks,
            "message": self.format_hook_message(event_name, executable_hooks)
        }

    def execute_hook(self, hook: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个钩子命令. 

        注意: 此方法返回有关如何执行钩子的信息. 
        实际执行委托给 AI 代理. 

        Args:
            hook: 钩子配置

        Returns:
            包含执行信息的字典:
            - command: str - 要执行的命令
            - extension: str - 扩展 ID
            - optional: bool - 钩子是否可选
            - description: str - 钩子描述
        """
        return {
            "command": hook.get("command"),
            "extension": hook.get("extension"),
            "optional": hook.get("optional", True),
            "description": hook.get("description", ""),
            "prompt": hook.get("prompt", "")
        }

    def enable_hooks(self, extension_id: str):
        """启用扩展的所有钩子. 

        Args:
            extension_id: 扩展 ID
        """
        config = self.get_project_config()

        if "hooks" not in config:
            return

        # 启用此扩展的所有钩子
        for hook_name in config["hooks"]:
            for hook in config["hooks"][hook_name]:
                if hook.get("extension") == extension_id:
                    hook["enabled"] = True

        self.save_project_config(config)

    def disable_hooks(self, extension_id: str):
        """禁用扩展的所有钩子. 

        Args:
            extension_id: 扩展 ID
        """
        config = self.get_project_config()

        if "hooks" not in config:
            return

        # 禁用此扩展的所有钩子
        for hook_name in config["hooks"]:
            for hook in config["hooks"][hook_name]:
                if hook.get("extension") == extension_id:
                    hook["enabled"] = False

        self.save_project_config(config)



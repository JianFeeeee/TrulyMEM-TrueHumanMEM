"""配置服务"""

from pathlib import Path
from typing import TYPE_CHECKING
from ..models.config import AppConfig

if TYPE_CHECKING:
    from ..core.imports import GraphMemoryClient


class ConfigService:
    """配置服务"""

    DEFAULT_CONFIG_FILE = Path.home() / ".graph_memory_tui" / "config.json"

    def __init__(self, config_file: Path | None = None):
        self._config_file = config_file or self.DEFAULT_CONFIG_FILE
        self._config = self._load_config()

    def _load_config(self) -> AppConfig:
        """加载配置"""
        # 优先从文件加载
        if self._config_file.exists():
            return AppConfig.from_file(self._config_file)

        # 否则从环境变量加载
        return AppConfig.from_env()

    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self._config

    def set_config(self, config: AppConfig) -> None:
        """设置配置"""
        self._config = config
        self._save_config()

    def _save_config(self) -> None:
        """保存配置"""
        self._config.save(self._config_file)

    def apply_to_client(self, client: "GraphMemoryClient") -> None:
        """应用配置到 API 客户端"""
        # 更新客户端配置
        client.api_key = self._config.api_key
        client.base_url = self._config.base_url
        client.model = self._config.model

    def get_config_file(self) -> Path:
        """获取配置文件路径"""
        return self._config_file

"""
配置管理 - 支持持久化
"""

import json
from pathlib import Path
from .config import AppConfig


class ConfigManager:
    """配置管理器 - 支持持久化"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
    
    def save(self, config: AppConfig) -> None:
        """保存配置到文件"""
        data = {
            "api_key": config.api_key,
            "model": config.model,
            "base_url": config.base_url
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> AppConfig:
        """从文件加载配置"""
        if not self.config_file.exists():
            return AppConfig()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return AppConfig(
                api_key=data.get("api_key", ""),
                model=data.get("model", "deepseek-chat"),
                base_url=data.get("base_url", "https://api.deepseek.com")
            )
        except Exception:
            return AppConfig()
    
    def exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_file.exists()

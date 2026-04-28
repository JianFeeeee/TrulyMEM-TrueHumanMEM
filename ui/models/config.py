"""配置数据模型"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """应用配置"""
    api_key: str = ""
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"
    persona_update_max: int = 1
    task_update_max: int = 5
    memory_query_max: int = 20
    memory_update_max: int = 10
    web_username: str = ""
    web_password: str = ""
    enable_web: bool = False
    web_port: int = 4096
    enable_tui: bool = True

    @classmethod
    def from_env(cls, username: str = "") -> "AppConfig":
        """
        从环境变量加载配置。
        如果指定了 username，尝试从用户的配置文件加载。
        """
        # 如果指定了用户名，尝试从用户的配置文件加载
        if username:
            from pathlib import Path
            user_config_path = Path.home() / ".trulymem" / username / "config.json"
            if user_config_path.exists():
                return cls.from_file(user_config_path)
        
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            persona_update_max=int(os.getenv("PERSONA_UPDATE_MAX", 1)),
            task_update_max=int(os.getenv("TASK_UPDATE_MAX", 5)),
            memory_query_max=int(os.getenv("MEMORY_QUERY_MAX", 20)),
            memory_update_max=int(os.getenv("MEMORY_UPDATE_MAX", 10)),
            web_username=os.getenv("WEB_USERNAME", ""),
            web_password=os.getenv("WEB_PASSWORD", ""),
            enable_web=os.getenv("ENABLE_WEB", "false").lower() == "true",
            web_port=int(os.getenv("WEB_PORT", 4096)),
            enable_tui=os.getenv("ENABLE_TUI", "true").lower() == "true",
        )

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            api_key=data.get("api_key", ""),
            model=data.get("model", "deepseek-v4-flash"),
            base_url=data.get("base_url", "https://api.deepseek.com"),
            persona_update_max=data.get("persona_update_max", 1),
            task_update_max=data.get("task_update_max", 5),
            memory_query_max=data.get("memory_query_max", 20),
            memory_update_max=data.get("memory_update_max", 10),
            web_username=data.get("web_username", ""),
            web_password=data.get("web_password", ""),
            enable_web=data.get("enable_web", False),
            web_port=data.get("web_port", 4096),
            enable_tui=data.get("enable_tui", True),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

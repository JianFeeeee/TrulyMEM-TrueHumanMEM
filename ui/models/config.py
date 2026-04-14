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
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    persona_query_max: int = 1
    persona_update_max: int = 1
    task_query_max: int = 4
    task_update_max: int = 2
    memory_query_max: int = 20
    memory_update_max: int = 10

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("MODEL_NAME", "deepseek-chat"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            persona_query_max=int(os.getenv("PERSONA_QUERY_MAX", 1)),
            persona_update_max=int(os.getenv("PERSONA_UPDATE_MAX", 1)),
            task_query_max=int(os.getenv("TASK_QUERY_MAX", 4)),
            task_update_max=int(os.getenv("TASK_UPDATE_MAX", 2)),
            memory_query_max=int(os.getenv("MEMORY_QUERY_MAX", 20)),
            memory_update_max=int(os.getenv("MEMORY_UPDATE_MAX", 10)),
        )

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            api_key=data.get("api_key", ""),
            model=data.get("model", "deepseek-chat"),
            base_url=data.get("base_url", "https://api.deepseek.com"),
            persona_query_max=data.get("persona_query_max", 1),
            persona_update_max=data.get("persona_update_max", 1),
            task_query_max=data.get("task_query_max", 4),
            task_update_max=data.get("task_update_max", 2),
            memory_query_max=data.get("memory_query_max", 20),
            memory_update_max=data.get("memory_update_max", 10),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

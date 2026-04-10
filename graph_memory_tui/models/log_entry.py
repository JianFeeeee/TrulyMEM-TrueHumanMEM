"""日志条目数据模型"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    tool_name: str
    arguments: Dict[str, Any]
    result: str
    duration: float

    @property
    def args_summary(self) -> str:
        """参数摘要（截断到50字符）"""
        args_str = str(self.arguments)
        if len(args_str) > 50:
            return args_str[:50] + "..."
        return args_str

    @property
    def result_summary(self) -> str:
        """结果摘要（截断到100字符）"""
        if len(self.result) > 100:
            return self.result[:100] + "..."
        return self.result

"""消息数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Literal, Optional, Any


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_call_id: str
    name: str
    arguments: Dict[str, Any]
    result: str
    success: bool


@dataclass
class Message:
    """消息"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None

"""工具服务"""

import asyncio
import time
from datetime import datetime
from typing import Callable, TYPE_CHECKING
from ..core.imports import execute_tool
from ..models.log_entry import LogEntry
from ..models.message import ToolCall, ToolResult

if TYPE_CHECKING:
    from ..core.imports import Neo4jGraph


class ToolService:
    """工具执行服务"""

    def __init__(
        self,
        graph: "Neo4jGraph",
        log_callback: Callable[[LogEntry], None] | None = None
    ):
        self._graph = graph
        self._log_callback = log_callback

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """异步执行工具"""
        start_time = time.time()

        try:
            # 在线程池中执行同步工具
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: execute_tool(self._graph, tool_call.name, tool_call.arguments)
            )

            duration = time.time() - start_time

            # 创建日志条目
            log_entry = LogEntry(
                timestamp=datetime.now(),
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                result=result,
                duration=duration
            )

            # 回调日志
            if self._log_callback:
                self._log_callback(log_entry)

            # 返回结果
            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                arguments=tool_call.arguments,
                result=result,
                success=not result.startswith("工具执行错误")
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"工具执行异常: {str(e)}"

            # 创建错误日志
            log_entry = LogEntry(
                timestamp=datetime.now(),
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                result=error_msg,
                duration=duration
            )

            if self._log_callback:
                self._log_callback(log_entry)

            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                arguments=tool_call.arguments,
                result=error_msg,
                success=False
            )

    def set_log_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """设置日志回调"""
        self._log_callback = callback

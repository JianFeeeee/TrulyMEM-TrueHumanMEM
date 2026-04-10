"""聊天服务"""

import asyncio
from datetime import datetime
from typing import AsyncIterator, TYPE_CHECKING
from ..core.imports import GraphMemoryClient
from ..models.message import ToolCall, ToolResult
from .tool_service import ToolService

if TYPE_CHECKING:
    from ..core.imports import Neo4jGraph


class ChatService:
    """聊天业务服务"""

    def __init__(
        self,
        graph: "Neo4jGraph",
        client: GraphMemoryClient,
        tool_service: ToolService
    ):
        self._graph = graph
        self._client = client
        self._tool_service = tool_service
        self._messages: list[dict] = []

    async def send_message(self, user_input: str) -> AsyncIterator[dict]:
        """发送消息并流式返回事件"""
        # 1. 发送用户消息事件
        yield {
            "type": "user_message",
            "content": user_input
        }

        try:
            # 2. 异步调用 API
            response = await self._call_api_async(user_input)

            # 3. 处理工具调用
            tool_calls = None
            tool_results = None

            if response.tool_calls:
                tool_calls = []
                tool_results = []

                for tool_call_data in response.tool_calls:
                    # 创建工具调用对象
                    tool_call = ToolCall(
                        id=tool_call_data.id,
                        name=tool_call_data.function.name,
                        arguments=tool_call_data.function.arguments
                    )
                    tool_calls.append(tool_call)

                    # 发送工具调用事件
                    yield {
                        "type": "tool_call",
                        "tool_call": tool_call
                    }

                    # 执行工具
                    result = await self._tool_service.execute(tool_call)
                    tool_results.append(result)

                    # 发送工具结果事件
                    log_entry = ToolService._create_log_entry(tool_call, result)
                    yield {
                        "type": "tool_result",
                        "tool_result": result,
                        "log_entry": log_entry
                    }

            # 4. 返回最终回复
            yield {
                "type": "assistant_message",
                "content": response.content,
                "tool_calls": tool_calls,
                "tool_results": tool_results
            }

        except Exception as e:
            # 错误处理
            yield {
                "type": "error",
                "error": str(e)
            }

    async def _call_api_async(self, message: str):
        """异步调用 API"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.send_message(message)
        )

    def clear_history(self) -> None:
        """清空消息历史"""
        self._messages.clear()

    def get_history(self) -> list[dict]:
        """获取消息历史"""
        return self._messages.copy()

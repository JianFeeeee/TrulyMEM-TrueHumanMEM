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
            # 2. 使用流式API调用
            accumulated_content = ""
            tool_calls_data = []
            
            # 流式处理响应
            async for chunk in self._call_api_stream_async(user_input):
                # 处理内容增量
                if chunk.get("content_delta"):
                    accumulated_content += chunk["content_delta"]
                    yield {
                        "type": "content_delta",
                        "content": accumulated_content
                    }
                
                # 处理工具调用
                if chunk.get("tool_calls"):
                    tool_calls_data = chunk["tool_calls"]
            
            # 3. 处理工具调用
            tool_calls = None
            tool_results = None

            if tool_calls_data:
                tool_calls = []
                tool_results = []

                for tool_call_data in tool_calls_data:
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
                "content": accumulated_content,
                "tool_calls": tool_calls,
                "tool_results": tool_results
            }

        except Exception as e:
            # 错误处理
            yield {
                "type": "error",
                "error": str(e)
            }

    async def _call_api_stream_async(self, message: str) -> AsyncIterator[dict]:
        """异步流式调用 API"""
        loop = asyncio.get_event_loop()
        
        # 在executor中运行同步流式API
        def process_stream():
            stream = self._client.send_message_stream(message)
            tool_calls_accumulated = []
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                # 处理内容增量
                if delta.content:
                    yield {"content_delta": delta.content}
                
                # 处理工具调用
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        # 累积工具调用数据
                        if tc.index >= len(tool_calls_accumulated):
                            tool_calls_accumulated.append({
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            })
                        
                        if tc.function:
                            if tc.function.name:
                                tool_calls_accumulated[tc.index]["function"]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_accumulated[tc.index]["function"]["arguments"] += tc.function.arguments
            
            # 返回完整的工具调用
            if tool_calls_accumulated:
                yield {"tool_calls": tool_calls_accumulated}
        
        # 使用run_in_executor处理生成器
        for result in await loop.run_in_executor(None, lambda: list(process_stream())):
            yield result

    def clear_history(self) -> None:
        """清空消息历史"""
        self._messages.clear()

    def get_history(self) -> list[dict]:
        """获取消息历史"""
        return self._messages.copy()

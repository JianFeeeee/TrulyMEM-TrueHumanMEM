"""聊天服务"""

import asyncio
import json
from datetime import datetime
from typing import AsyncIterator, TYPE_CHECKING, List, Dict, Any
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
        self._messages: List[Dict[str, Any]] = []

    async def send_message(self, user_input: str) -> AsyncIterator[dict]:
        """发送消息并流式返回事件"""
        # 1. 发送用户消息事件
        yield {
            "type": "user_message",
            "content": user_input
        }

        try:
            # 2. 第一次API调用
            accumulated_content = ""
            tool_calls_data = []
            
            # 流式处理响应
            async for chunk in self._call_api_stream_async(user_input):
                if chunk.get("content_delta"):
                    accumulated_content += chunk["content_delta"]
                    yield {
                        "type": "content_delta",
                        "content": accumulated_content
                    }
                
                if chunk.get("tool_calls"):
                    tool_calls_data = chunk["tool_calls"]
            
            # 3. 如果有工具调用，执行并继续调用API
            tool_calls = None
            tool_results = None

            if tool_calls_data:
                tool_calls = []
                tool_results = []

                # 执行所有工具
                for tool_call_data in tool_calls_data:
                    tool_call = ToolCall(
                        id=tool_call_data["id"],
                        name=tool_call_data["function"]["name"],
                        arguments=tool_call_data["function"]["arguments"]
                    )
                    tool_calls.append(tool_call)

                    yield {
                        "type": "tool_call",
                        "tool_call": tool_call
                    }

                    result = await self._tool_service.execute(tool_call)
                    tool_results.append(result)

                    log_entry = ToolService._create_log_entry(tool_call, result)
                    yield {
                        "type": "tool_result",
                        "tool_result": result,
                        "log_entry": log_entry
                    }

                # 构建工具结果消息
                tool_messages = []
                for tc, tr in zip(tool_calls, tool_results):
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tr.content
                    })

                # 构建assistant消息（包含tool_calls）
                assistant_message = {
                    "role": "assistant",
                    "content": accumulated_content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": tc.arguments
                            }
                        } for tc in tool_calls
                    ]
                }

                # 第二次API调用，传入工具结果
                final_content = ""
                async for chunk in self._call_api_stream_with_tools(
                    user_input, 
                    assistant_message, 
                    tool_messages
                ):
                    if chunk.get("content_delta"):
                        final_content += chunk["content_delta"]
                        yield {
                            "type": "content_delta",
                            "content": final_content
                        }
                
                accumulated_content = final_content

            # 4. 返回最终回复
            yield {
                "type": "assistant_message",
                "content": accumulated_content,
                "tool_calls": tool_calls,
                "tool_results": tool_results
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }

    async def _call_api_stream_async(self, message: str) -> AsyncIterator[dict]:
        """异步流式调用 API"""
        loop = asyncio.get_event_loop()
        
        def process_stream():
            stream = self._client.send_message_stream(message)
            tool_calls_accumulated = []
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                if delta.content:
                    yield {"content_delta": delta.content}
                
                if delta.tool_calls:
                    for tc in delta.tool_calls:
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
            
            if tool_calls_accumulated:
                yield {"tool_calls": tool_calls_accumulated}
        
        for result in await loop.run_in_executor(None, lambda: list(process_stream())):
            yield result

    async def _call_api_stream_with_tools(
        self, 
        user_input: str,
        assistant_message: dict,
        tool_messages: list
    ) -> AsyncIterator[dict]:
        """带工具结果的流式调用"""
        loop = asyncio.get_event_loop()
        
        def process_stream():
            # 构建完整的消息列表
            messages = [
                {"role": "user", "content": user_input},
                assistant_message
            ]
            messages.extend(tool_messages)
            
            # 调用API
            response = self._client.client.chat.completions.create(
                model=self._client.tools[0]["function"]["name"] if self._client.tools else "deepseek-chat",
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {"content_delta": delta.content}
        
        for result in await loop.run_in_executor(None, lambda: list(process_stream())):
            yield result

    def clear_history(self) -> None:
        """清空消息历史"""
        self._messages.clear()

    def get_history(self) -> list[dict]:
        """获取消息历史"""
        return self._messages.copy()

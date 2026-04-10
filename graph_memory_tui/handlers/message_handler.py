"""消息处理器"""

from datetime import datetime
from typing import TYPE_CHECKING
from ..models.message import Message, ToolCall, ToolResult

if TYPE_CHECKING:
    from ..services.chat_service import ChatService
    from ..widgets.message_history import MessageHistory
    from ..widgets.operation_log import OperationLog


class MessageHandler:
    """消息处理器"""

    def __init__(
        self,
        chat_service: "ChatService",
        message_history: "MessageHistory",
        operation_log: "OperationLog"
    ):
        self._chat_service = chat_service
        self._message_history = message_history
        self._operation_log = operation_log

    async def handle_user_message(self, content: str) -> None:
        """处理用户消息"""
        # 创建用户消息
        user_message = Message(
            role="user",
            content=content,
            timestamp=datetime.now()
        )

        # 添加到历史
        self._message_history.add_message(user_message)

        # 发送到聊天服务
        await self._process_response(content)

    async def _process_response(self, user_input: str) -> None:
        """处理响应"""
        async for event in self._chat_service.send_message(user_input):
            if event["type"] == "user_message":
                # 用户消息已处理
                pass

            elif event["type"] == "assistant_message":
                # 模型消息
                message = Message(
                    role="assistant",
                    content=event["content"],
                    timestamp=datetime.now(),
                    tool_calls=event.get("tool_calls"),
                    tool_results=event.get("tool_results")
                )
                self._message_history.add_message(message)

            elif event["type"] == "tool_call":
                # 工具调用开始
                pass

            elif event["type"] == "tool_result":
                # 工具执行结果
                log_entry = event["log_entry"]
                self._operation_log.add_log(log_entry)

            elif event["type"] == "error":
                # 错误处理
                error_message = Message(
                    role="assistant",
                    content=f"错误: {event['error']}",
                    timestamp=datetime.now()
                )
                self._message_history.add_message(error_message)

"""消息组件"""

from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.message import Message
from ..models.message import Message as MessageModel


class MessageWidget(Container):
    """单条消息组件"""

    def __init__(self, message: MessageModel, **kwargs):
        super().__init__(**kwargs)
        self._message = message
        self._show_tool_details = False

    def compose(self):
        """构建消息组件"""
        # 消息头
        role_emoji = "🟠" if self._message.role == "user" else "🔵"
        timestamp_str = self._message.timestamp.strftime("%H:%M:%S")
        yield Static(
            f"{role_emoji} [{self._message.role}] {timestamp_str}",
            classes="message-header"
        )

        # 消息内容
        yield Static(self._message.content, classes="message-content")

        # 工具调用指示器
        if self._message.tool_calls:
            tool_count = len(self._message.tool_calls)
            yield Static(
                f"[工具:{tool_count}次] (F3展开)",
                classes="tool-indicator"
            )

            # 工具调用详情（默认折叠）
            if self._show_tool_details:
                with Vertical(classes="tool-details"):
                    for i, tool_call in enumerate(self._message.tool_calls, 1):
                        yield Static(
                            f"工具 {i}: {tool_call.name}",
                            classes="tool-name"
                        )
                        yield Static(
                            f"参数: {tool_call.arguments}",
                            classes="tool-args"
                        )

                        # 显示执行结果
                        if self._message.tool_results:
                            for result in self._message.tool_results:
                                if result.tool_call_id == tool_call.id:
                                    yield Static(
                                        f"结果: {result.result[:200]}...",
                                        classes="tool-result"
                                    )

    def toggle_tool_details(self) -> None:
        """切换工具详情显示状态"""
        if self._message.tool_calls:
            self._show_tool_details = not self._show_tool_details
            self.refresh()

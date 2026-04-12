"""消息历史组件"""

from textual.containers import ScrollableContainer
from textual.message import Message
from .message_widget import MessageWidget
from ..models.message import Message as MessageModel


class MessageHistory(ScrollableContainer):
    """消息历史区域"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._messages: list[MessageModel] = []

    def compose(self):
        """构建消息历史"""
        for message in self._messages:
            yield MessageWidget(message)

    def add_message(self, message: MessageModel) -> None:
        """添加新消息"""
        self._messages.append(message)
        # 添加新组件
        message_widget = MessageWidget(message)
        self.mount(message_widget)
        # 滚动到最新消息
        self.scroll_to_widget(message_widget, animate=False)

    def update_latest_message(self, content: str) -> None:
        """更新最新消息的内容"""
        if self.children:
            latest_widget = self.children[-1]
            if isinstance(latest_widget, MessageWidget):
                latest_widget.update_content(content)
                # 确保滚动到最新消息
                self.scroll_to_widget(latest_widget, animate=False)

    def clear_messages(self) -> None:
        """清空消息历史"""
        self._messages.clear()
        # 移除所有子组件
        for child in self.children:
            child.remove()

    def get_latest_message(self) -> MessageModel | None:
        """获取最新消息"""
        if self._messages:
            return self._messages[-1]
        return None

    def toggle_latest_tool_details(self) -> None:
        """切换最新消息的工具详情"""
        if self.children:
            latest_widget = self.children[-1]
            if isinstance(latest_widget, MessageWidget):
                latest_widget.toggle_tool_details()

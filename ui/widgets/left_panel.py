"""左侧面板"""

from textual.containers import Container
from textual.app import ComposeResult
from .message_history import MessageHistory
from .input_box import InputBox


class LeftPanel(Container):
    """左侧主面板"""

    def compose(self) -> ComposeResult:
        """构建左侧面板"""
        yield MessageHistory()
        yield InputBox()

    def get_message_history(self) -> MessageHistory:
        """获取消息历史组件"""
        return self.query_one(MessageHistory)

    def get_input_box(self) -> InputBox:
        """获取输入框组件"""
        return self.query_one(InputBox)

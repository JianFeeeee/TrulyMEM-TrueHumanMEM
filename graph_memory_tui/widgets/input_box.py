"""输入框组件"""

from textual.containers import Container
from textual.widgets import Input
from textual.message import Message


class InputBox(Container):
    """输入框组件"""

    class SendMessage(Message):
        """发送消息事件"""
        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: list[str] = []
        self._history_index: int = -1

    def compose(self):
        """构建输入框"""
        yield Input(
            placeholder="输入消息... (Enter发送)",
            id="input-textarea"
        )

    def on_mount(self) -> None:
        """组件挂载时"""
        # 设置焦点
        input_widget = self.query_one(Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交事件"""
        content = event.value.strip()
        if content:
            # 保存到历史
            self._history.append(content)
            self._history_index = len(self._history)
            # 发送消息
            self.post_message(self.SendMessage(content))
            # 清空输入框
            event.input.value = ""

    def focus(self) -> None:
        """聚焦输入框"""
        input_widget = self.query_one(Input)
        input_widget.focus()

"""输入框组件"""

from textual.containers import Container, Horizontal
from textual.widgets import TextArea, Button
from textual.message import Message


class InputBox(Container):
    """输入框组件"""

    class SendMessage(Message):
        """发送消息事件"""
        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()
    
    class ClearHistory(Message):
        """清空聊天记录事件"""
        def __init__(self) -> None:
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: list[str] = []
        self._history_index: int = -1

    def compose(self):
        """构建输入框"""
        yield TextArea(
            placeholder="输入消息... (Enter换行)",
            id="input-textarea"
        )
        with Horizontal(classes="input-buttons"):
            yield Button("清空", id="clear-button", variant="default")
            yield Button("发送", id="send-button", variant="primary")

    def on_mount(self) -> None:
        """组件挂载时"""
        # 设置焦点
        textarea = self.query_one(TextArea)
        textarea.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "send-button":
            self._send_message()
        elif event.button.id == "clear-button":
            self.post_message(self.ClearHistory())

    def on_key(self, event) -> None:
        """处理按键事件"""
        if event.key == "enter" and event.ctrl:
            self._send_message()
            event.stop()

    def _send_message(self) -> None:
        """发送消息"""
        textarea = self.query_one(TextArea)
        content = textarea.text.strip()
        if content:
            # 保存到历史
            self._history.append(content)
            self._history_index = len(self._history)
            # 发送消息
            self.post_message(self.SendMessage(content))
            # 清空输入框
            textarea.clear()

    def focus(self) -> None:
        """聚焦输入框"""
        textarea = self.query_one(TextArea)
        textarea.focus()

"""Cypher查询框组件"""

from textual.containers import Container, Horizontal
from textual.widgets import Static, TextArea, Button
from textual.app import ComposeResult
from textual.message import Message


class CypherQueryBox(Container):
    """快捷Cypher查询输入框"""

    class ExecuteQuery(Message):
        """执行查询事件"""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    def compose(self) -> ComposeResult:
        """构建查询框"""
        yield Static("F4:执行Cypher查询", classes="query-title")
        yield TextArea(
            placeholder="输入Cypher查询语句...",
            id="cypher-textarea"
        )
        with Horizontal(classes="query-buttons"):
            yield Button("执行", id="execute-button", variant="primary")
            yield Button("清空", id="clear-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "execute-button":
            self._execute_query()
        elif event.button.id == "clear-button":
            self._clear_query()

    def on_key(self, event) -> None:
        """处理按键事件"""
        if event.key == "enter" and event.ctrl:
            event.stop()
            self._execute_query()

    def _execute_query(self) -> None:
        """执行查询"""
        textarea = self.query_one("#cypher-textarea", TextArea)
        query = textarea.text.strip()
        if query:
            self.post_message(self.ExecuteQuery(query))

    def _clear_query(self) -> None:
        """清空查询"""
        textarea = self.query_one("#cypher-textarea", TextArea)
        textarea.clear()

    def focus(self) -> None:
        """聚焦查询框"""
        textarea = self.query_one("#cypher-textarea", TextArea)
        textarea.focus()

"""消息组件"""

from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.message import Message
from textual.css.query import NoMatches
from ..models.message import Message as MessageModel


class MessageWidget(Container):
    """单条消息组件"""

    def __init__(self, message: MessageModel, **kwargs):
        super().__init__(**kwargs)
        self._message = message
        self._show_tool_details = False
        self._content_widget = None  # 保存内容组件的引用
        self._tool_details_container = None  # 保存工具详情容器引用

    def compose(self):
        """构建消息组件"""
        # 消息头
        role_emoji = "🟠" if self._message.role == "user" else "🔵"
        timestamp_str = self._message.timestamp.strftime("%H:%M:%S")
        yield Static(
            f"{role_emoji}  {timestamp_str}",
            classes="message-header"
        )

        # 消息内容 - 保存引用以便后续更新
        self._content_widget = Static(
            self._message.content,
            classes="message-content"
        )
        yield self._content_widget

        # 工具调用指示器
        if self._message.tool_calls:
            tool_count = len(self._message.tool_calls)
            toggle_hint = "(F3折叠)" if self._show_tool_details else "(F3展开)"
            yield Static(
                f"[工具:{tool_count}次] {toggle_hint}",
                classes="tool-indicator"
            )

            # 工具调用详情容器 - 始终创建，但根据状态显示/隐藏
            self._tool_details_container = Vertical(classes="tool-details")
            with self._tool_details_container:
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
                                # 显示完整结果，不截断
                                result_text = result.result
                                # 如果结果太长，只显示前1000字符，但提供完整信息
                                if len(result_text) > 1000:
                                    result_text = result_text[:1000] + f"\n... (共{len(result.result)}字符，按F3查看完整内容)"
                                yield Static(
                                    f"结果: {result_text}",
                                    classes="tool-result"
                                )
            
            # 根据状态设置初始显示/隐藏
            if not self._show_tool_details:
                self._tool_details_container.styles.display = "none"

    def update_content(self, new_content: str) -> None:
        """更新消息内容"""
        self._message.content = new_content
        if self._content_widget:
            self._content_widget.update(new_content)

    def toggle_tool_details(self) -> None:
        """切换工具详情显示状态"""
        if self._message.tool_calls and self._tool_details_container:
            self._show_tool_details = not self._show_tool_details
            
            # 切换显示/隐藏
            if self._show_tool_details:
                self._tool_details_container.styles.display = "block"
            else:
                self._tool_details_container.styles.display = "none"
            
            # 更新指示器文字
            self._update_indicator()
            
            # 刷新布局
            self.refresh(layout=True)

    def _update_indicator(self) -> None:
        """更新工具调用指示器文字"""
        try:
            indicator = self.query_one(".tool-indicator", Static)
            tool_count = len(self._message.tool_calls)
            toggle_hint = "(F3折叠)" if self._show_tool_details else "(F3展开)"
            indicator.update(f"[工具:{tool_count}次] {toggle_hint}")
        except NoMatches:
            pass

"""操作日志组件"""

from datetime import datetime
from textual.containers import ScrollableContainer
from textual.widgets import Static
from ..models.log_entry import LogEntry


class OperationLog(ScrollableContainer):
    """图操作日志区域"""

    def __init__(self, max_entries: int = 100, **kwargs):
        super().__init__(**kwargs)
        self._logs: list[LogEntry] = []
        self._max_entries = max_entries

    def compose(self):
        """构建日志区域"""
        if not self._logs:
            yield Static("暂无操作日志", classes="log-empty")

    def add_log(self, entry: LogEntry) -> None:
        """添加日志（插入到顶部）"""
        # 限制日志数量
        if len(self._logs) >= self._max_entries:
            self._logs.pop()
            # 移除最旧的组件
            if self.children:
                self.children[-1].remove()

        # 插入到列表开头
        self._logs.insert(0, entry)

        # 创建日志显示组件
        log_widget = self._create_log_widget(entry)

        # 挂载到顶部
        self.mount(log_widget, before=0 if self.children else None)

        # 滚动到顶部
        self.scroll_to(0, animate=False)

    def _create_log_widget(self, entry: LogEntry) -> Static:
        """创建日志显示组件"""
        timestamp_str = entry.timestamp.strftime("%H:%M:%S")
        text = (
            f"[{timestamp_str}] {entry.tool_name}\n"
            f"  参数: {entry.args_summary}\n"
            f"  结果: {entry.result_summary}\n"
            f"  耗时: {entry.duration:.2f}s"
        )
        return Static(text, classes="log-entry")

    def clear_logs(self) -> None:
        """清空日志"""
        self._logs.clear()
        for child in self.children:
            child.remove()
        # 显示空状态
        self.mount(Static("暂无操作日志", classes="log-empty"))

    def get_latest_log(self) -> LogEntry | None:
        """获取最新日志"""
        if self._logs:
            return self._logs[0]
        return None

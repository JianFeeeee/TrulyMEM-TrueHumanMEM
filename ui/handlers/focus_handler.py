"""焦点管理器"""

from textual.app import App


class FocusHandler:
    """焦点管理器"""

    # 焦点循环顺序
    FOCUS_RING = [
        "input-textarea",      # 左侧输入框
        "api-key-input",       # 右侧配置区 API Key
        "model-input",         # 右侧配置区 Model
        "base-url-input",      # 右侧配置区 Base URL
        "cypher-textarea",     # 右侧 Cypher 查询框
    ]

    # 焦点名称映射
    FOCUS_NAMES = {
        "input-textarea": "Input",
        "api-key-input": "Config-API",
        "model-input": "Config-Model",
        "base-url-input": "Config-URL",
        "cypher-textarea": "Query",
    }

    def __init__(self):
        self._current_index = 0

    def next_focus(self, app: App) -> None:
        """切换到下一个焦点"""
        self._current_index = (self._current_index + 1) % len(self.FOCUS_RING)
        widget_id = self.FOCUS_RING[self._current_index]
        self._focus_widget(app, widget_id)

    def prev_focus(self, app: App) -> None:
        """切换到上一个焦点"""
        self._current_index = (self._current_index - 1) % len(self.FOCUS_RING)
        widget_id = self.FOCUS_RING[self._current_index]
        self._focus_widget(app, widget_id)

    def focus_input(self, app: App) -> None:
        """聚焦到输入框"""
        self._current_index = 0
        self._focus_widget(app, self.FOCUS_RING[0])

    def focus_query(self, app: App) -> None:
        """聚焦到查询框"""
        self._current_index = len(self.FOCUS_RING) - 1
        self._focus_widget(app, self.FOCUS_RING[-1])

    def get_current_focus_name(self) -> str:
        """获取当前焦点名称"""
        widget_id = self.FOCUS_RING[self._current_index]
        return self.FOCUS_NAMES.get(widget_id, "Unknown")

    def _focus_widget(self, app: App, widget_id: str) -> None:
        """聚焦到指定组件"""
        try:
            widget = app.query_one(f"#{widget_id}")
            widget.focus()
        except Exception:
            # 如果找不到组件，回退到输入框
            self.focus_input(app)

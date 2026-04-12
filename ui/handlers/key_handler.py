"""快捷键处理器"""

from textual.app import App
from textual.message import Message
from .focus_handler import FocusHandler


class KeyHandler:
    """快捷键处理器"""

    class ShowHelp(Message):
        """显示帮助事件"""
        pass

    class ToggleSidebar(Message):
        """切换侧边栏事件"""
        pass

    class ToggleToolDetails(Message):
        """切换工具详情事件"""
        pass

    class FocusQuery(Message):
        """聚焦查询框事件"""
        pass

    class ClearHistory(Message):
        """清屏事件"""
        pass

    class QuitApp(Message):
        """退出应用事件"""
        pass

    def __init__(self, focus_handler: FocusHandler):
        self._focus_handler = focus_handler

    def handle_f1(self, app: App) -> None:
        """处理 F1 键 - 显示帮助"""
        app.post_message(self.ShowHelp())

    def handle_f2(self, app: App) -> None:
        """处理 F2 键 - 切换侧边栏"""
        app.post_message(self.ToggleSidebar())

    def handle_f3(self, app: App) -> None:
        """处理 F3 键 - 切换工具详情"""
        app.post_message(self.ToggleToolDetails())

    def handle_f4(self, app: App) -> None:
        """处理 F4 键 - 聚焦查询框"""
        app.post_message(self.FocusQuery())

    def handle_f5(self, app: App) -> None:
        """处理 F5 键 - 清屏"""
        app.post_message(self.ClearHistory())

    def handle_f6(self, app: App) -> None:
        """处理 F6 键 - 退出"""
        app.post_message(self.QuitApp())

    def handle_tab(self, app: App) -> None:
        """处理 Tab 键 - 焦点循环"""
        self._focus_handler.next_focus(app)

    def handle_shift_tab(self, app: App) -> None:
        """处理 Shift+Tab 键 - 反向焦点循环"""
        self._focus_handler.prev_focus(app)

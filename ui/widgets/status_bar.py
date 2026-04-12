"""状态栏组件"""

from textual.widgets import Static
from textual.message import Message


class StatusBar(Static):
    """底部状态栏"""

    class FocusChanged(Message):
        """焦点变更事件"""
        def __init__(self, focus_name: str) -> None:
            self.focus_name = focus_name
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._shortcuts = "F1:帮助 F2:侧边栏 F3:工具详情 F4:查询 F5:清屏 F6:退出"
        self._license_info = "本项目由jianf设计，以GPLv3形式开源"

    def on_mount(self) -> None:
        """组件挂载时"""
        self._update_display()

    def _update_display(self) -> None:
        """更新显示"""
        self.update(f"{self._license_info} | {self._shortcuts}")

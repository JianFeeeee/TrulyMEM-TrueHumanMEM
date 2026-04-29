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
        self._shortcuts = "F1:帮助 F2:侧边栏 F3:工具详情 F5:清屏 F6:退出"
        self._license_info = "本项目由jianf设计，以GPLv3形式开源"
        self._api_status = "未配置"
        self._web_status = "未启动"
        self._processing = False

    def on_mount(self) -> None:
        """组件挂载时"""
        self._update_display()

    def _update_display(self) -> None:
        """更新显示"""
        status_icon = "●" if self._api_status == "已配置" else "○"
        web_icon = "●" if self._web_status != "未启动" else "○"
        processing_indicator = " [处理中...]" if self._processing else ""
        self.update(f"{status_icon} API: {self._api_status} | {web_icon} Web: {self._web_status}{processing_indicator} | {self._license_info} | {self._shortcuts}")

    def set_api_status(self, configured: bool) -> None:
        """设置API状态"""
        self._api_status = "已配置" if configured else "未配置"
        self._update_display()

    def set_processing(self, processing: bool) -> None:
        """设置处理状态"""
        self._processing = processing
        self._update_display()

    def set_web_status(self, running: bool, port: int = 0) -> None:
        """设置Web服务状态"""
        if running:
            self._web_status = f"运行中(:{port})"
        else:
            self._web_status = "未启动"
        self._update_display()

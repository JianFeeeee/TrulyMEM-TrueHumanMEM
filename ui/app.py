import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding

from core import BackendServer, BackendClient
from .models.message import Message


class GraphMemoryApp(App):
    CSS_PATH = [
        Path(__file__).parent / "styles" / "app.css",
        Path(__file__).parent / "styles" / "messages.css",
        Path(__file__).parent / "styles" / "components.css",
    ]

    BINDINGS = [
        Binding("f1", "show_help", "帮助"),
        Binding("f2", "toggle_sidebar", "侧边栏"),
        Binding("f3", "toggle_tool_details", "工具详情"),
        Binding("f5", "clear_history", "清屏"),
        Binding("f6", "quit", "退出"),
    ]

    def __init__(self, backend_server: BackendServer = None, **kwargs):
        super().__init__(**kwargs)
        self._backend_server = backend_server
        self._backend_client = BackendClient(backend_server) if backend_server else None

    def compose(self) -> ComposeResult:
        from .widgets.left_panel import LeftPanel
        from .widgets.right_panel import RightPanel
        from .widgets.status_bar import StatusBar
        yield LeftPanel()
        yield RightPanel()
        yield StatusBar()

    def on_mount(self) -> None:
        if not self._backend_server:
            from .widgets.message_history import MessageHistory
            history = self.query_one(MessageHistory)
            error = Message(role="assistant", content="后端未初始化")
            history.add_message(error)
            return
        
        status = self._backend_client.get_status()
        api_configured = status.get("config", {}).get("api_key", "") != ""
        
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        welcome = Message(
            role="assistant",
            content=f"系统就绪\nAPI Key: {'已配置' if api_configured else '未配置'}\n\n输入消息开始对话"
        )
        history.add_message(welcome)

    def on_unmount(self) -> None:
        if self._backend_client:
            self._backend_client.shutdown()

    def action_show_help(self) -> None:
        self.notify("F1-帮助 F2-侧边栏 F3-工具详情 F5-清屏 F6-退出", title="快捷键", timeout=10)

    def action_toggle_sidebar(self) -> None:
        from .widgets.right_panel import RightPanel
        sidebar = self.query_one(RightPanel)
        sidebar.toggle()

    def action_toggle_tool_details(self) -> None:
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        history.toggle_latest_tool_details()

    def action_clear_history(self) -> None:
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        history.clear_messages()

    def on_input_box_send_message(self, event) -> None:
        if not self._backend_client:
            return
        
        user_input = event.content
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        
        history.add_message(Message(role="user", content=user_input))
        history.add_message(Message(role="assistant", content="处理中..."))
        
        asyncio.create_task(self._process(user_input))

    async def _process(self, user_input: str) -> None:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._backend_client.send_message(user_input)
            )
            
            from .widgets.message_history import MessageHistory
            history = self.query_one(MessageHistory)
            history.clear_messages()
            
            history.add_message(Message(role="user", content=user_input))
            
            if result.get("success"):
                content = result.get("content", "(无回复)")
                history.add_message(Message(role="assistant", content=content))
            else:
                error = result.get("error", "未知错误")
                history.add_message(Message(role="assistant", content=f"错误: {error}"))
                
        except Exception as e:
            from .widgets.message_history import MessageHistory
            history = self.query_one(MessageHistory)
            history.add_message(Message(role="assistant", content=f"错误: {str(e)}"))

    def on_config_changed(self, event) -> None:
        if not self._backend_client:
            return
        
        api_key = event.api_key
        base_url = event.base_url
        
        result = self._backend_client.update_config(api_key=api_key, base_url=base_url)
        self.notify("配置已保存" if result.get("success") else "配置失败", title="配置")
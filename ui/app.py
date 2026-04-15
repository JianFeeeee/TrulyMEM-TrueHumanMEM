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

    def __init__(self, backend_server: BackendServer = None, config_file: str = None, **kwargs):
        super().__init__(**kwargs)
        self._backend_server = backend_server
        self._backend_client = BackendClient(backend_server) if backend_server else None
        self._api_configured = False

    def compose(self) -> ComposeResult:
        from .widgets.left_panel import LeftPanel
        from .widgets.right_panel import RightPanel
        from .widgets.status_bar import StatusBar
        from .models.config import AppConfig
        
        initial_config = AppConfig()
        
        if self._backend_client:
            settings_result = self._backend_client.get_settings()
            settings_data = settings_result.get("data", {})
            
            api_config = settings_data.get("api_config", {})
            initial_config.api_key = api_config.get("api_key", "")
            initial_config.base_url = api_config.get("base_url", "https://api.deepseek.com")
            initial_config.model = api_config.get("model", "deepseek-chat")
            
            tool_limits = settings_data.get("tool_limits", {})
            initial_config.persona_query_max = tool_limits.get("persona_query_max", 1)
            initial_config.persona_update_max = tool_limits.get("persona_update_max", 1)
            initial_config.task_query_max = tool_limits.get("task_query_max", 4)
            initial_config.task_update_max = tool_limits.get("task_update_max", 2)
            initial_config.memory_query_max = tool_limits.get("memory_query_max", 20)
            initial_config.memory_update_max = tool_limits.get("memory_update_max", 10)
        
        yield LeftPanel()
        yield RightPanel(config=initial_config)
        yield StatusBar()

    def on_mount(self) -> None:
        from .widgets.status_bar import StatusBar
        from .widgets.message_history import MessageHistory
        status_bar = self.query_one(StatusBar)
        
        if not self._backend_server:
            from .widgets.message_history import MessageHistory
            history = self.query_one(MessageHistory)
            error = Message(role="assistant", content="后端未初始化")
            history.add_message(error)
            status_bar.set_api_status(False)
            return
        
        status = self._backend_client.get_status()
        data = status.get("data", {})
        self._api_configured = data.get("config", {}).get("api_key", "") != ""
        status_bar.set_api_status(self._api_configured)
        
        history = self.query_one(MessageHistory)
        
        if self._api_configured:
            chat_history = self._backend_client.get_history()
            if chat_history:
                for msg in chat_history:
                    message = Message(role=msg["role"], content=msg["content"])
                    history.add_message(message)
        
        welcome = Message(
            role="assistant",
            content=f"系统就绪\nAPI Key: {'已配置' if self._api_configured else '未配置'}\n\n输入消息开始对话"
        )
        history.add_message(welcome)

    def on_unmount(self) -> None:
        if self._backend_client:
            self._backend_client.shutdown()

    def action_show_help(self) -> None:
        from pathlib import Path
        config_path = Path.home() / ".trulymem" / "config.json"
        db_path = Path.home() / ".trulymem" / "graph_memory.db"
        
        help_text = (
            "F1-帮助 F2-侧边栏 F3-工具详情 F5-清屏 F6-退出\n\n"
            f"配置文件: {config_path}\n"
            f"数据库: {db_path}"
        )
        self.notify(help_text, title="快捷键 & 配置路径", timeout=15)

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
            self.notify("后端未初始化", title="错误", severity="error")
            return
        
        if not self._api_configured:
            self.notify("请先配置 API Key (按 F2 打开侧边栏)", title="提示", severity="warning")
            return
        
        user_input = event.content
        from .widgets.message_history import MessageHistory
        from .widgets.status_bar import StatusBar
        
        history = self.query_one(MessageHistory)
        status_bar = self.query_one(StatusBar)
        
        history.add_message(Message(role="user", content=user_input))
        history.add_message(Message(role="assistant", content="⏳ 正在处理..."))
        status_bar.set_processing(True)
        
        asyncio.create_task(self._process(user_input))
    
    def on_input_box_clear_history(self, event) -> None:
        """处理清空聊天记录事件"""
        if not self._backend_client:
            self.notify("后端未初始化", title="错误", severity="error")
            return
        
        self._backend_client.clear_history()
        
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        history.clear_messages()
        
        self.notify("聊天记录已清空，AI记忆保持不变", title="提示", severity="information")
    
    async def _process(self, user_input: str) -> None:
        from .widgets.message_history import MessageHistory
        from .widgets.status_bar import StatusBar
        from .widgets.right_panel import RightPanel
        from .models.log_entry import LogEntry
        from datetime import datetime
        
        history = self.query_one(MessageHistory)
        status_bar = self.query_one(StatusBar)
        
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._backend_client.process_message(user_input)
        )
        
        if result.get("success"):
            # 响应结构: {"success": True, "data": {"content": "...", "tool_calls": [...], ...}, "error": None}
            data = result.get("data", {})
            content = data.get("content", "(无回复)")
            history.update_latest_message(content)
            
            # 处理工具调用信息，更新操作日志
            tool_calls = data.get("tool_calls", [])
            if tool_calls:
                try:
                    right_panel = self.query_one(RightPanel)
                    operation_log = right_panel.get_operation_log()
                    
                    for tool_call in tool_calls:
                        entry = LogEntry(
                            timestamp=datetime.now(),
                            tool_name=tool_call.get("name", "unknown"),
                            arguments=tool_call.get("arguments", {}),
                            result=str(tool_call.get("result", "")),
                            duration=0.0  # 后端没有返回耗时信息
                        )
                        operation_log.add_log(entry)
                except Exception:
                    pass  # 忽略操作日志更新失败
        else:
            error = result.get("error", "未知错误")
            history.update_latest_message(f"❌ 错误: {error}")
        
        status_bar.set_processing(False)

    def on_config_section_config_changed(self, event) -> None:
        if not self._backend_client:
            self.notify("后端未初始化，无法保存配置", title="错误", severity="error")
            return
        
        asyncio.create_task(self._update_settings_async(event.config))
    
    async def _update_settings_async(self, config) -> None:
        from .widgets.status_bar import StatusBar
        from .widgets.config_section import ConfigSection
        
        status_bar = self.query_one(StatusBar)
        
        api_config = {
            "api_key": config.api_key,
            "base_url": config.base_url,
            "model": getattr(config, 'model', 'deepseek-chat')
        }
        
        tool_limits = {
            "persona_query_max": config.persona_query_max,
            "persona_update_max": config.persona_update_max,
            "task_query_max": config.task_query_max,
            "task_update_max": config.task_update_max,
            "memory_query_max": config.memory_query_max,
            "memory_update_max": config.memory_update_max,
        }
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._backend_client.update_settings(
                    api_config=api_config,
                    tool_limits=tool_limits
                )
            )
            
            if result.get("success"):
                self._api_configured = bool(config.api_key)
                status_bar.set_api_status(self._api_configured)
                
                settings_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._backend_client.get_settings()
                )
                settings_data = settings_result.get("data", {})
                
                try:
                    config_section = self.query_one(ConfigSection)
                    api_cfg = settings_data.get("api_config", {})
                    tool_lmts = settings_data.get("tool_limits", {})
                    config_section.set_config(AppConfig(
                        api_key=api_cfg.get("api_key", ""),
                        base_url=api_cfg.get("base_url", "https://api.deepseek.com"),
                        model=api_cfg.get("model", "deepseek-chat"),
                        persona_query_max=tool_lmts.get("persona_query_max", 1),
                        persona_update_max=tool_lmts.get("persona_update_max", 1),
                        task_query_max=tool_lmts.get("task_query_max", 4),
                        task_update_max=tool_lmts.get("task_update_max", 2),
                        memory_query_max=tool_lmts.get("memory_query_max", 20),
                        memory_update_max=tool_lmts.get("memory_update_max", 10),
                    ))
                except Exception:
                    pass
                
                self.notify("✅ 配置已保存并生效", title="配置成功", severity="information")
            else:
                error = result.get("error", "未知错误")
                self.notify(f"❌ 配置失败: {error}", title="配置失败", severity="error")
        except Exception as e:
            self.notify(f"❌ 配置异常: {str(e)}", title="配置失败", severity="error")
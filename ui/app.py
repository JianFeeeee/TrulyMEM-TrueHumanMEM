import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from datetime import datetime

from core import BackendServer, BackendClient
from .models.message import Message, ToolCall, ToolResult
from .models.config import AppConfig
from .models.log_entry import LogEntry
from .services.config_manager import ConfigManager
from core import BackendClient


class GraphMemoryApp(App[None]):
    CSS_PATH = [
        Path(__file__).parent / "styles" / "app.css",
        Path(__file__).parent / "styles" / "messages.css",
        Path(__file__).parent / "styles" / "components.css",
    ]

    BINDINGS = [
        Binding("f1", "show_help", "帮助"),
        Binding("f2", "toggle_sidebar", "侧边栏"),
        Binding("f3", "toggle_tool_details", "工具详情"),
        Binding("f4", "focus_query", "查询"),
        Binding("f5", "clear_history", "清屏"),
        Binding("f6", "quit", "退出"),
    ]

    def __init__(self, config: AppConfig | None = None, backend_server: BackendServer | None = None, **kwargs):
        super().__init__(**kwargs)
        self._config_manager = ConfigManager()
        
        if config:
            self._config = config
        elif self._config_manager.exists():
            self._config = self._config_manager.load()
        else:
            self._config = AppConfig.from_env()
        
        if backend_server:
            self._backend_server = backend_server
            self._backend_client = BackendClient(backend_server)
        else:
            self._backend_server: BackendServer | None = None
            self._backend_client: BackendClient | None = None

    def compose(self) -> ComposeResult:
        from .widgets.left_panel import LeftPanel
        from .widgets.right_panel import RightPanel
        from .widgets.status_bar import StatusBar
        
        yield LeftPanel()
        yield RightPanel(self._config, use_embedded_db=True)
        yield StatusBar()

    def on_mount(self) -> None:
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)

        try:
            self._backend_server = BackendServer(
                db_path="graph_memory.db",
                use_embedded_db=True
            )
            self._backend_server.start(
                api_key=self._config.api_key,
                base_url=self._config.base_url
            )
            
            self._backend_client = BackendClient(self._backend_server)

            welcome = Message(
                role="assistant",
                content="系统初始化成功！\n\n"
                       f"数据库: 内嵌SQLite (graph_memory.db)\n"
                       f"API Key: {'已配置' if self._config.api_key else '未配置'}\n\n"
                       "现在可以开始对话了！",
            )
            history.add_message(welcome)

        except Exception as e:
            error = Message(
                role="assistant",
                content=f"初始化失败: {str(e)}\n\n"
                       "请检查：\n"
                       "1. API Key 是否配置\n"
                       "2. 网络连接是否正常\n\n"
                       "按F2打开侧边栏配置API Key",
            )
            history.add_message(error)

    def on_unmount(self) -> None:
        if self._backend_server:
            self._backend_server.shutdown()

    def action_show_help(self) -> None:
        help_text = """
快捷键：
F1 - 帮助
F2 - 切换侧边栏
F3 - 工具详情
F4 - 查询框
F5 - 清屏
F6 - 退出

输入消��后按 Enter 发送
        """
        self.notify(help_text, title="帮助", timeout=10)

    def action_toggle_sidebar(self) -> None:
        from .widgets.right_panel import RightPanel
        sidebar = self.query_one(RightPanel)
        sidebar.toggle()
        sidebar.update_title()

    def action_toggle_tool_details(self) -> None:
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        history.toggle_latest_tool_details()

    def action_focus_query(self) -> None:
        from .widgets.right_panel import RightPanel
        sidebar = self.query_one(RightPanel)
        
        if not sidebar.has_cypher_query_box():
            self.notify("查询框仅在 Neo4j 模式下可用", title="提示", timeout=3)
            return
        
        if sidebar.is_collapsed():
            sidebar.toggle()
            sidebar.update_title()
        
        query_box = sidebar.get_cypher_query_box()
        if query_box:
            query_box.focus()

    def action_clear_history(self) -> None:
        from .widgets.message_history import MessageHistory
        history = self.query_one(MessageHistory)
        history.clear_messages()

    def on_input_box_send_message(self, event) -> None:
        from .widgets.input_box import InputBox
        from .widgets.message_history import MessageHistory
        from .widgets.right_panel import RightPanel
        
        try:
            history = self.query_one(MessageHistory)
            user_message = Message(role="user", content=event.content)
            history.add_message(user_message)

            if not self._config.api_key:
                response_msg = Message(
                    role="assistant",
                    content="请先配置API Key。\n\n按F2打开侧边栏，输入API Key后按Enter保存。",
                )
                history.add_message(response_msg)
                return

            processing_msg = Message(role="assistant", content="正在处理...")
            history.add_message(processing_msg)

            asyncio.create_task(self._process_message_async(event.content))

        except Exception as e:
            error_msg = Message(role="assistant", content=f"错误: {str(e)}")
            history.add_message(error_msg)

    async def _process_message_async(self, user_input: str) -> None:
        from .widgets.message_history import MessageHistory
        from .widgets.right_panel import RightPanel
        
        history = self.query_one(MessageHistory)
        log = self.query_one(RightPanel).get_operation_log()

        try:
            if not self._backend_client:
                raise Exception("后端未初始化")

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._backend_client.process_message(user_input)
            )

            content = result.get("content", "(无回复)")
            tool_calls_data = result.get("tool_calls", [])
            rejected_tools = result.get("rejected_tools", [])

            tool_calls = []
            tool_results = []
            
            for tc in tool_calls_data:
                tc_obj = ToolCall(
                    id=tc.get("id", ""),
                    name=tc.get("name", ""),
                    arguments=tc.get("arguments", {})
                )
                tool_calls.append(tc_obj)
                
                tr = ToolResult(
                    tool_call_id=tc_obj.id,
                    name=tc_obj.name,
                    arguments=tc_obj.arguments,
                    result=tc.get("result", ""),
                    success=not tc.get("result", "").startswith("工具执行���误")
                )
                tool_results.append(tr)
                
                log_entry = LogEntry(
                    tool_name=tc_obj.name,
                    arguments=tc_obj.arguments,
                    result=tc.get("result", ""),
                )
                log.add_log(log_entry)

            assistant_message = Message(
                role="assistant",
                content=content,
                tool_calls=tool_calls if tool_calls else None,
                tool_results=tool_results if tool_results else None
            )

            history.add_message(assistant_message)
            self.refresh()

        except Exception as e:
            error_msg = str(e)
            
            if "Connection error" in error_msg or "connection" in error_msg.lower():
                help_text = """
网络连接错误！可能的原因：
1. API Key 未配置或无效
2. 网络无法访问 API 服务器
3. API 服务器暂时不可用

解决方法：
按 F2 展开侧边栏，检查并配置 API Key
检查网络连接
"""
            elif "API Key" in error_msg:
                help_text = """
API Key 未配置！

请按以下步骤配置：
1. 按 F2 展开右侧边栏
2. 点击"配置"展开配置区
3. 在 API Key 输入框输入你的密钥
4. 按 Enter 键保存配置

获取 API Key: https://platform.deepseek.com/
"""
            else:
                help_text = f"\n详细错误: {error_msg}"
            
            error_message = Message(role="assistant", content=f"错误: {error_msg}\n{help_text}")
            history.add_message(error_message)

    def on_config_section_config_changed(self, event) -> None:
        from .widgets.right_panel import RightPanel
        
        self._config = event.config
        self._config_manager.save(self._config)
        
        try:
            right_panel = self.query_one(RightPanel)
            right_panel._config = self._config
        except Exception:
            pass
        
        if self._backend_client:
            self._backend_client.update_config(
                api_key=self._config.api_key,
                base_url=self._config.base_url
            )
            self.notify("配置已保存并应用", title="配置")
        else:
            self.notify("配置已保存，但后端未初始化", title="警告")
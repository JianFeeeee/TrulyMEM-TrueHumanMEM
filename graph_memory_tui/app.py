"""主应用类 - 参考demo实现"""

import asyncio
import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static
from textual.containers import Container
from datetime import datetime

from .widgets.left_panel import LeftPanel
from .widgets.right_panel import RightPanel
from .widgets.status_bar import StatusBar
from .widgets.input_box import InputBox
from .widgets.message_history import MessageHistory
from .models.message import Message, ToolCall, ToolResult
from .models.config import AppConfig
from .models.log_entry import LogEntry
from .services.config_manager import ConfigManager
from .core.imports import (
    Neo4jGraph,
    GraphMemoryClient,
    execute_tool,
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    MODEL_NAME,
    USE_EMBEDDED_DB,
)
from .core.tools.tool_limiter import ToolLimiter


class GraphMemoryApp(App[None]):
    """Textual TUI 主应用"""

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

    def __init__(self, config: AppConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        # 配置管理器
        self._config_manager = ConfigManager()
        # 优先使用传入的配置，其次加载持久化配置，最后使用环境变量
        if config:
            self._config = config
        elif self._config_manager.exists():
            self._config = self._config_manager.load()
        else:
            self._config = AppConfig.from_env()
        
        # 核心组件
        self._graph: Neo4jGraph | None = None
        self._client: GraphMemoryClient | None = None
        
        # 工具调用限制器
        self._tool_limiter = ToolLimiter()

    def compose(self) -> ComposeResult:
        """构建组件树"""
        yield LeftPanel()
        yield RightPanel(self._config, use_embedded_db=USE_EMBEDDED_DB)
        yield StatusBar()

    def on_mount(self) -> None:
        """应用启动初始化"""
        history = self.query_one(MessageHistory)

        try:
            # 初始化内嵌图数据库
            self._graph = Neo4jGraph(db_path="graph_memory.db")

            # 初始化 API 客户端
            self._init_client()

            # 显示连接成功消息
            welcome = Message(
                role="assistant",
                content="✅ 系统初始化成功！\n\n"
                       f"• 数据库: 内嵌SQLite (graph_memory.db)\n"
                       f"• API Key: {'已配置' if self._config.api_key else '未配置'}\n\n"
                       "现在可以开始对话了！",
                timestamp=datetime.now()
            )
            history.add_message(welcome)

        except Exception as e:
            # 显示错误消息
            error = Message(
                role="assistant",
                content=f"❌ 初始化失败: {str(e)}\n\n"
                       "请检查：\n"
                       "1. Neo4j 数据库是否启动 (运行: docker start neo4j)\n"
                       "2. API Key 是否配置\n"
                       "3. 网络连接是否正常\n\n"
                       "启动Neo4j: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/graphmemory123 neo4j:latest",
                timestamp=datetime.now()
            )
            history.add_message(error)

    def _init_client(self) -> None:
        """初始化API客户端"""
        if self._config.api_key and self._graph:
            self._client = GraphMemoryClient(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
                graph=self._graph
            )

    def on_unmount(self) -> None:
        """应用退出清理"""
        if self._graph:
            self._graph.close()

    # 快捷键动作
    def action_show_help(self) -> None:
        """显示帮助"""
        help_text = """
快捷键：
F1 - 帮助
F2 - 切换侧边栏
F3 - 工具详情
F4 - 查询框（仅 Neo4j 模式）
F5 - 清屏
F6 - 退出

输入消息后按 Enter 发送
        """
        self.notify(help_text, title="帮助", timeout=10)

    def action_toggle_sidebar(self) -> None:
        """切换侧边栏"""
        sidebar = self.query_one(RightPanel)
        sidebar.toggle()
        sidebar.update_title()

    def action_toggle_tool_details(self) -> None:
        """切换工具详情"""
        history = self.query_one(MessageHistory)
        history.toggle_latest_tool_details()

    def action_focus_query(self) -> None:
        """聚焦查询框（仅 Neo4j 模式可用）"""
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
        """清屏"""
        history = self.query_one(MessageHistory)
        history.clear_messages()

    # 事件处理
    def on_input_box_send_message(self, event: InputBox.SendMessage) -> None:
        """处理发送消息事件"""
        try:
            # 添加用户消息
            history = self.query_one(MessageHistory)
            user_message = Message(
                role="user",
                content=event.content,
                timestamp=datetime.now()
            )
            history.add_message(user_message)

            # 简单响应（避免崩溃）
            if not self._config.api_key:
                response_msg = Message(
                    role="assistant",
                    content="请先配置API Key。\n\n按F2打开侧边栏，输入API Key后按Enter保存。",
                    timestamp=datetime.now()
                )
                history.add_message(response_msg)
                return

            # 显示处理中消息
            processing_msg = Message(
                role="assistant",
                content="正在处理...",
                timestamp=datetime.now()
            )
            history.add_message(processing_msg)

            # 异步处理
            asyncio.create_task(self._process_message_async(event.content))

        except Exception as e:
            # 显示错误
            error_msg = Message(
                role="assistant",
                content=f"错误: {str(e)}",
                timestamp=datetime.now()
            )
            history.add_message(error_msg)

    async def _process_message_async(self, user_input: str) -> None:
        """异步处理消息 - 参考demo实现"""
        history = self.query_one(MessageHistory)
        log = self.query_one(RightPanel).get_operation_log()

        try:
            # 检查客户端
            if not self._client:
                # 尝试重新初始化
                self._init_client()
                if not self._client:
                    raise Exception("API Key 未配置。请按 F2 展开侧边栏，在配置区输入 API Key，然后按 Enter 保存")

            # 重置工具调用限制器（新的一轮对话）
            self._tool_limiter.reset()

            # 构建初始消息历史
            messages_history = [{"role": "user", "content": user_input}]

            # 参考demo的调用方式
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.send_message_with_history(messages_history)
            )
            
            message = response.choices[0].message
            
            # 处理工具调用循环
            tool_calls = []
            tool_results = []
            accumulated_content = ""  # 累积所有中间内容
            rejected_tools = []  # 被拒绝的工具调用

            # 显示工具调用摘要
            if message.tool_calls:
                tool_summary = f"🔧 正在调用 {len(message.tool_calls)} 个工具..."
                summary_msg = Message(
                    role="assistant",
                    content=tool_summary,
                    timestamp=datetime.now()
                )
                history.add_message(summary_msg)

            while message.tool_calls:
                # 累积中间内容（如果有）
                if message.content:
                    accumulated_content += message.content + "\n\n"

                # 构建包含 tool_calls 的 assistant 消息
                assistant_msg = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                }
                
                # 添加到消息历史
                messages_history.append(assistant_msg)

                # 执行当前轮的所有工具调用
                current_tool_results = []
                for tool_call in message.tool_calls:
                    tc = ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments)
                    )
                    
                    # 检查工具调用限制
                    allowed, reason = self._tool_limiter.can_call(tc.name, tc.arguments)
                    
                    if not allowed:
                        # 拒绝调用
                        rejected_tools.append((tc.name, reason))
                        result = f"⚠️ 工具调用被拒绝: {reason}"
                        
                        # 添加到当前轮结果
                        tool_result_msg = {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result
                        }
                        current_tool_results.append(tool_result_msg)
                        
                        # 添加日志
                        log_entry = LogEntry(
                            timestamp=datetime.now(),
                            tool_name=tc.name,
                            arguments=tc.arguments,
                            result=result,
                            duration=0.0
                        )
                        log.add_log(log_entry)
                        continue
                    
                    # 记录调用
                    self._tool_limiter.record_call(tc.name, tc.arguments)
                    tool_calls.append(tc)

                    # 执行工具
                    start_time = datetime.now()
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: execute_tool(self._graph, tc.name, tc.arguments)
                    )
                    duration = (datetime.now() - start_time).total_seconds()

                    # 保存工具结果
                    tr = ToolResult(
                        tool_call_id=tc.id,
                        name=tc.name,
                        arguments=tc.arguments,
                        result=result,
                        success=not result.startswith("工具执行错误")
                    )
                    tool_results.append(tr)

                    # 添加到当前轮结果
                    tool_result_msg = {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result
                    }
                    current_tool_results.append(tool_result_msg)

                    # 添加日志
                    log_entry = LogEntry(
                        timestamp=datetime.now(),
                        tool_name=tc.name,
                        arguments=tc.arguments,
                        result=result,
                        duration=duration
                    )
                    log.add_log(log_entry)

                # 将工具结果添加到消息历史
                messages_history.extend(current_tool_results)

                # 继续调用API（使用累积的消息历史）
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.send_message_with_history(messages_history)
                )
                message = response.choices[0].message
            
            # 添加助手消息（完整内容）
            # 使用累积的内容 + 最终内容
            final_content = message.content or ""
            content = accumulated_content + final_content if accumulated_content else final_content

            if not content:
                content = "(无回复)"

            # 如果有工具调用，添加工具调用摘要
            if tool_calls:
                tool_names = [tc.name for tc in tool_calls]
                content = f"✅ 已执行工具: {', '.join(tool_names)}\n\n{content}"
            
            # 如果有被拒绝的工具，添加提示
            if rejected_tools:
                rejected_info = "\n".join([f"• {name}: {reason}" for name, reason in rejected_tools])
                content += f"\n\n⚠️ 部分工具调用被限制:\n{rejected_info}"
                content += f"\n\n📊 工具调用统计:\n{self._tool_limiter.get_summary()}"
            
            assistant_message = Message(
                role="assistant",
                content=content,
                timestamp=datetime.now(),
                tool_calls=tool_calls if tool_calls else None,
                tool_results=tool_results if tool_results else None
            )

            history.add_message(assistant_message)

            # 强制刷新界面
            self.refresh()

        except Exception as e:
            # 显示详细错误
            error_msg = str(e)
            
            if "Connection error" in error_msg or "connection" in error_msg.lower():
                help_text = """
网络连接错误！可能的原因：
1. API Key 未配置或无效
2. 网络无法访问 API 服务器
3. API 服务器暂时不可用

解决方法：
• 按 F2 展开侧边栏，检查并配置 API Key
• 检查网络连接
• 尝试使用代理或 VPN
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
            
            error_message = Message(
                role="assistant",
                content=f"❌ 错误: {error_msg}\n{help_text}",
                timestamp=datetime.now()
            )
            history.add_message(error_message)

    def on_config_section_config_changed(self, event) -> None:
        """处理配置变更事件"""
        # 更新配置
        self._config = event.config
        
        # 持久化保存配置
        self._config_manager.save(self._config)
        
        # 同步更新 RightPanel 的配置
        try:
            right_panel = self.query_one(RightPanel)
            right_panel._config = self._config
        except Exception:
            pass
        
        # 重新初始化客户端
        self._init_client()
        
        if self._client:
            self.notify("✅ 配置已保存并应用", title="配置")
        else:
            self.notify("⚠️ 配置已保存，但API Key无效", title="警告")

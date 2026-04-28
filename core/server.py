import threading
import queue
import time
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from .embedded_db import EmbeddedGraphDB
from .activity_recorder import get_recorder


class PacketType(Enum):
    PROCESS_MESSAGE = "process_message"
    EXECUTE_TOOL = "execute_tool"
    GET_STATUS = "get_status"
    GET_SETTINGS = "get_settings"      # 合并：获取 api_config + tool_limits
    SET_SETTINGS = "set_settings"     # 合并：设置 api_config + tool_limits
    GET_WEB_USERS = "get_web_users"     # 获取 Web 用户列表
    SET_WEB_USER = "set_web_user"       # 设置 Web 用户（用户名+密码）
    GET_WEB_SERVICE_STATUS = "get_web_service_status"  # 获取 Web 服务运行状态
    GET_CONFIG = "get_config"                           # 获取完整配置
    GET_HISTORY = "get_history"
    SAVE_HISTORY = "save_history"
    SHUTDOWN = "shutdown"


@dataclass
class Packet:
    id: str
    type: PacketType
    body: Dict[str, Any]
    response_queue: Optional[queue.Queue] = field(default=None)
    created_at: float = field(default_factory=time.time)


@dataclass
class PacketResponse:
    id: str
    success: bool
    data: Any = None
    error: Optional[str] = None


class BackendServer:
    
    DEFAULT_CONFIG_PATH = Path.home() / ".trulymem" / "config.json"
    
    def __init__(self, db_path: str = "graph_memory.db", use_embedded_db: bool = True, config_file: str = None, username: str = ""):
        self._db_path = db_path
        self._use_embedded_db = use_embedded_db
        self._config_file = Path(config_file) if config_file else self.DEFAULT_CONFIG_PATH
        self._username = username
        
        self._graph = None
        self._client = None
        self._tool_limiter = None
        
        self._input_queue: queue.Queue[Packet] = queue.Queue()
        self._response_queues: Dict[str, queue.Queue] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self._lock = threading.Lock()
        self._config = {}
        self._tool_limits: Dict[str, int] = {}
        self._message_history: list = []

    def start(self, api_key: str = "", base_url: str = "https://api.deepseek.com", model: str = "deepseek-v4-flash") -> None:
        if self._running:
            return
        
        self._load_config()
        
        if api_key:
            self._config["api_key"] = api_key
        if base_url:
            self._config["base_url"] = base_url
        if model:
            self._config["model"] = model
        
        self._init_graph()
        self._tool_limiter = self._create_tool_limiter()
        
        if self._config["api_key"]:
            from .graph_client import GraphMemoryClient
            self._client = GraphMemoryClient(
                api_key=self._config["api_key"],
                base_url=self._config["base_url"],
                model=self._config.get("model", "deepseek-v4-flash"),
                graph=self._graph
            )
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    # 工具限制默认值（仅首次启动无 config.json 时使用）
    # 启动后请直接编辑配置文件修改
    _DEFAULT_LIMITS = {
        "persona_update_max": 1,
        "task_update_max": 20,
        "task_query_max": 30,
        "memory_query_max": 30,
        "memory_update_max": 15,
    }
    _DEFAULT_CONFIG = {
        "api_key": "",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-v4-flash",
        "message_timeout": 600,  # 消息处理超时（秒），默认10分钟
    }

    def _load_config(self) -> None:
        """加载配置。如果指定了用户名，从用户的 config_path 加载。
        所有工具调用限制值均从配置文件读取，不硬编码在代码中。"""
        config_file = self._config_file
        
        # 如果指定了用户名，尝试从全局数据库获取用户的配置路径
        if self._username:
            try:
                global_db_path = Path.home() / ".trulymem" / "trulymem.db"
                if global_db_path.exists():
                    from .embedded_db import EmbeddedGraphDB
                    temp_db = EmbeddedGraphDB(db_path=str(global_db_path))
                    user_info = temp_db.get_web_user(self._username)
                    temp_db.close()
                    if user_info and user_info.get('config_path'):
                        config_file = Path(user_info['config_path'])
            except Exception:
                pass
        
        # 工具限制字段列表
        limit_keys = list(self._DEFAULT_LIMITS.keys())
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    saved = json.load(f)
                    # 通用配置（含 api_key, base_url, model, message_timeout 等）
                    for key in self._DEFAULT_CONFIG:
                        if key in saved:
                            self._config[key] = saved[key]
                        else:
                            self._config[key] = self._DEFAULT_CONFIG[key]
                    # 工具限制
                    for key in limit_keys:
                        if key in saved:
                            self._tool_limits[key] = int(saved[key])
                        else:
                            self._tool_limits[key] = self._DEFAULT_LIMITS[key]
            except Exception:
                # 读取失败时使用默认值
                for key in self._DEFAULT_CONFIG:
                    self._config[key] = self._DEFAULT_CONFIG[key]
                for key in limit_keys:
                    self._tool_limits[key] = self._DEFAULT_LIMITS[key]
        else:
            # 首次启动，用默认值写入配置文件
            for key in self._DEFAULT_CONFIG:
                self._config[key] = self._DEFAULT_CONFIG[key]
            self._tool_limits = dict(self._DEFAULT_LIMITS)
            self._save_config()

    def _save_config(self) -> None:
        """保存配置。如果指定了用户名，保存到用户的 config_path。"""
        config_file = self._config_file
        
        # 如果指定了用户名，尝试从全局数据库获取用户的配置路径
        if self._username:
            try:
                global_db_path = Path.home() / ".trulymem" / "trulymem.db"
                if global_db_path.exists():
                    from .embedded_db import EmbeddedGraphDB
                    temp_db = EmbeddedGraphDB(db_path=str(global_db_path))
                    user_info = temp_db.get_web_user(self._username)
                    temp_db.close()
                    if user_info and user_info.get('config_path'):
                        config_file = Path(user_info['config_path'])
            except Exception:
                pass
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        # 合并通用配置和工具限制（过滤掉内部字段如 _history 等）
        save_cfg = {k: self._config[k] for k in self._DEFAULT_CONFIG if k in self._config}
        saved_data = {**save_cfg, **self._tool_limits}
        with open(config_file, 'w') as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)

    def _create_tool_limiter(self):
        from .tool_limiter import ToolLimiter, ToolLimits
        # 所有值从 _tool_limits 读取（由 _load_config 从 config.json 加载）
        # _load_config 已保证所有键存在
        limits = ToolLimits(
            persona_update_max=self._tool_limits["persona_update_max"],
            task_update_max=self._tool_limits["task_update_max"],
            task_query_max=self._tool_limits["task_query_max"],
            memory_query_max=self._tool_limits["memory_query_max"],
            memory_update_max=self._tool_limits["memory_update_max"],
        )
        return ToolLimiter(limits)

    def _init_graph(self) -> None:
        """初始化图数据库。如果指定了用户名，从全局数据库获取用户的 db_path。"""
        db_path = self._db_path
        
        # 如果指定了用户名，尝试从全局数据库获取用户的数据库路径
        if self._username:
            try:
                # 临时连接全局数据库获取用户信息
                global_db_path = Path.home() / ".trulymem" / "trulymem.db"
                if global_db_path.exists():
                    temp_db = EmbeddedGraphDB(db_path=str(global_db_path))
                    user_info = temp_db.get_web_user(self._username)
                    temp_db.close()
                    if user_info and user_info.get('db_path'):
                        db_path = user_info['db_path']
                        self._db_path = db_path  # 更新 _db_path，供外部（如 web_api.py）获取正确的路径
            except Exception:
                pass  # 如果获取失败，使用默认路径
        
        if self._use_embedded_db:
            self._graph = EmbeddedGraphDB(db_path=db_path)
        else:
            from .graph_client import Neo4jGraph
            self._graph = Neo4jGraph(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="graphmemory123"
            )

    def _run_loop(self) -> None:
        while self._running:
            try:
                packet = self._input_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            
            self._process_packet(packet)

    def _process_packet(self, packet: Packet) -> None:
        response_body = {"error": "not implemented"}
        
        try:
            if packet.type == PacketType.PROCESS_MESSAGE:
                response_body = self._handle_process_message(packet.body)
            elif packet.type == PacketType.EXECUTE_TOOL:
                response_body = self._handle_execute_tool(packet.body)
            elif packet.type == PacketType.GET_STATUS:
                response_body = self._handle_get_status()
            elif packet.type == PacketType.GET_SETTINGS:
                response_body = self._handle_get_settings()
            elif packet.type == PacketType.SET_SETTINGS:
                response_body = self._handle_set_settings(packet.body)
            elif packet.type == PacketType.GET_WEB_USERS:
                response_body = {"users": self._graph.get_web_users()}
            elif packet.type == PacketType.SET_WEB_USER:
                username = packet.body.get("username", "")
                password = packet.body.get("password", "")
                if not username or not password:
                    response_body = {"success": False, "error": "用户名和密码不能为空"}
                else:
                    # 使用全局数据库（trulymem.db）来管理用户
                    global_db_path = Path.home() / ".trulymem" / "trulymem.db"
                    from .embedded_db import EmbeddedGraphDB
                    global_db = EmbeddedGraphDB(db_path=str(global_db_path))
                    response_body = global_db.set_web_user(username, password)
                    global_db.close()
            elif packet.type == PacketType.GET_WEB_SERVICE_STATUS:
                body = packet.body
                response_body = {"running": body.get("running", False), "port": body.get("port", 4096)}
            elif packet.type == PacketType.GET_CONFIG:
                response_body = self._get_full_config()
            elif packet.type == PacketType.GET_HISTORY:
                response_body = self._handle_get_history()
            elif packet.type == PacketType.SAVE_HISTORY:
                response_body = self._handle_save_history(packet.body)
            elif packet.type == PacketType.SHUTDOWN:
                self._running = False
                response_body = {"success": True, "status": "shutdown"}
            
            if "success" not in response_body:
                response_body["success"] = True
        except Exception as e:
            response_body["success"] = False
            response_body["error"] = str(e)
        
        self._send_response(packet.id, PacketResponse(
            id=packet.id,
            success=response_body.get("success", False),
            data=response_body if response_body.get("success") else None,
            error=response_body.get("error")
        ))

    def _handle_process_message(self, body: Dict) -> Dict:
        from .tool_executor import execute_tool
        
        get_recorder().clear()
        
        user_input = body.get("user_input", "")
        
        if not self._client:
            return {"success": False, "error": "API Key 未配置", "content": "请先配置 API Key"}
        
        self._graph.save_chat_records([{"role": "user", "content": user_input}])
        
        self._tool_limiter.reset()
        
        messages_history = [{"role": "user", "content": user_input}]
        
        response = self._client.send_message_with_history(messages_history)
        message = response.choices[0].message
        
        tool_calls = []
        accumulated_content = ""
        rejected_tools = []
        
        while message.tool_calls:
            if message.content:
                accumulated_content += message.content + "\n\n"
            
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
            # 保留 DeepSeek thinking 模式的 reasoning_content
            reasoning_content = getattr(message, 'reasoning_content', None)
            if reasoning_content:
                assistant_msg["reasoning_content"] = reasoning_content
            messages_history.append(assistant_msg)
            
            current_tool_results = []
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                
                allowed, reason = self._tool_limiter.can_call(tool_call.function.name, args)
                
                if not allowed:
                    rejected_tools.append((tool_call.function.name, reason))
                    result = f"工具调用被拒绝: {reason}"
                    tool_result_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    }
                    current_tool_results.append(tool_result_msg)
                    continue
                
                self._tool_limiter.record_call(tool_call.function.name, args)
                
                if tool_call.function.name == "context_rewrite":
                    result = execute_tool(self._graph, tool_call.function.name, args)
                    result_data = json.loads(result)
                    
                    # 记录到 tool_calls，让 TUI 显示这个工具调用
                    tool_calls.append({
                        "name": tool_call.function.name,
                        "arguments": args,
                        "result": result
                    })
                    
                    if result_data.get("status") == "success":
                        user_msg = messages_history[0]
                        # 添加特殊标记，让 AI 知道这是上下文压缩的结果
                        compressed_content = f"<context_compressed>\n{result_data['summary']}\n</context_compressed>"
                        messages_history[:] = [
                            user_msg,
                            {"role": "assistant", "content": compressed_content}
                        ]
                    # context_rewrite 压缩上下文后，不需要添加 tool 结果消息
                    # 因为 messages_history 已经被重写为压缩后的状态
                    continue
                
                result = execute_tool(self._graph, tool_call.function.name, args)
                tool_calls.append({
                    "name": tool_call.function.name,
                    "arguments": args,
                    "result": result
                })
                
                tool_result_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
                current_tool_results.append(tool_result_msg)
            
            messages_history.extend(current_tool_results)
            
            response = self._client.send_message_with_history(messages_history)
            message = response.choices[0].message
        
        final_content = message.content or ""
        content = accumulated_content + final_content if accumulated_content else final_content
        
        if not content:
            content = "(无回复)"
        
        if tool_calls:
            tool_names = [tc["name"] for tc in tool_calls]
            content = f"已执行工具: {', '.join(tool_names)}\n\n{content}"
        
        if rejected_tools:
            rejected_info = "\n".join([f"{name}: {reason}" for name, reason in rejected_tools])
            content += f"\n\n部分工具调用被限制:\n{rejected_info}"
            content += f"\n\n工具调用统计:\n{self._tool_limiter.get_summary()}"
        
        self._graph.save_chat_records([{"role": "assistant", "content": content}])
        
        return {
            "success": True,
            "content": content,
            "tool_calls": tool_calls,
            "rejected_tools": rejected_tools
        }

    def _handle_execute_tool(self, body: Dict) -> Dict:
        from .tool_executor import execute_tool
        
        try:
            tool_name = body.get("tool_name")
            arguments = body.get("arguments", {})
            
            result = execute_tool(self._graph, tool_name, arguments)
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_get_status(self) -> Dict:
        return {
            "running": self._running,
            "config": self._config,
            "graph_initialized": self._graph is not None,
            "client_initialized": self._client is not None
        }

    def _handle_get_settings(self) -> Dict:
        return {
            "api_config": self._config.copy(),
            "tool_limits": self._tool_limits.copy()
        }

    def _get_full_config(self) -> Dict:
        return {
            "api_config": self._config.copy(),
            "tool_limits": self._tool_limits.copy(),
        }

    def _handle_set_settings(self, body: Dict) -> Dict:
        api_config = body.get("api_config", {})
        tool_limits = body.get("tool_limits", {})
        
        # 仅当 api_config 有值时更新 API 配置（避免单独保存 tool_limits 时清空 API key）
        if api_config:
            api_key = api_config.get("api_key", self._config.get("api_key", ""))
            base_url = api_config.get("base_url", self._config.get("base_url", "https://api.deepseek.com"))
            model = api_config.get("model", self._config.get("model", "deepseek-v4-flash"))
            self.update_config(api_key, base_url, model)
            # 通用配置字段（如 message_timeout）
            for key in ["message_timeout"]:
                if key in api_config:
                    self._config[key] = int(api_config[key])
        
        limits_keys = [
            "persona_update_max",
            "task_update_max",
            "task_query_max",
            "memory_query_max",
            "memory_update_max",
        ]
        for key in limits_keys:
            if key in tool_limits:
                value = int(tool_limits[key])
                if value < 1:
                    return {"success": False, "error": f"{key} must be >= 1, got {value}"}
                self._tool_limits[key] = value
        
        self._tool_limiter = self._create_tool_limiter()
        self._save_config()
        return {"status": "settings_updated"}

    def _handle_get_history(self) -> Dict:
        history = self._graph.get_chat_records(limit=500)
        return {"history": history}

    def _handle_save_history(self, body: Dict) -> Dict:
        messages = body.get("messages", [])
        if not messages:
            self._graph.clear_chat_records()
            return {"status": "history_cleared"}
        result = self._graph.save_chat_records(messages)
        return {"status": "history_saved"}
    
    def _send_response(self, request_id: str, response: PacketResponse) -> None:
        with self._lock:
            q = self._response_queues.pop(request_id, None)
        if q:
            q.put(response)

    def send(self, packet: Packet) -> Packet:
        resp_q = queue.Queue()
        
        with self._lock:
            self._response_queues[packet.id] = resp_q
        
        self._input_queue.put(packet)
        
        try:
            timeout = self._config.get("message_timeout", 600)
            response = resp_q.get(timeout=timeout)
            return Packet(
                id=response.id,
                type=packet.type,
                body={
                    "success": response.success,
                    "data": response.data,
                    "error": response.error
                }
            )
        except queue.Empty:
            return Packet(
                id=packet.id,
                type=packet.type,
                body={"success": False, "error": "timeout"}
            )
        finally:
            with self._lock:
                self._response_queues.pop(packet.id, None)

    def process_message(self, user_input: str) -> Dict[str, Any]:
        packet = Packet(
            id=f"{time.time()}",
            type=PacketType.PROCESS_MESSAGE,
            body={"user_input": user_input}
        )
        
        response = self.send(packet)
        return response.body

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        packet = Packet(
            id=f"{time.time()}",
            type=PacketType.EXECUTE_TOOL,
            body={"tool_name": tool_name, "arguments": arguments}
        )
        
        response = self.send(packet)
        return response.body

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-v4-flash") -> None:
        with self._lock:
            self._config["api_key"] = api_key
            self._config["base_url"] = base_url
            self._config["model"] = model
        
        if api_key and self._graph:
            from .graph_client import GraphMemoryClient
            self._client = GraphMemoryClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                graph=self._graph
            )

    def get_config(self) -> Dict[str, str]:
        return self._config.copy()

    def save_message_history(self, messages: list) -> None:
        self._message_history = messages

    def get_message_history(self) -> list:
        return self._message_history.copy()

    def shutdown(self) -> None:
        if not self._running:
            return
        
        packet = Packet(
            id=f"{time.time()}",
            type=PacketType.SHUTDOWN,
            body={}
        )
        self.send(packet)
        
        if self._thread:
            self._thread.join(timeout=2.0)
        
        if self._graph:
            self._graph.close()
            self._graph = None
        
        self._running = False
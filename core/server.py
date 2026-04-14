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


class PacketType(Enum):
    PROCESS_MESSAGE = "process_message"
    EXECUTE_TOOL = "execute_tool"
    GET_STATUS = "get_status"
    GET_CONFIG = "get_config"
    SET_CONFIG = "set_config"
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
    
    def __init__(self, db_path: str = "graph_memory.db", use_embedded_db: bool = True, config_file: str = None):
        self._db_path = db_path
        self._use_embedded_db = use_embedded_db
        self._config_file = Path(config_file) if config_file else self.DEFAULT_CONFIG_PATH
        
        self._graph = None
        self._client = None
        self._tool_limiter = None
        
        self._input_queue: queue.Queue[Packet] = queue.Queue()
        self._response_queues: Dict[str, queue.Queue] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self._lock = threading.Lock()
        self._config = {"api_key": "", "base_url": "https://api.deepseek.com", "model": "deepseek-chat"}
        self._message_history: list = []

    def start(self, api_key: str = "", base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat") -> None:
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
                model=self._config.get("model", "deepseek-chat"),
                graph=self._graph
            )
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _load_config(self) -> None:
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    saved = json.load(f)
                    self._config.update(saved)
            except Exception:
                pass

    def _save_config(self) -> None:
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def _create_tool_limiter(self):
        from .tool_limiter import ToolLimiter
        return ToolLimiter()

    def _init_graph(self) -> None:
        if self._use_embedded_db:
            self._graph = EmbeddedGraphDB(db_path=self._db_path)
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
            elif packet.type == PacketType.GET_CONFIG:
                response_body = self._handle_get_config()
            elif packet.type == PacketType.SET_CONFIG:
                response_body = self._handle_set_config(packet.body)
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
        
        user_input = body.get("user_input", "")
        
        if not self._client:
            return {"success": False, "error": "API Key 未配置", "content": "请先配置 API Key"}
        
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

    def _handle_get_config(self) -> Dict:
        return self._config.copy()

    def _handle_set_config(self, body: Dict) -> Dict:
        api_key = body.get("api_key", "")
        base_url = body.get("base_url", "https://api.deepseek.com")
        model = body.get("model", "deepseek-chat")
        
        self.update_config(api_key, base_url, model)
        self._save_config()
        return {"status": "config_updated"}

    def _handle_get_history(self) -> Dict:
        return {"history": self._message_history}

    def _handle_save_history(self, body: Dict) -> Dict:
        messages = body.get("messages", [])
        self._message_history = messages
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
            response = resp_q.get(timeout=30.0)
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

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat") -> None:
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
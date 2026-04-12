import threading
import queue
import time
from typing import Any, Dict
from dataclasses import dataclass, field
from enum import Enum


class PacketType(Enum):
    MESSAGE = "message"
    CONFIG = "config"
    TOOL = "tool"
    STATUS = "status"
    HISTORY = "history"


@dataclass
class Packet:
    id: str
    type: PacketType
    body: Dict[str, Any]
    created_at: float = field(default_factory=time.time)


from .embedded_db import EmbeddedGraphDB


class BackendServer:
    def __init__(self, db_path: str = "graph_memory.db", use_embedded_db: bool = True):
        self._db_path = db_path
        self._use_embedded_db = use_embedded_db
        self._graph = None
        self._client = None
        self._running = False
        self._thread = None
        self._input_queue: queue.Queue[Packet] = queue.Queue()
        self._response_queues: Dict[str, queue.Queue] = {}
        self._lock = threading.Lock()
        self._config = {"api_key": "", "base_url": "https://api.deepseek.com"}

    def start(self, api_key: str = "", base_url: str = "https://api.deepseek.com") -> None:
        if self._running:
            return
        self._init_graph()
        self._config = {"api_key": api_key, "base_url": base_url}
        if api_key:
            from .graph_client import GraphMemoryClient
            self._client = GraphMemoryClient(api_key=api_key, base_url=base_url, graph=self._graph)
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _init_graph(self) -> None:
        if self._use_embedded_db:
            self._graph = EmbeddedGraphDB(db_path=self._db_path)
        else:
            from .graph_client import Neo4jGraph
            self._graph = Neo4jGraph(uri="bolt://localhost:7687", user="neo4j", password="graphmemory123")

    def _run_loop(self) -> None:
        while self._running:
            try:
                packet = self._input_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            self._process_packet(packet)

    def _process_packet(self, packet: Packet) -> None:
        body = {"success": False, "error": "not implemented"}
        try:
            if packet.type == PacketType.MESSAGE:
                body = self._handle_message(packet.body)
            elif packet.type == PacketType.CONFIG:
                body = self._handle_config(packet.body)
            elif packet.type == PacketType.TOOL:
                body = self._handle_tool(packet.body)
            elif packet.type == PacketType.STATUS:
                body = self._handle_status()
            elif packet.type == PacketType.HISTORY:
                body = self._handle_history(packet.body)
            body["success"] = True
        except Exception as e:
            body["error"] = str(e)
        finally:
            self._send_response(packet.id, Packet(id=packet.id, type=packet.type, body=body))

    def _handle_message(self, body: Dict) -> Dict:
        from .tool_executor import execute_tool
        from .tool_limiter import ToolLimiter
        
        limiter = ToolLimiter()
        user_input = body.get("message", "")
        if not self._client:
            return {"error": "API Key not configured", "content": "请先配置 API Key"}
        
        messages = [{"role": "user", "content": user_input}]
        response = self._client.send_message_with_history(messages)
        message = response.choices[0].message
        content = message.content or "(无��复)"
        tool_calls = []
        
        while message.tool_calls:
            args = {}
            try:
                import json
                args = json.loads(message.tool_calls[0].function.arguments)
            except:
                pass
            
            allowed, reason = limiter.can_call(message.tool_calls[0].function.name, args)
            if not allowed:
                tool_calls.append({"name": message.tool_calls[0].function.name, "result": f"工具调用被拒绝: {reason}"})
                continue
            
            limiter.record_call(message.tool_calls[0].function.name, args)
            result = execute_tool(self._graph, message.tool_calls[0].function.name, args)
            tool_calls.append({"name": message.tool_calls[0].function.name, "result": result})
            messages.append({"role": "assistant", "tool_calls": [{"id": "1", "function": {"name": message.tool_calls[0].function.name, "arguments": message.tool_calls[0].function.arguments}}]})
            messages.append({"role": "tool", "tool_call_id": "1", "content": result})
            response = self._client.send_message_with_history(messages)
            message = response.choices[0].message
            content = message.content or content
        
        return {"content": content, "tool_calls": tool_calls}

    def _handle_config(self, body: Dict) -> Dict:
        api_key = body.get("api_key", "")
        base_url = body.get("base_url", "https://api.deepseek.com")
        self._config = {"api_key": api_key, "base_url": base_url}
        if api_key and self._graph:
            from .graph_client import GraphMemoryClient
            self._client = GraphMemoryClient(api_key=api_key, base_url=base_url, graph=self._graph)
        return {"status": "config_updated"}

    def _handle_tool(self, body: Dict) -> Dict:
        from .tool_executor import execute_tool
        name = body.get("name", "")
        args = body.get("arguments", {})
        result = execute_tool(self._graph, name, args)
        return {"result": result}

    def _handle_status(self) -> Dict:
        return {"running": self._running, "config": self._config, "client_ready": self._client is not None}

    def _handle_history(self, body: Dict) -> Dict:
        action = body.get("action", "get")
        if action == "save":
            self._message_history = body.get("messages", [])
            return {"status": "saved"}
        return {"history": getattr(self, "_message_history", [])}

    def send(self, packet: Packet) -> Packet:
        resp_q = queue.Queue()
        with self._lock:
            self._response_queues[packet.id] = resp_q
        self._input_queue.put(packet)
        try:
            return resp_q.get(timeout=30.0)
        except queue.Empty:
            return Packet(id=packet.id, type=packet.type, body={"success": False, "error": "timeout"})
        finally:
            with self._lock:
                self._response_queues.pop(packet.id, None)

    def _send_response(self, request_id: str, packet: Packet) -> None:
        with self._lock:
            q = self._response_queues.pop(request_id, None)
        if q:
            q.put(packet)

    def shutdown(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._graph:
            self._graph.close()
            self._graph = None


class BackendClient:
    def __init__(self, server: BackendServer):
        self._server = server
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"{time.time()}_{self._counter}"

    def send_message(self, message: str) -> Dict:
        packet = Packet(id=self._next_id(), type=PacketType.MESSAGE, body={"message": message})
        return self._server.send(packet).body

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com") -> Dict:
        packet = Packet(id=self._next_id(), type=PacketType.CONFIG, body={"api_key": api_key, "base_url": base_url})
        return self._server.send(packet).body

    def execute_tool(self, name: str, arguments: Dict) -> str:
        packet = Packet(id=self._next_id(), type=PacketType.TOOL, body={"name": name, "arguments": arguments})
        return self._server.send(packet).body.get("result", "")

    def get_status(self) -> Dict:
        packet = Packet(id=self._next_id(), type=PacketType.STATUS, body={})
        return self._server.send(packet).body

    def save_history(self, messages: list) -> None:
        packet = Packet(id=self._next_id(), type=PacketType.HISTORY, body={"action": "save", "messages": messages})
        self._server.send(packet)

    def get_history(self) -> list:
        packet = Packet(id=self._next_id(), type=PacketType.HISTORY, body={"action": "get"})
        return self._server.send(packet).body.get("history", [])

    def shutdown(self) -> None:
        self._server.shutdown()


__all__ = ["BackendServer", "BackendClient", "EmbeddedGraphDB", "Packet", "PacketType"]
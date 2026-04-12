import threading
import queue
import time
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from .embedded_db import EmbeddedGraphDB
from .graph_client import GraphMemoryClient
from .tool_executor import execute_tool
from .tool_limiter import ToolLimiter


class MessageType(Enum):
    PROCESS_MESSAGE = "process_message"
    EXECUTE_TOOL = "execute_tool"
    GET_STATUS = "get_status"
    SHUTDOWN = "shutdown"


@dataclass
class BackendRequest:
    request_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    response_queue: queue.Queue = field(default=None)


@dataclass
class BackendResponse:
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None


class BackendServer:
    def __init__(self, db_path: str = "graph_memory.db", use_embedded_db: bool = True):
        self._db_path = db_path
        self._use_embedded_db = use_embedded_db
        
        self._graph = None
        self._client = None
        self._tool_limiter = ToolLimiter()
        
        self._request_queue: queue.Queue[BackendRequest] = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self._lock = threading.Lock()

    def start(self, api_key: str = "", base_url: str = "https://api.deepseek.com") -> None:
        if self._running:
            return
        
        self._init_graph()
        
        if api_key:
            self._client = GraphMemoryClient(
                api_key=api_key,
                base_url=base_url,
                graph=self._graph
            )
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

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
                request = self._request_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            
            if request.message_type == MessageType.PROCESS_MESSAGE:
                self._handle_process_message(request)
            elif request.message_type == MessageType.EXECUTE_TOOL:
                self._handle_execute_tool(request)
            elif request.message_type == MessageType.GET_STATUS:
                self._handle_get_status(request)
            elif request.message_type == MessageType.SHUTDOWN:
                self._running = False
                self._send_response(request, BackendResponse(
                    request_id=request.request_id,
                    success=True,
                    data={"status": "shutdown"}
                ))

    def _handle_process_message(self, request: BackendRequest) -> None:
        try:
            user_input = request.payload.get("user_input", "")
            
            if not self._client:
                self._send_response(request, BackendResponse(
                    request_id=request.request_id,
                    success=False,
                    error="API Key 未配置"
                ))
                return
            
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
            
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=True,
                data={
                    "content": content,
                    "tool_calls": tool_calls,
                    "rejected_tools": rejected_tools
                }
            ))
            
        except Exception as e:
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            ))

    def _handle_execute_tool(self, request: BackendRequest) -> None:
        try:
            tool_name = request.payload.get("tool_name")
            arguments = request.payload.get("arguments", {})
            
            allowed, reason = self._tool_limiter.can_call(tool_name, arguments)
            if not allowed:
                self._send_response(request, BackendResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"工具调用被拒绝: {reason}"
                ))
                return
            
            self._tool_limiter.record_call(tool_name, arguments)
            
            result = execute_tool(self._graph, tool_name, arguments)
            
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=True,
                data={"result": result}
            ))
            
        except Exception as e:
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            ))

    def _handle_get_status(self, request: BackendRequest) -> None:
        try:
            status = {
                "graph_initialized": self._graph is not None,
                "client_initialized": self._client is not None,
                "running": self._running
            }
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=True,
                data=status
            ))
        except Exception as e:
            self._send_response(request, BackendResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            ))

    def _send_response(self, request: BackendRequest, response: BackendResponse) -> None:
        if request.response_queue:
            request.response_queue.put(response)

    def process_message(self, user_input: str, timeout: float = 30.0) -> Dict[str, Any]:
        request_id = f"{time.time()}"
        response_queue = queue.Queue()
        
        request = BackendRequest(
            request_id=request_id,
            message_type=MessageType.PROCESS_MESSAGE,
            payload={"user_input": user_input},
            response_queue=response_queue
        )
        
        self._request_queue.put(request)
        
        try:
            response = response_queue.get(timeout=timeout)
            if not response.success:
                raise Exception(response.error)
            return response.data
        except queue.Empty:
            raise TimeoutError("请求超时")

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: float = 10.0) -> str:
        request_id = f"{time.time()}"
        response_queue = queue.Queue()
        
        request = BackendRequest(
            request_id=request_id,
            message_type=MessageType.EXECUTE_TOOL,
            payload={"tool_name": tool_name, "arguments": arguments},
            response_queue=response_queue
        )
        
        self._request_queue.put(request)
        
        try:
            response = response_queue.get(timeout=timeout)
            if not response.success:
                raise Exception(response.error)
            return response.data["result"]
        except queue.Empty:
            raise TimeoutError("工具执行超时")

    def shutdown(self) -> None:
        if not self._running:
            return
        
        request_id = f"{time.time()}"
        response_queue = queue.Queue()
        
        request = BackendRequest(
            request_id=request_id,
            message_type=MessageType.SHUTDOWN,
            payload={},
            response_queue=response_queue
        )
        
        self._request_queue.put(request)
        
        if self._thread:
            self._thread.join(timeout=2.0)
        
        if self._graph:
            self._graph.close()
            self._graph = None

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com") -> None:
        with self._lock:
            if api_key and self._graph:
                self._client = GraphMemoryClient(
                    api_key=api_key,
                    base_url=base_url,
                    graph=self._graph
                )
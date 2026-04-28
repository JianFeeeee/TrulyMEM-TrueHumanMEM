import threading
import time
from typing import Any, Dict

from .server import BackendServer, Packet, PacketType


class BackendClient:
    
    def __init__(self, server: BackendServer):
        self._server = server
        self._counter = 0
        self._lock = threading.Lock()

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"{time.time()}_{self._counter}"

    def send(self, message: str) -> Dict:
        return self.process_message(message)

    def process_message(self, user_input: str) -> Dict:
        return self._server.process_message(user_input)

    def get_settings(self) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_SETTINGS,
            body={}
        )
        return self._server.send(packet).body

    def update_settings(self, api_config: Dict = None, tool_limits: Dict = None) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SET_SETTINGS,
            body={
                "api_config": api_config or {},
                "tool_limits": tool_limits or {}
            }
        )
        return self._server.send(packet).body

    def execute_tool(self, name: str, arguments: Dict) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.EXECUTE_TOOL,
            body={"tool_name": name, "arguments": arguments}
        )
        return self._server.send(packet).body

    def get_status(self) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_STATUS,
            body={}
        )
        return self._server.send(packet).body

    def save_history(self, messages: list) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SAVE_HISTORY,
            body={"messages": messages}
        )
        response = self._server.send(packet)
        return response.body.get("data", {})

    def get_history(self) -> list:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_HISTORY,
            body={}
        )
        response = self._server.send(packet)
        data = response.body.get("data", {})
        return data.get("history", [])
    
    def clear_history(self) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SAVE_HISTORY,
            body={"messages": []}
        )
        response = self._server.send(packet)
        return response.body.get("data", {})

    def get_web_users(self) -> list:
        """获取 Web 用户列表"""
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_WEB_USERS,
            body={}
        )
        return self._server.send(packet).body.get("users", [])

    def set_web_user(self, username: str, password: str) -> Dict:
        """设置 Web 用户"""
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SET_WEB_USER,
            body={"username": username, "password": password}
        )
        return self._server.send(packet).body.get("data", {"success": False})

    def get_full_config(self) -> Dict:
        """获取完整配置"""
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_CONFIG,
            body={}
        )
        response = self._server.send(packet)
        return response.body if response.body else {"api_config": {}, "tool_limits": {}}

    def report_web_status(self, running: bool, port: int = 4096) -> Dict:
        """向后端报告 Web 服务运行状态"""
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_WEB_SERVICE_STATUS,
            body={"running": running, "port": port}
        )
        response = self._server.send(packet)
        return response.body if response.body else {"success": False}
    
    def shutdown(self) -> None:
        self._server.shutdown()

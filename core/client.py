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

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat") -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SET_CONFIG,
            body={"api_key": api_key, "base_url": base_url, "model": model}
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

    def get_config(self) -> Dict:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_CONFIG,
            body={}
        )
        return self._server.send(packet).body

    def save_history(self, messages: list) -> None:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.SAVE_HISTORY,
            body={"messages": messages}
        )
        self._server.send(packet)

    def get_history(self) -> list:
        packet = Packet(
            id=self._next_id(),
            type=PacketType.GET_HISTORY,
            body={}
        )
        return self._server.send(packet).body.get("history", [])

    def shutdown(self) -> None:
        self._server.shutdown()
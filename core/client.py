import threading
from typing import Any, Dict

from .server import BackendServer


class BackendClient:
    def __init__(self, server: BackendServer):
        self._server = server
        self._request_counter = 0
        self._lock = threading.Lock()

    def process_message(self, user_input: str, timeout: float = 30.0) -> Dict[str, Any]:
        with self._lock:
            self._request_counter += 1
        return self._server.process_message(user_input, timeout)

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: float = 10.0) -> str:
        with self._lock:
            self._request_counter += 1
        return self._server.execute_tool(tool_name, arguments, timeout)

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com") -> None:
        self._server.update_config(api_key, base_url)

    def shutdown(self) -> None:
        self._server.shutdown()
import threading
from typing import Any, Dict

from .server import BackendServer, MessageType


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

    def update_config(self, api_key: str, base_url: str = "https://api.deepseek.com") -> Dict[str, Any]:
        return self._send_request(MessageType.SET_CONFIG, {"api_key": api_key, "base_url": base_url})

    def get_config(self) -> Dict[str, str]:
        result = self._send_request(MessageType.GET_CONFIG, {})
        return result.get("data", {"api_key": "", "base_url": "https://api.deepseek.com"})

    def get_message_history(self) -> list:
        result = self._send_request(MessageType.GET_HISTORY, {})
        return result.get("data", {}).get("history", [])

    def save_message_history(self, messages: list) -> None:
        self._send_request(MessageType.SAVE_HISTORY, {"messages": messages})

    def _send_request(self, message_type: MessageType, payload: Dict[str, Any]) -> Dict[str, Any]:
        import queue
        request_id = f"{id(self)}"
        response_queue = queue.Queue()
        
        from .server import BackendRequest
        request = BackendRequest(
            request_id=request_id,
            message_type=message_type,
            payload=payload,
            response_queue=response_queue
        )
        
        self._server._request_queue.put(request)
        
        try:
            response = response_queue.get(timeout=5.0)
            if not response.success:
                raise Exception(response.error)
            return {"success": True, "data": response.data}
        except queue.Empty:
            return {"success": False, "error": "timeout"}

    def shutdown(self) -> None:
        self._server.shutdown()
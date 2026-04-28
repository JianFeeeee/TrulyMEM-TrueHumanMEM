import pytest
import os
import tempfile
import time
import threading
import queue

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestPacketTypeEnum:

    @pytest.mark.parametrize("packet_type,expected_value", [
        ("PROCESS_MESSAGE", "process_message"),
        ("EXECUTE_TOOL", "execute_tool"),
        ("GET_STATUS", "get_status"),
        ("GET_SETTINGS", "get_settings"),
        ("SET_SETTINGS", "set_settings"),
        ("GET_HISTORY", "get_history"),
        ("SAVE_HISTORY", "save_history"),
        ("SHUTDOWN", "shutdown"),
    ])
    def test_packet_type_exists(self, packet_type, expected_value):
        from core import PacketType
        pt = getattr(PacketType, packet_type)
        assert pt is not None
        assert pt.value == expected_value

    def test_packet_type_count(self):
        from core import PacketType
        assert len(list(PacketType)) == 8


class TestPacketCreation:
    """测试 Packet 创建"""
    
    def test_packet_with_id_and_type(self):
        from core import Packet, PacketType
        packet = Packet(id="test-1", type=PacketType.PROCESS_MESSAGE, body={"user_input": "hello"})
        assert packet.id == "test-1"
        assert packet.type == PacketType.PROCESS_MESSAGE

    def test_packet_body(self):
        from core import Packet, PacketType
        body = {"user_input": "test", "extra": "data"}
        packet = Packet(id="test-2", type=PacketType.EXECUTE_TOOL, body=body)
        assert packet.body == body

    def test_packet_with_empty_body(self):
        from core import Packet, PacketType
        packet = Packet(id="test-3", type=PacketType.GET_STATUS, body={})
        assert packet.body == {}

    def test_packet_created_at_default(self):
        from core import Packet, PacketType
        before = time.time()
        packet = Packet(id="test-4", type=PacketType.GET_SETTINGS, body={})
        after = time.time()
        assert before <= packet.created_at <= after


class TestPacketResponse:
    """测试 PacketResponse"""
    
    def test_packet_response_success(self):
        from core import PacketResponse
        response = PacketResponse(id="resp-1", success=True, data={"result": "ok"})
        assert response.id == "resp-1"
        assert response.success is True
        assert response.data == {"result": "ok"}

    def test_packet_response_error(self):
        from core import PacketResponse
        response = PacketResponse(id="resp-2", success=False, error="error msg")
        assert response.id == "resp-2"
        assert response.success is False
        assert response.error == "error msg"


class TestBackendServerCreation:
    """测试 BackendServer 创建"""
    
    def test_backend_server_init(self):
        from core import BackendServer
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        assert server._db_path == ":memory:"
        assert server._use_embedded_db is True
        assert server._graph is None
        assert server._client is None
        assert server._tool_limiter is None

    def test_backend_server_default_params(self):
        from core import BackendServer
        server = BackendServer()
        assert server._db_path == "graph_memory.db"
        assert server._use_embedded_db is True


class TestBackendServerLifecycle:
    """测试 BackendServer 生命周期"""
    
    def test_backend_server_start_stop(self):
        from core import BackendServer
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        
        assert server._running is True
        assert server._graph is not None
        assert server._tool_limiter is not None
        
        server.shutdown()
        assert server._running is False

    def test_backend_server_start_with_api_key(self):
        from core import BackendServer
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="test-key", base_url="https://api.deepseek.com")
        
        assert server._client is not None
        assert server._config["api_key"] == "test-key"
        
        server.shutdown()


class TestBackendClientCreation:
    """测试 BackendClient 创建"""
    
    def test_backend_client_init(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        client = BackendClient(server)
        
        assert client._server is server
        assert client._counter == 0


class TestBackendClientAPI:
    """测试 BackendClient API"""
    
    def test_get_status(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        result = client.get_status()
        assert result.get("success") is True
        data = result.get("data", {})
        assert data.get("running") is True
        
        server.shutdown()

    def test_update_settings(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        result = client.update_settings(
            api_config={"api_key": "new-key", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash"},
            tool_limits={"persona_update_max": 2}
        )
        assert result.get("success") is True
        
        server.shutdown()

    def test_get_settings(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="test-key")
        client = BackendClient(server)
        
        result = client.get_settings()
        assert result.get("success") is True
        data = result.get("data", {})
        assert data.get("api_config", {}).get("api_key") == "test-key"
        
        server.shutdown()

    def test_process_message_no_api_key(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        # 无 API key 应该返回错误（success 为 False）
        result = client.process_message("hello")
        # 由于 API 调用失败，success 应该是 False
        assert result.get("success") is False
        
        server.shutdown()

    def test_execute_tool(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        result = client.execute_tool("memory_introspect", {})
        assert result.get("success") is True
        
        server.shutdown()

    def test_clear_history(self):
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        # 先保存一些历史
        client.save_history([
            {"role": "user", "content": "test message 1"},
            {"role": "assistant", "content": "test response 1"}
        ])
        
        # 验证历史已保存
        history = client.get_history()
        assert len(history) >= 2
        
        # 清空历史
        result = client.clear_history()
        assert result.get("status") == "history_cleared"
        
        # 验证历史已清空
        history = client.get_history()
        assert len(history) == 0
        
        server.shutdown()

    def test_send_message_is_alias(self):
        """测试 send 方法是 process_message 的别名"""
        from core import BackendServer, BackendClient
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        server.start(api_key="")
        client = BackendClient(server)
        
        # send 方法应该等同于 process_message
        # 由于没有真实 API key，应该返回失败
        result = client.send("test")
        assert result.get("success") is False
        
        server.shutdown()



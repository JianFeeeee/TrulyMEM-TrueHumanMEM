import pytest
import os
import tempfile
import time
import threading
import queue

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestPacketTypeEnum:
    """测试 PacketType 枚举"""
    
    def test_packet_type_process_message_exists(self):
        from core import PacketType
        assert PacketType.PROCESS_MESSAGE is not None
        assert PacketType.PROCESS_MESSAGE.value == "process_message"

    def test_packet_type_execute_tool_exists(self):
        from core import PacketType
        assert PacketType.EXECUTE_TOOL is not None
        assert PacketType.EXECUTE_TOOL.value == "execute_tool"

    def test_packet_type_get_status_exists(self):
        from core import PacketType
        assert PacketType.GET_STATUS is not None
        assert PacketType.GET_STATUS.value == "get_status"

    def test_packet_type_get_settings_exists(self):
        from core import PacketType
        assert PacketType.GET_SETTINGS is not None
        assert PacketType.GET_SETTINGS.value == "get_settings"

    def test_packet_type_set_settings_exists(self):
        from core import PacketType
        assert PacketType.SET_SETTINGS is not None
        assert PacketType.SET_SETTINGS.value == "set_settings"

    def test_packet_type_get_history_exists(self):
        from core import PacketType
        assert PacketType.GET_HISTORY is not None
        assert PacketType.GET_HISTORY.value == "get_history"

    def test_packet_type_save_history_exists(self):
        from core import PacketType
        assert PacketType.SAVE_HISTORY is not None
        assert PacketType.SAVE_HISTORY.value == "save_history"

    def test_packet_type_shutdown_exists(self):
        from core import PacketType
        assert PacketType.SHUTDOWN is not None
        assert PacketType.SHUTDOWN.value == "shutdown"

    def test_packet_type_all_values(self):
        from core import PacketType
        values = [pt.value for pt in PacketType]
        assert "process_message" in values
        assert "execute_tool" in values
        assert "get_status" in values
        assert "get_settings" in values
        assert "set_settings" in values
        assert "get_history" in values
        assert "save_history" in values
        assert "shutdown" in values
        assert len(values) == 8


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
            api_config={"api_key": "new-key", "base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
            tool_limits={"persona_query_max": 2}
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


class TestToolLimiter:
    """测试工具限制器"""
    
    def test_tool_limiter_init(self):
        from core.tool_limiter import ToolLimiter
        limiter = ToolLimiter()
        assert limiter.counts.persona_query == 0
        assert limiter.counts.persona_update == 0

    def test_tool_limiter_classify(self):
        from core.tool_limiter import ToolLimiter
        limiter = ToolLimiter()
        
        category, operation = limiter._classify_tool("memory_recall", {"query_intent": "test"})
        assert category == "memory"
        assert operation == "query"
        
        category, operation = limiter._classify_tool("persona_update", {})
        assert category == "persona"
        assert operation == "update"
        
        category, operation = limiter._classify_tool("task_create", {})
        assert category == "task"
        assert operation == "update"

    def test_tool_limiter_can_call(self):
        from core.tool_limiter import ToolLimiter
        limiter = ToolLimiter()
        
        allowed, reason = limiter.can_call("persona_update", {})
        assert allowed is True
        
        limiter.record_call("persona_update", {})
        allowed, reason = limiter.can_call("persona_update", {})
        assert allowed is False
        assert "已达上限" in reason

    def test_tool_limiter_reset(self):
        from core.tool_limiter import ToolLimiter
        limiter = ToolLimiter()
        
        limiter.record_call("persona_update", {})
        assert limiter.counts.persona_update == 1
        
        limiter.reset()
        assert limiter.counts.persona_update == 0


class TestEmbeddedGraphDB:
    """测试图数据库"""
    
    def test_embedded_db_init(self):
        from core.embedded_db import EmbeddedGraphDB
        db = EmbeddedGraphDB(db_path=":memory:")
        assert db.conn is not None
        db.close()

    def test_embedded_db_commit_and_recall(self):
        from core.embedded_db import EmbeddedGraphDB
        db = EmbeddedGraphDB(db_path=":memory:")
        
        # 写入记忆 (使用 triplets 参数)
        result = db.commit(
            triplets=[
                {"subject": "测试", "relation": "是", "object": "test"}
            ],
            session_id="test-session"
        )
        
        # 读取记忆
        results = db.recall("测试")
        assert len(results.get("entities", [])) > 0
        
        db.close()
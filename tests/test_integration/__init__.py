import pytest
import os
import tempfile

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestIntegrationPacketFlow:
    """测试 Packet 通信流程"""
    
    def test_packet_round_trip_process_message(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            # 无 API key 时应该返回错误而非抛异常
            result = client.process_message("test message")
            assert result.get("success") is False
            assert "error" in result
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_packet_round_trip_config(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            result = client.update_config(api_key="test-api", base_url="https://test.com")
            assert result.get("success") is True
            
            status = client.get_status()
            data = status.get("data", {})
            assert data.get("config", {}).get("api_key") == "test-api"
            assert data.get("config", {}).get("base_url") == "https://test.com"
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_packet_round_trip_status(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            result = client.get_status()
            assert result.get("success") is True
            data = result.get("data", {})
            assert data.get("running") is True
            assert data.get("graph_initialized") is True
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_packet_round_trip_execute_tool(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            result = client.execute_tool("memory_introspect", {})
            assert result.get("success") is True
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationToolLimiter:
    """测试工具限制器集成"""
    
    def test_external_tool_call_not_limited(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            # 外部调用多次应该成功
            for i in range(5):
                result = client.execute_tool("memory_introspect", {})
                assert result.get("success") is True
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_internal_tool_call_limited(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="fake-key")  # 假 key 会失败但不影响测试
            client = BackendClient(server)
            
            # 内部调用受限，tool_limiter 存在
            assert server._tool_limiter is not None
            
            # 初始状态
            assert server._tool_limiter.counts.persona_update == 0
            
            # 记录一次调用
            server._tool_limiter.record_call("persona_update", {})
            assert server._tool_limiter.counts.persona_update == 1
            
            # 再次调用应该被拒绝
            allowed, reason = server._tool_limiter.can_call("persona_update", {})
            assert allowed is False
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationErrorHandling:
    """测试错误处理"""
    
    def test_process_message_returns_error_not_raise(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            # 应该返回错误，而不是抛出异常
            result = client.process_message("hello")
            assert result.get("success") is False
            assert "error" in result
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_execute_tool_error_handling(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            # 不存在的工具应该返回错误
            result = client.execute_tool("nonexistent_tool", {})
            assert result.get("success") is False
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
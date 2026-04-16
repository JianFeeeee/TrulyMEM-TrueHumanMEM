"""Integration tests - Packet flow, tool limiter, and error handling across layers."""
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

            result = client.update_settings(
                api_config={"api_key": "test-api", "base_url": "https://test.com"},
            )
            assert result.get("success") is True

            settings = client.get_settings()
            data = settings.get("data", {})
            assert data.get("api_config", {}).get("api_key") == "test-api"
            assert data.get("api_config", {}).get("base_url") == "https://test.com"

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

            for i in range(5):
                result = client.execute_tool("memory_introspect", {})
                assert result.get("success") is True

            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_internal_tool_call_limited(self):
        from core.tool_limiter import ToolLimiter, ToolLimits
        limiter = ToolLimiter(ToolLimits(persona_update_max=1))

        assert limiter.counts.persona_update == 0

        limiter.record_call("persona_update", {})
        assert limiter.counts.persona_update == 1

        allowed, reason = limiter.can_call("persona_update", {})
        assert allowed is False
        assert "已达上限" in reason


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

            result = client.execute_tool("nonexistent_tool", {})
            data = result.get("data", {})
            assert "未知工具" in data.get("result", "")

            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

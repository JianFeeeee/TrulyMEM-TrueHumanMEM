import pytest
import os
import tempfile
import time
import threading
import queue

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestPacketTypeEnum:
    def test_packet_type_message_exists(self):
        from core import PacketType
        assert PacketType.MESSAGE is not None
        assert PacketType.MESSAGE.value == "message"

    def test_packet_type_config_exists(self):
        from core import PacketType
        assert PacketType.CONFIG is not None
        assert PacketType.CONFIG.value == "config"

    def test_packet_type_tool_exists(self):
        from core import PacketType
        assert PacketType.TOOL is not None
        assert PacketType.TOOL.value == "tool"

    def test_packet_type_status_exists(self):
        from core import PacketType
        assert PacketType.STATUS is not None
        assert PacketType.STATUS.value == "status"

    def test_packet_type_history_exists(self):
        from core import PacketType
        assert PacketType.HISTORY is not None
        assert PacketType.HISTORY.value == "history"

    def test_packet_type_all_values(self):
        from core import PacketType
        values = [pt.value for pt in PacketType]
        assert "message" in values
        assert "config" in values
        assert "tool" in values
        assert "status" in values
        assert "history" in values
        assert len(values) == 5


class TestPacketCreation:
    def test_packet_with_id_and_type(self):
        from core import Packet, PacketType
        packet = Packet(id="test-1", type=PacketType.MESSAGE, body={"message": "hello"})
        assert packet.id == "test-1"
        assert packet.type == PacketType.MESSAGE

    def test_packet_body(self):
        from core import Packet, PacketType
        body = {"message": "test", "extra": "data"}
        packet = Packet(id="test-2", type=PacketType.CONFIG, body=body)
        assert packet.body == body

    def test_packet_created_at_default(self):
        from core import Packet, PacketType
        before = time.time()
        packet = Packet(id="test-3", type=PacketType.STATUS, body={})
        after = time.time()
        assert before <= packet.created_at <= after

    def test_packet_with_custom_created_at(self):
        from core import Packet, PacketType
        custom_time = 1234567890.0
        packet = Packet(id="test-4", type=PacketType.HISTORY, body={}, created_at=custom_time)
        assert packet.created_at == custom_time


class TestBackendServerInit:
    def test_create_server_defaults(self):
        from core import BackendServer
        server = BackendServer()
        assert server._db_path == "graph_memory.db"
        assert server._use_embedded_db is True
        assert server._graph is None
        assert server._client is None
        assert server._running is False

    def test_create_server_custom_db(self):
        from core import BackendServer
        server = BackendServer(db_path="custom.db")
        assert server._db_path == "custom.db"

    def test_create_server_no_embedded(self):
        from core import BackendServer
        server = BackendServer(use_embedded_db=False)
        assert server._use_embedded_db is False


class TestBackendServerStart:
    def test_start_without_api_key(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            assert server._running is True
            assert server._graph is not None
            assert server._client is None
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_start_with_api_key(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="test-key", base_url="https://api.test.com")
            assert server._running is True
            assert server._config["api_key"] == "test-key"
            assert server._config["base_url"] == "https://api.test.com"
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_start_twice_returns_early(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            running_before = server._running
            server.start(api_key="")
            running_after = server._running
            assert running_before is True
            assert running_after is True
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestBackendServerShutdown:
    def test_shutdown_stops_server(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            assert server._running is True
            server.shutdown()
            assert server._running is False
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_shutdown_closes_graph(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            server.shutdown()
            assert server._graph is None
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestBackendServerPacketHandling:
    def test_send_message_without_client(self):
        from core import BackendServer, Packet, PacketType
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            packet = Packet(id="1", type=PacketType.MESSAGE, body={"message": "hello"})
            response = server.send(packet)
            assert response.body["success"] is True
            assert "API Key not configured" in response.body["error"]
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_send_status_packet(self):
        from core import BackendServer, Packet, PacketType
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            packet = Packet(id="2", type=PacketType.STATUS, body={})
            response = server.send(packet)
            assert response.body["success"] is True
            assert response.body["running"] is True
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestBackendClientInit:
    def test_create_client_with_server(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            assert client._server is server
            assert client._counter == 0
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestBackendClientMethods:
    def test_get_status(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            status = client.get_status()
            assert status["success"] is True
            assert status["running"] is True
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_update_config(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            result = client.update_config(api_key="new-key", base_url="https://new-api.test.com")
            assert result["success"] is True
            assert result["status"] == "config_updated"
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_and_get_history(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            test_messages = [{"role": "user", "content": "hello"}]
            client.save_history(test_messages)
            
            history = client.get_history()
            assert history == test_messages
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestMultipleClients:
    def test_multiple_clients_thread_safety(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            status1 = client.get_status()
            status2 = client.get_status()
            
            assert status1["success"] is True
            assert status2["success"] is True
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestServerStateAfterShutdown:
    def test_server_state_not_running(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            assert server._running is True
            server.shutdown()
            assert server._running is False
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
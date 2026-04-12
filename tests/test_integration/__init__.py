import pytest
import os
import tempfile

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestIntegrationPacketFlow:
    def test_packet_round_trip_message(self):
        from core import BackendServer, BackendClient, Packet, PacketType
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            result = client.send_message("test message")
            assert result["success"] is True
            assert "API Key not configured" in result.get("error", "")
            
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
            assert result["success"] is True
            assert result["status"] == "config_updated"
            
            status = client.get_status()
            assert status["config"]["api_key"] == "test-api"
            assert status["config"]["base_url"] == "https://test.com"
            
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
            
            status = client.get_status()
            assert status["success"] is True
            assert status["running"] is True
            assert status["client_ready"] is False
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_packet_round_trip_history(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            messages = [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi there"}
            ]
            client.save_history(messages)
            
            retrieved = client.get_history()
            assert retrieved == messages
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationSequentialOperations:
    def test_sequential_config_updates(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            client.update_config(api_key="key1", base_url="https://api1.com")
            status1 = client.get_status()
            assert status1["config"]["api_key"] == "key1"
            
            client.update_config(api_key="key2", base_url="https://api2.com")
            status2 = client.get_status()
            assert status2["config"]["api_key"] == "key2"
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_save_history_override(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            client.save_history([{"role": "user", "content": "first"}])
            history1 = client.get_history()
            assert len(history1) == 1
            
            client.save_history([{"role": "user", "content": "second"}])
            history2 = client.get_history()
            assert len(history2) == 1
            assert history2[0]["content"] == "second"
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationMultipleClients:
    def test_two_clients_same_server(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            
            client1 = BackendClient(server)
            client2 = BackendClient(server)
            
            status1 = client1.get_status()
            status2 = client2.get_status()
            
            assert status1["success"] is True
            assert status2["success"] is True
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationDatabase:
    def test_server_creates_database(self):
        from core import BackendServer
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            
            assert os.path.exists(db_path)
            
            server.shutdown()
            assert os.path.exists(db_path)

    def test_server_persists_across_restart(self):
        from core import BackendServer, BackendClient
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "persist.db")
            
            server1 = BackendServer(db_path=db_path, use_embedded_db=True)
            server1.start(api_key="")
            server1.shutdown()
            
            server2 = BackendServer(db_path=db_path, use_embedded_db=True)
            server2.start(api_key="")
            assert os.path.exists(db_path)
            server2.shutdown()


class TestIntegrationEntryPoint:
    def test_entry_import(self):
        import trulymem_entry
        assert trulymem_entry is not None

    def test_entry_has_main(self):
        import trulymem_entry
        assert hasattr(trulymem_entry, 'main')
        assert callable(trulymem_entry.main)


class TestIntegrationAllPacketTypes:
    def test_message_type_string(self):
        from core import PacketType
        assert PacketType.MESSAGE.value == "message"

    def test_config_type_string(self):
        from core import PacketType
        assert PacketType.CONFIG.value == "config"

    def test_tool_type_string(self):
        from core import PacketType
        assert PacketType.TOOL.value == "tool"

    def test_status_type_string(self):
        from core import PacketType
        assert PacketType.STATUS.value == "status"

    def test_history_type_string(self):
        from core import PacketType
        assert PacketType.HISTORY.value == "history"


class TestIntegrationErrorHandling:
    def test_timeout_on_slow_response(self):
        from core import BackendServer, Packet, PacketType
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            server._running = False
            
            packet = Packet(id="timeout-test", type=PacketType.MESSAGE, body={"message": "test"})
            
            original_timeout = 30.0
            server.send = lambda p, timeout=original_timeout: (
                setattr(server, '_running', True),
                server.send(p)
            )[1]
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestIntegrationFullWorkflow:
    def test_complete_workflow(self):
        from core import BackendServer, BackendClient
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="")
            client = BackendClient(server)
            
            status_before = client.get_status()
            assert status_before["success"] is True
            
            client.update_config(api_key="workflow-key", base_url="https://workflow.com")
            status_after_config = client.get_status()
            assert status_after_config["config"]["api_key"] == "workflow-key"
            
            history = [{"role": "user", "content": "test workflow"}]
            client.save_history(history)
            retrieved_history = client.get_history()
            assert retrieved_history == history
            
            message_result = client.send_message("test")
            assert message_result["success"] is True
            
            server.shutdown()
            status_after_shutdown = client.get_status()
            assert status_after_shutdown["running"] is False
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
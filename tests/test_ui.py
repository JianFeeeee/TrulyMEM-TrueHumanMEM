import pytest
import os
import tempfile

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestUIImport:
    def test_import_app(self):
        from ui import GraphMemoryApp
        assert GraphMemoryApp is not None


class TestUIApp:
    def test_create_app_without_backend(self):
        from ui import GraphMemoryApp
        app = GraphMemoryApp()
        assert app is not None
        assert app._backend_server is None
        assert app._backend_client is None

    def test_create_app_with_backend(self):
        from ui import GraphMemoryApp
        from core import BackendServer
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="", base_url="https://api.test.com")
            
            app = GraphMemoryApp(backend_server=server)
            
            assert app._backend_server is server
            assert app._backend_client is not None
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestAppConfig:
    def test_config_from_env(self):
        from ui import AppConfig
        config = AppConfig.from_env()
        assert config is not None

    def test_config_default_values(self):
        from ui import AppConfig
        config = AppConfig()
        assert config.api_key == ""
        assert config.model == "deepseek-chat"
        assert config.base_url == "https://api.deepseek.com"


class TestPacketProtocol:
    def test_import_packet(self):
        from core import Packet, PacketType
        assert Packet is not None
        assert PacketType is not None

    def test_packet_creation(self):
        from core import Packet, PacketType
        packet = Packet(id="test-1", type=PacketType.MESSAGE, body={"message": "hello"})
        assert packet.id == "test-1"
        assert packet.type == PacketType.MESSAGE
        assert packet.body["message"] == "hello"
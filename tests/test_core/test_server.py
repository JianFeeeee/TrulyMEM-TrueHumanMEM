import pytest
import os
import tempfile

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestCoreImport:
    def test_import_backend_server(self):
        from core import BackendServer
        assert BackendServer is not None

    def test_import_backend_client(self):
        from core import BackendClient
        assert BackendClient is not None

    def test_import_embedded_db(self):
        from core import EmbeddedGraphDB
        assert EmbeddedGraphDB is not None


class TestBackendServer:
    def test_create_server(self):
        from core import BackendServer
        server = BackendServer(db_path=":memory:", use_embedded_db=True)
        assert server is not None
        assert server._running is False

    def test_start_server(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            server = BackendServer(db_path=db_path, use_embedded_db=True)
            server.start(api_key="", base_url="https://api.test.com")
            
            assert server._running is True
            assert server._graph is not None
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_shutdown(self):
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        server = BackendServer(db_path=db_path, use_embedded_db=True)
        server.start(api_key="", base_url="https://api.test.com")
        
        assert server._running is True
        
        server.shutdown()
        assert server._running is False
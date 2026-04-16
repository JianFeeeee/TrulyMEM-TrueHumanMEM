import pytest
import os
import tempfile
from pathlib import Path

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestUIImport:
    """测试 UI 模块导入"""
    
    def test_import_graphmemoryapp(self):
        from ui import GraphMemoryApp
        assert GraphMemoryApp is not None

    def test_import_appconfig(self):
        from ui import AppConfig
        assert AppConfig is not None

    def test_import_message(self):
        from ui.models.message import Message, ToolCall, ToolResult
        assert Message is not None
        assert ToolCall is not None
        assert ToolResult is not None

    def test_import_config(self):
        from ui.models.config import AppConfig
        assert AppConfig is not None

    def test_import_log_entry(self):
        from ui.models.log_entry import LogEntry
        assert LogEntry is not None


class TestAppConfig:
    """测试配置模型"""
    
    def test_config_default_values(self):
        from ui.models.config import AppConfig
        config = AppConfig()
        assert config.api_key == ""
        assert config.model == "deepseek-chat"
        assert config.base_url == "https://api.deepseek.com"

    def test_config_from_env(self):
        from ui.models.config import AppConfig
        config = AppConfig.from_env()
        assert "fake-test-key" in config.api_key


class TestMessageModel:
    """测试消息模型"""
    
    def test_message_creation_user(self):
        from ui.models.message import Message
        from datetime import datetime
        msg = Message(role="user", content="test content")
        assert msg.role == "user"
        assert msg.content == "test content"
        assert isinstance(msg.timestamp, datetime)

    def test_message_creation_assistant(self):
        from ui.models.message import Message
        msg = Message(role="assistant", content="assistant response")
        assert msg.role == "assistant"

    def test_message_with_tool_calls(self):
        from ui.models.message import Message, ToolCall
        tc = ToolCall(id="call-1", name="memory_recall", arguments={"query": "test"})
        msg = Message(role="assistant", content="response", tool_calls=[tc])
        assert msg.tool_calls is not None
        assert len(msg.tool_calls) == 1


class TestAppCSSPath:
    """测试 App CSS 配置"""
    
    def test_app_has_css_path(self):
        from ui import GraphMemoryApp
        assert hasattr(GraphMemoryApp, 'CSS_PATH')
        assert len(GraphMemoryApp.CSS_PATH) > 0


class TestAppBindings:
    """测试 App 快捷键"""
    
    def test_app_has_bindings(self):
        from ui import GraphMemoryApp
        assert hasattr(GraphMemoryApp, 'BINDINGS')
        assert len(GraphMemoryApp.BINDINGS) > 0


class TestWidgetImports:
    """测试组件导入"""
    
    def test_import_left_panel(self):
        from ui.widgets.left_panel import LeftPanel
        assert LeftPanel is not None

    def test_import_right_panel(self):
        from ui.widgets.right_panel import RightPanel
        assert RightPanel is not None

    def test_import_input_box(self):
        from ui.widgets.input_box import InputBox
        assert InputBox is not None

    def test_import_message_history(self):
        from ui.widgets.message_history import MessageHistory
        assert MessageHistory is not None

    def test_import_status_bar(self):
        from ui.widgets.status_bar import StatusBar
        assert StatusBar is not None


class TestHandlerImports:
    """测试处理器导入"""
    
    def test_import_focus_handler(self):
        from ui.handlers.focus_handler import FocusHandler
        assert FocusHandler is not None

    def test_import_key_handler(self):
        from ui.handlers.key_handler import KeyHandler
        assert KeyHandler is not None


class TestServiceImports:
    """测试服务导入"""
    
    def test_import_config_service(self):
        from ui.services.config_service import ConfigService
        assert ConfigService is not None

    def test_import_config_manager(self):
        from ui.services.config_manager import ConfigManager
        assert ConfigManager is not None


class TestAppInitialization:
    """测试 App 初始化"""
    
    def test_app_without_backend(self):
        from ui import GraphMemoryApp
        app = GraphMemoryApp()
        assert app._backend_server is None
        assert app._backend_client is None

    def test_app_with_backend(self):
        from ui import GraphMemoryApp
        from core import BackendServer
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            app = GraphMemoryApp(backend_server=server)
            assert app._backend_server is server
            assert app._backend_client is not None
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestUIWithBackendClient:
    """测试 UI 与后端通信"""
    
    def test_app_sends_message_via_backend_client(self):
        from ui import GraphMemoryApp
        from core import BackendServer, BackendClient
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            
            app = GraphMemoryApp(backend_server=server)
            client = app._backend_client
            
            status = client.get_status()
            assert status.get("success") is True
            
            result = client.update_settings(
                api_config={"api_key": "sk-test", "base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
                tool_limits={"persona_update_max": 1}
            )
            assert result.get("success") is True
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_ui_get_history(self):
        from ui import GraphMemoryApp
        from core import BackendServer
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            
            app = GraphMemoryApp(backend_server=server)
            client = app._backend_client
            
            history = client.get_history()
            assert isinstance(history, list)
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_ui_only_uses_backend_client(self):
        from ui import GraphMemoryApp
        from core import BackendServer
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            server = BackendServer(db_path=db_path)
            server.start(api_key="")
            
            app = GraphMemoryApp(backend_server=server)
            
            # UI 不应该直接访问后端内部
            assert hasattr(app, '_backend_client')
            assert app._backend_client is not None
            
            # 不应该有 _graph, _client 等直接访问
            assert not hasattr(app, '_graph')
            assert not hasattr(app, '_client')
            
            server.shutdown()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
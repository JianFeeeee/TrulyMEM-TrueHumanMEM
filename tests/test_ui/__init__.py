import pytest
import os
import tempfile
from pathlib import Path

os.environ["DEEPSEEK_API_KEY"] = "fake-test-key"


class TestUIImportFull:
    def test_import_graphmemoryapp(self):
        from ui import GraphMemoryApp
        assert GraphMemoryApp is not None

    def test_import_appconfig(self):
        from ui import AppConfig
        assert AppConfig is not None

    def test_import_from_models(self):
        from ui.models.message import Message, ToolCall, ToolResult
        assert Message is not None
        assert ToolCall is not None
        assert ToolResult is not None

    def test_import_from_models_config(self):
        from ui.models.config import AppConfig
        assert AppConfig is not None

    def test_import_from_models_log_entry(self):
        from ui.models.log_entry import LogEntry
        assert LogEntry is not None

    def test_import_from_widgets(self):
        from ui.widgets.left_panel import LeftPanel
        from ui.widgets.right_panel import RightPanel
        from ui.widgets.input_box import InputBox
        from ui.widgets.message_history import MessageHistory
        from ui.widgets.status_bar import StatusBar
        assert LeftPanel is not None
        assert RightPanel is not None
        assert InputBox is not None
        assert MessageHistory is not None
        assert StatusBar is not None

    def test_import_from_handlers(self):
        from ui.handlers.focus_handler import FocusHandler
        from ui.handlers.key_handler import KeyHandler
        from ui.handlers.message_handler import MessageHandler
        assert FocusHandler is not None
        assert KeyHandler is not None
        assert MessageHandler is not None

    def test_import_from_services(self):
        from ui.services.config_manager import ConfigManager
        from ui.services.config_service import ConfigService
        from ui.services.chat_service import ChatService
        from ui.services.tool_service import ToolService
        assert ConfigManager is not None
        assert ConfigService is not None
        assert ChatService is not None
        assert ToolService is not None


class TestAppConfigFull:
    def test_config_default_values(self):
        from ui.models.config import AppConfig
        config = AppConfig()
        assert config.api_key == ""
        assert config.model == "deepseek-chat"
        assert config.base_url == "https://api.deepseek.com"

    def test_config_from_env_with_key(self):
        from ui.models.config import AppConfig
        config = AppConfig.from_env()
        assert "fake-test-key" in config.api_key

    def test_config_from_env_custom(self):
        os.environ["DEEPSEEK_API_KEY"] = "my-key"
        os.environ["MODEL_NAME"] = "my-model"
        os.environ["DEEPSEEK_BASE_URL"] = "https://my-api.com"
        
        from ui.models.config import AppConfig
        config = AppConfig.from_env()
        
        assert config.api_key == "my-key"
        assert config.model == "my-model"
        assert config.base_url == "https://my-api.com"


class TestMessageModelFull:
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
        assert msg.content == "assistant response"

    def test_message_with_tool_calls(self):
        from ui.models.message import Message, ToolCall
        tc = ToolCall(id="call-1", name="memory_recall", arguments={"query": "test"})
        msg = Message(role="assistant", content="response", tool_calls=[tc])
        assert msg.role == "assistant"
        assert msg.tool_calls is not None
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].name == "memory_recall"

    def test_message_with_tool_results(self):
        from ui.models.message import Message, ToolResult
        tr = ToolResult(tool_call_id="call-1", name="memory_recall", arguments={}, result="result", success=True)
        msg = Message(role="assistant", content="response", tool_results=[tr])
        assert msg.tool_results is not None
        assert len(msg.tool_results) == 1
        assert msg.tool_results[0].success is True


class TestToolCallModelFull:
    def test_toolcall_creation(self):
        from ui.models.message import ToolCall
        tc = ToolCall(id="call-1", name="memory_recall", arguments={"query": "test"})
        assert tc.id == "call-1"
        assert tc.name == "memory_recall"
        assert tc.arguments["query"] == "test"


class TestToolResultModelFull:
    def test_toolresult_creation_success(self):
        from ui.models.message import ToolResult
        tr = ToolResult(tool_call_id="call-1", name="memory_recall", arguments={}, result="success result", success=True)
        assert tr.tool_call_id == "call-1"
        assert tr.name == "memory_recall"
        assert tr.success is True
        assert tr.result == "success result"

    def test_toolresult_creation_failure(self):
        from ui.models.message import ToolResult
        tr = ToolResult(tool_call_id="call-1", name="memory_recall", arguments={}, result="error", success=False)
        assert tr.success is False
        assert tr.result == "error"


class TestLogEntryModelFull:
    def test_logentry_creation(self):
        from ui.models.log_entry import LogEntry
        from datetime import datetime
        entry = LogEntry(
            timestamp=datetime.now(),
            tool_name="memory_recall",
            arguments={"query": "test"},
            result="result",
            duration=0.5
        )
        assert entry.tool_name == "memory_recall"
        assert entry.duration == 0.5

    def test_logentry_args_summary(self):
        from ui.models.log_entry import LogEntry
        from datetime import datetime
        entry = LogEntry(
            timestamp=datetime.now(),
            tool_name="memory_recall",
            arguments={"query": "test query with many characters"},
            result="result",
            duration=0.5
        )
        summary = entry.args_summary
        assert isinstance(summary, str)
        assert "query" in summary

    def test_logentry_result_summary(self):
        from ui.models.log_entry import LogEntry
        from datetime import datetime
        entry = LogEntry(
            timestamp=datetime.now(),
            tool_name="memory_recall",
            arguments={},
            result="a" * 200,
            duration=0.5
        )
        summary = entry.result_summary
        assert len(summary) <= 103


class TestAppCSSPathFull:
    def test_app_has_css_path(self):
        from ui import GraphMemoryApp
        assert hasattr(GraphMemoryApp, 'CSS_PATH')
        assert len(GraphMemoryApp.CSS_PATH) > 0

    def test_css_path_are_paths(self):
        from ui import GraphMemoryApp
        for path in GraphMemoryApp.CSS_PATH:
            assert isinstance(path, Path)


class TestAppBindingsFull:
    def test_app_has_bindings(self):
        from ui import GraphMemoryApp
        assert hasattr(GraphMemoryApp, 'BINDINGS')
        assert len(GraphMemoryApp.BINDINGS) > 0

    def test_bindings_have_required_keys(self):
        from ui import GraphMemoryApp
        for binding in GraphMemoryApp.BINDINGS:
            assert hasattr(binding, 'key')
            assert hasattr(binding, 'action')


class TestWidgetImportsFull:
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

    def test_import_message_widget(self):
        from ui.widgets.message_widget import MessageWidget
        assert MessageWidget is not None

    def test_import_status_bar(self):
        from ui.widgets.status_bar import StatusBar
        assert StatusBar is not None

    def test_import_config_section(self):
        from ui.widgets.config_section import ConfigSection
        assert ConfigSection is not None

    def test_import_operation_log(self):
        from ui.widgets.operation_log import OperationLog
        assert OperationLog is not None

    def test_import_cypher_query_box(self):
        from ui.widgets.cypher_query_box import CypherQueryBox
        assert CypherQueryBox is not None


class TestHandlerImportsFull:
    def test_import_focus_handler(self):
        from ui.handlers.focus_handler import FocusHandler
        assert FocusHandler is not None

    def test_import_key_handler(self):
        from ui.handlers.key_handler import KeyHandler
        assert KeyHandler is not None

    def test_import_message_handler(self):
        from ui.handlers.message_handler import MessageHandler
        assert MessageHandler is not None


class TestServiceImportsFull:
    def test_import_config_manager(self):
        from ui.services.config_manager import ConfigManager
        assert ConfigManager is not None

    def test_import_config_service(self):
        from ui.services.config_service import ConfigService
        assert ConfigService is not None

    def test_import_chat_service(self):
        from ui.services.chat_service import ChatService
        assert ChatService is not None

    def test_import_tool_service(self):
        from ui.services.tool_service import ToolService
        assert ToolService is not None


class TestAppInitializationFull:
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


class TestConfigManagerFull:
    def test_config_manager_creation(self):
        from ui.services.config_manager import ConfigManager
        cm = ConfigManager()
        assert cm is not None

    def test_config_manager_config_path(self):
        from ui.services.config_manager import ConfigManager
        cm = ConfigManager()
        assert cm._config_path is not None

    def test_config_manager_exists_false(self):
        from ui.services.config_manager import ConfigManager
        cm = ConfigManager()
        assert cm.exists() is False
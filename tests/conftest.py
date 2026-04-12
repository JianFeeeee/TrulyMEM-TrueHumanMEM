import pytest
from datetime import datetime
from ui.models.message import Message, ToolCall, ToolResult
from ui.models.config import AppConfig
from ui.models.log_entry import LogEntry


@pytest.fixture
def sample_config():
    return AppConfig(
        api_key="test-api-key",
        model="test-model",
        base_url="https://test.api.com"
    )


@pytest.fixture
def sample_message():
    return Message(
        role="user",
        content="测试消息",
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_tool_call():
    return ToolCall(
        id="test-call-id",
        name="memory_recall",
        arguments={"query_intent": "测试查询"}
    )


@pytest.fixture
def sample_tool_result():
    return ToolResult(
        tool_call_id="test-call-id",
        name="memory_recall",
        arguments={"query_intent": "测试查询"},
        result="测试结果",
        success=True
    )


@pytest.fixture
def sample_log_entry():
    return LogEntry(
        timestamp=datetime.now(),
        tool_name="memory_recall",
        arguments={"query_intent": "测试查询"},
        result="测试结果",
        duration=0.5
    )
"""测试配置"""

import pytest
from datetime import datetime
from graph_memory_tui.models.message import Message, ToolCall, ToolResult
from graph_memory_tui.models.config import AppConfig
from graph_memory_tui.models.log_entry import LogEntry


@pytest.fixture
def sample_config():
    """示例配置"""
    return AppConfig(
        api_key="test-api-key",
        model="test-model",
        base_url="https://test.api.com"
    )


@pytest.fixture
def sample_message():
    """示例消息"""
    return Message(
        role="user",
        content="测试消息",
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_tool_call():
    """示例工具调用"""
    return ToolCall(
        id="test-call-id",
        name="memory_recall",
        arguments={"query_intent": "测试查询"}
    )


@pytest.fixture
def sample_tool_result():
    """示例工具结果"""
    return ToolResult(
        tool_call_id="test-call-id",
        name="memory_recall",
        arguments={"query_intent": "测试查询"},
        result="测试结果",
        success=True
    )


@pytest.fixture
def sample_log_entry():
    """示例日志条目"""
    return LogEntry(
        timestamp=datetime.now(),
        tool_name="memory_recall",
        arguments={"query_intent": "测试查询"},
        result="测试结果",
        duration=0.5
    )

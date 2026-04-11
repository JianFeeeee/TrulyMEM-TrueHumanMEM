"""数据模型测试"""

import pytest
from datetime import datetime
from graph_memory_tui.models.message import Message, ToolCall, ToolResult
from graph_memory_tui.models.config import AppConfig
from graph_memory_tui.models.log_entry import LogEntry


def test_message_creation(sample_message):
    """测试消息创建"""
    assert sample_message.role == "user"
    assert sample_message.content == "测试消息"
    assert isinstance(sample_message.timestamp, datetime)


def test_message_with_tool_calls():
    """测试带工具调用的消息"""
    tool_call = ToolCall(
        id="test-id",
        name="memory_recall",
        arguments={"query_intent": "测试"}
    )

    message = Message(
        role="assistant",
        content="测试回复",
        tool_calls=[tool_call]
    )

    assert message.role == "assistant"
    assert message.tool_calls is not None
    assert len(message.tool_calls) == 1
    assert message.tool_calls[0].name == "memory_recall"


def test_tool_call_creation(sample_tool_call):
    """测试工具调用创建"""
    assert sample_tool_call.id == "test-call-id"
    assert sample_tool_call.name == "memory_recall"
    assert sample_tool_call.arguments == {"query_intent": "测试查询"}


def test_tool_result_creation(sample_tool_result):
    """测试工具结果创建"""
    assert sample_tool_result.tool_call_id == "test-call-id"
    assert sample_tool_result.success is True
    assert sample_tool_result.result == "测试结果"


def test_config_creation(sample_config):
    """测试配置创建"""
    assert sample_config.api_key == "test-api-key"
    assert sample_config.model == "test-model"
    assert sample_config.base_url == "https://test.api.com"


def test_config_from_env():
    """测试从环境变量加载配置"""
    import os
    os.environ["DEEPSEEK_API_KEY"] = "env-api-key"
    os.environ["MODEL_NAME"] = "env-model"

    config = AppConfig.from_env()
    assert config.api_key == "env-api-key"
    assert config.model == "env-model"


def test_log_entry_creation(sample_log_entry):
    """测试日志条目创建"""
    assert sample_log_entry.tool_name == "memory_recall"
    assert sample_log_entry.duration == 0.5


def test_log_entry_summary(sample_log_entry):
    """测试日志条目摘要"""
    args_summary = sample_log_entry.args_summary
    result_summary = sample_log_entry.result_summary

    assert isinstance(args_summary, str)
    assert isinstance(result_summary, str)
    assert len(args_summary) <= 53  # 50 + "..."
    assert len(result_summary) <= 103  # 100 + "..."

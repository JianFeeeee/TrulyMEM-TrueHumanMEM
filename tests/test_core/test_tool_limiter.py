"""工具限制器测试"""

import pytest
from graph_memory_tui.core.tools.tool_limiter import (
    ToolLimiter,
    ToolLimits,
    ToolCallCount
)


@pytest.fixture
def limiter():
    """创建限制器实例"""
    return ToolLimiter()


def test_classify_persona_tools(limiter):
    """测试人设工具分类"""
    category, operation = limiter._classify_tool('persona_update', {})
    assert category == 'persona'
    assert operation == 'update'
    
    category, operation = limiter._classify_tool('persona_clear', {})
    assert category == 'persona'
    assert operation == 'update'


def test_classify_task_tools(limiter):
    """测试任务工具分类"""
    category, operation = limiter._classify_tool('task_create', {})
    assert category == 'task'
    assert operation == 'update'
    
    category, operation = limiter._classify_tool('task_set_state', {})
    assert category == 'task'
    assert operation == 'update'
    
    category, operation = limiter._classify_tool('task_delete', {})
    assert category == 'task'
    assert operation == 'update'
    
    category, operation = limiter._classify_tool('task_link_info', {})
    assert category == 'task'
    assert operation == 'update'


def test_classify_memory_recall(limiter):
    """测试 memory_recall 分类"""
    category, operation = limiter._classify_tool('memory_recall', {'query_intent': 'Python'})
    assert category == 'memory'
    assert operation == 'query'


def test_classify_memory_recall_persona_query(limiter):
    """测试 memory_recall 查询人设图"""
    category, operation = limiter._classify_tool(
        'memory_recall',
        {'query_intent': 'AI,人设,角色'}
    )
    assert category == 'persona'
    assert operation == 'query'


def test_classify_memory_recall_task_query(limiter):
    """测试 memory_recall 查询工作记忆链"""
    category, operation = limiter._classify_tool(
        'memory_recall',
        {'query_intent': 'TaskNode,工作记忆'}
    )
    assert category == 'task'
    assert operation == 'query'


def test_can_call_allowed(limiter):
    """测试允许调用"""
    allowed, reason = limiter.can_call('memory_recall', {'query_intent': 'test'})
    assert allowed is True


def test_can_call_limit_reached(limiter):
    """测试达到限制"""
    for _ in range(20):
        limiter.record_call('memory_recall', {'query_intent': 'test'})
    
    allowed, reason = limiter.can_call('memory_recall', {'query_intent': 'test'})
    assert allowed is False
    assert '上限' in reason


def test_record_call(limiter):
    """测试记录调用"""
    initial_count = limiter.counts.memory_query
    
    limiter.record_call('memory_recall', {'query_intent': 'test'})
    
    assert limiter.counts.memory_query == initial_count + 1


def test_reset(limiter):
    """测试重置计数"""
    limiter.record_call('memory_recall', {'query_intent': 'test'})
    limiter.record_call('memory_recall', {'query_intent': 'test'})
    
    limiter.reset()
    
    assert limiter.counts.memory_query == 0
    assert limiter.counts.memory_update == 0


def test_get_summary(limiter):
    """测试获取统计摘要"""
    limiter.record_call('memory_recall', {'query_intent': 'test'})
    
    summary = limiter.get_summary()
    
    assert isinstance(summary, str)
    assert '一般记忆' in summary
    assert '查询1' in summary


def test_custom_limits():
    """测试自定义限制"""
    limits = ToolLimits(
        memory_query_max=5,
        memory_update_max=3
    )
    limiter = ToolLimiter(limits)
    
    assert limiter.limits.memory_query_max == 5
    assert limiter.limits.memory_update_max == 3


def test_persona_query_limit(limiter):
    """测试人设图查询限制"""
    for _ in range(1):
        limiter.record_call('memory_recall', {'query_intent': '人设'})
    
    allowed, _ = limiter.can_call('memory_recall', {'query_intent': '人设'})
    assert allowed is False


def test_task_query_limit(limiter):
    """测试工作记忆链查询限制"""
    for _ in range(4):
        limiter.record_call('memory_recall', {'query_intent': 'TaskNode'})
    
    allowed, _ = limiter.can_call('memory_recall', {'query_intent': 'TaskNode'})
    assert allowed is False

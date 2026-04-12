"""记忆工具测试"""

import pytest
from graph_memory_tui.core.tools.memory_tools import (
    MEMORY_TOOLS,
    PERSONA_TOOLS,
    WORKING_MEMORY_TOOLS,
    TOOLS
)


def test_memory_tools_exist():
    """测试记忆工具存在"""
    assert len(MEMORY_TOOLS) >= 6


def test_persona_tools_exist():
    """测试人设工具存在"""
    assert len(PERSONA_TOOLS) >= 2


def test_working_memory_tools_exist():
    """测试工作记忆工具存在"""
    assert len(WORKING_MEMORY_TOOLS) >= 4


def test_all_tools_combined():
    """测试工具合并"""
    assert len(TOOLS) == len(MEMORY_TOOLS) + len(PERSONA_TOOLS) + len(WORKING_MEMORY_TOOLS)


def test_memory_recall_tool():
    """测试 memory_recall 工具定义"""
    recall = next((t for t in TOOLS if t['function']['name'] == 'memory_recall'), None)
    assert recall is not None
    
    params = recall['function']['parameters']['properties']
    assert 'query_intent' in params
    assert 'seed_entities' in params
    assert 'depth' in params


def test_memory_commit_tool():
    """测试 memory_commit 工具定义"""
    commit = next((t for t in TOOLS if t['function']['name'] == 'memory_commit'), None)
    assert commit is not None
    
    params = commit['function']['parameters']['properties']
    assert 'triplets' in params


def test_memory_purge_tool():
    """测试 memory_purge 工具定义"""
    purge = next((t for t in TOOLS if t['function']['name'] == 'memory_purge'), None)
    assert purge is not None
    
    params = purge['function']['parameters']['properties']
    assert 'criteria' in params
    assert 'mode' in params


def test_memory_introspect_tool():
    """测试 memory_introspect 工具定义"""
    introspect = next((t for t in TOOLS if t['function']['name'] == 'memory_introspect'), None)
    assert introspect is not None


def test_persona_update_tool():
    """测试 persona_update 工具定义"""
    update = next((t for t in TOOLS if t['function']['name'] == 'persona_update'), None)
    assert update is not None
    
    params = update['function']['parameters']['properties']
    assert 'attributes' in params


def test_persona_clear_tool():
    """测试 persona_clear 工具定义"""
    clear = next((t for t in TOOLS if t['function']['name'] == 'persona_clear'), None)
    assert clear is not None


def test_task_create_tool():
    """测试 task_create 工具定义"""
    create = next((t for t in TOOLS if t['function']['name'] == 'task_create'), None)
    assert create is not None
    
    params = create['function']['parameters']['properties']
    assert 'task_id' in params
    assert 'description' in params


def test_task_set_state_tool():
    """测试 task_set_state 工具定义"""
    set_state = next((t for t in TOOLS if t['function']['name'] == 'task_set_state'), None)
    assert set_state is not None
    
    params = set_state['function']['parameters']['properties']
    assert 'task_id' in params
    assert 'state' in params


def test_task_delete_tool():
    """测试 task_delete 工具定义"""
    delete = next((t for t in TOOLS if t['function']['name'] == 'task_delete'), None)
    assert delete is not None


def test_task_link_info_tool():
    """测试 task_link_info 工具定义"""
    link = next((t for t in TOOLS if t['function']['name'] == 'task_link_info'), None)
    assert link is not None
    
    params = link['function']['parameters']['properties']
    assert 'task_id' in params
    assert 'info_node_names' in params


def test_tool_has_required_fields():
    """测试工具都有必需字段"""
    for tool in TOOLS:
        assert 'type' in tool
        assert tool['type'] == 'function'
        assert 'function' in tool
        assert 'name' in tool['function']
        assert 'description' in tool['function']
        assert 'parameters' in tool['function']


def test_tool_state_enum():
    """测试 task_set_state 的状态枚举"""
    set_state = next((t for t in TOOLS if t['function']['name'] == 'task_set_state'), None)
    state_enum = set_state['function']['parameters']['properties']['state']['enum']
    
    assert '进行中' in state_enum
    assert '已完成' in state_enum
    assert '已暂停' in state_enum
    assert '已取消' in state_enum

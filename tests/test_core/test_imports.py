"""核心逻辑导入测试"""

import pytest


def test_import_neo4j_graph():
    """测试 Neo4jGraph 类导入"""
    from graph_memory_tui.core.imports import Neo4jGraph
    assert Neo4jGraph is not None
    assert hasattr(Neo4jGraph, 'recall')
    assert hasattr(Neo4jGraph, 'commit')
    assert hasattr(Neo4jGraph, 'purge')


def test_import_graph_memory_client():
    """测试 GraphMemoryClient 类导入"""
    from graph_memory_tui.core.imports import GraphMemoryClient
    assert GraphMemoryClient is not None
    assert hasattr(GraphMemoryClient, 'send_message')


def test_import_tools():
    """测试 TOOLS 定义导入"""
    from graph_memory_tui.core.imports import TOOLS
    assert TOOLS is not None
    assert isinstance(TOOLS, list)
    assert len(TOOLS) > 0
    assert any(t['function']['name'] == 'memory_recall' for t in TOOLS)


def test_import_execute_tool():
    """测试 execute_tool 函数导入"""
    from graph_memory_tui.core.imports import execute_tool
    assert execute_tool is not None
    assert callable(execute_tool)


def test_import_config_vars():
    """测试配置变量导入"""
    from graph_memory_tui.core.imports import (
        DEEPSEEK_API_KEY,
        DEEPSEEK_BASE_URL,
        MODEL_NAME,
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD,
    )
    assert DEEPSEEK_BASE_URL is not None
    assert MODEL_NAME is not None
    assert NEO4J_URI is not None

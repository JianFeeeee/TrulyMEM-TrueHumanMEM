import pytest


def test_import_backend_server():
    from core import BackendServer
    assert BackendServer is not None


def test_import_backend_client():
    from core import BackendClient
    assert BackendClient is not None


def test_import_embedded_db():
    from core import EmbeddedGraphDB
    assert EmbeddedGraphDB is not None


def test_import_graph_client():
    from core.graph_client import GraphMemoryClient
    assert GraphMemoryClient is not None


def test_import_tool_limiter():
    from core.tool_limiter import ToolLimiter
    assert ToolLimiter is not None


def test_import_tool_executor():
    from core.tool_executor import execute_tool
    assert execute_tool is not None
    assert callable(execute_tool)
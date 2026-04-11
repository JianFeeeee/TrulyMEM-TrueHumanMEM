"""焦点处理器测试"""

import pytest
from graph_memory_tui.handlers.focus_handler import FocusHandler


def test_focus_handler_creation():
    """测试焦点处理器创建"""
    handler = FocusHandler()
    assert handler is not None
    assert handler._current_index == 0


def test_focus_ring():
    """测试焦点循环"""
    handler = FocusHandler()
    assert len(handler.FOCUS_RING) == 5
    assert "input-textarea" in handler.FOCUS_RING
    assert "cypher-textarea" in handler.FOCUS_RING


def test_get_current_focus_name():
    """测试获取当前焦点名称"""
    handler = FocusHandler()
    name = handler.get_current_focus_name()
    assert name == "Input"


def test_focus_names_mapping():
    """测试焦点名称映射"""
    handler = FocusHandler()
    assert handler.FOCUS_NAMES["input-textarea"] == "Input"
    assert handler.FOCUS_NAMES["cypher-textarea"] == "Query"

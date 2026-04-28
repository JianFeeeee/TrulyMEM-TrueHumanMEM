"""Tests for PromptManager - system prompt loading"""

from core.prompts import PromptManager


def test_get_system_prompt_not_empty():
    """系统提示词不应为空"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert prompt is not None
    assert len(prompt) > 100


def test_system_prompt_contains_identity():
    """系统提示词应包含核心身份"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "TrulyMEM" in prompt


def test_system_prompt_has_execution_order():
    """系统提示词应包含强制执行顺序"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "强制执行顺序" in prompt


def test_system_prompt_has_memory_commit_step():
    """系统提示词应包含 memory_commit 写入步骤"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "memory_commit (写入关键信息)" in prompt


def test_system_prompt_has_five_steps():
    """系统提示词应有5个执行步骤"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    # 检查步骤个数
    steps = [l for l in prompt.split('\n') if l.strip().startswith('步骤')]
    assert len(steps) == 5, f"期望5个步骤，实际{len(steps)}个"


def test_system_prompt_has_triplet_rules():
    """系统提示词应包含三元组规范"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "三元组规范" in prompt or "短关键字" in prompt


def test_system_prompt_has_memory_tools():
    """系统提示词应列出记忆工具"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "memory_recall" in prompt
    assert "memory_commit" in prompt
    assert "memory_purge" in prompt


def test_system_prompt_has_persona_tools():
    """系统提示词应列出人设工具"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "persona_update" in prompt
    assert "persona_clear" in prompt


def test_system_prompt_has_task_tools():
    """系统提示词应列出任务工具"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "task_create" in prompt
    assert "task_set_state" in prompt
    assert "task_delete" in prompt


def test_system_prompt_no_python_function_notes():
    """系统提示词不应包含Python函数实现注记"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "Python函数" not in prompt


def test_system_prompt_has_memory_principles():
    """系统提示词应包含记忆原则"""
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert "明确内容必须写入" in prompt

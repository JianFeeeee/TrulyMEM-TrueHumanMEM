"""context_rewrite 全面测试 - 单元 + 集成"""

import pytest
import json
import tempfile
import os
from core.tools.memory_tools import TOOLS, MEMORY_TOOLS
from core.tool_executor import execute_tool, execute_context_rewrite
from core.tool_limiter import ToolLimiter, ToolLimits
from core import EmbeddedGraphDB


# ========== 工具定义测试 ==========

class TestToolDefinition:
    def test_context_rewrite_in_tools(self):
        tool_names = [t["function"]["name"] for t in TOOLS]
        assert "context_rewrite" in tool_names

    def test_context_rewrite_in_memory_tools(self):
        tool_names = [t["function"]["name"] for t in MEMORY_TOOLS]
        assert "context_rewrite" in tool_names

    def test_context_rewrite_has_required_params(self):
        tool_def = None
        for t in MEMORY_TOOLS:
            if t["function"]["name"] == "context_rewrite":
                tool_def = t
                break
        assert tool_def is not None
        assert "summary" in tool_def["function"]["parameters"]["required"]

    def test_context_rewrite_description_not_empty(self):
        for t in MEMORY_TOOLS:
            if t["function"]["name"] == "context_rewrite":
                assert len(t["function"]["description"]) > 100
                break


# ========== 执行器测试 ==========

class TestContextRewriteExecutor:
    @pytest.fixture
    def db(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        db = EmbeddedGraphDB(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_valid_summary(self, db):
        args = {"summary": "[工具调用总结: 本次总结了 2 次工具调用 | 调用工具: memory_recall, memory_recall]\n\n- 查询人设图：未找到"}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "success"
        assert result["message"] == "上下文已压缩"
        assert "memory_recall" in result["summary"]

    def test_missing_marker(self, db):
        args = {"summary": "查询人设图：未找到"}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "error"
        assert "必须包含" in result["message"]

    def test_empty_summary(self, db):
        args = {"summary": ""}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "error"

    def test_marker_only(self, db):
        args = {"summary": "[工具调用总结"}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "success"

    def test_via_execute_tool(self, db):
        args = {"summary": "[工具调用总结: 本次总结了 1 次工具调用 | 调用工具: memory_recall]\n\n- 查询记忆：找到 3 个实体"}
        result_str = execute_tool(db, "context_rewrite", args)
        result = json.loads(result_str)
        assert result["status"] == "success"

    def test_unicode_content(self, db):
        args = {"summary": "[工具调用总结: 本次总结了 3 次工具调用 | 调用工具: memory_recall, memory_commit, task_create]\n\n- 查询：找到实体\"用户\"\n- 写入：{\"subject\": \"用户\", \"relation\": \"喜欢\"}\n- 任务：Task_测试"}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "success"
        assert "用户" in result["summary"]

    def test_newlines_preserved(self, db):
        summary = "[工具调用总结: 本次总结了 2 次工具调用 | 调用工具: memory_recall, memory_recall]\n\n- 查询1：结果1\n- 查询2：结果2"
        args = {"summary": summary}
        result = execute_context_rewrite(db, args)
        assert result["summary"] == summary

    def test_long_summary(self, db):
        summary = "[工具调用总结: 本次总结了 5 次工具调用 | 调用工具: memory_recall, memory_recall, memory_commit, task_create, task_set_state]\n\n" + "详细结果\n" * 50
        args = {"summary": summary}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "success"
        assert len(result["summary"]) == len(summary)

    def test_special_json_chars(self, db):
        args = {"summary": '[工具调用总结: 本次总结了 1 次工具调用 | 调用工具: memory_commit]\n\n- 写入：{"subject": "测试", "relation": "包含\"引号"}'}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "success"

    def test_missing_summary_key(self, db):
        args = {}
        result = execute_context_rewrite(db, args)
        assert result["status"] == "error"


# ========== 工具限流器测试 ==========

class TestContextRewriteLimiter:
    def test_classified_as_memory_query(self):
        limiter = ToolLimiter(ToolLimits(memory_query_max=1))
        category, operation = limiter._classify_tool("context_rewrite", {})
        assert category == "memory"
        assert operation == "query"

    def test_counts_toward_memory_query_limit(self):
        limiter = ToolLimiter(ToolLimits(memory_query_max=1))
        allowed, _ = limiter.can_call("context_rewrite", {})
        assert allowed
        limiter.record_call("context_rewrite", {})
        allowed, reason = limiter.can_call("context_rewrite", {})
        assert not allowed
        assert "一般记忆查询次数已达上限" in reason

    def test_does_not_affect_memory_update(self):
        limiter = ToolLimiter(ToolLimits(memory_update_max=1))
        limiter.record_call("context_rewrite", {})
        allowed, _ = limiter.can_call("memory_commit", {})
        assert allowed

    def test_reset_clears_count(self):
        limiter = ToolLimiter(ToolLimits(memory_query_max=1))
        limiter.record_call("context_rewrite", {})
        limiter.reset()
        allowed, _ = limiter.can_call("context_rewrite", {})
        assert allowed


# ========== 集成测试：messages_history 压缩流程 ==========

class TestMessagesHistoryCompression:
    def test_compression_preserves_user_message(self):
        messages_history = [
            {"role": "user", "content": "我们之前聊过成语接龙吗？"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "tc1", "type": "function", "function": {"name": "memory_recall", "arguments": '{"query_intent": "人设"}'}}]},
            {"role": "tool", "tool_call_id": "tc1", "content": "===== 记忆检索结果 =====\n\n(未找到相关记忆)\n=============================="},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "tc2", "type": "function", "function": {"name": "memory_recall", "arguments": '{"query_intent": "工作记忆"}'}}]},
            {"role": "tool", "tool_call_id": "tc2", "content": "===== 记忆检索结果 =====\n\n实体 (2 个):\n  - Task_成语接龙 (类型: unknown, 提及: 1次)\n=============================="},
        ]

        summary = "[工具调用总结: 本次总结了 2 次工具调用 | 调用工具: memory_recall, memory_recall]\n\n- 查询人设图：未找到人设\n- 查询工作记忆链：发现 Task_成语接龙，状态已暂停"

        user_msg = messages_history[0]
        messages_history[:] = [
            user_msg,
            {"role": "assistant", "content": summary}
        ]

        assert len(messages_history) == 2
        assert messages_history[0]["role"] == "user"
        assert messages_history[0]["content"] == "我们之前聊过成语接龙吗？"
        assert messages_history[1]["role"] == "assistant"
        assert "memory_recall" in messages_history[1]["content"]
        assert "成语接龙" in messages_history[1]["content"]

    def test_compression_removes_json_noise(self):
        messages_history = [
            {"role": "user", "content": "查询用户信息"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "tc1", "type": "function", "function": {"name": "memory_recall", "arguments": '{"query_intent": "用户"}'}}]},
            {"role": "tool", "tool_call_id": "tc1", "content": json.dumps({"entities": [{"name": "用户", "type": "person", "mention_count": 5}], "relations": [{"source": "用户", "target": "Python", "type": "喜欢"}]})},
        ]

        summary = "[工具调用总结: 本次总结了 1 次工具调用 | 调用工具: memory_recall]\n\n- 查询用户：找到用户实体，提及5次，喜欢Python"

        user_msg = messages_history[0]
        messages_history[:] = [user_msg, {"role": "assistant", "content": summary}]

        for msg in messages_history[1:]:
            assert "entities" not in msg.get("content", "")
            assert "relations" not in msg.get("content", "")

    def test_compression_retains_tool_meta_cognition(self):
        messages_history = [
            {"role": "user", "content": "查询"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "tc1", "type": "function", "function": {"name": "memory_recall", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "tc1", "content": "结果"},
        ]

        summary = "[工具调用总结: 本次总结了 1 次工具调用 | 调用工具: memory_recall]\n\n- 查询记忆：无结果"

        user_msg = messages_history[0]
        messages_history[:] = [user_msg, {"role": "assistant", "content": summary}]

        content = messages_history[1]["content"]
        assert "工具调用总结" in content
        assert "memory_recall" in content
        assert "1 次" in content

    def test_multiple_compressions_in_sequence(self):
        messages_history = [
            {"role": "user", "content": "多轮查询"},
        ]

        for i in range(3):
            messages_history.append({"role": "assistant", "content": None, "tool_calls": [{"id": f"tc{i}", "type": "function", "function": {"name": "memory_recall", "arguments": "{}"}}]})
            messages_history.append({"role": "tool", "tool_call_id": f"tc{i}", "content": f"结果{i}"})

            summary = f"[工具调用总结: 本次总结了 {i+1} 次工具调用 | 调用工具: memory_recall]\n\n- 第{i+1}轮查询：结果{i}"
            user_msg = messages_history[0]
            messages_history[:] = [user_msg, {"role": "assistant", "content": summary}]

        assert len(messages_history) == 2
        assert messages_history[0]["content"] == "多轮查询"
        assert "第3轮查询" in messages_history[1]["content"]

"""
工具调用限制器 - 限制每轮对话中各类工具的调用次数
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class ToolLimits:
    """工具调用限制配置"""
    persona_update_max: int = 1
    task_update_max: int = 20      # 工作记忆链修改（create/set_state/delete/link_info）
    task_query_max: int = 30      # 工作记忆链查询（memory_recall 查任务相关）
    memory_query_max: int = 30
    memory_update_max: int = 15


@dataclass
class ToolCallCount:
    """工具调用计数"""
    persona_update: int = 0
    task_update: int = 0
    task_query: int = 0
    memory_query: int = 0
    memory_update: int = 0


class ToolLimiter:
    """工具调用限制器"""

    def __init__(self, limits: Optional[ToolLimits] = None):
        self.limits = limits or ToolLimits()
        self.counts = ToolCallCount()

    def _classify_tool(self, tool_name: str, arguments: dict) -> tuple:
        """
        分类工具调用
        返回: (category, operation)
        category: 'persona', 'task', 'memory'
        operation: 'query', 'update'
        """
        if tool_name in ('persona_update', 'persona_remove', 'persona_clear'):
            return ('persona', 'update')

        if tool_name in ('task_create', 'task_set_state', 'task_delete', 'task_link_info'):
            return ('task', 'update')

        if tool_name == 'task_query':
            return ('task', 'query')

        if tool_name == 'memory_recall':
            # 尝试区分工作记忆链查询 vs 一般记忆查询
            query = (arguments.get('queryIntent', '') + ' ' + ' '.join(
                arguments.get('seedEntities', []))).strip().lower()
            task_keywords = ['task', '任务', '工作记忆', '当前轮', '会话', '过程', '流程']
            if any(kw in query for kw in task_keywords):
                return ('task', 'query')
            return ('memory', 'query')

        if tool_name == 'memory_commit':
            return ('memory', 'update')

        if tool_name == 'memory_purge':
            return ('memory', 'update')

        if tool_name == 'memory_introspect':
            return ('memory', 'query')

        if tool_name in ('memory_archive', 'memory_cleanup'):
            return ('memory', 'update')

        if tool_name == 'context_rewrite':
            return ('memory', 'query')

        return ('memory', 'update')

    def can_call(self, tool_name: str, arguments: dict) -> tuple:
        """
        检查是否允许调用工具
        返回: (allowed, reason)
        """
        category, operation = self._classify_tool(tool_name, arguments)

        if category == 'persona':
            if self.counts.persona_update >= self.limits.persona_update_max:
                return (False, f"人设图修改次数已达上限({self.limits.persona_update_max}次)")

        elif category == 'task':
            if operation == 'query':
                if self.counts.task_query >= self.limits.task_query_max:
                    return (False, f"工作记忆链查询次数已达上限({self.limits.task_query_max}次)")
            elif self.counts.task_update >= self.limits.task_update_max:
                return (False, f"工作记忆链修改次数已达上限({self.limits.task_update_max}次)")

        elif category == 'memory':
            if operation == 'query':
                if self.counts.memory_query >= self.limits.memory_query_max:
                    return (False, f"一般记忆查询次数已达上限({self.limits.memory_query_max}次)")
            else:
                if self.counts.memory_update >= self.limits.memory_update_max:
                    return (False, f"一般记忆修改次数已达上限({self.limits.memory_update_max}次)")

        return (True, "允许调用")

    def record_call(self, tool_name: str, arguments: dict) -> None:
        """记录工具调用"""
        category, operation = self._classify_tool(tool_name, arguments)

        if category == 'persona':
            self.counts.persona_update += 1

        elif category == 'task':
            if operation == 'query':
                self.counts.task_query += 1
            else:
                self.counts.task_update += 1

        elif category == 'memory':
            if operation == 'query':
                self.counts.memory_query += 1
            else:
                self.counts.memory_update += 1

    def get_summary(self) -> str:
        """获取调用统计摘要"""
        lines = [
            f"人设图: 修改{self.counts.persona_update}/{self.limits.persona_update_max}次",
            f"工作记忆链: 查询{self.counts.task_query}/{self.limits.task_query_max}次, "
            f"修改{self.counts.task_update}/{self.limits.task_update_max}次",
            f"一般记忆: 查询{self.counts.memory_query}/{self.limits.memory_query_max}次, "
            f"修改{self.counts.memory_update}/{self.limits.memory_update_max}次"
        ]
        return "\n".join(lines)

    def reset(self) -> None:
        """重置计数（新的一轮对话开始时调用）"""
        self.counts = ToolCallCount()

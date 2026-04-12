"""
工具调用限制器 - 限制每轮对话中各类工具的调用次数
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ToolLimits:
    """工具调用限制配置"""
    # 人设图限制
    persona_query_max: int = 1      # 每轮最多查询1次人设图
    persona_update_max: int = 1      # 每轮最多修改1次人设图
    
    # 工作记忆链限制
    task_query_max: int = 4          # 每轮最多查询4次工作记忆链
    task_update_max: int = 2          # 每轮最多修改2次工作记忆链
    
    # 一般记忆限制
    memory_query_max: int = 20        # 每轮最多查询20次一般记忆
    memory_update_max: int = 10        # 每轮最多修改10次一般记忆


@dataclass
class ToolCallCount:
    """工具调用计数"""
    # 人设图
    persona_query: int = 0
    persona_update: int = 0
    
    # 工作记忆链
    task_query: int = 0
    task_update: int = 0
    
    # 一般记忆
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
        # 人设图工具
        if tool_name in ('persona_update', 'persona_clear'):
            return ('persona', 'update')
        
        # 工作记忆链工具
        if tool_name in ('task_create', 'task_set_state', 'task_delete', 'task_link_info'):
            # task_link_info 是关联操作，算作更新
            return ('task', 'update')
        
        # 一般记忆工具
        if tool_name == 'memory_recall':
            # 判断是查询人设图、工作记忆链还是一般记忆
            query_intent = arguments.get('query_intent', '').lower()
            
            # 检查是否查询人设图
            if any(kw in query_intent for kw in ['人设', '角色', '性格', '语气', '说话风格', '扮演']):
                return ('persona', 'query')
            
            # 检查是否查询工作记忆链
            if any(kw in query_intent for kw in ['tasknode', '工作记忆', '任务链', '任务', 'task']):
                return ('task', 'query')
            
            # 一般记忆查询
            return ('memory', 'query')
        
        if tool_name == 'memory_commit':
            return ('memory', 'update')
        
        if tool_name == 'memory_purge':
            return ('memory', 'update')
        
        if tool_name == 'memory_introspect':
            return ('memory', 'query')
        
        if tool_name in ('memory_archive', 'memory_cleanup'):
            return ('memory', 'update')
        
        # 未知工具，归类为一般记忆更新
        return ('memory', 'update')
    
    def can_call(self, tool_name: str, arguments: dict) -> tuple:
        """
        检查是否允许调用工具
        返回: (allowed, reason)
        """
        category, operation = self._classify_tool(tool_name, arguments)
        
        # 获取当前计数和限制
        if category == 'persona':
            if operation == 'query':
                if self.counts.persona_query >= self.limits.persona_query_max:
                    return (False, f"人设图查询次数已达上限({self.limits.persona_query_max}次)")
            else:  # update
                if self.counts.persona_update >= self.limits.persona_update_max:
                    return (False, f"人设图修改次数已达上限({self.limits.persona_update_max}次)")
        
        elif category == 'task':
            if operation == 'query':
                if self.counts.task_query >= self.limits.task_query_max:
                    return (False, f"工作记忆链查询次数已达上限({self.limits.task_query_max}次)")
            else:  # update
                if self.counts.task_update >= self.limits.task_update_max:
                    return (False, f"工作记忆链修改次数已达上限({self.limits.task_update_max}次)")
        
        elif category == 'memory':
            if operation == 'query':
                if self.counts.memory_query >= self.limits.memory_query_max:
                    return (False, f"一般记忆查询次数已达上限({self.limits.memory_query_max}次)")
            else:  # update
                if self.counts.memory_update >= self.limits.memory_update_max:
                    return (False, f"一般记忆修改次数已达上限({self.limits.memory_update_max}次)")
        
        return (True, "允许调用")
    
    def record_call(self, tool_name: str, arguments: dict) -> None:
        """记录工具调用"""
        category, operation = self._classify_tool(tool_name, arguments)
        
        if category == 'persona':
            if operation == 'query':
                self.counts.persona_query += 1
            else:
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
            f"人设图: 查询{self.counts.persona_query}/{self.limits.persona_query_max}次, "
            f"修改{self.counts.persona_update}/{self.limits.persona_update_max}次",
            f"工作记忆链: 查询{self.counts.task_query}/{self.limits.task_query_max}次, "
            f"修改{self.counts.task_update}/{self.limits.task_update_max}次",
            f"一般记忆: 查询{self.counts.memory_query}/{self.limits.memory_query_max}次, "
            f"修改{self.counts.memory_update}/{self.limits.memory_update_max}次"
        ]
        return "\n".join(lines)
    
    def reset(self) -> None:
        """重置计数（新的一轮对话开始时调用）"""
        self.counts = ToolCallCount()

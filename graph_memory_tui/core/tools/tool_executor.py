"""
工具执行器
"""
import json
from typing import Any, Dict


def execute_tool(graph: Any, tool_name: str, arguments: dict) -> str:
    """执行工具调用"""
    print(f"\n[工具调用] {tool_name}")
    print(f"[参数] {json.dumps(arguments, ensure_ascii=False, indent=2)}")
    
    try:
        # 基础记忆工具
        if tool_name == "memory_recall":
            result = graph.recall(
                query_intent=arguments.get("query_intent", ""),
                seed_entities=arguments.get("seed_entities"),
                depth=arguments.get("depth", 2),
                time_range=arguments.get("time_range"),
                session_filter=arguments.get("session_filter")
            )
            return format_recall_result(result)
        
        elif tool_name == "memory_commit":
            result = graph.commit(
                triplets=arguments.get("triplets", []),
                entity_types=arguments.get("entity_types"),
                temporal_tag=arguments.get("temporal_tag")
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_purge":
            result = graph.purge(
                criteria=arguments.get("criteria", {}),
                mode=arguments.get("mode", "soft"),
                new_relation=arguments.get("new_relation")
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_introspect":
            result = graph.introspect(session_id=arguments.get("session_id"))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_archive":
            result = graph.archive(days=arguments.get("days", 30))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_cleanup":
            result = graph.cleanup(dry_run=arguments.get("dry_run", True))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        # 人设图管理工具
        elif tool_name == "persona_update":
            result = execute_persona_update(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "persona_clear":
            result = execute_persona_clear(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        # 工作记忆链管理工具
        elif tool_name == "task_create":
            result = execute_task_create(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_set_state":
            result = execute_task_set_state(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_delete":
            result = execute_task_delete(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_link_info":
            result = execute_task_link_info(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        return f"未知工具: {tool_name}"
    
    except Exception as e:
        return f"工具执行错误: {str(e)}"


def format_recall_result(result: dict) -> str:
    """格式化检索结果"""
    lines = ["===== 记忆检索结果 ====="]
    
    if result.get("entities"):
        lines.append(f"\n实体 ({len(result['entities'])} 个):")
        for e in result["entities"]:
            if e and isinstance(e, dict):
                lines.append(f"  - {e.get('name', 'N/A')} (类型: {e.get('type', 'unknown')}, 提及: {e.get('mention_count', 1)}次)")
    
    if result.get("relations"):
        lines.append(f"\n关系 ({len(result['relations'])} 条):")
        for r in result["relations"]:
            if r and isinstance(r, dict):
                lines.append(f"  - {r.get('source', 'N/A')} --[{r.get('type', 'N/A')}]--> {r.get('target', 'N/A')}")
                created = r.get("created_at", "N/A")
                if created and created != "N/A":
                    created = created[:19] if "T" in str(created) else str(created)
                session_id = r.get('session_id', 'N/A')
                session_display = session_id[:20] if session_id and session_id != 'N/A' else 'N/A'
                lines.append(f"    时间: {created}, 会话: {session_display}, 轮次: {r.get('turn_id', 0)}, 置信度: {r.get('confidence', 1.0)}")
    
    if not result.get("entities") and not result.get("relations"):
        lines.append("\n(未找到相关记忆)")
    
    lines.append("=" * 30)
    return "\n".join(lines)


# 人设图管理工具实现
def execute_persona_update(graph: Any, arguments: dict) -> dict:
    """更新人设"""
    attributes = arguments.get("attributes", [])
    mode = arguments.get("mode", "merge")
    
    if mode == "replace":
        # 先清除旧人设
        graph.purge(
            criteria={"subject_contains": "AI", "relation_type": "扮演角色"},
            mode="soft"
        )
        graph.purge(
            criteria={"subject_contains": "AI", "relation_type": "说话风格"},
            mode="soft"
        )
        graph.purge(
            criteria={"subject_contains": "AI", "relation_type": "性格特点"},
            mode="soft"
        )
    
    # 写入新人设
    triplets = []
    for attr in attributes:
        triplets.append({
            "subject": "AI",
            "relation": attr["attribute"],
            "object": attr["value"],
            "confidence": 1.0
        })
    
    result = graph.commit(triplets=triplets)
    return {
        "status": "success",
        "mode": mode,
        "updated_attributes": len(attributes),
        "details": result
    }


def execute_persona_clear(graph: Any, arguments: dict) -> dict:
    """清除人设"""
    if not arguments.get("confirm", True):
        return {"status": "cancelled", "message": "需要确认才能清除人设"}
    
    # 删除所有人设相关关系
    result1 = graph.purge(
        criteria={"subject_contains": "AI", "relation_type": "扮演角色"},
        mode="soft"
    )
    result2 = graph.purge(
        criteria={"subject_contains": "AI", "relation_type": "说话风格"},
        mode="soft"
    )
    result3 = graph.purge(
        criteria={"subject_contains": "AI", "relation_type": "性格特点"},
        mode="soft"
    )
    result4 = graph.purge(
        criteria={"subject_contains": "AI", "relation_type": "语气特征"},
        mode="soft"
    )
    
    total_deleted = (
        result1.get("deleted_count", 0) +
        result2.get("deleted_count", 0) +
        result3.get("deleted_count", 0) +
        result4.get("deleted_count", 0)
    )
    
    return {
        "status": "success",
        "deleted_count": total_deleted,
        "message": "人设已清除，恢复默认身份"
    }


# 工作记忆链管理工具实现
def execute_task_create(graph: Any, arguments: dict) -> dict:
    """创建任务节点"""
    task_id = arguments.get("task_id")
    description = arguments.get("description")
    info_nodes = arguments.get("info_nodes", [])
    
    # 创建任务节点
    triplets = [
        {"subject": task_id, "relation": "is_type", "object": "TaskNode"},
        {"subject": task_id, "relation": "has_description", "object": description},
        {"subject": task_id, "relation": "HAS_STATE", "object": "State_进行中"}
    ]
    
    result = graph.commit(triplets=triplets)
    
    # 关联信息节点
    if info_nodes:
        link_triplets = []
        for node_name in info_nodes:
            link_triplets.append({
                "subject": task_id,
                "relation": "CONTAINS_INFO",
                "object": node_name
            })
        graph.commit(triplets=link_triplets)
    
    return {
        "status": "success",
        "task_id": task_id,
        "description": description,
        "info_nodes": info_nodes,
        "details": result
    }


def execute_task_set_state(graph: Any, arguments: dict) -> dict:
    """设置任务状态"""
    task_id = arguments.get("task_id")
    state = arguments.get("state")
    
    # 删除旧状态
    graph.purge(
        criteria={"subject_contains": task_id, "relation_type": "HAS_STATE"},
        mode="soft"
    )
    
    # 设置新状态
    state_node = f"State_{state}"
    result = graph.commit(
        triplets=[{"subject": task_id, "relation": "HAS_STATE", "object": state_node}]
    )
    
    return {
        "status": "success",
        "task_id": task_id,
        "new_state": state,
        "details": result
    }


def execute_task_delete(graph: Any, arguments: dict) -> dict:
    """删除任务节点"""
    task_id = arguments.get("task_id")
    delete_info_nodes = arguments.get("delete_info_nodes", True)
    
    # 查询关联的信息节点
    if delete_info_nodes:
        recall_result = graph.recall(
            query_intent=f"{task_id},CONTAINS_INFO",
            depth=1
        )
        
        # 删除信息节点
        for relation in recall_result.get("relations", []):
            if relation.get("type") == "CONTAINS_INFO" and relation.get("source") == task_id:
                info_node = relation.get("target")
                graph.purge(
                    criteria={"subject_contains": info_node},
                    mode="soft"
                )
    
    # 删除任务节点
    result = graph.purge(
        criteria={"subject_contains": task_id},
        mode="soft"
    )
    
    return {
        "status": "success",
        "task_id": task_id,
        "deleted_info_nodes": delete_info_nodes,
        "details": result
    }


def execute_task_link_info(graph: Any, arguments: dict) -> dict:
    """关联信息节点"""
    task_id = arguments.get("task_id")
    info_node_names = arguments.get("info_node_names", [])
    
    triplets = []
    for node_name in info_node_names:
        triplets.append({
            "subject": task_id,
            "relation": "CONTAINS_INFO",
            "object": node_name
        })
    
    result = graph.commit(triplets=triplets)
    
    return {
        "status": "success",
        "task_id": task_id,
        "linked_nodes": info_node_names,
        "details": result
    }

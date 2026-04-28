"""
工具执行器
"""
import json
from typing import Any, Dict

from .activity_recorder import get_recorder


def execute_tool(graph: Any, tool_name: str, arguments: dict) -> str:
    """执行工具调用"""
    print(f"\n[工具调用] {tool_name}")
    print(f"[参数] {json.dumps(arguments, ensure_ascii=False, indent=2)}")
    
    try:
        recorder = get_recorder()
        
        # 基础记忆工具
        if tool_name == "memory_recall":
            entity = arguments.get("query_intent", "") or str(arguments.get("seed_entities", ""))
            recorder.record("query", tool_name, entity)
            result = graph.recall(
                query_intent=arguments.get("query_intent", ""),
                seed_entities=arguments.get("seed_entities"),
                depth=arguments.get("depth", 2),
                time_range=arguments.get("time_range"),
                session_filter=arguments.get("session_filter")
            )
            # 记录召回结果中的实体名，供 WebUI 高亮+拉镜头用
            for e in result.get("entities", []):
                if e and isinstance(e, dict) and e.get("name"):
                    recorder.record("query", tool_name + "_found", e["name"])
            return format_recall_result(result)
        
        elif tool_name == "memory_commit":
            triplets = arguments.get("triplets", [])
            entity = triplets[0].get("subject", "") if triplets else ""
            recorder.record("create", tool_name, entity, f"{len(triplets)} triplets")
            result = graph.commit(
                triplets=triplets,
                entity_types=arguments.get("entity_types"),
                temporal_tag=arguments.get("temporal_tag")
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_purge":
            criteria = arguments.get("criteria", {})
            entity = criteria.get("subject_contains", str(criteria))
            recorder.record("delete", tool_name, entity)
            result = graph.purge(
                criteria=criteria,
                mode=arguments.get("mode", "soft"),
                new_relation=arguments.get("new_relation")
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_introspect":
            recorder.record("query", tool_name, "数据库统计")
            result = graph.introspect(session_id=arguments.get("session_id"))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_archive":
            recorder.record("archive", tool_name, "旧记忆")
            result = graph.archive(days=arguments.get("days", 30))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "memory_cleanup":
            recorder.record("cleanup", tool_name, "已删除数据")
            result = graph.cleanup(dry_run=arguments.get("dry_run", True))
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "context_rewrite":
            result = execute_context_rewrite(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        # 人设图管理工具
        elif tool_name == "persona_update":
            recorder.record("update", tool_name, "人设属性")
            result = execute_persona_update(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "persona_remove":
            recorder.record("delete", tool_name, arguments.get("attribute", ""))
            result = execute_persona_remove(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)

        elif tool_name == "persona_clear":
            recorder.record("delete", tool_name, "所有人设")
            result = execute_persona_clear(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        # 工作记忆链管理工具
        elif tool_name == "task_create":
            desc = arguments.get("description", "")
            recorder.record("create", tool_name, desc)
            result = execute_task_create(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_set_state":
            desc = arguments.get("task_id", "")
            recorder.record("update", tool_name, desc)
            result = execute_task_set_state(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_delete":
            desc = arguments.get("task_id", "")
            recorder.record("delete", tool_name, desc)
            result = execute_task_delete(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_link_info":
            desc = arguments.get("task_id", "")
            recorder.record("update", tool_name, desc)
            result = execute_task_link_info(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)
        
        elif tool_name == "task_archive":
            recorder.record("update", tool_name, arguments.get("task_id", ""))
            result = execute_task_archive(graph, arguments)
            return json.dumps(result, ensure_ascii=False, default=str)

        elif tool_name == "task_query":
            recorder.record("query", tool_name, "")
            result = execute_task_query(graph, arguments)
            # 记录查询到的任务描述，供 WebUI 高亮
            for t in result.get("tasks", []):
                if t and isinstance(t, dict) and t.get("description"):
                    recorder.record("query", tool_name + "_found", t["description"])
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


def execute_context_rewrite(graph: Any, arguments: dict) -> dict:
    """压缩工具调用上下文"""
    summary = arguments.get("summary", "")
    
    # 验证格式：必须包含工具调用标记
    if "[工具调用总结" not in summary:
        return {
            "status": "error",
            "message": "总结格式错误：必须包含 [工具调用总结: 本次总结了 N 次工具调用 | 调用工具: ...] 标记"
        }
    
    return {
        "status": "success",
        "message": "上下文已压缩",
        "summary": summary
    }


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


def execute_persona_remove(graph: Any, arguments: dict) -> dict:
    """删除单条人设属性"""
    attribute = arguments.get("attribute")
    if not attribute:
        return {"status": "error", "message": "请指定要删除的属性名"}

    # 查询当前AI的所有人设关系，找到匹配属性名的
    recall_result = graph.recall(query_intent="AI,人设,角色", depth=1)
    found = False
    deleted_count = 0

    for rel in recall_result.get("relations", []):
        if rel.get("source") == "AI" and rel.get("type") == attribute:
            result = graph.purge(
                criteria={"subject_contains": "AI", "relation_type": attribute},
                mode="soft"
            )
            deleted_count += result.get("deleted_count", 0)
            found = True

    if not found:
        # 也许属性名不完全匹配，尝试直接用这个类型删除
        result = graph.purge(
            criteria={"subject_contains": "AI", "relation_type": attribute},
            mode="soft"
        )
        deleted_count = result.get("deleted_count", 0)

    return {
        "status": "success" if deleted_count > 0 else "not_found",
        "deleted_attribute": attribute,
        "deleted_count": deleted_count,
        "message": f"已删除属性「{attribute}」" if deleted_count > 0 else f"未找到属性「{attribute}」"
    }


def execute_persona_clear(graph: Any, arguments: dict) -> dict:
    """清除所有人设"""
    if not arguments.get("confirm"):
        return {"status": "cancelled", "message": "请设置 confirm=true 确认清除人设"}

    # 先查询AI的所有人设关系
    recall_result = graph.recall(query_intent="AI,人设,角色", depth=1)

    # 收集所有AI到其他实体的关系类型
    relation_types = set()
    for rel in recall_result.get("relations", []):
        if rel.get("source") == "AI" and rel.get("type"):
            relation_types.add(rel.get("type"))

    total_deleted = 0
    deleted_types = []

    for rtype in relation_types:
        result = graph.purge(
            criteria={"subject_contains": "AI", "relation_type": rtype},
            mode="soft"
        )
        count = result.get("deleted_count", 0)
        if count > 0:
            total_deleted += count
            deleted_types.append(rtype)

    return {
        "status": "success",
        "deleted_count": total_deleted,
        "deleted_types": deleted_types,
        "message": f"人设已清除，恢复默认身份（删除了 {len(deleted_types)} 类属性）"
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

def execute_task_archive(graph: Any, arguments: dict) -> dict:
    """归档任务"""
    task_id = arguments.get("task_id")
    summary = arguments.get("summary", "")
    
    if not task_id:
        return {"status": "error", "message": "请指定要归档的任务ID"}
    
    # 1. 设置任务状态为 archived
    triplets_state = [
        {"subject": task_id, "relation": "HAS_STATE", "object": "State_归档"}
    ]
    graph.commit(triplets=triplets_state)
    
    # 2. 如果有摘要，写入完成记录
    if summary:
        summary_triplets = [
            {"subject": task_id, "relation": "归档摘要", "object": summary}
        ]
        graph.commit(triplets=summary_triplets)
    
    # 3. 尝试更新 description 标记为已归档
    archive_triplet = [
        {"subject": task_id, "relation": "has_description", "object": f"[已归档] {summary or '任务已完成'}"}
    ]
    graph.commit(triplets=archive_triplet)
    
    return {
        "status": "success",
        "task_id": task_id,
        "archived": True,
        "summary": summary or "无摘要",
        "message": f"任务「{task_id}」已归档" + (f"，摘要：{summary}" if summary else "")
    }


def execute_task_query(graph: Any, arguments: dict) -> dict:
    """查询最近的任务列表"""
    limit = arguments.get("limit", 10)
    state_filter = arguments.get("state_filter")
    
    result = graph.get_recent_tasks(limit=limit, state_filter=state_filter)
    
    return {
        "status": "success",
        "tasks": result["tasks"],
        "total": result["total"],
        "message": f"找到 {result['total']} 个任务"
    }

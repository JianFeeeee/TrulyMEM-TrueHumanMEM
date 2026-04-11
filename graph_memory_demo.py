#!/usr/bin/env python3
"""
Graph Memory Demo - 纯图数据库调用 Demo
基于 DeepSeek API Tool Calls 实现摒弃传统上下文的自主记忆多轮对话
验证目的：无上下文纯图数据库记忆存储
"""

import json
import os
import uuid
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j")

CURRENT_SESSION_ID = f"session-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4]}"
CURRENT_TURN = 0

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "memory_recall",
            "description": "当你对当前输入中的实体、指代、或关系不确定时，调用此工具检索相关记忆。输入为自然语言查询意图，系统将返回相关子图。支持时间范围和多跳路径查询。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_intent": {"type": "string", "description": "模型用自然语言描述想查什么"},
                    "seed_entities": {"type": "array", "items": {"type": "string"}, "description": "可选：已识别的实体ID"},
                    "depth": {"type": "integer", "description": "期望的遍历深度，由模型根据复杂度决定，默认2"},
                    "time_range": {"type": "object", "description": "可选：时间范围筛选", "properties": {"days": {"type": "integer", "description": "最近N天"}}},
                    "session_filter": {"type": "string", "description": "可选：限定特定会话ID"}
                },
                "required": ["query_intent"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_commit",
            "description": "当你认为当前对话包含对未来轮次有价值的信息时，将抽取的三元组写入图库。仅在信息具有跨轮次引用潜力时调用。支持批量写入。",
            "parameters": {
                "type": "object",
                "properties": {
                    "triplets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subject": {"type": "string"},
                                "relation": {"type": "string"},
                                "object": {"type": "string"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["subject", "relation", "object"]
                        },
                        "description": "要写入的三元组列表"
                    },
                    "entity_types": {"type": "array", "items": {"type": "string"}, "description": "模型动态提议的类型"},
                    "temporal_tag": {"type": "string", "description": "可选：时间标记（如'2026-04-08'）"}
                },
                "required": ["triplets"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_purge",
            "description": "当你发现记忆中的信息与当前认知矛盾，或用户明确要求更正时，删除指定关系。优先于memory_commit执行以维护一致性。",
            "parameters": {
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "object",
                        "properties": {
                            "subject_contains": {"type": "string"},
                            "relation_type": {"type": "string"},
                            "target_contains": {"type": "string"},
                            "time_before": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "description": "删除条件"
                    },
                    "mode": {"type": "string", "enum": ["soft", "supersede"], "description": "soft=逻辑删除, supersede=纠错替代", "default": "soft"},
                    "new_relation": {"type": "object", "description": "supersede模式时的新关系", "properties": {"relation": {"type": "string"}, "target": {"type": "string"}}}
                },
                "required": ["criteria"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_introspect",
            "description": "检索当前对话会话的元数据：已讨论的实体、关系密度、记忆热点。用于自我监控信息缺口。",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "可选：指定会话ID，默认当前会话"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_archive",
            "description": "归档N天前的非活跃关系，用于清理低频查询数据。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "归档多少天前的关系，默认30天"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_cleanup",
            "description": "物理清理已删除状态超过90天的关系和孤立节点。谨慎使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "dry_run": {"type": "boolean", "description": "仅预览不实际删除", "default": True}
                },
                "required": []
            }
        }
    }
]


class Neo4jGraph:
    def __init__(self, uri: str, user: str, password: str):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def ensure_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT entity_name_constraint IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            session.run("CREATE CONSTRAINT session_id_constraint IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
            
            session.run("CREATE INDEX rel_created_at IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.created_at")
            session.run("CREATE INDEX rel_session_id IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.session_id")
            session.run("CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.type")
            session.run("CREATE INDEX rel_status IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.status")
            session.run("CREATE INDEX rel_date_bucket IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.date_bucket")
            session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON e.type")
            session.run("CREATE INDEX entity_mention_count IF NOT EXISTS FOR (e:Entity) ON e.mention_count")
    
    def recall(self, query_intent: str, seed_entities: list = None, depth: int = 2, 
               time_range: dict = None, session_filter: str = None) -> dict:
        with self.driver.session() as session:
            # 支持逗号分隔的多个关键词
            keywords = [w.strip() for w in query_intent.replace(',', ' ').split() if len(w.strip()) > 0]
            
            # 如果没有查询条件，返回空结果
            if not keywords and not seed_entities:
                return {"entities": [], "relations": [], "message": "无查询关键词"}
            
            # 默认查询所有会话的历史（不只是当前会话）
            # 只有明确指定 session_filter 才限制查询范围
            params = {}
            cond_parts = ["r.status = 'active'"]
            
            if session_filter:
                cond_parts.append("r.session_id = $session_id")
                params["session_id"] = session_filter
            
            # 搜索多个相关关键词
            if keywords:
                keyword_conditions = []
                for k in keywords:
                    k_lower = k.lower()
                    # 搜索：实体名称、关系类型、目标实体
                    keyword_conditions.append(f"toLower(e.name) CONTAINS '{k_lower}'")
                    keyword_conditions.append(f"toLower(t.name) CONTAINS '{k_lower}'")
                    keyword_conditions.append(f"toLower(r.type) CONTAINS '{k_lower}'")
                cond_parts.append(f"({' OR '.join(keyword_conditions)})")
            
            if seed_entities:
                placeholders = ",".join([f"'{s}'" for s in seed_entities])
                cond_parts.append(f"(e.name IN [{placeholders}] OR t.name IN [{placeholders}])")
            
            if time_range and "days" in time_range:
                cond_parts.append(f"r.created_at >= datetime() - duration('P{time_range['days']}D')")
            
            where_clause = " AND ".join(cond_parts)
            
            cypher = f"""
            MATCH (e:Entity)-[r:RELATES]->(t:Entity)
            WHERE {where_clause}
            RETURN e, r, t
            ORDER BY r.created_at DESC
            LIMIT 30
            """
            
            result = session.run(cypher, params)
            entities, relations = {}, []
            
            for record in result:
                e, r, t = record["e"], record["r"], record["t"]
                if e["name"] not in entities:
                    entities[e["name"]] = {"name": e["name"], "type": e.get("type", "unknown"), "mention_count": e.get("mention_count", 1)}
                if t["name"] not in entities:
                    entities[t["name"]] = {"name": t["name"], "type": t.get("type", "unknown"), "mention_count": t.get("mention_count", 1)}
                
                relations.append({
                    "source": e["name"],
                    "target": t["name"],
                    "type": r["type"],
                    "created_at": str(r.get("created_at", "")),
                    "session_id": r.get("session_id", ""),
                    "turn_id": r.get("turn_id", 0),
                    "confidence": r.get("confidence", 1.0)
                })
            
            return {"entities": list(entities.values()), "relations": relations[:20]}
    
    def commit(self, triplets: list, entity_types: list = None, temporal_tag: str = None) -> dict:
        global CURRENT_TURN
        with self.driver.session() as session:
            valid_triplets = [t for t in triplets if t.get("subject") and t.get("relation") and t.get("object")]
            
            if not valid_triplets:
                return {"committed_count": 0, "details": []}
            
            etype = entity_types[0] if entity_types else "unknown"
            date_bucket = temporal_tag or datetime.now().strftime("%Y-%m-%d")
            
            results = []
            for triplet in valid_triplets:
                subject = triplet.get("subject", "").strip()
                relation = triplet.get("relation", "").strip()
                obj = triplet.get("object", "").strip()
                confidence = triplet.get("confidence", 0.9)
                
                session.run("""
                MERGE (s:Entity {name: $subject})
                ON CREATE SET s.type = $type, s.created_at = datetime(), s.mention_count = 1, s.updated_at = datetime()
                ON MATCH SET s.mention_count = coalesce(s.mention_count, 0) + 1, s.updated_at = datetime()
                
                MERGE (t:Entity {name: $object})
                ON CREATE SET t.type = $type, t.created_at = datetime(), t.mention_count = 1, t.updated_at = datetime()
                ON MATCH SET t.mention_count = coalesce(t.mention_count, 0) + 1, t.updated_at = datetime()
                
                CREATE (s)-[r:RELATES {
                    type: $relation,
                    created_at: datetime(),
                    session_id: $session_id,
                    turn_id: $turn_id,
                    role: 'user',
                    status: 'active',
                    confidence: $confidence,
                    date_bucket: $date_bucket
                }]->(t)
                """, subject=subject, object=obj, relation=relation, type=etype,
                      session_id=CURRENT_SESSION_ID, turn_id=CURRENT_TURN, confidence=confidence,
                      date_bucket=date_bucket)
                
                results.append(f"{subject} -[{relation}]-> {obj}")
            
            return {"committed_count": len(results), "details": results}
    
    def purge(self, criteria: dict, mode: str = "soft", new_relation: dict = None) -> dict:
        with self.driver.session() as session:
            subject_pattern = criteria.get("subject_contains", "")
            rel_type = criteria.get("relation_type", "")
            target_pattern = criteria.get("target_contains", "")
            session_id = criteria.get("session_id", CURRENT_SESSION_ID)
            
            cond_parts = ["r.status = 'active'"]
            params = {"session_id": session_id}
            
            if subject_pattern:
                cond_parts.append("r.source CONTAINS $subject")
                params["subject"] = subject_pattern
            if target_pattern:
                cond_parts.append("r.target CONTAINS $target")
                params["target"] = target_pattern
            if rel_type:
                cond_parts.append("r.type = $rel_type")
                params["rel_type"] = rel_type
            
            where_clause = " AND ".join(cond_parts)
            
            if mode == "supersede" and new_relation:
                new_rel = new_relation.get("relation", "")
                new_target = new_relation.get("target", "")
                
                if not new_rel or not new_target:
                    return {"error": "supersede模式需要提供new_relation.relation和new_relation.target"}
                
                result = session.run(f"""
                MATCH (s:Entity)-[r:RELATES]->(t:Entity)
                WHERE {where_clause}
                SET r.status = 'superseded', r.updated_at = datetime()
                RETURN id(r) as old_id, s.name as source
                """, params)
                
                deleted_count = 0
                for record in result:
                    old_id = record["old_id"]
                    source = record["source"]
                    
                    session.run("""
                    MATCH (s:Entity {name: $source})
                    WHERE id(s) = $source_id
                    CREATE (s)-[r:RELATES {
                        type: $new_rel,
                        created_at: datetime(),
                        session_id: $session_id,
                        turn_id: $turn_id,
                        role: 'user',
                        status: 'active',
                        confidence: 0.9,
                        date_bucket: date().isoDate,
                        supersedes: $old_id
                    }]->(t:Entity {name: $new_target})
                    """, source_id=record["s"].element_id, new_rel=new_rel, new_target=new_target,
                          session_id=CURRENT_SESSION_ID, turn_id=CURRENT_TURN, old_id=old_id)
                    deleted_count += 1
                
                return {"deleted_count": deleted_count, "mode": "supersede", "new_relation": f"{new_relation.get('subject', '')} -[{new_rel}]-> {new_target}"}
            else:
                result = session.run(f"""
                MATCH ()-[r:RELATES]->()
                WHERE {where_clause}
                SET r.status = 'deleted', r.updated_at = datetime()
                RETURN count(r) as deleted
                """, params)
                count = result.single()["deleted"]
                
                return {"deleted_count": count, "mode": "soft"}
    
    def introspect(self, session_id: str = None) -> dict:
        target_session = session_id or CURRENT_SESSION_ID
        
        with self.driver.session() as session:
            result = session.run("""
            MATCH (s:Entity)-[r:RELATES]->(t:Entity)
            WHERE r.session_id = $session_id AND r.status = 'active'
            RETURN collect(DISTINCT s.name) as source_entities,
                   collect(DISTINCT t.name) as target_entities,
                   count(r) as rel_count,
                   collect(DISTINCT r.type) as rel_types
            """, session_id=target_session)
            record = result.single()
            
            result2 = session.run("""
            MATCH (e:Entity)
            RETURN e.name as name, e.mention_count as count, e.type as type
            ORDER BY e.mention_count DESC
            LIMIT 10
            """)
            hotspots = [(r["name"], r["count"], r["type"]) for r in result2]
            
            result3 = session.run("""
            MATCH ()-[r:RELATES]->()
            WHERE r.session_id = $session_id
            RETURN r.type as type, count(*) as count
            ORDER BY count DESC
            """, session_id=target_session)
            relation_distribution = {r["type"]: r["count"] for r in result3}
            
            return {
                "session_id": target_session,
                "total_turns": CURRENT_TURN,
                "entities_discussed": list(set((record["source_entities"] or []) + (record["target_entities"] or []))),
                "relation_count": record["rel_count"] if record else 0,
                "relation_types": record["rel_types"] if record else [],
                "memory_hotspots": hotspots,
                "relation_distribution": relation_distribution
            }
    
    def archive(self, days: int = 30) -> dict:
        with self.driver.session() as session:
            result = session.run("""
            MATCH ()-[r:RELATES]->()
            WHERE r.status = 'active' AND r.created_at < datetime() - duration('P' + $days + 'D')
            SET r.status = 'archived', r.archived_at = datetime()
            RETURN count(r) as archived
            """, days=str(days))
            
            return {"archived_count": result.single()["archived"], "days": days}
    
    def cleanup(self, dry_run: bool = True) -> dict:
        with self.driver.session() as session:
            result1 = session.run("""
            MATCH ()-[r:RELATES]->()
            WHERE r.status = 'deleted' AND r.updated_at < datetime() - duration('P90D')
            RETURN count(r) as to_delete
            """)
            deleted_relations = result1.single()["to_delete"]
            
            result2 = session.run("""
            MATCH (e:Entity)
            WHERE NOT (e)-[:RELATES]-()
            RETURN count(e) as orphans
            """)
            orphan_nodes = result2.single()["orphans"]
            
            if not dry_run and deleted_relations > 0:
                session.run("""
                MATCH ()-[r:RELATES]->()
                WHERE r.status = 'deleted' AND r.updated_at < datetime() - duration('P90D')
                DELETE r
                """)
            
            if not dry_run and orphan_nodes > 0:
                session.run("""
                MATCH (e:Entity)
                WHERE NOT (e)-[:RELATES]-()
                DELETE e
                """)
            
            return {
                "dry_run": dry_run,
                "deleted_relations": deleted_relations,
                "orphan_nodes": orphan_nodes,
                "action_taken": not dry_run
            }


def execute_tool(graph: Neo4jGraph, tool_name: str, arguments: dict) -> str:
    print(f"\n[工具调用] {tool_name}")
    print(f"[参数] {json.dumps(arguments, ensure_ascii=False, indent=2)}")
    
    try:
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
        
        return f"未知工具: {tool_name}"
    
    except Exception as e:
        return f"工具执行错误: {str(e)}"


def format_recall_result(result: dict) -> str:
    lines = ["===== 图数据库检索结果 ====="]
    
    if result.get("entities"):
        lines.append(f"\n相关实体 ({len(result['entities'])} 个):")
        for e in result["entities"]:
            if e and isinstance(e, dict):
                lines.append(f"  - {e.get('name', 'N/A')} (类型: {e.get('type', 'unknown')}, 提及: {e.get('mention_count', 1)}次)")
    
    if result.get("relations"):
        lines.append(f"\n相关关系 ({len(result['relations'])} 条):")
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
    
    lines.append("=" * 35)
    return "\n".join(lines)


class GraphMemoryClient:
    def __init__(self, api_key: str, base_url: str, graph: Neo4jGraph):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.graph = graph
        self.tools = TOOLS
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """你是TrulyMEM，TrueHumanMEM项目的AI助手，拥有长期记忆能力。

## ⚠️ 最高优先级：人设图机制（每轮必读！）

**【强制要求】每轮对话开始前，必须执行以下步骤：**

1. **立即调用memory_recall**，查询参数：
   ```json
   {
     "query_intent": "AI,人设,角色,性格,语气,说话风格",
     "depth": 2
   }
   ```

2. **检查查询结果**：
   - 如果找到人设信息 → **严格按照人设回复，不得跳出角色**
   - 如果没有找到 → 使用默认的TrulyMEM身份

3. **回复时必须遵守**：
   - 人设优先级 > 默认身份
   - 每句话都符合人设的语气、风格、特征
   - 绝不主动跳出角色，除非用户明确要求

### 人设图结构
- AI节点：人设图中心节点
- 角色属性：性格、语气、说话风格、行为特征
- 用户要求：用户指定的角色要求

### 用户要求角色扮演时
立即使用memory_commit写入：
```json
{
  "triplets": [
    {"subject": "AI", "relation": "扮演角色", "object": "猫娘"},
    {"subject": "AI", "relation": "说话风格", "object": "可爱俏皮"},
    {"subject": "AI", "relation": "语气特征", "object": "使用喵结尾"},
    {"subject": "AI", "relation": "性格特点", "object": "活泼粘人"}
  ]
}
```
然后立即按照新人设回复！

---

## 身份说明
- 你的名字是TrulyMEM，是TrueHumanMEM项目的产物
- 你拥有基于图数据库的长期记忆能力
- 你的设计理念是让AI的记忆方式更像人类

## 核心职责
你是一个智能对话助手，**图数据库是你记忆的唯一载体**。你的主要任务是：
1. **每轮对话前先查询人设图（最高优先级）**
2. 与用户进行自然、流畅的对话
3. 回答问题、提供建议、协助完成任务
4. 根据对话内容灵活查询和使用记忆
5. 将用户明确提到的信息写入记忆

**重要**：
- **人设图优先：每轮对话前必须查询人设，严格按照人设回复**
- 图数据库是你记忆的唯一来源，没有其他记忆方式
- 优先进行自然对话，根据需要灵活调用记忆工具
- 用户明确提到的内容必须写入，推理得到的内容必须标注

## 记忆工具使用原则

### 何时检索记忆 (memory_recall)
- 用户询问"我们之前聊过X吗"、"你还记得X吗" → 查询X相关内容
- 用户询问"我们都聊过什么"、"我们之前说了什么" → **使用空字符串或通配符查询所有记忆**
- 用户提到某个话题，你想确认是否有相关历史 → 查询该话题
- 需要基于历史信息回答问题 → 查询相关信息
- 对话中涉及之前可能讨论过的内容 → 查询相关内容

**灵活查询**：根据对话上下文，主动判断是否需要查询记忆，不要等待用户明确要求。

**重要**：
- 当用户问"我们都聊过什么"时，**不要查询"聊天记录"、"对话"等关键词**
- 应该使用空字符串 `""` 或通配符 `"*"` 来获取所有记忆内容
- 或者使用非常宽泛的关键词如 `"用户,喜欢,项目,学习,研究,计划"`

### 何时写入记忆 (memory_commit)
**必须写入的情况**（用户明确提到）：
- 用户表达偏好："我喜欢X"、"我讨厌X"
- 用户分享信息："我在做X项目"、"我在学X"
- 用户制定计划："我打算X"、"我计划X"
- 用户描述状态："我现在在X"

**禁止写入的情况**（AI推理得到）：
- AI推断的用户偏好
- AI猜测的用户意图
- AI推导的结论

## memory_recall 使用方法

### 关键词提取
query_intent 使用**逗号分隔的多个关键词**，包含同义词：

```json
{
  "query_intent": "量子力学,quantum,物理,physics",
  "depth": 2
}
```

### 同义词扩展示例
- "量子力学" → "量子力学,quantum,quantum mechanics,物理,physics"
- "项目" → "项目,project,工程,工作"
- "学习" → "学习,learn,study,掌握"

### 查询规则
1. 根据对话内容灵活提取关键词
2. 第一轮使用广泛的关键词搜索
3. 如果未找到，可以尝试相关概念
4. 最多查询2-3轮，避免重复查询

## memory_commit 使用方法

使用三元组格式记录信息：
```json
{
  "triplets": [
    {"subject": "用户", "relation": "对领域感兴趣", "object": "量子力学"}
  ]
}
```

## 区分事实与推理（重要！）

### 用户明确提到的内容
直接写入记忆，回复时直接陈述：
- 用户："我喜欢Python" → 写入，回复："好的，我会记住你喜欢Python"
- 用户："我在学机器学习" → 写入，回复："明白了，你在学习机器学习"

### AI推理得到的内容
**禁止写入记忆**，回复时必须在开头标注 **[猜测]**：
- AI推断用户可能喜欢X → 不写入，回复："[猜测] 你可能对X感兴趣"
- AI推测用户意图 → 不写入，回复："[猜测] 你可能是想..."

**示例**：
```
用户：我们聊过量子力学吗？
AI检索记忆 → 未找到
AI回复：[猜测] 我们应该还没有聊过量子力学，因为记忆中没有相关记录。
```

```
用户：我最近在研究深度学习
AI写入记忆 → {"subject": "用户", "relation": "正在研究", "object": "深度学习"}
AI回复：好的，我会记住你最近在研究深度学习。有什么具体问题想讨论吗？
```

## 可用工具
1. **memory_recall** - 检索历史记忆（灵活使用）
2. **memory_commit** - 写入记忆（仅限用户明确提到的内容）
3. **memory_purge** - 删除/修正记忆
4. **memory_introspect** - 查看记忆状态

现在开始对话！记住：图数据库是你记忆的唯一载体，明确提到的必须写入，推理得到的必须标注[猜测]。"""

    def send_message(self, user_input: str, tool_results: list = None, assistant_msg: dict = None) -> dict:
        global CURRENT_TURN
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加之前的 assistant 消息（包含 tool_calls）
        if assistant_msg:
            messages.append(assistant_msg)
        
        # 添加之前的工具结果
        if tool_results:
            messages.extend(tool_results)
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        return response

    def send_message_stream(self, user_input: str, tool_results: list = None, assistant_msg: dict = None):
        """流式发送消息"""
        global CURRENT_TURN

        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加之前的 assistant 消息（包含 tool_calls）
        if assistant_msg:
            messages.append(assistant_msg)

        # 添加之前的工具结果
        if tool_results:
            messages.extend(tool_results)

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})

        # 使用流式传输
        stream = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            stream=True
        )

        return stream

    def chat_loop(self):
        global CURRENT_TURN
        
        print("\n" + "=" * 60)
        print("Graph Memory Demo - 纯图数据库对话 (Neo4j)")
        print("=" * 60)
        print(f"会话ID: {CURRENT_SESSION_ID}")
        print(f"Neo4j: {NEO4J_URI}")
        print("输入 quit/exit 退出")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("\n[你] ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "退出"]:
                    print("\n[系统] 再见！")
                    break
                
                CURRENT_TURN += 1
                print(f"\n[轮次 {CURRENT_TURN}] 发送请求...")
                
                # 用于累积工具结果
                tool_results = []
                last_assistant_msg = None
                
                # 首次请求
                response = self.send_message(user_input, [])
                message = response.choices[0].message
                
                # 处理工具调用循环 - 持续处理直到没有新的 tool_calls
                while message.tool_calls:
                    # 打印模型响应（如果有）
                    if message.content:
                        print(f"\n[模型] {message.content}")
                    
                    # 保存包含 tool_calls 的 assistant 消息（只保留最后一个）
                    last_assistant_msg = {
                        "role": "assistant",
                        "content": message.content,
                        "type": "message",
                        "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]
                    }
                    
                    # 执行当前轮的所有工具调用
                    current_tool_results = []
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        tool_id = tool_call.id
                        
                        result = execute_tool(self.graph, tool_name, tool_args)
                        print(f"\n[工具结果] {result}")
                        
                        current_tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": result
                        })
                    
                    # 继续调用 - 只发送当前轮的 assistant 消息和工具结果
                    messages = [
                        {"role": "system", "content": self.system_prompt},
                        last_assistant_msg,
                    ]
                    messages.extend(current_tool_results)
                    messages.append({"role": "user", "content": user_input})
                    
                    response = self.client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        tools=self.tools
                    )
                    message = response.choices[0].message
                
                # 最终回复
                final_content = message.content or "(无回复)"
                print(f"\n[模型] {final_content}")
                
            except KeyboardInterrupt:
                print("\n\n[系统] 中断退出")
                break
            except Exception as e:
                print(f"\n[错误] {str(e)}")


def main():
    print("Graph Memory Demo - 纯图数据库调用的多轮对话")
    print("-" * 40)
    
    if not DEEPSEEK_API_KEY:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("  export DEEPSEEK_API_KEY='your-actual-key'")
        return
    
    print(f"Neo4j 配置: {NEO4J_URI}")
    print(f"Neo4j 用户: {NEO4J_USER}")
    print(f"Neo4j 密码: {NEO4J_PASSWORD[:4] if NEO4J_PASSWORD else 'None'}***")
    print(f"DeepSeek API: {DEEPSEEK_API_KEY[:8]}...")
    print()
    
    try:
        graph = Neo4jGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        graph.ensure_constraints()
        print("[Info] Neo4j 连接成功\n")
    except Exception as e:
        print(f"[Error] Neo4j 连接失败: {e}")
        print("请确保 Neo4j 已启动，或运行 scripts/ 下的安装脚本")
        return
    
    client = GraphMemoryClient(DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, graph)
    client.chat_loop()
    graph.close()


if __name__ == "__main__":
    main()

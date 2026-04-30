#!/usr/bin/env python3
"""
Graph Memory Client - 图记忆客户端核心实现（重构版）
使用模块化的工具和提示词系统
"""

import json
import os
import uuid
from datetime import datetime
from openai import OpenAI

from .tools import TOOLS
from .tool_executor import execute_tool
from .prompts.prompt_manager import PromptManager

# 环境配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek-v4-flash")

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j")

# 会话配置
CURRENT_SESSION_ID = f"session-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4]}"
CURRENT_TURN = 0


class Neo4jGraph:
    """Neo4j图数据库客户端"""
    
    def __init__(self, uri: str, user: str, password: str):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def ensure_constraints(self):
        """确保约束和索引存在"""
        with self.driver.session() as session:
            # 实体约束
            session.run("CREATE CONSTRAINT entity_name_constraint IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            session.run("CREATE CONSTRAINT session_id_constraint IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
            
            # 关系索引
            session.run("CREATE INDEX rel_created_at IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.created_at")
            session.run("CREATE INDEX rel_session_id IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.session_id")
            session.run("CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.type")
            session.run("CREATE INDEX rel_status IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.status")
            session.run("CREATE INDEX rel_date_bucket IF NOT EXISTS FOR ()-[r:RELATES]-() ON r.date_bucket")
            
            # 实体索引
            session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON e.type")
            session.run("CREATE INDEX entity_mention_count IF NOT EXISTS FOR (e:Entity) ON e.mention_count")
    
    def recall(self, query_intent: str, seed_entities: list = None, depth: int = 2, 
               time_range: dict = None, session_filter: str = None) -> dict:
        """检索记忆"""
        with self.driver.session() as session:
            # 支持逗号分隔的多个关键词
            keywords = [w.strip() for w in query_intent.replace(',', ' ').split() if len(w.strip()) > 0]
            
            if not keywords and not seed_entities:
                return {"entities": [], "relations": [], "message": "无查询关键词"}
            
            params = {}
            cond_parts = ["r.status = 'active'"]
            
            if session_filter:
                cond_parts.append("r.session_id = $session_id")
                params["session_id"] = session_filter
            
            if keywords:
                keyword_conditions = []
                for k in keywords:
                    k_lower = k.lower()
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
        """写入记忆"""
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
        """删除记忆"""
        with self.driver.session() as session:
            subject_pattern = criteria.get("subject_contains", "")
            rel_type = criteria.get("relation_type", "")
            target_pattern = criteria.get("target_contains", "")
            source_type = criteria.get("source_type", "")
            target_type = criteria.get("target_type", "")
            source_status = criteria.get("source_has_status", "")
            session_id = criteria.get("session_id", CURRENT_SESSION_ID)
            
            cond_parts = ["r.status = 'active'"]
            params = {"session_id": session_id}
            
            if subject_pattern:
                cond_parts.append("e.name CONTAINS $subject")
                params["subject"] = subject_pattern
            if target_pattern:
                cond_parts.append("t.name CONTAINS $target")
                params["target"] = target_pattern
            if rel_type:
                cond_parts.append("r.type = $rel_type")
                params["rel_type"] = rel_type
            if source_type:
                cond_parts.append("s.entity_type = $source_type")
                params["source_type"] = source_type
            if target_type:
                cond_parts.append("t.entity_type = $target_type")
                params["target_type"] = target_type
            if source_status:
                cond_parts.append("s.status = $source_status")
                params["source_status"] = source_status
            
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
                RETURN count(r) as count
                """, params)
                
                count = result.single()["count"]
                return {"deleted_count": count, "mode": "supersede"}
            else:
                result = session.run(f"""
                MATCH (s:Entity)-[r:RELATES]->(t:Entity)
                WHERE {where_clause}
                SET r.status = 'deleted', r.updated_at = datetime()
                RETURN count(r) as deleted
                """, params)
                count = result.single()["deleted"]
                
                # 删除孤立节点（没有任何关系的实体）
                orphan_result = session.run("""
                MATCH (e:Entity)
                WHERE NOT (e)-[:RELATES]-()
                DELETE e
                RETURN count(e) as orphans
                """)
                orphan_count = orphan_result.single()["orphans"]
                
                return {"deleted_count": count, "orphan_count": orphan_count, "mode": "soft"}
    
    def introspect(self, session_id: str = None) -> dict:
        """查看记忆状态"""
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
            
            return {
                "session_id": target_session,
                "total_turns": CURRENT_TURN,
                "entities_discussed": list(set((record["source_entities"] or []) + (record["target_entities"] or []))),
                "relation_count": record["rel_count"] if record else 0,
                "relation_types": record["rel_types"] if record else [],
                "memory_hotspots": hotspots
            }
    
    def archive(self, days: int = 30) -> dict:
        """归档旧记忆"""
        with self.driver.session() as session:
            result = session.run("""
            MATCH ()-[r:RELATES]->()
            WHERE r.status = 'active' AND r.created_at < datetime() - duration('P' + $days + 'D')
            SET r.status = 'archived', r.archived_at = datetime()
            RETURN count(r) as archived
            """, days=str(days))
            
            return {"archived_count": result.single()["archived"], "days": days}
    
    def cleanup(self, dry_run: bool = True) -> dict:
        """清理无效数据"""
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


class GraphMemoryClient:
    """图记忆客户端"""
    
    def __init__(self, api_key: str, base_url: str, graph, model: str = "deepseek-v4-flash"):
        # 清理可能存在的错误代理环境变量
        import os
        proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']
        for var in proxy_vars:
            if var in os.environ:
                value = os.environ[var]
                # 如果代理URL没有scheme前缀，添加http://
                if value and not value.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
                    os.environ[var] = f'http://{value}'
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.graph = graph
        self.tools = TOOLS
        self.model = model
        
        prompt_manager = PromptManager()
        self.system_prompt = prompt_manager.get_system_prompt()
    
    def send_message(self, user_input: str, tool_results: list = None, assistant_msg: dict = None) -> dict:
        """发送消息"""
        global CURRENT_TURN
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 添加 assistant 消息（包含 tool_calls）
        if assistant_msg:
            messages.append(assistant_msg)
        
        # 添加工具结果
        if tool_results:
            messages.extend(tool_results)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        return response
    
    def send_message_with_history(self, messages_history: list) -> dict:
        """使用消息历史发送消息"""
        global CURRENT_TURN
        
        # 构建完整消息列表
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(messages_history)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        return response

    def send_message_stream(self, user_input: str, tool_results: list = None, assistant_msg: dict = None):
        """流式发送消息"""
        global CURRENT_TURN

        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加用户消息
        messages.append({"role": "user", "content": user_input})

        # 添加 assistant 消息（包含 tool_calls）
        if assistant_msg:
            messages.append(assistant_msg)

        # 添加工具结果
        if tool_results:
            messages.extend(tool_results)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            stream=True
        )

        return stream

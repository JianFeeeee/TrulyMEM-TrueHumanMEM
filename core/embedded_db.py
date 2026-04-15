"""
内嵌图数据库 - 基于SQLite实现
无需Docker，开箱即用
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class EmbeddedGraphDB:
    """内嵌图数据库 - SQLite实现"""
    
    def __init__(self, db_path: str = "graph_memory.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # 创建实体表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT,
                mention_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                status TEXT DEFAULT 'active',
                session_id TEXT,
                turn_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_bucket TEXT,
                superseded_by INTEGER,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_source ON relations(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_target ON relations(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_type ON relations(relation_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_status ON relations(status)")
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='chat_records'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE chat_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_chat_created ON chat_records(created_at)")
        
        self.conn.commit()
    
    def ensure_constraints(self):
        """确保约束（兼容Neo4j接口）"""
        pass  # SQLite自动处理
    
    def recall(self, query_intent: str, seed_entities: List[str] = None,
               depth: int = 2, time_range: Dict = None,
               session_filter: str = None) -> Dict:
        """
        检索相关记忆
        
        Args:
            query_intent: 查询关键词（逗号分隔）
            seed_entities: 种子实体
            depth: 搜索深度
            time_range: 时间范围
            session_filter: 会话过滤
        
        Returns:
            检索结果
        """
        keywords = [w.strip().lower() for w in query_intent.replace(',', ' ').split() if w.strip()]

        cursor = self.conn.cursor()

        # 搜索实体
        entities = []
        entity_ids = set()

        # 如果没有关键词，返回所有实体（用于"我们都聊过什么"这类问题）
        if not keywords and not seed_entities:
            cursor.execute("""
                SELECT id, name, type, mention_count
                FROM entities
                ORDER BY mention_count DESC
                LIMIT 50
            """)

            for row in cursor.fetchall():
                entity_ids.add(row['id'])
                entities.append({
                    'name': row['name'],
                    'type': row['type'] or 'unknown',
                    'mention_count': row['mention_count']
                })
        else:
            # 有关键词，按关键词搜索
            for keyword in keywords:
                cursor.execute("""
                    SELECT id, name, type, mention_count
                    FROM entities
                    WHERE LOWER(name) LIKE ?
                """, (f"%{keyword}%",))

                for row in cursor.fetchall():
                    if row['id'] not in entity_ids:
                        entity_ids.add(row['id'])
                        entities.append({
                            'name': row['name'],
                            'type': row['type'] or 'unknown',
                            'mention_count': row['mention_count']
                        })
        
        # 搜索关系
        relations = []
        
        if entity_ids:
            placeholders = ','.join('?' * len(entity_ids))
            
            query = f"""
                SELECT r.id, e1.name as source, e2.name as target,
                       r.relation_type as type, r.confidence, r.session_id,
                       r.turn_id, r.created_at, r.status
                FROM relations r
                JOIN entities e1 ON r.source_id = e1.id
                JOIN entities e2 ON r.target_id = e2.id
                WHERE (r.source_id IN ({placeholders}) OR r.target_id IN ({placeholders}))
                  AND r.status = 'active'
            """
            
            params = list(entity_ids) + list(entity_ids)
            
            if session_filter:
                query += " AND r.session_id = ?"
                params.append(session_filter)
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                relations.append({
                    'source': row['source'],
                    'target': row['target'],
                    'type': row['type'],
                    'confidence': row['confidence'],
                    'session_id': row['session_id'],
                    'turn_id': row['turn_id'],
                    'created_at': row['created_at'],
                    'status': row['status']
                })
        
        return {
            "entities": entities,
            "relations": relations,
            "message": f"找到 {len(entities)} 个实体, {len(relations)} 条关系"
        }
    
    def commit(self, triplets: List[Dict], entity_types: Dict = None,
               temporal_tag: str = None, session_id: str = None,
               turn_id: int = None) -> Dict:
        """
        写入记忆
        
        Args:
            triplets: 三元组列表
            entity_types: 实体类型
            temporal_tag: 时间标签
            session_id: 会话ID
            turn_id: 轮次ID
        
        Returns:
            写入结果
        """
        cursor = self.conn.cursor()
        
        created_entities = 0
        created_relations = 0
        
        for triplet in triplets:
            subject = triplet.get('subject')
            relation = triplet.get('relation')
            obj = triplet.get('object')
            confidence = triplet.get('confidence', 1.0)
            
            if not all([subject, relation, obj]):
                continue
            
            # 创建或更新实体
            for entity_name in [subject, obj]:
                entity_type = entity_types.get(entity_name) if entity_types else None
                
                cursor.execute("""
                    INSERT INTO entities (name, type)
                    VALUES (?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        mention_count = mention_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                """, (entity_name, entity_type))
                
                if cursor.rowcount > 0:
                    created_entities += 1
            
            # 获取实体ID
            cursor.execute("SELECT id FROM entities WHERE name = ?", (subject,))
            source_id = cursor.fetchone()['id']
            
            cursor.execute("SELECT id FROM entities WHERE name = ?", (obj,))
            target_id = cursor.fetchone()['id']
            
            # 创建关系
            date_bucket = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT INTO relations (
                    source_id, target_id, relation_type, confidence,
                    session_id, turn_id, date_bucket
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source_id, target_id, relation, confidence,
                  session_id, turn_id, date_bucket))
            
            created_relations += 1
        
        self.conn.commit()
        
        return {
            "created_entities": created_entities,
            "created_relations": created_relations,
            "message": f"创建了 {created_entities} 个实体, {created_relations} 条关系"
        }
    
    def purge(self, criteria: Dict, mode: str = "soft",
              new_relation: Dict = None) -> Dict:
        """
        删除或修正记忆
        
        Args:
            criteria: 删除条件
            mode: 删除模式 (soft/hard)
            new_relation: 替代关系
        
        Returns:
            删除结果
        """
        cursor = self.conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if criteria.get('source'):
            cursor.execute("SELECT id FROM entities WHERE name = ?", (criteria['source'],))
            row = cursor.fetchone()
            if row:
                conditions.append("source_id = ?")
                params.append(row['id'])
        
        if criteria.get('target'):
            cursor.execute("SELECT id FROM entities WHERE name = ?", (criteria['target'],))
            row = cursor.fetchone()
            if row:
                conditions.append("target_id = ?")
                params.append(row['id'])
        
        if criteria.get('relation'):
            conditions.append("relation_type = ?")
            params.append(criteria['relation'])
        
        if not conditions:
            return {"deleted": 0, "message": "无删除条件"}
        
        where_clause = " AND ".join(conditions)
        
        if mode == "soft":
            cursor.execute(f"""
                UPDATE relations
                SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                WHERE {where_clause} AND status = 'active'
            """, params)
        else:
            cursor.execute(f"""
                DELETE FROM relations
                WHERE {where_clause}
            """, params)
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        return {
            "deleted": deleted,
            "mode": mode,
            "message": f"删除了 {deleted} 条关系"
        }
    
    def introspect(self, session_id: str = None) -> Dict:
        """
        查看会话状态
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话状态
        """
        cursor = self.conn.cursor()
        
        # 统计实体
        cursor.execute("SELECT COUNT(*) as count FROM entities")
        entity_count = cursor.fetchone()['count']
        
        # 统计关系
        cursor.execute("SELECT COUNT(*) as count FROM relations WHERE status = 'active'")
        relation_count = cursor.fetchone()['count']
        
        return {
            "entity_count": entity_count,
            "relation_count": relation_count,
            "session_id": session_id,
            "message": f"数据库包含 {entity_count} 个实体, {relation_count} 条关系"
        }
    
    def archive(self, days: int = 30) -> Dict:
        """归档旧关系"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE relations
            SET status = 'archived', updated_at = CURRENT_TIMESTAMP
            WHERE status = 'active'
              AND created_at < datetime('now', ?)
        """, (f'-{days} days',))
        
        archived = cursor.rowcount
        self.conn.commit()
        
        return {
            "archived": archived,
            "message": f"归档了 {archived} 条关系"
        }
    
    def cleanup(self, dry_run: bool = True) -> Dict:
        """清理已删除数据"""
        cursor = self.conn.cursor()
        
        if dry_run:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM relations
                WHERE status = 'deleted'
                  AND updated_at < datetime('now', '-90 days')
            """)
            deleted_relations = cursor.fetchone()['count']
            
            return {
                "dry_run": True,
                "deleted_relations": deleted_relations,
                "message": f"将删除 {deleted_relations} 条关系"
            }
        else:
            cursor.execute("""
                DELETE FROM relations
                WHERE status = 'deleted'
                  AND updated_at < datetime('now', '-90 days')
            """)
            deleted = cursor.rowcount
            self.conn.commit()
            
            return {
                "dry_run": False,
                "deleted": deleted,
                "message": f"删除了 {deleted} 条关系"
            }
    
    def save_chat_records(self, messages: list) -> Dict:
        """保存聊天记录到数据库"""
        cursor = self.conn.cursor()
        
        saved = 0
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                cursor.execute(
                    "INSERT INTO chat_records (role, content) VALUES (?, ?)",
                    (role, content)
                )
                saved += 1
        
        self.conn.commit()
        
        cursor.execute("""
            DELETE FROM chat_records 
            WHERE id NOT IN (
                SELECT id FROM chat_records 
                ORDER BY id DESC 
                LIMIT 500
            )
        """)
        self.conn.commit()
        
        return {"saved": saved}
    
    def get_chat_records(self, limit: int = 500) -> list:
        """从数据库获取聊天记录"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, content FROM chat_records 
            ORDER BY id ASC LIMIT ?
        """, (limit,))
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    
    def clear_chat_records(self) -> Dict:
        """清空聊天记录（保留图数据库）"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM chat_records")
        self.conn.commit()
        return {"cleared": True}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 兼容性别名
Neo4jGraph = EmbeddedGraphDB


if __name__ == '__main__':
    # 测试
    print("Testing Embedded Graph Database...")
    
    with EmbeddedGraphDB("test.db") as db:
        # 写入测试
        result = db.commit(
            triplets=[
                {"subject": "用户", "relation": "喜欢", "object": "Python"},
                {"subject": "用户", "relation": "学习", "object": "AI"}
            ],
            session_id="test-session",
            turn_id=1
        )
        print(f"Commit: {result}")
        
        # 检索测试
        result = db.recall("Python,AI")
        print(f"Recall: {result}")
        
        # 状态测试
        result = db.introspect()
        print(f"Introspect: {result}")
    
    print("\nTest completed!")

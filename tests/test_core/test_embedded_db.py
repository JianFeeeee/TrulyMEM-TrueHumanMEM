"""嵌入式数据库测试"""

import pytest
import tempfile
import os
from core import EmbeddedGraphDB


@pytest.fixture
def db():
    """创建临时数据库用于测试"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = EmbeddedGraphDB(db_path)
    yield db
    
    db.close()
    os.unlink(db_path)


def test_db_init(db):
    """测试数据库初始化"""
    assert db.conn is not None
    assert db.db_path.exists()


def test_commit_and_recall(db):
    """测试写入和检索记忆"""
    result = db.commit(
        triplets=[
            {"subject": "用户", "relation": "喜欢", "object": "Python"},
            {"subject": "用户", "relation": "正在学习", "object": "AI"}
        ],
        session_id="test-session",
        turn_id=1
    )
    
    assert result["created_entities"] >= 2
    assert result["created_relations"] >= 2


def test_recall_with_keywords(db):
    """测试关键词检索"""
    db.commit(
        triplets=[
            {"subject": "项目A", "relation": "使用技术", "object": "React"}
        ]
    )
    
    result = db.recall("React")
    assert len(result["entities"]) > 0


def test_recall_empty_keywords(db):
    """测试空关键词检索"""
    db.commit(
        triplets=[
            {"subject": "测试实体", "relation": "关系", "object": "测试对象"}
        ]
    )
    
    result = db.recall("")
    assert len(result["entities"]) > 0


def test_purge_soft(db):
    """测试软删除"""
    db.commit(
        triplets=[
            {"subject": "待删除", "relation": "测试", "object": "删除内容"}
        ]
    )
    
    result = db.purge(
        criteria={"source": "待删除"},
        mode="soft"
    )
    
    assert result["deleted"] >= 0
    assert result["mode"] == "soft"


def test_introspect(db):
    """测试状态查看"""
    db.commit(
        triplets=[
            {"subject": "实体1", "relation": "关系", "object": "实体2"}
        ]
    )
    
    result = db.introspect()
    
    assert "entity_count" in result
    assert "relation_count" in result
    assert result["entity_count"] >= 1


def test_archive(db):
    """测试归档"""
    result = db.archive(days=30)
    assert "archived" in result


def test_cleanup_dry_run(db):
    """测试清理（预览模式）"""
    result = db.cleanup(dry_run=True)
    
    assert result["dry_run"] is True
    assert "deleted_relations" in result


def test_multiple_triplets(db):
    """测试批量写入"""
    result = db.commit(
        triplets=[
            {"subject": "实体A", "relation": "关系1", "object": "实体B"},
            {"subject": "实体B", "relation": "关系2", "object": "实体C"},
            {"subject": "实体C", "relation": "关系3", "object": "实体A"}
        ],
        session_id="batch-test",
        turn_id=1
    )
    
    assert result["created_entities"] >= 3
    assert result["created_relations"] == 3


def test_entity_mention_count(db):
    """测试实体提及次数增加"""
    db.commit(
        triplets=[{"subject": "热门实体", "relation": "关系", "object": "对象1"}]
    )
    db.commit(
        triplets=[{"subject": "热门实体", "relation": "关系", "object": "对象2"}]
    )
    
    result = db.recall("热门实体")
    entity = next((e for e in result["entities"] if e["name"] == "热门实体"), None)
    
    assert entity is not None
    assert entity["mention_count"] >= 2


def test_close_and_context_manager():
    """测试关闭和上下文管理器"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        with EmbeddedGraphDB(db_path) as db:
            db.commit(
                triplets=[{"subject": "测试", "relation": "上下文", "object": "管理器"}]
            )
            assert db.conn is not None
        
        with EmbeddedGraphDB(db_path) as db:
            result = db.introspect()
            assert result["entity_count"] >= 1
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_save_and_get_chat_records(db):
    """测试聊天记录保存和读取"""
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么可以帮你？"}
    ]
    
    result = db.save_chat_records(messages)
    assert result["saved"] == 2
    
    history = db.get_chat_records()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "你好"
    assert history[1]["role"] == "assistant"


def test_chat_records_limit_500(db):
    """测试聊天记录限制500条"""
    for i in range(600):
        db.save_chat_records([{"role": "user", "content": f"消息{i}"}])
    
    history = db.get_chat_records()
    assert len(history) == 500


def test_get_chat_records_default_limit(db):
    """测试默认limit参数"""
    for i in range(100):
        db.save_chat_records([{"role": "user", "content": f"msg{i}"}])
    
    history_50 = db.get_chat_records(limit=50)
    assert len(history_50) == 50
    
    history_default = db.get_chat_records()
    assert len(history_default) == 100


def test_clear_chat_records(db):
    """测试清空聊天记录"""
    db.save_chat_records([
        {"role": "user", "content": "测试1"},
        {"role": "assistant", "content": "回复1"},
        {"role": "user", "content": "测试2"},
    ])
    
    history = db.get_chat_records()
    assert len(history) == 3
    
    result = db.clear_chat_records()
    assert result["cleared"] is True
    
    history_after = db.get_chat_records()
    assert len(history_after) == 0

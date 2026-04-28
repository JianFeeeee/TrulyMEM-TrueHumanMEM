"""
自动迁移模块 - 从旧版单用户架构迁移到多用户隔离架构
"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


def _trulymem_dir() -> Path:
    return Path.home() / ".trulymem"

def _old_config_path() -> Path:
    return _trulymem_dir() / "config.json"

def _old_db_path() -> Path:
    return _trulymem_dir() / "graph_memory.db"

def _new_global_db_path() -> Path:
    return _trulymem_dir() / "trulymem.db"

def _migrated_flag() -> Path:
    return _trulymem_dir() / ".migrated"


def need_migration() -> bool:
    """检测是否需要迁移"""
    # 如果已经迁移过，不需要再迁移
    if is_migrated():
        return False
    
    old_config_exists = _old_config_path().exists()
    old_db_exists = _old_db_path().exists()
    new_db_exists = _new_global_db_path().exists()
    if (old_config_exists or old_db_exists) and not new_db_exists:
        return True
    
    return False


def is_migrated() -> bool:
    """检查是否已完成迁移"""
    return _migrated_flag().exists()


def _mark_migrated():
    """标记迁移完成"""
    _trulymem_dir().mkdir(parents=True, exist_ok=True)
    with open(_migrated_flag(), 'w') as f:
        f.write(datetime.now().isoformat())


def run_migration(username: str, password: str) -> Dict:
    """
    执行迁移
    
    Args:
        username: 新用户名
        password: 新用户密码
    
    Returns:
        迁移结果字典
    """
    try:
        # 1. 创建用户目录
        user_dir = _trulymem_dir() / username
        user_dir.mkdir(parents=True, exist_ok=True)
        new_config_path = user_dir / "config.json"
        if _old_config_path().exists():
            shutil.copy2(_old_config_path(), new_config_path)
        new_db_path = user_dir / f"{username}_graph.db"
        if _old_db_path().exists():
            shutil.copy2(_old_db_path(), new_db_path)
        
        # 4. 创建全局数据库并写入 web_users 表
        from .embedded_db import EmbeddedGraphDB
        
        global_db = EmbeddedGraphDB(db_path=str(_new_global_db_path()))
        
        # 设置用户（会自动创建记录）
        result = global_db.set_web_user(username, password)
        if not result.get("success"):
            return {"success": False, "error": f"创建用户失败: {result.get('error')}"}
        
        # 如果用户目录已存在，更新路径（确保正确）
        cursor = global_db.conn.cursor()
        config_path = str(new_config_path)
        db_path = str(new_db_path)
        cursor.execute("""
            UPDATE web_users 
            SET config_path = ?, db_path = ?
            WHERE username = ?
        """, (config_path, db_path, username))
        global_db.conn.commit()
        
        # 5. 标记迁移完成
        _mark_migrated()
        
        global_db.close()
        
        return {
            "success": True,
            "username": username,
            "config_path": config_path,
            "db_path": db_path,
            "message": "迁移完成"
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def rollback_migration():
    """回滚迁移（用于失败恢复）"""
    try:
        # 删除全局数据库
        if _new_global_db_path().exists():
            _new_global_db_path().unlink()
        if _migrated_flag().exists():
            _migrated_flag().unlink()
        
        return {"success": True, "message": "回滚完成"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == '__main__':
    # 测试
    print("Migration module test")
    print(f"Need migration: {need_migration()}")
    print(f"Is migrated: {is_migrated()}")

"""
核心逻辑导入 - 优先使用内嵌数据库
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

# 数据库配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "graphmemory123")

# 优先使用内嵌数据库
USE_EMBEDDED_DB = os.getenv("USE_EMBEDDED_DB", "true").lower() == "true"

if USE_EMBEDDED_DB:
    # 使用内嵌SQLite数据库
    from .embedded_db import EmbeddedGraphDB as Neo4jGraph
    print("[INFO] Using embedded SQLite database (no Docker needed)")
else:
    # 使用Neo4j数据库
    try:
        from graph_memory_demo import Neo4jGraph
        print("[INFO] Using Neo4j database")
    except ImportError:
        from .embedded_db import EmbeddedGraphDB as Neo4jGraph
        print("[INFO] Fallback to embedded SQLite database")

# 导入其他组件
from graph_memory_demo import (
    GraphMemoryClient,
    TOOLS,
    execute_tool,
)

__all__ = [
    "Neo4jGraph",
    "GraphMemoryClient",
    "TOOLS",
    "execute_tool",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "MODEL_NAME",
    "NEO4J_URI",
    "NEO4J_USER",
    "NEO4J_PASSWORD",
]

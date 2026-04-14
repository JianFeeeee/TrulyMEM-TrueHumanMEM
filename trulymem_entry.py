#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 用户配置文件始终放在用户目录
CONFIG_PATH = Path.home() / ".trulymem" / "config.json"
DB_PATH = Path.home() / ".trulymem" / "graph_memory.db"

# 源码运行时使用项目目录，打包后使用用户目录
if getattr(sys, 'frozen', False):
    # 打包版本：创建用户目录
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
else:
    # 源码版本：检查项目目录是否有配置（向后兼容）
    project_dir = Path(__file__).parent
    project_config = project_dir / "config.json"
    project_db = project_dir / "graph_memory.db"
    
    if project_config.exists():
        CONFIG_PATH = project_config
    if project_db.exists():
        DB_PATH = project_db

sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

from core import BackendServer
from ui import GraphMemoryApp


def main():
    backend_server = BackendServer(
        db_path=str(DB_PATH),
        use_embedded_db=True,
        config_file=str(CONFIG_PATH)
    )
    backend_server.start()
    
    app = GraphMemoryApp(backend_server=backend_server, config_file=str(CONFIG_PATH))
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n退出")
    finally:
        backend_server.shutdown()


if __name__ == "__main__":
    main()
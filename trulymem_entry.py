#!/usr/bin/env python3
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))
import os
os.chdir(application_path)

from core import BackendServer
from ui import GraphMemoryApp
from ui.services.config_service import ConfigService


def main():
    # 配置文件保存在应用根目录（exe同级目录或源码根目录）
    config_file = application_path / "config.json"
    
    # 加载配置
    config_service = ConfigService(config_file=config_file)
    config = config_service.get_config()
    
    backend_server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
    backend_server.start(api_key=config.api_key, base_url=config.base_url)
    
    app = GraphMemoryApp(backend_server=backend_server, config_service=config_service)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n退出")
    finally:
        backend_server.shutdown()


if __name__ == "__main__":
    main()
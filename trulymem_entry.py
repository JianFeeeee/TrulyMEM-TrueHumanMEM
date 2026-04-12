#!/usr/bin/env python3
import sys
import os
from pathlib import Path

if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

os.chdir(application_path)

if str(application_path) not in sys.path:
    sys.path.insert(0, str(application_path))

from core import BackendServer
from ui import GraphMemoryApp, AppConfig


def main():
    backend_server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
    
    try:
        config = AppConfig.from_env()
        backend_server.start(api_key=config.api_key, base_url=config.base_url)
    except Exception as e:
        print(f"后端启动失败: {e}")
    
    app = GraphMemoryApp(backend_server=backend_server)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n应用已退出")
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        backend_server.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
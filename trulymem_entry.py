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


def main():
    backend_server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
    backend_server.start(api_key="", base_url="https://api.deepseek.com")
    
    app = GraphMemoryApp(backend_server=backend_server)
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n退出")
    finally:
        backend_server.shutdown()


if __name__ == "__main__":
    main()
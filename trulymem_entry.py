#!/usr/bin/env python3
import argparse
import sys
import os
import signal
import threading
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
    parser = argparse.ArgumentParser(description='TrulyMEM - True Human Memory')
    parser.add_argument('--web', action='store_true', help='以 Web 服务模式启动（headless，不启动 TUI）')
    parser.add_argument('--port', type=int, default=4096, help='Web 服务端口（默认 4096）')
    args = parser.parse_args()

    if args.web:
        # Web headless 模式 — web_api.run_web_server 会自动初始化 Backend
        from core.web_api import run_web_server, stop_web_server

        print(f"TrulyMEM Web 服务启动在 http://0.0.0.0:{args.port}")
        run_web_server(port=args.port, host='0.0.0.0')

        # 阻塞主线程直到收到信号
        shutdown_event = threading.Event()
        def _handle_signal(signum, frame):
            print("\n收到停止信号，正在关闭...")
            shutdown_event.set()
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        shutdown_event.wait()
        stop_web_server()
        print("TrulyMEM Web 服务已停止")
    else:
        # TUI 模式（默认）
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
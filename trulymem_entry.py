#!/usr/bin/env python3
"""
TrulyMEM 独立入口文件
用于打包为可执行文件
"""

import sys
import os
from pathlib import Path

# 确保工作目录正确
if getattr(sys, 'frozen', False):
    # 打包后的可执行文件
    application_path = Path(sys.executable).parent
else:
    # 开发环境
    application_path = Path(__file__).parent

# 切换到应用目录
os.chdir(application_path)

# 添加项目路径
if str(application_path) not in sys.path:
    sys.path.insert(0, str(application_path))

# 导入并运行应用
from graph_memory_tui.app import GraphMemoryApp

def main():
    """主函数"""
    try:
        app = GraphMemoryApp()
        app.run()
    except KeyboardInterrupt:
        print("\n应用已退出")
        sys.exit(0)
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

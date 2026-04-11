"""Graph Memory TUI 入口"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from .app import GraphMemoryApp
from .models.config import AppConfig


def main():
    """主函数"""
    try:
        # 不传入配置，让应用自己从配置文件或环境变量加载
        app = GraphMemoryApp()
        app.run()

    except KeyboardInterrupt:
        print("\n应用已退出")
        sys.exit(0)

    except Exception as e:
        print(f"应用启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

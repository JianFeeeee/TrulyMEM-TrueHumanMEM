# TrulyMEM - TrueHumanMEM

> **📜 开源协议**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)  
> 本项目自由开源，可自由使用、修改和分发，但修改后的作品必须以相同许可证发布。

**让 AI 拥有自知、可塑、有分寸感的长期记忆**

*The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## 简介

TrulyMEM (TrueHumanMEM) 是一个让 AI 拥有长期记忆能力的图记忆系统。通过 SQLite 内嵌图数据库存储实体关系，让 AI 能够像人类一样记忆、回忆和管理信息。

### 核心特性

- 🧠 **长期记忆** - 基于 SQLite 图数据库的持久化存储，开箱即用
- 🎭 **人设图机制** - AI 角色保持和角色扮演支持
- 🔗 **工作记忆链** - 维持对话连贯性的任务跟踪机制
- 🖥️ **现代化 TUI** - 基于 Textual 框架的终端用户界面，键盘驱动
- 💾 **内嵌数据库** - SQLite 实现，无需 Docker/Neo4j
- 📦 **独立部署** - 支持打包为独立可执行文件
- 🌍 **跨平台** - 支持 Windows/Linux/macOS
- 🔌 **后端独立** - 后端可脱离 UI 独立运行

- 该项目最核心的机制在于，一切皆图。llm推理时产生与需要读取的一切数据，均以三元组的形式存储在图数据库中，即“起始节点”，“关系”，“目标节点”。这为llm提供了一整套可记录可溯源的关系存储机制。相较传统messages数组上下文，显著提高了模型输入的质量，更加充分的利用了模型有限的上下文空间。同时也保证了模型的上下文消息不会随着聊天轮次的叠加逐渐膨胀，最终触发记忆压缩或滑动窗口机制，造成记忆的废弃。从根本上解决模型的长期记忆问题，为llm记忆存储提供了新范式
---

## 快速开始

### 方式一：打包后的可执行文件

```bash
# Windows: TrulyMEM.exe
# Linux/macOS: TrulyMEM
chmod +x TrulyMEM
./TrulyMEM
```

### 方式二：从源码运行

```bash
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

pip install -r requirements.txt

python trulymem_entry.py
```

### 配置

1. 按 **F2** 展开侧边栏
2. 输入 **API Key**（支持 DeepSeek、OpenAI 等兼容 API）
3. 按 **Enter** 保存配置
4. 开始对话！

---

## 架构设计

### 核心原则

- **后端独立**: BackendServer 可脱离 UI 独立运行
- **数据包通信**: 所有通信使用 Packet 格式 `{id, type, body}`
- **多线程**: 后端在独立线程处理请求
- **UI 简化**: UI 仅负责输入和显示

### 数据包协议

```python
@dataclass
class Packet:
    id: str           # 包ID，用于识别
    type: PacketType  # MESSAGE | CONFIG | TOOL | STATUS | HISTORY
    body: Dict         # 包体
```

### 项目结构

```
TrulyMEM-TrueHumanMEM/
├── trulymem_entry.py    # 入口
├── core/               # 后端（独立运行）
│   ├── __init__.py    # BackendServer, BackendClient, Packet
│   ├── embedded_db.py # SQLite 图数据库
│   ├── graph_client.py # LLM 客户端
│   └── tools/         # 工具定义
├── ui/               # TUI 显示层
│   ├── app.py        # 主应用
│   ├── widgets/     # UI 组件
│   └── models/       # 数据模型
└── tests/            # 测试 (37 tests)
```

### 启动流程

```python
# 1. 加载配置
from ui.services.config_service import ConfigService
config_service = ConfigService(config_file="config.json")
config = config_service.get_config()

# 2. 创建后端
server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
server.start(api_key=config.api_key, base_url=config.base_url)

# 3. 创建UI（可选，后端可独立使用）
app = GraphMemoryApp(backend_server=server, config_service=config_service)
app.run()

# 或直接使用后端
client = BackendClient(server)
result = client.process_message("hello")
```

---

## 功能说明

### 记忆管理工具

| 工具 | 功能 | 说明 |
|------|------|------|
| `memory_recall` | 检索记忆 | 根据意图查询相关记忆 |
| `memory_commit` | 写入记忆 | 将信息存储为图结构 |
| `memory_purge` | 删除记忆 | 删除过期或错误信息 |
| `memory_introspect` | 查看状态 | 查看记忆系统状态 |
| `memory_archive` | 归档记忆 | 归档旧记忆 |
| `memory_cleanup` | 清理数据 | 清理无效数据 |

### 人设工具

| 工具 | 功能 | 说明 |
|------|------|------|
| `persona_update` | 更新人设 | 修改 AI 的角色、性格、语气 |
| `persona_clear` | 清除人设 | 恢复默认身份 |

### 任务工具（工作记忆链）

| 工具 | 功能 | 说明 |
|------|------|------|
| `task_create` | 创建任务 | 跟踪连续性任务 |
| `task_set_state` | 设置状态 | 更新任务状态 |
| `task_delete` | 删除任务 | 清理完成任务 |
| `task_link_info` | 关联信息 | 连接任务与记忆 |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏 |
| F3 | 工具详情 |
| F5 | 清屏 |
| F6 | 退出 |

---

## 测试

```bash
pytest tests/
```

37 个测试用例覆盖：
- 数据包协议
- 后端初始化/启动/关闭
- 客户端方法
- 配置管理
- 消息历史
- UI 组件
- 集成测试

---

## 技术栈

- **Python 3.8+** - 编程语言
- **Textual** - TUI 框架
- **SQLite** - 内嵌图数据库
- **OpenAI SDK** - API 调用（兼容 DeepSeek）
- **threading** - 多线程通信
- **queue** - 线程安全队列

---

## 许可证

本项目采用 **GNU General Public License v3.0 (GPLv3)** 许可证开源。

详见 [LICENSE](LICENSE) 文件。

> **⚠️ 使用本项目即表示您同意：**
> - 可以自由使用、修改和分发
> - 必须保留版权声明和许可证
> - 修改后的作品必须以 GPLv3 许可证发布
> - 必须提供源代码

---
## 特别鸣谢（不分先后）
- 感谢 [Prof.Meiting Wang ](https://www.xxmu.edu.cn/yxgcxy/info/1260/4252.htm) 为本项目提供学术指导

- 感谢 [逝水秋生白](https://atomgit.com/cenber)为 本项目提供的架构支持

- 感谢 anzhitinglan 为本项目提供的测试资源支持与相关指导

- 感谢 崔莉萍老师 为本项目提供的理论指导

- 感谢 Annie 为本项目提供的专业指导

- 感谢 王梓沣，马悦华，隆梦婷 三位同学提供的学术资料与神经科学理论支持
---
## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request
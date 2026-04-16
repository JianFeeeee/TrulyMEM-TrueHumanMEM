# TrulyMEM 架构设计

## 核心原则

- 键盘驱动，零鼠标依赖
- 极简视觉，信息密度优先
- 工具痕迹默认隐藏，需要时可展开
- TUI 与后端分离，多线程通信
- **一切皆图**，AI 推理全部在后端

## 项目结构

```
TrulyMEM-TrueHumanMEM/
├── trulymem_entry.py    # 入口：先启动 core → 再启动 ui
├── core/               # 后端/业务逻辑
│   ├── __init__.py     # 导出 BackendServer, BackendClient, EmbeddedGraphDB
│   ├── server.py       # BackendServer (Packet 通信协议)
│   ├── client.py       # BackendClient (Packet 协议客户端)
│   ├── embedded_db.py  # SQLite 图数据库实现
│   ├── graph_client.py # OpenAI/DeepSeek API 客户端
│   ├── tool_executor.py # 工具执行器
│   ├── tool_limiter.py # 工具调用限制器
│   ├── tools/          # 工具定义
│   │   └── memory_tools.py
│   └── prompts/        # 提示词管理
├── ui/                 # TUI 显示层（仅显示，无 AI 逻辑）
│   ├── __init__.py     # 导出 GraphMemoryApp
│   ├── app.py          # GraphMemoryApp (通过 BackendClient 通信)
│   ├── widgets/        # TUI 组件
│   ├── models/         # 数据模型
│   ├── services/       # 服务层（仅配置管理）
│   ├── handlers/      # 事件处理
│   └── styles/         # 样式文件
└── tests/              # 测试 (54 tests)
```

## 架构图

```
trulymem_entry.py
    │
    ├─ BackendServer.start() → 独立线程运行
    │   ├─ 处理 PROCESS_MESSAGE 请求 → AI 推理 + 工具调用
    │   ├─ 处理 EXECUTE_TOOL 请求 → 外部工具调用（不限次数）
    │   ├─ 处理 GET/SET_CONFIG 请求
    │   └─ 管理 GraphMemoryClient, EmbeddedGraphDB
    │
    └─ GraphMemoryApp(backend_server=server)
            │
            └─ BackendClient ← Packet 通信 → BackendServer
```

## 组件职责

### core/ (后端)

| 组件 | 职责 |
|------|------|
| `server.py` | Packet 协议处理，多线程队列通信，AI 推理，工具限制 |
| `client.py` | 客户端封装，UI 与后端通信桥梁 |
| `embedded_db.py` | SQLite 图数据库 CRUD |
| `graph_client.py` | OpenAI/DeepSeek API 客户端 |
| `tool_executor.py` | 工具执行逻辑 |
| `tool_limiter.py` | 工具调用频率限制（仅限 AI 推理） |

### ui/ (显示层)

| 组件 | 职责 |
|------|------|
| `app.py` | Textual 应用主类，仅通过 BackendClient 通信 |
| `services/` | 仅配置管理，无 AI 逻辑 |

### 通信协议

UI 与后端通过 **Packet 通信协议** 交互：

```python
from core import BackendServer, BackendClient, Packet, PacketType

# 后端启动
server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
server.start(api_key="your-key")

# 客户端通信
client = BackendClient(server)
result = client.process_message("你好")  # AI 推理
result = client.execute_tool("memory_introspect", {})  # 外部工具调用
```

---

## 数据流

```
用户输入 → InputBox → on_input_box_send_message
    ↓
BackendClient.process_message(user_input)
    ↓
Packet (type=PROCESS_MESSAGE) → queue.Queue
    ↓
BackendServer (独立线程)
    ↓
GraphMemoryClient.send_message_with_history()
    ↓
OpenAI API / DeepSeek API
    ↓
execute_tool() + ToolLimiter (AI 推理时受限)
    ↓
EmbeddedGraphDB (图数据库)
    ↓
循环调用 API 直到无 tool_calls
    ↓
Packet 响应返回
    ↓
MessageHistory 显示
```

---

## 启动流程

```python
# trulymem_entry.py
def main():
    # 配置文件路径 (~/.trulymem/config.json 或项目目录)
    CONFIG_PATH = Path.home() / ".trulymem" / "config.json"
    DB_PATH = Path.home() / ".trulymem" / "graph_memory.db"
    
    # 创建后端（配置由后端管理）
    backend_server = BackendServer(
        db_path=str(DB_PATH),
        use_embedded_db=True,
        config_file=str(CONFIG_PATH)
    )
    backend_server.start()  # 自动加载配置
    
    # 创建UI（通过 BackendClient 通信）
    app = GraphMemoryApp(backend_server=backend_server, config_file=str(CONFIG_PATH))
    app.run()
    
    backend_server.shutdown()
```

---

## 工具系统

### 记忆工具 (7个)
- `memory_recall` - 检索记忆
- `memory_commit` - 写入记忆
- `memory_purge` - 删除记忆
- `memory_introspect` - 查看状态
- `memory_archive` - 归档记忆
- `memory_cleanup` - 清理数据
- `context_rewrite` - 压缩单轮工具调用上下文（实验性）

### 人设工具 (2个)
- `persona_update` - 更新人设
- `persona_clear` - 清除人设

### 任务工具 (4个)
- `task_create` - 创建任务
- `task_set_state` - 设置状态
- `task_delete` - 删除任务
- `task_link_info` - 关联信息

---

## 工具调用限制

| 类别 | 操作 | 每轮上限 |
|------|------|---------|
| 人设图 | 修改 | 1 次 |
| 工作记忆链 | 修改 | 5 次 |
| 一般记忆 | 查询 | 20 次 |
| 一般记忆 | 修改 | 10 次 |

> 注：`memory_recall` 统一计入一般记忆查询，不再区分人设/工作记忆查询。

---

## 错误处理原则

所有 API **不抛出异常**，错误通过返回字典传递：

```python
result = client.process_message("hello")

if result.get("success"):
    print(result["content"])
else:
    print(result["error"])  # 错误描述
```
# BackendServer API 文档

本文档描述后端服务器的 API 接口，供开发者扩展其他连接方式（如网络接口、WebSocket 等）。

## 概述

TrulyMEM 后端采用 **Packet 通信协议**，通过 `queue.Queue` 实现线程安全通信。后端在独立线程中运行，处理来自客户端的请求。

### 核心组件

| 组件 | 说明 |
|------|------|
| `BackendServer` | 后端服务器，独立线程运行 |
| `BackendClient` | 客户端封装，提供便捷方法 |
| `PacketType` | 请求类型枚举 |
| `Packet` | 数据包（请求） |
| `PacketResponse` | 数据包响应 |

---

## 请求类型 (PacketType)

```python
class PacketType(Enum):
    PROCESS_MESSAGE = "process_message"  # 处理消息
    EXECUTE_TOOL = "execute_tool"        # 执行工具
    GET_STATUS = "get_status"            # 获取状态
    GET_SETTINGS = "get_settings"         # 获取完整配置（api_config + tool_limits）
    SET_SETTINGS = "set_settings"        # 设置完整配置（api_config + tool_limits）
    GET_HISTORY = "get_history"           # 获取历史
    SAVE_HISTORY = "save_history"         # 保存历史
    SHUTDOWN = "shutdown"                 # 关闭服务
```

---

## 数据包格式

### Packet

```python
@dataclass
class Packet:
    id: str                      # 唯一标识
    type: PacketType             # 请求类型
    body: Dict[str, Any]        # 请求参数
    response_queue: queue.Queue # 响应队列（可选）
    created_at: float           # 创建时间
```

### PacketResponse

```python
@dataclass
class PacketResponse:
    id: str                      # 对应的请求ID
    success: bool                # 是否成功
    data: Any = None             # 返回数据
    error: Optional[str] = None  # 错误信息
```

---

## API 接口详情

### 1. PROCESS_MESSAGE - 处理消息

发送用户消息，AI 将处理并返回回复（可能包含工具调用）。

**请求参数：**
```python
body = {
    "user_input": str  # 用户输入的消息
}
```

**响应数据：**
```python
{
    "success": True,
    "content": str,           # AI 回复内容
    "tool_calls": [           # 工具调用记录
        {
            "name": str,      # 工具名称
            "arguments": dict,# 工具参数
            "result": str     # 工具执行结果
        }
    ],
    "rejected_tools": [       # 被拒绝的工具调用
        (str, str)            # (工具名, 拒绝原因)
    ]
}
```

**示例：**
```python
from core import BackendServer, BackendClient

server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
server.start(api_key="your-api-key")

client = BackendClient(server)
result = client.process_message("你好，请记住我的名字是小明")

if result.get("success"):
    print(result["content"])
```

---

### 2. EXECUTE_TOOL - 执行工具

直接执行指定的记忆工具。

> **注意**：前端直接调用的工具**不受次数限制**，只有模型发起的工具调用才受限制。

**请求参数：**
```python
body = {
    "tool_name": str,     # 工具名称
    "arguments": dict    # 工具参数
}
```

**响应数据：**
```python
{
    "success": True,
    "result": str  # 工具执行结果
}
```

**示例：**
```python
result = client.execute_tool("memory_recall", {"query_intent": "用户信息"})
```

---

### 3. GET_STATUS - 获取状态

获取后端运行状态。

**请求参数：**
```python
body = {}  # 无参数
```

**响应数据：**
```python
{
    "running": bool,              # 后端是否运行中
    "config": dict,              # 当前配置
    "graph_initialized": bool,   # 图数据库是否初始化
    "client_initialized": bool   # API 客户端是否初始化
}
```

**示例：**
```python
status = client.get_status()
print(status["data"]["running"])  # True
```

---

### 4. GET_SETTINGS - 获取完整配置

获取当前 API 配置和工具限制（一次获取全部）。

**请求参数：**
```python
body = {}  # 无参数
```

**响应数据：**
```python
{
    "api_config": {
        "api_key": str,   # API Key
        "base_url": str,  # API Base URL
        "model": str     # 模型名称
    },
    "tool_limits": {
        "persona_query_max": int,   # 人设图查询上限
        "persona_update_max": int,  # 人设图修改上限
        "task_query_max": int,       # 工作记忆查询上限
        "task_update_max": int,      # 工作记忆修改上限
        "memory_query_max": int,     # 一般记忆查询上限
        "memory_update_max": int    # 一般记忆修改上限
    }
}
```

**示例：**
```python
result = client.get_settings()
api_config = result["data"]["api_config"]
tool_limits = result["data"]["tool_limits"]
```

---

### 5. SET_SETTINGS - 设置完整配置

更新 API 配置和工具限制（一次设置全部）。

**请求参数：**
```python
body = {
    "api_config": {
        "api_key": str,    # API Key
        "base_url": str,   # API Base URL (默认: https://api.deepseek.com)
        "model": str       # 模型名称 (默认: deepseek-chat)
    },
    "tool_limits": {
        "persona_query_max": int,   # 人设图查询上限 (≥1)
        "persona_update_max": int,  # 人设图修改上限 (≥1)
        "task_query_max": int,       # 工作记忆查询上限 (≥1)
        "task_update_max": int,     # 工作记忆修改上限 (≥1)
        "memory_query_max": int,    # 一般记忆查询上限 (≥1)
        "memory_update_max": int     # 一般记忆修改上限 (≥1)
    }
}
```

**响应数据：**
```python
{
    "status": "settings_updated"
}
```

**示例：**
```python
result = client.update_settings(
    api_config={
        "api_key": "sk-xxxxx",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
    tool_limits={
        "persona_query_max": 2,
        "task_query_max": 5,
        "memory_query_max": 30
    }
)
```

---

### 6. GET_HISTORY - 获取消息历史

获取保存的消息历史（从数据库读取，用于UI显示，不参与模型推理）。

**请求参数：**
```python
body = {}  # 无参数
```

**响应数据：**
```python
{
    "history": list  # 消息历史列表 [{"role": "user/assistant", "content": "..."}]
}
```

**说明：**
- 消息历史存储在数据库 `chat_records` 表中
- 最多返回最近 500 条记录
- 历史消息仅用于 UI 显示，不参与模型推理

---

### 7. SAVE_HISTORY - 保存消息历史

保存消息历史到数据库（每次处理消息后自动保存，用户消息和AI回复分别保存）。

**请求参数：**
```python
body = {
    "messages": list  # 消息列表 [{"role": "...", "content": "..."}]
}
```

**响应数据：**
```python
{
    "status": "history_saved"
}
```

**说明：**
- 消息自动保存到数据库 `chat_records` 表
- 系统自动限制最多保留 500 条记录，超出后自动删除旧记录
- 每次调用 `PROCESS_MESSAGE` 时，会自动保存用户消息和AI回复

---

### 8. SHUTDOWN - 关闭服务

关闭后端服务器。

**请求参数：**
```python
body = {}  # 无参数
```

**响应数据：**
```python
{
    "status": "shutdown"
}
```

---

## 使用示例

### 基础使用

```python
from core import BackendServer, BackendClient

# 1. 创建并启动后端
# config_file 默认: ~/.trulymem/config.json
server = BackendServer(
    db_path="graph_memory.db",
    use_embedded_db=True,
    config_file=None  # 可选，自定义配置路径
)
server.start(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
    model="deepseek-chat"  # 可选，模型名称
)

# 2. 创建客户端
client = BackendClient(server)

# 3. 发送消息
result = client.process_message("你好")
if result.get("success"):
    print(result["content"])

# 4. 关闭
client.shutdown()
```

### 使用 Packet 协议

```python
import queue
from core import BackendServer, Packet, PacketType

server = BackendServer(config_file=None)
server.start(api_key="your-key", model="deepseek-chat")

# 创建请求包
response_queue = queue.Queue()
packet = Packet(
    id="req-001",
    type=PacketType.PROCESS_MESSAGE,
    body={"user_input": "你好"},
    response_queue=response_queue
)

# 发送请求
result = server.send(packet)
print(result.body)

# 关闭
server.shutdown()
```

---

## 扩展指南

### 扩展为 HTTP API

```python
from flask import Flask, request, jsonify
from core import BackendServer, BackendClient

app = Flask(__name__)
server = BackendServer()
client = BackendClient(server)

@app.route("/message", methods=["POST"])
def send_message():
    data = request.json
    result = client.process_message(data["message"])
    return jsonify(result)

@app.route("/config", methods=["POST"])
def update_config():
    data = request.json
    result = client.update_settings(
        api_config=data.get("api_config", {}),
        tool_limits=data.get("tool_limits", {})
    )
    return jsonify(result)

@app.route("/status", methods=["GET"])
def get_status():
    result = client.get_status()
    return jsonify(result)

if __name__ == "__main__":
    server.start()
    app.run(port=8080)
```

### 扩展为 WebSocket

```python
import asyncio
import websockets
import json
from core import BackendServer, BackendClient

server = BackendServer()
client = BackendClient(server)

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        msg_type = data.get("type")
        
        if msg_type == "message":
            result = client.process_message(data["content"])
        elif msg_type == "settings":
            result = client.update_settings(
                api_config=data.get("api_config", {}),
                tool_limits=data.get("tool_limits", {})
            )
        elif msg_type == "status":
            result = client.get_status()
        else:
            result = {"success": False, "error": "unknown type"}
        
        await websocket.send(json.dumps(result))

async def main():
    server.start()
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())
```

---

## 线程安全说明

- `BackendServer` 使用 `threading.Lock` 保护共享资源
- 所有请求通过 `queue.Queue` 传递，线程安全
- 响应通过每个请求独立的响应队列返回
- 默认超时时间：30 秒

---

## 工具调用限制

### 限制范围

| 调用方式 | 是否受限 | 说明 |
|---------|---------|------|
| 模型发起的工具调用 | ✅ 受限 | 通过 `PROCESS_MESSAGE` 触发，模型自动调用工具 |
| 前端直接调用工具 | ❌ 不受限 | 通过 `EXECUTE_TOOL` 直接调用 |

### 限制规则（仅限模型发起）

| 类别 | 操作 | 每轮上限 |
|------|------|---------|
| 人设图 | 查询 | 1 次 |
| 人设图 | 修改 | 1 次 |
| 工作记忆链 | 查询 | 4 次 |
| 工作记忆链 | 修改 | 2 次 |
| 一般记忆 | 查询 | 20 次 |
| 一般记忆 | 修改 | 10 次 |

### 重置机制

- 每次调用 `PROCESS_MESSAGE` 时，计数器自动重置
- 前端直接调用 `EXECUTE_TOOL` 不会重置计数器

---

## 错误处理

所有 API 返回统一格式：

```python
# 成功
{
    "success": True,
    "data": {...}
}

# 失败
{
    "success": False,
    "error": "错误描述"
}
```

常见错误：

| 错误信息 | 说明 |
|---------|------|
| `API Key 未配置` | 未设置 API Key |
| `timeout` | 请求超时 |
| `工具调用被拒绝: ...` | 工具调用频率超限 |
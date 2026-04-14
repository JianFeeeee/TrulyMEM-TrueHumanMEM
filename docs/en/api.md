# BackendServer API Documentation

This document describes the backend server's API interfaces for developers extending other connection methods (such as HTTP interface, WebSocket, etc.).

## Overview

TrulyMEM backend uses **Packet Communication Protocol**, implemented via `queue.Queue` for thread-safe communication. The backend runs in an independent thread, processing requests from clients.

### Core Components

| Component | Description |
|-----------|-------------|
| `BackendServer` | Backend server, runs in independent thread |
| `BackendClient` | Client wrapper, provides convenient methods |
| `PacketType` | Request type enum |
| `Packet` | Data packet (request) |
| `PacketResponse` | Data packet response |

---

## Request Types (PacketType)

```python
class PacketType(Enum):
    PROCESS_MESSAGE = "process_message"  # Process message
    EXECUTE_TOOL = "execute_tool"        # Execute tool
    GET_STATUS = "get_status"            # Get status
    GET_CONFIG = "get_config"            # Get config
    SET_CONFIG = "set_config"            # Set config
    GET_TOOL_LIMITS = "get_tool_limits"   # Get tool limits
    SET_TOOL_LIMITS = "set_tool_limits"   # Set tool limits
    GET_HISTORY = "get_history"           # Get history
    SAVE_HISTORY = "save_history"         # Save history
    SHUTDOWN = "shutdown"                 # Shutdown service
```

---

## Data Packet Format

### Packet

```python
@dataclass
class Packet:
    id: str                      # Unique identifier
    type: PacketType             # Request type
    body: Dict[str, Any]        # Request parameters
    response_queue: queue.Queue # Response queue (optional)
    created_at: float           # Creation time
```

### PacketResponse

```python
@dataclass
class PacketResponse:
    id: str                      # Corresponding request ID
    success: bool                # Success flag
    data: Any = None             # Returned data
    error: Optional[str] = None  # Error message
```

---

## API Interface Details

### 1. PROCESS_MESSAGE - Process Message

Send user message, AI will process and return reply (may contain tool calls).

**Request parameters:**
```python
body = {
    "user_input": str  # User input message
}
```

**Response data:**
```python
{
    "success": True,
    "content": str,           # AI reply content
    "tool_calls": [           # Tool call records
        {
            "name": str,      # Tool name
            "arguments": dict,# Tool parameters
            "result": str     # Tool execution result
        }
    ],
    "rejected_tools": [       # Rejected tool calls
        (str, str)            # (tool name, rejection reason)
    ]
}
```

**Example:**
```python
from core import BackendServer, BackendClient

server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
server.start(api_key="your-api-key")

client = BackendClient(server)
result = client.process_message("Hello, please remember my name is Xiao Ming")

if result.get("success"):
    print(result["content"])
```

---

### 2. EXECUTE_TOOL - Execute Tool

Directly execute specified memory tools.

> **Note**: Tools called directly from frontend are **NOT limited** in number, only tool calls initiated by the model are limited.

**Request parameters:**
```python
body = {
    "tool_name": str,     # Tool name
    "arguments": dict    # Tool parameters
}
```

**Response data:**
```python
{
    "success": True,
    "result": str  # Tool execution result
}
```

**Example:**
```python
result = client.execute_tool("memory_recall", {"query_intent": "user information"})
```

---

### 3. GET_STATUS - Get Status

Get backend running status.

**Request parameters:**
```python
body = {}  # No parameters
```

**Response data:**
```python
{
    "running": bool,              # Whether backend is running
    "config": dict,              # Current config
    "graph_initialized": bool,   # Whether graph database is initialized
    "client_initialized": bool   # Whether API client is initialized
}
```

---

### 4. GET_CONFIG - Get Config

Get current API configuration.

**Request parameters:**
```python
body = {}  # No parameters
```

**Response data:**
```python
{
    "api_key": str,   # API Key
    "base_url": str,  # API Base URL
    "model": str     # Model name
}
```

---

### 5. SET_CONFIG - Set Config

Update API configuration (API Key and Base URL).

**Request parameters:**
```python
body = {
    "api_key": str,    # API Key
    "base_url": str,   # API Base URL (default: https://api.deepseek.com)
    "model": str       # Model name (default: deepseek-chat)
}
```

**Response data:**
```python
{
    "status": "config_updated"
}
```

---

### 6. GET_TOOL_LIMITS - Get Tool Limits

Get current AI reasoning tool call limits.

**Request Parameters:**
```python
body = {}  # No parameters
```

**Response Data:**
```python
{
    "persona_query_max": int,   # Persona graph query limit
    "persona_update_max": int,  # Persona graph update limit
    "task_query_max": int,       # Working memory query limit
    "task_update_max": int,     # Working memory update limit
    "memory_query_max": int,      # General memory query limit
    "memory_update_max": int    # General memory update limit
}
```

**Example:**
```python
result = client.get_tool_limits()
print(result["data"]["persona_query_max"])  # 1
```

---

### 7. SET_TOOL_LIMITS - Set Tool Limits

Set AI reasoning tool call limits.

**Request Parameters:**
```python
body = {
    "persona_query_max": int,   # Persona query limit (≥1)
    "persona_update_max": int,  # Persona update limit (≥1)
    "task_query_max": int,       # Working memory query limit (≥1)
    "task_update_max": int,      # Working memory update limit (≥1)
    "memory_query_max": int,     # General memory query limit (≥1)
    "memory_update_max": int     # General memory update limit (≥1)
}
```

**Response Data:**
```python
{
    "status": "tool_limits_updated",
    "limits": {...}  # Updated limits
}
```

**Example:**
```python
result = client.update_tool_limits(
    persona_query_max=2,
    task_query_max=5,
    memory_query_max=30
)
```

---

### 8. GET_HISTORY - Get Message History

Get saved message history.

**Request parameters:**
```python
body = {}  # No parameters
```

**Response data:**
```python
{
    "history": list  # Message history list
}
```

---

### 7. SAVE_HISTORY - Save Message History

Save message history to memory.

**Request parameters:**
```python
body = {
    "messages": list  # Message list
}
```

**Response data:**
```python
{
    "status": "history_saved"
}
```

---

### 8. SHUTDOWN - Shutdown Service

Shutdown backend server.

**Request parameters:**
```python
body = {}  # No parameters
```

**Response data:**
```python
{
    "status": "shutdown"
}
```

---

## Usage Examples

### Basic Usage

```python
from core import BackendServer, BackendClient

# 1. Create and start backend
# config_file default: ~/.trulymem/config.json
server = BackendServer(
    db_path="graph_memory.db",
    use_embedded_db=True,
    config_file=None  # Optional, custom config path
)
server.start(
    api_key="your-api-key",
    base_url="https://api.deepseek.com",
    model="deepseek-chat"  # Optional, model name
)

# 2. Create client
client = BackendClient(server)

# 3. Send message
result = client.process_message("Hello")
if result.get("success"):
    print(result["content"])

# 4. Shutdown
client.shutdown()
```

### Using Packet Protocol

```python
import queue
from core import BackendServer, Packet, PacketType

server = BackendServer(config_file=None)
server.start(api_key="your-key", model="deepseek-chat")

# Create request packet
response_queue = queue.Queue()
packet = Packet(
    id="req-001",
    type=PacketType.PROCESS_MESSAGE,
    body={"user_input": "Hello"},
    response_queue=response_queue
)

# Send request
result = server.send(packet)
print(result.body)

# Shutdown
server.shutdown()
```

---

## Extension Guide

### Extend to HTTP API

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
    result = client.update_config(data["api_key"], data.get("base_url"))
    return jsonify(result)

@app.route("/status", methods=["GET"])
def get_status():
    result = client.get_status()
    return jsonify(result)

if __name__ == "__main__":
    server.start()
    app.run(port=8080)
```

### Extend to WebSocket

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
        elif msg_type == "config":
            result = client.update_config(data["api_key"], data.get("base_url"))
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

## Thread Safety Notes

- `BackendServer` uses `threading.Lock` to protect shared resources
- All requests pass through `queue.Queue`, thread-safe
- Responses return through each request's independent response queue
- Default timeout: 30 seconds

---

## Tool Call Limits

### Limit Scope

| Call Method | Limited | Description |
|-------------|---------|-------------|
| Model-initiated tool calls | ✅ Limited | Triggered via `PROCESS_MESSAGE`, model automatically calls tools |
| Frontend direct tool calls | ❌ Not limited | Called directly via `EXECUTE_TOOL` |

### Limit Rules (Model-initiated only)

| Category | Operation | Per-Turn Limit |
|----------|-----------|---------------|
| Persona graph | Query | 1 time |
| Persona graph | Modify | 1 time |
| Working memory chain | Query | 4 times |
| Working memory chain | Modify | 2 times |
| General memory | Query | 20 times |
| General memory | Modify | 10 times |

### Reset Mechanism

- Counter resets automatically on each `PROCESS_MESSAGE` call
- Frontend direct `EXECUTE_TOOL` calls do NOT reset the counter

---

## Error Handling

All APIs return unified format:

```python
# Success
{
    "success": True,
    "data": {...}
}

# Failure
{
    "success": False,
    "error": "Error description"
}
```

Common errors:

| Error Message | Description |
|--------------|-------------|
| `API Key not configured` | API Key not set |
| `timeout` | Request timeout |
| `Tool call rejected: ...` | Tool call rate exceeded limit |
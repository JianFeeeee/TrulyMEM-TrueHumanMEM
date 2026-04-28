# TrulyMEM Architecture

## Core Principles

- Keyboard-driven, zero mouse dependency
- Minimalist visual, information density priority
- Tool traces hidden by default, expandable when needed
- TUI & backend separation, multi-threaded communication
- **Everything is a graph**, AI reasoning runs entirely in backend

## Project Structure

```
TrulyMEM-TrueHumanMEM/
├── trulymem_entry.py    # Entry: start core → then ui
├── core/               # Backend/business logic
│   ├── __init__.py     # Export BackendServer, BackendClient, EmbeddedGraphDB
│   ├── server.py       # BackendServer (Packet communication protocol)
│   ├── client.py       # BackendClient (Packet protocol client)
│   ├── embedded_db.py  # SQLite graph database implementation
│   ├── graph_client.py # OpenAI/DeepSeek API client
│   ├── tool_executor.py # Tool executor
│   ├── tool_limiter.py # Tool call limiter
│   ├── tools/          # Tool definitions
│   │   └── memory_tools.py
│   └── prompts/        # Prompt management
├── ui/                 # TUI display layer (display only, no AI logic)
│   ├── __init__.py     # Export GraphMemoryApp
│   ├── app.py          # GraphMemoryApp (communicates via BackendClient)
│   ├── widgets/        # TUI components
│   ├── models/         # Data models
│   ├── services/       # Service layer (config only)
│   ├── handlers/      # Event handlers
│   └── styles/         # Style files
├── web_api.py             # Web API service (login + RESTful API)
├── templates/login.html   # Login page template
├── static/                # Web frontend static files (star map visualization)
├── web_config.json        # Web service config file (sensitive, not committed)
└── web_config.example.json # Web config template
```

## Architecture Diagram

```
trulymem_entry.py
    │
    ├─ BackendServer.start() → Runs in independent thread
    │   ├─ Handle PROCESS_MESSAGE requests → AI reasoning + tool calls
    │   ├─ Handle EXECUTE_TOOL requests → External tool calls (unlimited)
    │   ├─ Handle GET/SET_CONFIG requests
    │   └─ Manage GraphMemoryClient, EmbeddedGraphDB
    │
    └─ GraphMemoryApp(backend_server=server)
            │
            └─ BackendClient ← Packet communication → BackendServer
```

## Component Responsibilities

### core/ (Backend)

| Component | Responsibility |
|------------|----------------|
| `server.py` | Packet protocol, multi-threaded queue, AI reasoning, tool limits |
| `client.py` | Client wrapper, UI-backend communication bridge |
| `embedded_db.py` | SQLite graph database CRUD |
| `graph_client.py` | OpenAI/DeepSeek API client |
| `tool_executor.py` | Tool execution logic |
| `tool_limiter.py` | Tool call rate limit (AI reasoning only) |

### ui/ (Display Layer)

| Component | Responsibility |
|------------|----------------|
| `app.py` | Textual app main class, communicates via BackendClient |
| `services/` | Config management only, no AI logic |

### Communication Protocol

UI and backend interact via **Packet Communication Protocol**:

```python
from core import BackendServer, BackendClient, Packet, PacketType

# Backend startup
server = BackendServer(db_path="graph_memory.db", use_embedded_db=True)
server.start(api_key="your-key")

# Client communication
client = BackendClient(server)
result = client.process_message("hello")  # AI reasoning
result = client.execute_tool("memory_introspect", {})  # Direct tool call
```

---

## Data Flow

```
User input → InputBox → on_input_box_send_message
    ↓
BackendClient.process_message(user_input)
    ↓
Packet (type=PROCESS_MESSAGE) → queue.Queue
    ↓
BackendServer (independent thread)
    ���
GraphMemoryClient.send_message_with_history()
    ↓
OpenAI API / DeepSeek API
    ↓
execute_tool() + ToolLimiter (limited during AI reasoning)
    ↓
EmbeddedGraphDB (graph database)
    ↓
Loop API calls until no tool_calls
    ↓
Packet response returns
    ↓
MessageHistory displays
```

---

## Startup Flow

```python
# trulymem_entry.py
def main():
    # Config path (~/.trulymem/config.json or project directory)
    CONFIG_PATH = Path.home() / ".trulymem" / "config.json"
    DB_PATH = Path.home() / ".trulymem" / "graph_memory.db"
    
    # Create backend (config managed by backend)
    backend_server = BackendServer(
        db_path=str(DB_PATH),
        use_embedded_db=True,
        config_file=str(CONFIG_PATH)
    )
    backend_server.start()  # Auto loads config
    
    # Create UI (communicates via BackendClient)
    app = GraphMemoryApp(backend_server=backend_server, config_file=str(CONFIG_PATH))
    app.run()
    
    backend_server.shutdown()
```

---

## Tool System

### Memory Tools (7)
- `memory_recall` - Retrieve memory
- `memory_commit` - Write memory
- `memory_purge` - Delete memory
- `memory_introspect` - View status
- `memory_archive` - Archive memory
- `memory_cleanup` - Clean data
- `context_rewrite` - Compress single-turn tool call context

### Persona Tools (2)
- `persona_update` - Update persona
- `persona_clear` - Clear persona

### Task Tools (4)
- `task_create` - Create task
- `task_set_state` - Set state
- `task_delete` - Delete task
- `task_link_info` - Link information

---

## Tool Call Limits

| Category | Operation | Per-Turn Limit |
|----------|-----------|---------------|
| Persona graph | Modify | 1 time |
| Working memory chain | Modify | 5 times |
| General memory | Query | 20 times |
| General memory | Modify | 10 times |

> Note: `memory_recall` is uniformly counted as general memory query, no longer distinguished by persona/working memory queries.

---

## Error Handling Principle

All APIs **do not throw exceptions**, errors are passed via return dictionary:

```python
result = client.process_message("hello")

if result.get("success"):
    print(result["content"])
else:
    print(result["error"])  # Error description
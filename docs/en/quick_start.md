# TrulyMEM Quick Start Guide

> **Version**: Multi-user (v2) — TUI login, user isolation, embedded Web server

---

## Running

### Quick Start

```bash
# From source
python trulymem_entry.py

# Packaged binary
./dist/TrulyMEM
```

### First Run — Login Flow

On first launch, TrulyMEM checks for legacy data and presents a **login screen**:

1. **Clean install** → Enter username/password (first user becomes admin)
2. **Legacy upgrade** → Detects `~/.trulymem/config.json`, guides migration setup
3. **Returning user** → Login directly

> 💡 All user data is isolated: `~/.trulymem/{username}/`

### Chat Configuration

After login, press **F2** to open the right-side configuration panel:

1. **API Key** — Required (DeepSeek, OpenAI, etc.)
2. **Model** — Optional
3. **Base URL** — Optional

Config saves automatically.

---

## Web Visualization

The Web service now runs **embedded in the main process** (no separate subprocess needed).

### Start via TUI (Admin only)

Admin users: press F2 → check "Enable Web Service".

### Start Manually

```bash
python -m core.web_api --port 4096
# Visit http://localhost:4096
```

### First Visit Flow

1. Open `http://localhost:4096` in browser
2. **No users** → Auto-redirect to setup page, create admin account
3. **Has users** → Login page
4. After login → Star map visualization

### Web Features

| Page | Access | Feature |
|------|--------|---------|
| 🌟 Star Map | All logged-in | Browse knowledge graph |
| ⚙ Settings | All logged-in | Change password |
| 🧑‍💼 User Management | **Admin only** | Add/delete users |

---

## Multi-User System

### Directory Layout

```
~/.trulymem/
├── trulymem.db          # Global user database (web_users table)
├── .migrated            # Migration flag
├── admin/
│   ├── config.json      # Admin config
│   └── admin_graph.db   # Admin knowledge graph
└── user2/
    ├── config.json      # user2 config
    └── user2_graph.db   # user2 knowledge graph
```

### Role Matrix

| Feature | User | Admin |
|---------|------|-------|
| Change password | ✅ | ✅ |
| Configure API Key / Model | ✅ | ✅ |
| Web service toggle (TUI) | ❌ | ✅ |
| Web login credentials | ❌ | ✅ |
| View user list | ❌ | ✅ |
| Add/delete users | ❌ | ✅ |

> ⚠️ First registered user becomes admin automatically. Add users via Web settings page.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F1 | Help |
| F2 | Toggle sidebar (config panel) |
| F3 | Tool details |
| F5 | Clear screen |
| F6 | Quit |

---

## Building

```bash
# Linux
bash build/build_linux.sh

# macOS
bash build/build_macos.sh

# Windows
build\build_windows.bat

# AppImage
bash build/build_appimage.sh
```

Output: `dist/TrulyMEM` (single binary — TUI and Web server embedded)

> 📦 Since v2, the Web server runs as a thread inside the main process. No need for a separate `trulymem-web` binary.

---

## Architecture

### Communication

```
TUI (Textual)  ←→  BackendClient  ←→  queue.Queue  ←→  BackendServer (thread)
```

### Config Management

- **Per-user**: `~/.trulymem/{username}/config.json`
- **Web config**: `~/.trulymem/trulymem.db` (web_users table)
- **Auto-load**: reads config for logged-in user on startup
- **Persistent**: saves automatically on change

### Web Service Architecture

```
┌──────────────────────┐
│   TrulyMEM Process   │
│  ┌──────┐ ┌────────┐ │
│  │ TUI  │ │ Flask  │ │  ← Same process, different threads
│  │      │ │ Thread │ │
│  └──────┘ └────────┘ │
└──────────────────────┘
```

---

## FAQ

### Python not found

Install Python 3.8+: https://www.python.org/downloads/

### Dependency installation fails

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Invalid API Key

Check format and whitespace. Reconfigure in TUI sidebar.

### Lost admin account

The first registered user is always admin. If all users lost admin, delete `trulymem.db` from the user directory and re-register.

### Legacy data migration

When old `~/.trulymem/config.json` and `graph_memory.db` are detected, TUI auto-enters migration flow. Legacy files are preserved.

---

## Dev Commands

```bash
pip install -r requirements.txt
pytest tests/
bash build/build_linux.sh
```

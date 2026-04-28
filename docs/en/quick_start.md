# TrulyMEM Quick Start Guide

## Running Methods

### Run from Source

```bash
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

pip install -r requirements.txt

python trulymem_entry.py
```

### Run After Build

After building, an executable will be generated:

```bash
# Linux/macOS
chmod +x TrulyMEM
./TrulyMEM

# Windows
TrulyMEM.exe
```

## System Requirements

- **Python 3.8+**
- **API Key** (DeepSeek, OpenAI, or other compatible APIs)

## First-Time Configuration

1. Run the application
2. Press **F2** to expand sidebar
3. Enter **API Key**, **Model**, **Base URL**
4. Press **Enter** to save

Config will be automatically saved to `~/.trulymem/config.json` and loaded on next startup.

### Web Visualization (Optional)

TrulyMEM provides a Web star-map visualization interface for browsing the knowledge graph in real-time:

```bash
# Start Web service
python web_api.py --port 4096
```

Then open `http://localhost:4096` in your browser.

**Login Setup:**
1. Copy `web_config.example.json` to `web_config.json`
2. Set login password (using SHA256) and secret key
3. Web service will automatically read the config

Default port is 4096, change with `--port` flag.

---

## Keyboard Shortcuts

| Key | Function |
|-----|-----------|
| F1 | Help |
| F2 | Toggle sidebar |
| F3 | Tool details |
| F5 | Clear screen |
| F6 | Exit |

## Data Storage

### Source Mode

| Data | Location |
|------|----------|
| Graph database | Project directory `graph_memory.db` |
| Config file | Project directory `config.json` (if exists) |
| Database format | SQLite |

### Packaged Mode

| Data | Location |
|------|----------|
| Graph database | `~/.trulymem/graph_memory.db` |
| Config file | `~/.trulymem/config.json` |
| Database format | SQLite |

> **Note**: Backend manages config uniformly. Frontend only displays messages; config modifications are persisted to filesystem through the backend.

## Architecture Explanation

### Communication Protocol

UI and backend communicate via **Packet Protocol**:

```
UI (Textual TUI)
    ↓ BackendClient
Packet → queue.Queue → BackendServer (independent thread)
    ↓
Process request → Return response
```

### Config Management

- **Storage location**: `~/.trulymem/config.json`
- **Auto-load**: Load config from file at startup
- **Dynamic update**: Config changes take effect immediately at runtime
- **Persistence**: Auto-save to file after modification

## Common Issues

### Python Not Found

Install Python 3.8+: https://www.python.org/downloads/

### Dependency Installation Failed

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Invalid API Key

Check API Key format, ensure no extra spaces.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Build
bash build/build_windows.bat   # Windows
bash build/build_linux.sh       # Linux
```
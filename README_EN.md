# TrulyMEM - TrueHumanMEM

<p align="center">
  <img src="pic/image.png" alt="TrulyMEM Logo" width="200">
</p>

> **📜 License**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)  
> This project is free and open source. You are free to use, modify, and distribute, but modified works must be distributed under the same license.

> **中文**: [切换到中文版](./README.md)

**Give AI self-awareness, plasticity, and a sense of proportion in long-term memory**

*The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Branch](https://img.shields.io/badge/branch-main-orange.svg)]()

---

## The Story

Industry believes that LLMs' massive parameters give them emergent intelligence. But this intelligence is "dead" — it cannot truly remember, nor understand the concept of "remembering". Everything it outputs is the probabilistic optimal solution calculated through countless forward passes on the current input text. The LLM cannot correct its weights based on errors in a conversation, nor perform a backward pass. Its consciousness is frozen — what appears as intelligence is merely the echo of this frozen consciousness.

Current "memory systems" merely externalize memory, letting the "system" remember for the LLM. Or they dump all context text to the LLM. This is a waste of the model's limited input context.

**TrulyMEM asks: since the LLM cannot correct model weights in real-time, why not give the memory authority back to the LLM?**

We provide a series of mechanisms for the LLM to decide what to remember, what to forget, what's important, what's trivial. The LLM's reasoning process is also its thinking and recalling process. Abandoning the traditional messages array context, all memories are stored as **triplets (graph)** in the graph database. When the LLM thinks, it can autonomously jump through graph links to associate related relationships, enabling natural association and recall.

Give the LLM true memory.

---

## Quick Start

### Method 1: Run Packaged Executable

```bash
# Windows: TrulyMEM.exe
# Linux/macOS: TrulyMEM
chmod +x TrulyMEM
./TrulyMEM
```

### Method 2: Run from Source

```bash
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

pip install -r requirements.txt

python trulymem_entry.py
```

### First Run (TUI Login)

On first launch, TrulyMEM will guide you through:

1. **TUI Login Screen** — Set up your username and password
2. **Auto Migration** — If old `~/.trulymem/config.json` is detected, guides you through multi-user migration
3. **First user becomes admin automatically**

After login:

1. Press **F2** to expand the right-side configuration panel
2. Enter your **API Key** (supports DeepSeek, OpenAI, etc.)
3. Press **Enter** to save
4. Start chatting!

📌 **Admin users** can manage Web service settings and Web login credentials in the side panel.
📌 **Regular users** can only configure API Key and model parameters.

---

### Multi-User System

TrulyMEM supports isolated multi-user environments. Each user has their own config and database:

```
~/.trulymem/
├── trulymem.db          # Global user database
├── .migrated            # Migration flag
├── admin/
│   ├── config.json      # Admin config
│   └── admin_graph.db   # Admin knowledge graph
└── user2/
    ├── config.json      # user2 config
    └── user2_graph.db   # user2 knowledge graph
```

- **First user becomes admin automatically**
- Admins can add/delete users on the Web settings page
- Regular users cannot see the user management section

### Web Visualization Interface

From TUI, admin users can enable Web service via the right-side panel checkbox, or start manually:

```bash
# Start Web service
python web_api.py --port 4096
```

Then open `http://localhost:4096` in your browser.

**First visit** → Auto-redirect to setup page → Create admin account → Redirect to star map visualization.

**Web features:**
- 🌟 Star map visualization for browsing the knowledge graph
- ⚙ Settings page: change password, manage users (admin only)
- 🔒 Session-based authentication with multi-user isolation

---

## Building

TrulyMEM supports PyInstaller packaging into single-file executables:

```bash
# Linux
bash build/build_linux.sh

# macOS
bash build/build_macos.sh

# Windows
build\build_windows.bat

# AppImage (Linux universal)
bash build/build_appimage.sh
```

Build outputs in `dist/`:

| File | Purpose |
|------|---------|
| `TrulyMEM` | TUI main program (can spawn Web subprocess) |
| `trulymem-web` | Web service standalone binary (auto-detected by TUI) |

### Web binary priority (within TUI)
1. `trulymem-web` in same directory (packaged)
2. `sys._MEIPASS/web_api.py` (PyInstaller data fallback)
3. `python3 web_api.py` (development fallback)

---

## Documentation Index

Detailed technical documentation in the [docs/en/](docs/en/) directory:

| Document | Content |
|----------|---------|
| [docs/en/architecture.md](docs/en/architecture.md) | System architecture and technical design |
| [docs/en/quick_start.md](docs/en/quick_start.md) | Complete startup guide and configuration |
| [docs/en/memory.md](docs/en/memory.md) | Internal memory working mechanism |
| [docs/en/persona.md](docs/en/persona.md) | Persona Graph mechanism |
| [docs/en/working_memory.md](docs/en/working_memory.md) | Continuous task handling mechanism |
| [docs/en/api.md](docs/en/api.md) | BackendServer API (for extension development) |
| [docs/en/prompts.md](docs/en/prompts.md) | Prompt management module |

---

## Contributing

Welcome to submit Issues and Pull Requests!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.  
See [LICENSE](LICENSE) file for details.

---

## Special Thanks

- [Prof. Meiting Wang](https://www.xxmu.edu.cn/yxgcxy/info/1260/4252.htm) — Academic guidance
- [逝水秋生白](https://atomgit.com/cenber) — Architecture support
- anzhitinglan — Testing resource support
- 崔莉萍老师 — Theoretical guidance
- Annie — Professional guidance
- 王梓沣、马悦华、隆梦婷 — Neuroscience theory support

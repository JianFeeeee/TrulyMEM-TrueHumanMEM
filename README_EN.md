# TrulyMEM - TrueHumanMEM

<p align="center">
  <img src="pic/image.png" alt="TrulyMEM Logo" width="200">
</p>

> **📜 License**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)

> **中文**: [README.md](./README.md)

**Give AI self-awareness, plasticity, and a sense of proportion in long-term memory** — *The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## In a Nutshell

TrulyMEM gives memory authority back to the LLM. Using graph database (triplets) instead of the traditional messages array, the LLM autonomously decides what to remember and what to forget.

---

## Quick Start

```bash
python trulymem_entry.py    # from source
./dist/TrulyMEM             # packaged binary
```

First run → TUI login screen → create/sign in → press **F2** for API Key → start chatting

📖 **Full guide**: [docs/en/quick_start.md](docs/en/quick_start.md)

---

## Features

| Feature | Description |
|---------|-------------|
| 🧠 **Graph Memory** | Triplet storage, LLM autonomous navigation |
| 🔐 **Multi-User** | Isolated profiles + Admin/User roles |
| 🌐 **Web UI** | Embedded Flask server (thread mode) for knowledge graph browsing |
| 🎮 **TUI** | Textual-based terminal UI with F2 config panel |
| 📦 **Single Binary** | PyInstaller build, Web server embedded |

---

## Documentation

| Document | Content |
|----------|---------|
| [docs/en/quick_start.md](docs/en/quick_start.md) | 🔥 **Full setup guide** (Web, multi-user, building) |
| [docs/en/architecture.md](docs/en/architecture.md) | System architecture and design |
| [docs/en/memory.md](docs/en/memory.md) | Memory working mechanism |
| [docs/en/persona.md](docs/en/persona.md) | Persona Graph mechanism |
| [docs/en/api.md](docs/en/api.md) | Backend API |
| [docs/en/prompts.md](docs/en/prompts.md) | Prompt management |

---

## Special Thanks

- [Prof. Meiting Wang](https://www.xxmu.edu.cn/yxgcxy/info/1260/4252.htm) — Academic guidance
- [逝水秋生白](https://atomgit.com/cenber) — Architecture support
- anzhitinglan — Testing resource support
- 崔莉萍老师 — Theoretical guidance
- Annie — Professional guidance
- 王梓沣、马悦华、隆梦婷 — Neuroscience theory support

---

## License

GNU General Public License v3.0 (GPLv3)

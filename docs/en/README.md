# TrulyMEM Documentation

Welcome to the TrulyMEM project documentation.

## Documentation Index

| Document | Content |
|----------|---------|
| [architecture.md](architecture.md) | System architecture and technical design |
| [quick_start.md](quick_start.md) | Complete startup guide and configuration |
| [memory.md](memory.md) | Internal memory working mechanism |
| [persona.md](persona.md) | Persona Graph mechanism |
| [working_memory.md](working_memory.md) | Continuous task handling mechanism |
| [api.md](api.md) | Backend API reference (for extension development) |
| [prompts.md](prompts.md) | Prompt management module |

## Project Introduction

TrulyMEM (TrueHumanMEM) is a graph-based memory system that gives AI long-term memory capabilities, allowing AI to remember, recall, and manage information like humans.

## Core Features

- **Long-term Memory**: SQLite embedded graph database, out-of-the-box
- **Persona Graph**: Role-playing and character settings support
- **Working Memory Chain**: Task tracking for conversation continuity
- **TUI & Backend Separation**: Multi-threaded Queue communication
- **Keyboard-driven TUI**: Full keyboard operation, no mouse required
- **Cross-platform**: Windows / Linux / macOS
- **Standalone Deployment**: Packaged as executable
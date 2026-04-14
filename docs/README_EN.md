# TrulyMEM Documentation

Welcome to the TrulyMEM project documentation.

## Documentation Index

- [Architecture](架构_EN.md) - System architecture and technical design
- [Quick Start](一键启动指南_EN.md) - Quick start guide
- [Memory Mechanism](记忆机制_EN.md) - Internal memory working mechanism
- [Working Memory Chain](工作记忆链_EN.md) - Continuous task handling
- [BackendServer API](api_EN.md) - Backend API reference (for extension development)
- [Prompt Manager](prompts_EN.md) - Prompt management module

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

---

## Story

Industry believes that LLMs' massive parameters give them emergent intelligence. But this intelligence is "dead" — it cannot truly remember, nor understand the concept of "remembering". Everything it outputs is the probabilistic optimal solution calculated through countless forward passes on the current input text. The LLM cannot correct its weights based on errors in a conversation, nor perform backward passes. Its consciousness is frozen — what appears as intelligence is merely the echo of this frozen consciousness.

Current "memory systems" merely externalize memory, letting the "system" remember for the LLM. Or they dump all context text to the LLM. This is a waste of the model's limited input context.

**TrulyMEM asks: since the LLM cannot correct model weights in real-time, why not give the memory authority back to the LLM?**

We provide a series of mechanisms for the LLM to decide what to remember, what to forget, what's important, what's trivial. The LLM's reasoning process is also its thinking and recalling process. Abandoning the traditional messages array context, all memories are stored as **triplets (graph)** in the graph database. When the LLM thinks, it can autonomously jump through graph links to associate related relationships, enabling natural association and recall.

Give the LLM true memory.
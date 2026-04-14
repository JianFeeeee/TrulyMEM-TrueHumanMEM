# Prompt Manager Documentation

This document describes the prompt management module.

## Overview

The prompt management module (`core/prompts/`) is responsible for loading and managing system prompts that tell the AI how to use memory tools.

## Core Components

| Component | Description |
|-----------|-------------|
| `PromptManager` | Prompt manager, singleton pattern |
| `system_prompt.md` | Main system prompt template |

## Usage

```python
from core.prompts import PromptManager

# Get singleton instance
prompt_manager = PromptManager()

# Get system prompt
system_prompt = prompt_manager.get_system_prompt()
```

## System Prompt Content

The system prompt contains:

### 1. Core Identity

- **Name**: TrulyMEM (TrueHumanMEM)
- **Capability**: Long-term memory based on graph database
- **Philosophy**: Make AI's memory more human-like

### 2. Core Capabilities

1. **Long-term Memory** - Graph database stores entity relationships
2. **Persona Management** - Role-playing and character settings
3. **Task Tracking** - Working memory chain

### 3. Memory Principles

- **Must write**: User-explicit preferences, shared information, plans
- **Must not write**: AI-inferred content (unless marked [speculation])
- **Annotation**: Inferred content must be marked **[speculation]**

### 4. Mandatory Execution Flow (Per Turn)

```
Step 1: Query persona graph (highest priority)
Step 2: Query working memory chain
Step 3: Process conversation
Step 4: Update working memory chain
```

### 5. Tool System

#### Memory Tools

| Tool | Function |
|------|----------|
| `memory_recall` | Retrieve memory |
| `memory_commit` | Write memory |
| `memory_purge` | Delete memory |
| `memory_introspect` | View status |

#### Persona Tools

| Tool | Function |
|------|----------|
| `persona_update` | Update persona |
| `persona_clear` | Clear persona |

#### Task Tools

| Tool | Function |
|------|----------|
| `task_create` | Create task |
| `task_set_state` | Set state |
| `task_delete` | Delete task |
| `task_link_info` | Link information |

### 6. Autonomy Principles

The AI can autonomously decide:
- Whether to query other memories
- Whether to write other memories
- How to use tools (outside mandatory requirements)

### 7. Conversation Style

- Natural and smooth
- Avoid mechanical tool calls
- Prioritize understanding user intent
- Use memory to enhance experience when appropriate

## File Structure

```
core/prompts/
├── __init__.py           # Export PromptManager
├── prompt_manager.py      # PromptManager class
└── templates/
    └── system_prompt.md # Main system prompt
```

## Customization

### Customizing System Prompt

Modify `core/prompts/templates/system_prompt.md` to customize the AI's behavior.

### Adding Custom Prompts

1. Add prompt template file to `core/prompts/templates/`
2. Modify `PromptManager` to support multiple prompts
3. Use `set_prompt()` to switch prompts

## Caching

- System prompts are cached in memory after first load
- `get_system_prompt()` returns cached content
- Cache is per-process, not persisted
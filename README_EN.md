# TrulyMEM - WaterFlow Adapter

Give AI true long-term memory capability - WaterFlow framework adapter version

[中文版本](./README.md)

---

## Introduction

This project ports TrulyMEM's graph memory capability to TypeScript for the WaterFlow framework.

As a built-in module for WaterFlow, it provides graph memory functionality:

- **recall**: Retrieve memories
- **commit**: Commit memories
- **purge**: Delete memories
- **introspect**: Inspect status
- **persona_update/clear**: Persona management
- **task_create/set_state/delete**: Task management

---

## Directory Structure

```
ts/
├── src/runtime/core/
│   ├── graph_memory/           # Graph memory core module
│   │   ├── types.ts            # Type definitions
│   │   ├── graph_database.ts   # Graph database
│   │   ├── memory_service.ts   # Memory service
│   │   └── index.ts            # Module exports
│   └── tools/
│       └── builtin/
│           └── graph_memory_tool.ts  # Tool implementation
│
├── bundled-skills/             # Skill definitions
│   └── graph_memory/
│       ├── SKILL.md            # Memory operations
│       ├── persona/SKILL.md   # Persona management
│       └── task/SKILL.md       # Task management
│
├── package.json                # Project config
└── tsconfig.json               # TypeScript config
```

---

## Usage in WaterFlow

### Method 1: Import as standalone module

Copy the `ts/` directory to your WaterFlow project:

```typescript
import { GraphMemoryTool, createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool';

const tool = createGraphMemoryTool();
const result = await tool.handler({
  action: 'commit',
  params: {
    triplets: [
      { subject: 'User', relation: 'likes', object: 'Programming' }
    ]
  }
}, context);
```

### Method 2: Use Skill

GraphMemory is configured as a bundled skill and can be called directly:

```
Use skill:graph_memory for memory operations
Use skill:graph_memory_persona for persona management
Use skill:graph_memory_task for task management
```

---

## API

### GraphMemoryTool

```typescript
const tool = new GraphMemoryTool(sessionId?: string);
```

#### Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `recall` | Retrieve memories | `queryIntent`, `seedEntities`, `sessionFilter` |
| `commit` | Commit memories | `triplets`, `sessionId`, `turnId` |
| `purge` | Delete memories | `criteria`, `mode` |
| `introspect` | Inspect status | - |
| `persona_update` | Update persona | `attributes`, `mode` |
| `persona_clear` | Clear persona | `confirm` |
| `task_create` | Create task | `task_id`, `description`, `info_nodes` |
| `task_set_state` | Set state | `task_id`, `state` |
| `task_delete` | Delete task | `task_id` |

---

## Examples

### Commit Memory

```json
{
  "action": "commit",
  "params": {
    "triplets": [
      { "subject": "User", "relation": "likes", "object": "TypeScript" },
      { "subject": "User", "relation": "is learning", "object": "WaterFlow" }
    ]
  }
}
```

### Recall Memory

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "User learning"
  }
}
```

### Create Task

```json
{
  "action": "task_create",
  "params": {
    "task_id": "Task_LearnTypeScript",
    "description": "Learn TypeScript and complete project",
    "info_nodes": ["Documentation", "Tutorial"]
  }
}
```

---

## License

[GNU General Public License v3.0 (GPLv3)](LICENSE)

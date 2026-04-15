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

This module supports two usage methods: **import as module** or **use as Skill**.

### Method 1: Import as Module (for developer integration)

#### Step 1: Copy source files

Copy the `ts/` directory to your WaterFlow project, for example:

```
your-waterflow-project/
├── src/
│   └── runtime/
│       └── core/
│           └── graph_memory/    # Copy from ts/src/runtime/core/
└── ts/                          # Or place in project root
    └── bundled-skills/          # Skill files
```

#### Step 2: Build TypeScript

```bash
cd ts/
npm install
npm run build
```

Compiled files will be output to `ts/dist/`.

#### Step 3: Import in your code

```typescript
import { createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool';

// Create tool instance, can pass sessionId to distinguish different sessions
const tool = createGraphMemoryTool('my-session-id');

// Prepare execution context
const context = {
  toolCallId: 'call-123',
  workingDirectory: '/project',
  abortController: { signal: {} },
  config: { timeout: 30000 },
  logger: {
    info: console.log,
    warn: console.warn,
    error: console.error,
    debug: console.debug
  }
};

// Commit memory example
const commitResult = await tool.handler({
  action: 'commit',
  params: {
    triplets: [
      { subject: 'User', relation: 'likes', object: 'Programming' },
      { subject: 'User', relation: 'is learning', object: 'TypeScript' }
    ]
  }
}, context);

console.log(commitResult);
// Output: {"success":true,"data":{"createdEntities":4,"createdRelations":2}}

// Recall memory example
const recallResult = await tool.handler({
  action: 'recall',
  params: {
    queryIntent: 'User Programming'
  }
}, context);

console.log(recallResult);
// Output: {"success":true,"data":{"entities":[...],"relations":[...],"message":"Found X entities, Y relations"}}
```

### Method 2: Use Skill (recommended for AI Agent)

#### Step 1: Configure Skill source

In your WaterFlow project, find the Skill configuration file and add bundled source pointing to this project's Skill directory:

```typescript
// skill_interface.ts or config file
import { DEFAULT_SKILL_LOADER_CONFIG } from './skill_interface';

const config = {
  ...DEFAULT_SKILL_LOADER_CONFIG,
  sources: {
    ...DEFAULT_SKILL_LOADER_CONFIG.sources,
    bundled: './ts/bundled-skills'  // Point to this project's Skill directory
  },
  enabledSources: ['project', 'bundled']
};
```

#### Step 2: Call Skill via Agent

In your Agent or Workflow, call Skill via Tool:

```
Use skill:graph_memory for:

1. Commit memory: I like programming, learning TypeScript
2. Recall memory: Find memories related to me and programming
```

Or call via code:

```typescript
// Call via SkillTool
const skillResult = await skillTool.handler({
  skill: 'graph_memory',
  args: 'recall - queryIntent: "User learning"'
}, context);
```

#### Available Skills

| Skill Name | Function | Use Case |
|------------|----------|----------|
| `graph_memory` | Memory CRUD | Read/Write/Delete memories |
| `graph_memory_persona` | Persona management | Set AI role/personality |
| `graph_memory_task` | Task management | Create/update long-term tasks |

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

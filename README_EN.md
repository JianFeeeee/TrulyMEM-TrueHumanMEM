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

This module requires **zero changes** to WaterFlow source code. Just register it in your entry file.

### Quick Start (Recommended)

#### Step 1: Install

```bash
npm install /path/to/TrulyMEM-TrueHumanMEM/ts
```

Or add to `package.json`:

```json
{
  "dependencies": {
    "trulymem-waterflow": "file:../TrulyMEM-TrueHumanMEM/ts"
  }
}
```

Then run:

```bash
npm install
```

#### Step 2: Register in your entry file

Just two lines, zero changes to WaterFlow:

```typescript
import { getPlatform } from 'waterflow/platform';
import { installTrulyMEM } from 'trulymem/tools';

// One-line install, returns configured ToolRegistry
const registry = installTrulyMEM(getPlatform(), 'my-session-id');

// Continue assembling WaterFlow...
const toolExecutor = new ToolExecutor(registry);
```

### Manual Registration (More control)

If you want to control ToolRegistry creation yourself:

```typescript
import { getPlatform } from 'waterflow/platform';
import { initializeToolRegistry } from 'waterflow/runtime/core/tools/builtin';
import { registerGraphMemoryTool } from 'trulymem/tools';

const platform = getPlatform();
const registry = initializeToolRegistry(platform);

// Register graph memory tool
registerGraphMemoryTool(registry, 'my-session-id');

// Continue assembling...
```

### Use Skill (AI Agent)

#### Step 1: Configure Skill source

```typescript
const config = {
  ...DEFAULT_SKILL_LOADER_CONFIG,
  sources: {
    ...DEFAULT_SKILL_LOADER_CONFIG.sources,
    bundled: './node_modules/trulymem-waterflow/bundled-skills'
  },
  enabledSources: ['project', 'bundled']
};
```

#### Step 2: Call via Agent

AI Agent automatically reads SKILL.md and calls `builtin:graph_memory` tool.

#### Available Skills

| Skill Name | Function | Use Case |
|------------|----------|----------|
| `graph_memory` | Memory CRUD | Read/Write/Delete memories |
| `persona` | Persona management | Set AI role/personality |
| `task` | Task management | Create/update long-term tasks |

#### Skill Definition Format

WaterFlow's SkillLoader extracts from `SKILL.md`:

- **name**: Extracted from directory name (e.g., `graph_memory`, `persona`, `task`)
- **description**: Extracted from first Markdown `#` heading
- **allowed-tools**: Converted to `allowedTools` field
- **arguments**: Properly mapped to SkillDefinition.arguments
- **user-invocable**: Converted to `userInvocable` field

**Note**: `when_to_use` info is integrated into Markdown body, searchable via SkillRegistry.search().

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

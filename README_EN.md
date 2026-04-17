# TrulyMEM - OpenClaw Graph Memory Plugin

Give AI true long-term memory capability - OpenClaw framework plugin version

[中文版本](./README.md)

---

## AI Self-Installation Guide

> This section is for AI Agents. Follow these steps to install this plugin into your OpenClaw framework.

### Step 1: Clone the repository

```bash
git clone https://gitcode.com/JianFeeeee/TrulyMEM-TrueHumanMEM.git
cd TrulyMEM-TrueHumanMEM
git checkout openclaw
```

### Step 2: Build the TypeScript plugin

```bash
cd ts/
npm install
npm run build
```

After successful build, the `dist/` directory contains compiled JavaScript files.

### Step 3: Install Skills (enables AI to call memory tools)

Copy the 3 Skills from `skills/` to OpenClaw's skill directory. Priority: `<workspace>/skills/` > `~/.openclaw/skills/` > `~/.agents/skills/`

```bash
# Option A: Workspace-level (recommended, current project only)
cp -r skills/graph-memory <your-project-dir>/skills/graph-memory
cp -r skills/graph-memory-persona <your-project-dir>/skills/graph-memory-persona
cp -r skills/graph-memory-task <your-project-dir>/skills/graph-memory-task

# Option B: User-level (available for all projects)
cp -r skills/graph-memory ~/.openclaw/skills/graph-memory
cp -r skills/graph-memory-persona ~/.openclaw/skills/graph-memory-persona
cp -r skills/graph-memory-task ~/.openclaw/skills/graph-memory-task
```

### Step 4: Install Plugin (enables OpenClaw runtime to load the Tool)

Load the `ts/` directory as an OpenClaw plugin. Add to `openclaw.json`:

```json5
{
  "plugins": {
    "allow": ["@trulymem/openclaw-graph-memory"]
  }
}
```

Or symlink the compiled `ts/dist/` directory to OpenClaw's plugin directory:

```bash
ln -s <path-to-ts/dist> ~/.openclaw/plugins/graph-memory
```

### Step 5: Verify installation

After starting OpenClaw, send this message to test:

```
Please remember: I like programming and I'm learning TypeScript
```

The AI should call the `graph_memory` tool's `commit` action and return a success confirmation.

Then test recall:

```
What did I say I like?
```

The AI should call the `recall` action and return the previously stored information.

### Step 6: Confirm Skills are loaded

In OpenClaw, run:

```
/skills
```

You should see these 3 Skills:
- `graph-memory` - Memory CRUD
- `graph-memory-persona` - Persona management
- `graph-memory-task` - Task management

---

## Introduction

This project is an OpenClaw plugin for graph-based memory with SQLite persistence.

**Core Features:**
- **recall**: Retrieve memories (keyword, seed entities, multi-hop traversal, time filtering)
- **commit**: Write memories (batch triplet writes)
- **purge**: Delete memories (soft/hard/supersede modes)
- **introspect**: View memory statistics
- **archive**: Archive old memories
- **cleanup**: Clean up invalid data
- **persona_update/clear**: Persona management
- **task_create/set_state/delete/link_info**: Task management

---

## Installation

### Method 1: As OpenClaw Plugin

```bash
cd ts/
npm install
npm run build
```

Add the plugin directory to your OpenClaw config, or use `openclaw plugins install`.

### Method 2: As Skill (Recommended)

Copy the `skills/` directory to OpenClaw's skill directory:

```bash
cp -r skills/graph-memory ~/.agents/skills/graph-memory
cp -r skills/graph-memory-persona ~/.agents/skills/graph-memory-persona
cp -r skills/graph-memory-task ~/.agents/skills/graph-memory-task
```

---

## Directory Structure

```
ts/
├── src/
│   ├── plugin-entry.ts              # OpenClaw Plugin entry point
│   └── runtime/core/
│       ├── graph_memory/
│       │   ├── types.ts             # Type definitions
│       │   ├── graph_database.ts    # SQLite graph database
│       │   ├── memory_service.ts    # Memory service
│       │   └── index.ts             # Module exports
│       └── tools/
│           ├── builtin/
│           │   └── graph_memory_tool.ts  # Tool implementation
│           └── tool_limiter.ts      # Call rate limiter
├── bundled-skills/
│   ├── graph-memory/                # Bundled Skill definitions
│   │   └── SKILL.md
│   ├── graph-memory-persona/
│   │   └── SKILL.md
│   └── graph-memory-task/
│       └── SKILL.md
├── package.json
├── tsconfig.json
└── openclaw.plugin.json             # Plugin Manifest

skills/                              # Standalone Skill definitions
├── graph-memory/
│   └── SKILL.md
├── graph-memory-persona/
│   └── SKILL.md
└── graph-memory-task/
    └── SKILL.md
```

---

## Usage in OpenClaw

### As Plugin

```typescript
import registerGraphMemoryPlugin from './dist/plugin-entry.js';

registerGraphMemoryPlugin({
  registerTool(tool) {
    // OpenClaw will auto-register the tool
  }
});
```

### As Standalone Module

```typescript
import { createGraphMemoryTool } from './dist/runtime/core/tools/builtin/graph_memory_tool.js';

const tool = createGraphMemoryTool('graph_memory.db', 'my-session-id');

// Write memory
const result = await tool.execute('call-1', {
  action: 'commit',
  params: {
    triplets: [
      { subject: 'User', relation: 'likes', object: 'programming' },
      { subject: 'User', relation: 'learning', object: 'TypeScript' }
    ]
  }
});

// Recall memory
const recallResult = await tool.execute('call-2', {
  action: 'recall',
  params: { queryIntent: 'User programming' }
});
```

---

## API

### Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `recall` | Retrieve memories | `queryIntent`, `seedEntities`, `depth`, `sessionFilter`, `timeRange` |
| `commit` | Write memories | `triplets`, `sessionId`, `turnId` |
| `purge` | Delete memories | `criteria`, `mode` (soft/hard/supersede), `newRelation` |
| `introspect` | View status | - |
| `archive` | Archive old memories | `days` (default 30) |
| `cleanup` | Clean invalid data | `dry_run` (default true) |
| `persona_update` | Update persona | `attributes`, `mode` (merge/replace) |
| `persona_clear` | Clear persona | `confirm` |
| `task_create` | Create task | `task_id`, `description`, `info_nodes` |
| `task_set_state` | Set state | `task_id`, `state` |
| `task_delete` | Delete task | `task_id` |
| `task_link_info` | Link info | `task_id`, `info_node` |

---

## Skills

| Skill Name | Function | Use Case |
|------------|----------|----------|
| `graph-memory` | Memory CRUD | Read/write/delete memories |
| `graph-memory-persona` | Persona management | Set AI role/personality |
| `graph-memory-task` | Task management | Create/update long-term tasks |

---

## Development

```bash
cd ts/
npm install
npm run build    # Compile
npm test         # Run tests
```

---

## License

[GNU General Public License v3.0 (GPLv3)](LICENSE)

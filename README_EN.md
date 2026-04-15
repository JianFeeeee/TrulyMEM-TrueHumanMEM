# TrulyMEM - OpenClaw Adapter

Give AI true long-term memory capability - OpenClaw framework adapter version

[中文版本](./README.md)

---

## 🤖 AI Self-Installation Guide

> This section is for AI Agents, guiding them how to self-install this Skill to OpenClaw

### Installation Steps

#### Step 1: Locate Skill Directory

OpenClaw Skill precedence: `/.agents/skills/` > `~/.agents/skills/` > `~/.openclaw/skills/`

Copy the `skills/` directory to a high-priority location:

```bash
# Method 1: User-level installation (recommended)
cp -r skills/ ~/.agents/skills/graph_memory

# Method 2: System-level installation
sudo cp -r skills/ /.agents/skills/graph_memory
```

#### Step 2: Verify Installation

Invoke Skill in OpenClaw:

```
Remember: I like programming and am learning TypeScript
```

AI should receive a confirmation message.

#### Step 3: Use the Skill

After installation, AI can use these commands:

| Command | Function |
|---------|----------|
| `commit` | Commit memories |
| `recall` | Retrieve memories |
| `purge` | Delete memories |
| `introspect` | Inspect status |
| `persona_update/clear` | Persona management |
| `task_create/set_state/delete` | Task management |

---

## Introduction

This project ports TrulyMEM's graph memory capability to TypeScript for the OpenClaw framework.

As an OpenClaw Skill module, it provides graph memory functionality:

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
│   │   ├── memory_service.ts  # Memory service
│   │   └── index.ts         # Module exports
│   └── tools/
│       └── builtin/
│           └── graph_memory_tool.ts  # Tool implementation
│
├── package.json            # Project config
└── tsconfig.json           # TypeScript config

skills/                     # OpenClaw Skill definitions
└── graph_memory/
    ├── SKILL.md            # Memory operations
    ├── persona/SKILL.md   # Persona management
    └── task/SKILL.md      # Task management
```

---

## Using in OpenClaw

### Method 1: As Module (for Developer Integration)

#### Step 1: Copy Source Code

Copy the `ts/` directory to your OpenClaw project:

```
yourOpenClawProject/
└── src/
    └── runtime/
        └── core/
            └── graph_memory/    # Copy from ts/src/runtime/core/
```

#### Step 2: Compile TypeScript

```bash
cd ts/
npm install
npm run build
```

Compiled files output to `ts/dist/` directory.

#### Step 3: Import in Code

```typescript
import { createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool';

// Create tool instance
const tool = createGraphMemoryTool('my-session-id');

// Commit memory example
const commitResult = await tool.handler({
  action: 'commit',
  params: {
    triplets: [
      { subject: '用户', relation: '喜欢', object: '编程' },
      { subject: '用户', relation: '正在学习', object: 'TypeScript' }
    ]
  }
}, context);

// Recall memory example
const recallResult = await tool.handler({
  action: 'recall',
  params: {
    queryIntent: '用户 编程'
  }
}, context);
```

### Method 2: Use Skill (Recommended for AI Agent)

#### Step 1: Place Skill Files

Copy `skills/` directory to OpenClaw's Skill directory:

```bash
cp -r skills/ ~/.agents/skills/graph_memory
```

#### Step 2: Invoke Skill

Use directly in OpenClaw:

```
Use graph_memory to remember: I like programming and am learning TypeScript
```

#### Available Skills

| Skill Name | Function | Use Case |
|------------|----------|----------|
| `graph_memory` | Memory CRUD | Read/write/delete memories |
| `graph_memory_persona` | Persona management | Set AI persona |
| `graph_memory_task` | Task management | Create/update tasks |

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
| `task_set_state` | Set task state | `task_id`, `state` |
| `task_delete` | Delete task | `task_id` |

---

## Examples

### Commit Memory

```json
{
  "action": "commit",
  "params": {
    "triplets": [
      { "subject": "用户", "relation": "喜欢", "object": "TypeScript" },
      { "subject": "用户", "relation": "正在学习", "object": "OpenClaw" }
    ]
  }
}
```

### Recall Memory

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "用户 学习"
  }
}
```

### Create Task

```json
{
  "action": "task_create",
  "params": {
    "task_id": "Task_学习TypeScript",
    "description": "学习 TypeScript 并完成项目",
    "info_nodes": ["文档链接", "教程链接"]
  }
}
```

---

## License

[GNU General Public License v3.0 (GPLv3)](LICENSE)
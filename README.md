# TrulyMEM - WaterFlow 适配版 / WaterFlow Adapter

让 AI 拥有真正的长期记忆能力 - WaterFlow 框架适配版

*Give AI true long-term memory capability - WaterFlow framework adapter version*

---

## 简介 / Introduction

本项目是将 TrulyMEM 的图记忆能力迁移到 WaterFlow 框架的 TypeScript 实现。

This project ports TrulyMEM's graph memory capability to TypeScript for the WaterFlow framework.

作为 WaterFlow 的内置模块，提供图记忆功能：

As a built-in module for WaterFlow, it provides graph memory functionality:

- **recall**: 检索记忆 / Retrieve memories
- **commit**: 写入记忆 / Commit memories
- **purge**: 删除记忆 / Delete memories
- **introspect**: 查看状态 / Inspect status
- **persona_update/clear**: 人设管理 / Persona management
- **task_create/set_state/delete**: 任务管理 / Task management

---

## 目录结构 / Directory Structure

```
ts/
├── src/runtime/core/
│   ├── graph_memory/           # 图记忆核心模块 / Graph memory core module
│   │   ├── types.ts            # 类型定义 / Type definitions
│   │   ├── graph_database.ts   # 图数据库 / Graph database
│   │   ├── memory_service.ts   # 记忆服务 / Memory service
│   │   └── index.ts            # 模块导出 / Module exports
│   └── tools/
│       └── builtin/
│           └── graph_memory_tool.ts  # Tool 实现 / Tool implementation
│
├── bundled-skills/             # Skill 定义 / Skill definitions
│   └── graph_memory/
│       ├── SKILL.md            # 记忆操作 / Memory operations
│       ├── persona/SKILL.md   # 人设管理 / Persona management
│       └── task/SKILL.md       # 任务管理 / Task management
│
├── package.json                # 项目配置 / Project config
└── tsconfig.json               # TypeScript 配置 / TypeScript config
```

---

## 在 WaterFlow 中使用 / Usage in WaterFlow

### 方式一：作为独立模块引用 / Method 1: Import as standalone module

将 `ts/` 目录复制到你的 WaterFlow 项目中：

Copy the `ts/` directory to your WaterFlow project:

```typescript
import { GraphMemoryTool, createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool';

const tool = createGraphMemoryTool();
const result = await tool.handler({
  action: 'commit',
  params: {
    triplets: [
      { subject: '用户', relation: '喜欢', object: '编程' }
    ]
  }
}, context);
```

### 方式二：使用 Skill / Method 2: Use Skill

GraphMemory 已配置为 bundled skill，可直接调用：

GraphMemory is configured as a bundled skill and can be called directly:

```
使用 skill:graph_memory 进行记忆操作 / Use skill:graph_memory for memory operations
使用 skill:graph_memory_persona 进行人设管理 / Use skill:graph_memory_persona for persona management
使用 skill:graph_memory_task 进行任务管理 / Use skill:graph_memory_task for task management
```

---

## API

### GraphMemoryTool

```typescript
const tool = new GraphMemoryTool(sessionId?: string);
```

#### Actions

| Action | 说明 / Description | 参数 / Parameters |
|--------|------|------|
| `recall` | 检索记忆 / Retrieve memories | `queryIntent`, `seedEntities`, `sessionFilter` |
| `commit` | 写入记忆 / Commit memories | `triplets`, `sessionId`, `turnId` |
| `purge` | 删除记忆 / Delete memories | `criteria`, `mode` |
| `introspect` | 查看状态 / Inspect status | - |
| `persona_update` | 更新人设 / Update persona | `attributes`, `mode` |
| `persona_clear` | 清除人设 / Clear persona | `confirm` |
| `task_create` | 创建任务 / Create task | `task_id`, `description`, `info_nodes` |
| `task_set_state` | 设置状态 / Set state | `task_id`, `state` |
| `task_delete` | 删除任务 / Delete task | `task_id` |

---

## 示例 / Examples

### 写入记忆 / Commit Memory

```json
{
  "action": "commit",
  "params": {
    "triplets": [
      { "subject": "用户", "relation": "喜欢", "object": "TypeScript" },
      { "subject": "用户", "relation": "正在学习", "object": "WaterFlow" }
    ]
  }
}
```

### 检索记忆 / Recall Memory

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "用户 学习"
  }
}
```

### 创建任务 / Create Task

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

## 许可证 / License

[GNU General Public License v3.0 (GPLv3)](LICENSE)

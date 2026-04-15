# TrulyMEM - WaterFlow Adapter

让 AI 拥有真正的长期记忆能力 - WaterFlow 框架适配版

---

## 简介

本项目是将 TrulyMEM 的图记忆能力迁移到 WaterFlow 框架的 TypeScript 实现。

作为 WaterFlow 的内置模块，提供图记忆功能：
- **recall**: 检索记忆
- **commit**: 写入记忆
- **purge**: 删除记忆
- **introspect**: 查看状态
- **persona_update/clear**: 人设管理
- **task_create/set_state/delete**: 任务管理

---

## 目录结构

```
ts/
├── src/runtime/core/
│   ├── graph_memory/           # 图记忆核心模块
│   │   ├── types.ts            # 类型定义
│   │   ├── graph_database.ts   # 图数据库
│   │   ├── memory_service.ts   # 记忆服务
│   │   └── index.ts            # 模块导出
│   └── tools/
│       └── builtin/
│           └── graph_memory_tool.ts  # Tool 实现
│
├── bundled-skills/             # Skill 定义
│   └── graph_memory/
│       ├── SKILL.md            # 记忆操作
│       ├── persona/SKILL.md   # 人设管理
│       └── task/SKILL.md       # 任务管理
│
├── package.json                # 项目配置
└── tsconfig.json               # TypeScript 配置
```

---

## 在 WaterFlow 中使用

### 方式一：作为独立模块引用

将 `ts/` 目录复制到你的 WaterFlow 项目中：

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

### 方式二：使用 Skill

GraphMemory 已配置为 bundled skill，可直接调用：

```
使用 skill:graph_memory 进行记忆操作
使用 skill:graph_memory_persona 进行人设管理
使用 skill:graph_memory_task 进行任务管理
```

---

## API

### GraphMemoryTool

```typescript
const tool = new GraphMemoryTool(sessionId?: string);
```

#### Actions

| Action | 说明 | 参数 |
|--------|------|------|
| `recall` | 检索记忆 | `queryIntent`, `seedEntities`, `sessionFilter` |
| `commit` | 写入记忆 | `triplets`, `sessionId`, `turnId` |
| `purge` | 删除记忆 | `criteria`, `mode` |
| `introspect` | 查看状态 | - |
| `persona_update` | 更新人设 | `attributes`, `mode` |
| `persona_clear` | 清除人设 | `confirm` |
| `task_create` | 创建任务 | `task_id`, `description`, `info_nodes` |
| `task_set_state` | 设置状态 | `task_id`, `state` |
| `task_delete` | 删除任务 | `task_id` |

---

## 示例

### 写入记忆

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

### 检索记忆

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "用户 学习"
  }
}
```

### 创建任务

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

## 许可证

[GNU General Public License v3.0 (GPLv3)](LICENSE)

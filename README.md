# TrulyMEM - WaterFlow 适配版

让 AI 拥有真正的长期记忆能力 - WaterFlow 框架适配版

[English Version](./README_EN.md)

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

本模块完全不动 WaterFlow 源码，只需在你的入口文件中注册即可。

### 快速开始（推荐）

#### 步骤 1：安装依赖

```bash
npm install /path/to/TrulyMEM-TrueHumanMEM/ts
```

或在 `package.json` 中添加：

```json
{
  "dependencies": {
    "trulymem-waterflow": "file:../TrulyMEM-TrueHumanMEM/ts"
  }
}
```

然后运行：

```bash
npm install
```

#### 步骤 2：在你的入口文件中注册

只需两行代码，完全不动 WaterFlow 源码：

```typescript
import { getPlatform } from 'waterflow/platform';
import { installTrulyMEM } from 'trulymem/tools';

// 一行安装，返回配置好的 ToolRegistry
const registry = installTrulyMEM(getPlatform(), 'my-session-id');

// 继续组装 WaterFlow...
const toolExecutor = new ToolExecutor(registry);
```

### 手动注册（更灵活）

如果你想自己控制 ToolRegistry 的创建：

```typescript
import { getPlatform } from 'waterflow/platform';
import { initializeToolRegistry } from 'waterflow/runtime/core/tools/builtin';
import { registerGraphMemoryTool } from 'trulymem/tools';

const platform = getPlatform();
const registry = initializeToolRegistry(platform);

// 注册图记忆工具
registerGraphMemoryTool(registry, 'my-session-id');

// 继续组装...
```

### 使用 Skill（AI Agent 调用）

#### 步骤 1：配置 Skill 来源

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

#### 步骤 2：通过 Agent 调用

AI Agent 会自动读取 SKILL.md 并调用 `builtin:graph_memory` 工具。

#### 可用 Skill 列表

| Skill 名称 | 功能 | 使用场景 |
|------------|------|----------|
| `graph_memory` | 记忆 CRUD | 读取/写入/删除记忆 |
| `graph_memory_persona` | 人设管理 | 设置 AI 角色性格 |
| `graph_memory_task` | 任务管理 | 创建/更新长期任务 |

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

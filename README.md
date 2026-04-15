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

本模块支持两种使用方式：**作为模块直接引用** 或 **作为 Skill 调用**。

### 方式一：作为模块直接引用（适合开发者集成）

#### 步骤 1：复制源码

将本项目的 `ts/` 目录复制到你的 WaterFlow 项目中，例如：

```
你的WaterFlow项目/
├── src/
│   └── runtime/
│       └── core/
│           └── graph_memory/    # 从 ts/src/runtime/core/ 复制
└── ts/                          # 或直接放在项目根目录
    └── bundled-skills/          # Skill 文件
```

#### 步骤 2：编译 TypeScript

```bash
cd ts/
npm install
npm run build
```

编译后的文件会输出到 `ts/dist/` 目录。

#### 步骤 3：在代码中引用

```typescript
import { createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool';

// 创建工具实例，可以传入 sessionId 来区分不同会话
const tool = createGraphMemoryTool('my-session-id');

// 准备执行上下文
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

// 写入记忆示例
const commitResult = await tool.handler({
  action: 'commit',
  params: {
    triplets: [
      { subject: '用户', relation: '喜欢', object: '编程' },
      { subject: '用户', relation: '正在学习', object: 'TypeScript' }
    ]
  }
}, context);

console.log(commitResult);
// 输出: {"success":true,"data":{"createdEntities":4,"createdRelations":2}}

// 检索记忆示例
const recallResult = await tool.handler({
  action: 'recall',
  params: {
    queryIntent: '用户 编程'
  }
}, context);

console.log(recallResult);
// 输出: {"success":true,"data":{"entities":[...],"relations":[...],"message":"找到 X 个实体, Y 条关系"}}
```

### 方式二：使用 Skill（推荐，适合 AI Agent 调用）

#### 步骤 1：配置 Skill 来源

在你的 WaterFlow 项目中，找到 Skill 配置文件，添加 bundled 来源指向本项目的 Skill 目录：

```typescript
// skill_interface.ts 或配置文件中
import { DEFAULT_SKILL_LOADER_CONFIG } from './skill_interface';

const config = {
  ...DEFAULT_SKILL_LOADER_CONFIG,
  sources: {
    ...DEFAULT_SKILL_LOADER_CONFIG.sources,
    bundled: './ts/bundled-skills'  // 指向本项目的 Skill 目录
  },
  enabledSources: ['project', 'bundled']
};
```

#### 步骤 2：通过 Agent 调用 Skill

在你的 Agent 或 Workflow 中，通过 Tool 调用 Skill：

```
使用 skill:graph_memory 进行以下操作:

1. 写入记忆: 我喜欢编程，正在学习 TypeScript
2. 检索记忆: 找出我和编程相关的记忆
```

或者通过代码调用：

```typescript
// 通过 SkillTool 调用
const skillResult = await skillTool.handler({
  skill: 'graph_memory',
  args: 'recall - queryIntent: "用户 学习"'
}, context);
```

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

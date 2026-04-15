# TrulyMEM - OpenClaw 适配版

让 AI 拥有真正的长期记忆能力 - OpenClaw 框架适配版

[English Version](./README_EN.md)

---

## 🤖 AI 自行安装指南

> 本节面向 AI Agent，指导其如何自主安装此 Skill 到 OpenClaw 框架

### 安装步骤

#### 步骤 1：定位 Skill 目录

OpenClaw 的 Skill 优先级：`/.agents/skills/` > `~/.agents/skills/` > `~/.openclaw/skills/`

将本项目的 `skills/` 目录复制到高优先级位置：

```bash
# 方式 1: 用户级安装 (推荐)
cp -r skills/ ~/.agents/skills/graph_memory

# 方式 2: 系统级安装
sudo cp -r skills/ /.agents/skills/graph_memory
```

#### 步骤 2：验证安装

在 OpenClaw 中调用 Skill：

```
记得: 我喜欢编程，正在学习 TypeScript
```

AI 应收到确认消息。

#### 步骤 3：使用 Skill

安装成功后，AI 可以使用以下命令：

| 命令 | 功能 |
|------|------|
| `commit` | 写入记忆 |
| `recall` | 检索记忆 |
| `purge` | 删除记忆 |
| `introspect` | 查看状态 |
| `persona_update/clear` | 人设管理 |
| `task_create/set_state/delete` | 任务管理 |

---

## 简介

本项目是将 TrulyMEM 的图记忆能力迁移到 OpenClaw 框架的 TypeScript 实现。

作为 OpenClaw 的 Skill 模块，提供图记忆功能：
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
│   │   ├── memory_service.ts  # 记忆服务
│   │   └── index.ts         # 模块导出
│   └── tools/
│       └── builtin/
│           └── graph_memory_tool.ts  # Tool 实现
│
├── package.json            # 项目配置
└── tsconfig.json           # TypeScript 配置

skills/                     # OpenClaw Skill 定义
└── graph_memory/
    ├── SKILL.md            # 记忆操作
    ├── persona/SKILL.md    # 人设管理
    └── task/SKILL.md        # 任务管理
```

---

## 在 OpenClaw 中使用

### 方式一：作为模块直接引用（适合开发者集成）

#### 步骤 1：复制源码

将本项目的 `ts/` 目录复制到你的 OpenClaw 项目中：

```
你的OpenClaw项目/
└── src/
    └── runtime/
        └── core/
            └── graph_memory/    # 从 ts/src/runtime/core/ 复制
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

// 创建工具实例
const tool = createGraphMemoryTool('my-session-id');

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

// 检索记忆示例
const recallResult = await tool.handler({
  action: 'recall',
  params: {
    queryIntent: '用户 编程'
  }
}, context);
```

### 方式二：使用 Skill（推荐，适合 AI Agent 调用）

#### 步骤 1：放置 Skill 文件

将 `skills/` 目录复制到 OpenClaw 的 Skill 目录：

```bash
cp -r skills/ ~/.agents/skills/graph_memory
```

#### 步骤 2：通过 Agent 调用 Skill

在 OpenClaw 中直接调用：

```
使用 graph_memory 记住: 我喜欢编程，正在学习 TypeScript
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
      { "subject": "用户", "relation": "正在学习", "object": "OpenClaw" }
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
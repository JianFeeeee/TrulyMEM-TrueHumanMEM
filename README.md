# TrulyMEM - OpenClaw Graph Memory Plugin

让 AI 拥有真正的长期记忆能力 - OpenClaw 框架插件版

[English Version](./README_EN.md)

---

## 简介

本项目是 OpenClaw 的图记忆插件，基于 SQLite 实现持久化图数据库。

**核心功能：**
- **recall**: 检索记忆（支持关键词、种子实体、多跳遍历、时间过滤）
- **commit**: 写入记忆（三元组批量写入）
- **purge**: 删除记忆（软删除/硬删除/纠错替代）
- **introspect**: 查看记忆状态
- **archive**: 归档旧记忆
- **cleanup**: 清理无效数据
- **persona_update/clear**: 人设管理
- **task_create/set_state/delete/link_info**: 任务管理

---

## 安装

### 方式一：作为 OpenClaw 插件安装

```bash
cd ts/
npm install
npm run build
```

将插件目录添加到 OpenClaw 配置中，或使用 `openclaw plugins install` 安装。

### 方式二：作为 Skill 安装（推荐）

将 `skills/` 目录复制到 OpenClaw 的 Skill 目录：

```bash
cp -r skills/graph-memory ~/.agents/skills/graph-memory
cp -r skills/graph-memory/persona ~/.agents/skills/graph-memory-persona
cp -r skills/graph-memory/task ~/.agents/skills/graph-memory-task
```

---

## 目录结构

```
ts/
├── src/
│   ├── plugin-entry.ts              # OpenClaw Plugin 入口
│   └── runtime/core/
│       ├── graph_memory/
│       │   ├── types.ts             # 类型定义
│       │   ├── graph_database.ts    # SQLite 图数据库
│       │   ├── memory_service.ts    # 记忆服务
│       │   └── index.ts             # 模块导出
│       └── tools/
│           ├── builtin/
│           │   └── graph_memory_tool.ts  # Tool 实现
│           └── tool_limiter.ts      # 调用限制器
├── bundled-skills/
│   └── graph-memory/                # 内置 Skill 定义
│       ├── SKILL.md
│       ├── persona/SKILL.md
│       └── task/SKILL.md
├── package.json
├── tsconfig.json
└── openclaw.plugin.json             # Plugin Manifest

skills/                              # 独立 Skill 定义
└── graph-memory/
    ├── SKILL.md
    ├── persona/SKILL.md
    └── task/SKILL.md
```

---

## 在 OpenClaw 中使用

### 作为 Plugin

```typescript
import registerGraphMemoryPlugin from './dist/plugin-entry.js';

registerGraphMemoryPlugin({
  registerTool(tool) {
    // OpenClaw 会自动注册工具
  }
});
```

### 作为独立模块

```typescript
import { createGraphMemoryTool } from './dist/runtime/core/tools/builtin/graph_memory_tool.js';

const tool = createGraphMemoryTool('graph_memory.db', 'my-session-id');

// 写入记忆
const result = await tool.execute('call-1', {
  action: 'commit',
  params: {
    triplets: [
      { subject: '用户', relation: '喜欢', object: '编程' },
      { subject: '用户', relation: '正在学习', object: 'TypeScript' }
    ]
  }
});

// 检索记忆
const recallResult = await tool.execute('call-2', {
  action: 'recall',
  params: { queryIntent: '用户 编程' }
});
```

---

## API

### Actions

| Action | 说明 | 参数 |
|--------|------|------|
| `recall` | 检索记忆 | `queryIntent`, `seedEntities`, `depth`, `sessionFilter`, `timeRange` |
| `commit` | 写入记忆 | `triplets`, `sessionId`, `turnId` |
| `purge` | 删除记忆 | `criteria`, `mode` (soft/hard/supersede), `newRelation` |
| `introspect` | 查看状态 | - |
| `archive` | 归档旧记忆 | `days` (默认 30) |
| `cleanup` | 清理无效数据 | `dry_run` (默认 true) |
| `persona_update` | 更新人设 | `attributes`, `mode` (merge/replace) |
| `persona_clear` | 清除人设 | `confirm` |
| `task_create` | 创建任务 | `task_id`, `description`, `info_nodes` |
| `task_set_state` | 设置状态 | `task_id`, `state` |
| `task_delete` | 删除任务 | `task_id` |
| `task_link_info` | 关联信息 | `task_id`, `info_node` |

---

## Skill 列表

| Skill 名称 | 功能 | 使用场景 |
|------------|------|----------|
| `graph-memory` | 记忆 CRUD | 读取/写入/删除记忆 |
| `graph-memory-persona` | 人设管理 | 设置 AI 角色性格 |
| `graph-memory-task` | 任务管理 | 创建/更新长期任务 |

---

## 开发

```bash
cd ts/
npm install
npm run build    # 编译
npm test         # 运行测试
```

---

## 许可证

[GNU General Public License v3.0 (GPLv3)](LICENSE)

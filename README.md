# TrulyMEM - OpenClaw Graph Memory Plugin

让 AI 拥有真正的长期记忆能力 - OpenClaw 框架插件版

[English Version](./README_EN.md)

---

## AI 自行安装指南

> 本节面向 AI Agent，按步骤指导你自主安装此插件到 OpenClaw 框架。

### 步骤 1：克隆仓库

```bash
git clone https://gitcode.com/JianFeeeee/TrulyMEM-TrueHumanMEM.git
cd TrulyMEM-TrueHumanMEM
git checkout openclaw
```

### 步骤 2：编译 TypeScript 插件

```bash
cd ts/
npm install
npm run build
```

编译成功后，`dist/` 目录会输出编译后的 JavaScript 文件。

### 步骤 3：安装 Skill（让 AI 能调用记忆工具）

将 `skills/` 目录下的 3 个 Skill 复制到 OpenClaw 的 Skill 目录。优先级：`<workspace>/skills/` > `~/.openclaw/skills/` > `~/.agents/skills/`

```bash
# 方式 A：工作空间级（推荐，仅当前项目可用）
cp -r skills/graph-memory <你的项目目录>/skills/graph-memory
cp -r skills/graph-memory-persona <你的项目目录>/skills/graph-memory-persona
cp -r skills/graph-memory-task <你的项目目录>/skills/graph-memory-task

# 方式 B：用户级（所有项目可用）
cp -r skills/graph-memory ~/.openclaw/skills/graph-memory
cp -r skills/graph-memory-persona ~/.openclaw/skills/graph-memory-persona
cp -r skills/graph-memory-task ~/.openclaw/skills/graph-memory-task
```

### 步骤 4：安装 Plugin（让 OpenClaw 运行时加载 Tool）

将编译后的 `ts/` 目录复制到 OpenClaw 的全局扩展目录：

```bash
# 复制到 OpenClaw extensions 目录
mkdir -p ~/.openclaw/extensions
cp -r ts ~/.openclaw/extensions/graph-memory
```

然后启用插件：

```bash
# 启用插件
openclaw plugins enable graph-memory

# 重启 Gateway（如果使用 systemd 托管）
systemctl --user restart openclaw-gateway
```

验证插件已加载：

```bash
openclaw plugins list
# 应显示 graph-memory 为 loaded 状态
```

**注意**：插件启用时会自动切换 `memory` 独占插槽到 `graph-memory`，禁用其他内存插件（如 `memory-core`）。

### 步骤 5：验证安装

启动 OpenClaw 后，发送以下消息测试：

```
请记住：我喜欢编程，正在学习 TypeScript
```

AI 应调用 `graph_memory` 工具的 `commit` action 并返回成功确认。

然后测试检索：

```
我之前说过喜欢什么？
```

AI 应调用 `recall` action 并返回之前写入的信息。

### 步骤 6：确认 Skill 已加载

在 OpenClaw 中执行：

```
/skills
```

你应该能看到以下 3 个 Skill：
- `graph-memory` - 记忆 CRUD
- `graph-memory-persona` - 人设管理
- `graph-memory-task` - 任务管理

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
cp -r skills/graph-memory-persona ~/.agents/skills/graph-memory-persona
cp -r skills/graph-memory-task ~/.agents/skills/graph-memory-task
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
│   ├── graph-memory/                # 内置 Skill 定义
│   │   └── SKILL.md
│   ├── graph-memory-persona/
│   │   └── SKILL.md
│   └── graph-memory-task/
│       └── SKILL.md
├── package.json
├── tsconfig.json
└── openclaw.plugin.json             # Plugin Manifest

skills/                              # 独立 Skill 定义
├── graph-memory/
│   └── SKILL.md
├── graph-memory-persona/
│   └── SKILL.md
└── graph-memory-task/
    └── SKILL.md
```

---

## 在 OpenClaw 中使用

### 作为 Plugin

插件入口导出符合 OpenClaw SDK 规范的对象：

```typescript
// plugin-entry.ts 导出格式
export default {
  id: 'graph-memory',
  name: 'Graph Memory',
  description: '让 AI 拥有真正的长期记忆能力',
  register(api) {
    api.registerTool(tool);
  }
};
```

OpenClaw 加载后会自动调用 `register(api)` 注册工具。

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

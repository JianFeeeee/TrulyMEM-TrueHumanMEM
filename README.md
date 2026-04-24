# TrulyMEM - AI 主要长期记忆系统

让 AI 拥有真正的长期记忆能力 - OpenClaw 框架插件版

[English Version](./README_EN.md)

---

## 定位声明

**TrulyMEM 是 AI 的主要长期记忆系统。**

与 OpenClaw 内置的 memory-core 并存运行：
- **memory-core**：负责 session transcripts 和对话历史管理
- **GraphMemory (TrulyMEM)**：负责**结构化长期记忆**——知识图谱、人设、任务、语义搜索

AI 在对话中应**优先**将重要信息（偏好、决策、任务、知识点）写入图数据库，而非依赖 message 历史。

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

**注意**：插件与 memory-core **并存运行**，不会禁用其他内存插件。memory-core 继续管理对话历史，GraphMemory 提供结构化长期记忆。

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
- `graph-memory` - 记忆 CRUD + 语义搜索 + 上下文压缩
- `graph-memory-persona` - 人设管理
- `graph-memory-task` - 任务管理

---

## 简介

本项目是 OpenClaw 的图记忆插件，基于 SQLite 实现持久化图数据库。

**设计理念：AI 的主要长期记忆系统**

本插件作为 AI 的**主要长期记忆存储**，与 memory-core 并存运行：
- **memory-core 管理对话历史**：session transcripts 和历史消息由 memory-core 自动管理
- **GraphMemory 管理结构化记忆**：重要事实、人设、任务、知识图谱由 AI 主动写入图数据库
- **AI 优先使用图记忆**：对于持久信息，AI 应优先写入图数据库而非依赖 message 上下文

**核心功能：**

### 基础记忆操作
- **recall**: 检索记忆（支持关键词、种子实体、多跳遍历、时间过滤）
- **commit**: 写入记忆（三元组批量写入）
- **purge**: 删除记忆（软删除/硬删除/纠错替代）
- **introspect**: 查看记忆状态
- **archive**: 归档旧记忆
- **cleanup**: 清理无效数据

### 高级功能（P2）
- **memory_search**: 语义搜索——基于本地 ONNX embedding 的向量相似度搜索
- **memory_get**: 精确读取——按路径读取记忆文件内容片段
- **context_rewrite**: 上下文压缩——将长对话历史压缩为关键记忆节点
- **working_memory_chain**: 工作记忆链——获取当前会话的活跃关系链
- **task_node_create/get_recent/get_chain**: 任务节点——创建和追踪连续性任务节点

### 人设与任务管理
- **persona_update/clear**: 人设管理（AI 应主动查询人设指导行为）
- **task_create/set_state/delete/link_info**: 任务管理（AI 应主动追踪任务状态）

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
│       │   ├── semantic_search.ts   # 语义搜索引擎（P2）
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

// 语义搜索
const searchResult = await tool.execute('call-2', {
  action: 'memory_search',
  params: { query: '编程相关', limit: 5 }
});

// 检索记忆
const recallResult = await tool.execute('call-3', {
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
| **语义搜索** | | |
| `memory_search` | 语义向量搜索 | `query`, `limit`, `corpus` |
| `memory_get` | 精确读取记忆文件 | `path`, `fromLine`, `lines` |
| **上下文压缩** | | |
| `context_rewrite` | 压缩长对话为记忆节点 | `context`, `maxEntities`, `summary` |
| `working_memory_chain` | 获取当前会话活跃关系链 | `maxDepth`, `recentOnly` |
| **任务节点** | | |
| `task_node_create` | 创建任务节点 | `session_id`, `turn_id`, `summary`, `key_facts` |
| `task_node_get_recent` | 获取最近任务节点 | `session_id`, `limit` |
| `task_node_get_chain` | 获取任务链 | `session_id`, `from_node_id` |
| **人设管理** | | |
| `persona_update` | 更新人设 | `attributes`, `mode` (merge/replace) |
| `persona_clear` | 清除人设 | `confirm` |
| **任务管理** | | |
| `task_create` | 创建任务 | `task_id`, `description`, `info_nodes` |
| `task_set_state` | 设置状态 | `task_id`, `state` |
| `task_delete` | 删除任务 | `task_id` |
| `task_link_info` | 关联信息 | `task_id`, `info_node` |

---

## Skill 列表

| Skill 名称 | 功能 | 使用场景 |
|------------|------|----------|
| `graph-memory` | 记忆 CRUD + 语义搜索 + 上下文压缩 | 读取/写入/删除记忆，语义搜索，压缩历史 |
| `graph-memory-persona` | 人设管理 | 设置 AI 角色性格，AI 主动查询人设 |
| `graph-memory-task` | 任务管理 | 创建/更新长期任务，AI 主动追踪任务 |

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

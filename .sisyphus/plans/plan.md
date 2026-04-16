# TrulyMEM → OpenClaw 重构修复计划

> **分支**: `openclaw`  
> **代码位置**: `/home/program/TrulyMEM-TrueHumanMEM/`  
> **目标**: 将当前 TypeScript 实现完全适配 OpenClaw 框架的接口规范，并补全 main 分支缺失的功能

---

## 背景分析

### 当前状态

openclaw 分支已完成骨架迁移：类型定义、核心类（GraphDatabase/MemoryService/GraphMemoryTool）、Skill 定义文件均已就位，TypeScript 编译通过。

### 核心问题

| 类别 | 问题 | 严重度 |
|---|---|---|
| **接口不兼容** | Tool 注册使用自定义 interface，非 OpenClaw Plugin SDK | 🔴 致命 |
| **Skill 格式错误** | 多行 YAML 嵌套结构（`arguments`、`allowed_tools`），OpenClaw 解析器只支持单行键值 | 🔴 致命 |
| **无持久化** | in-memory Map，进程重启后记忆全部丢失 | 🔴 致命 |
| **Schema 格式** | 手写 JSON Schema 对象，非 `@sinclair/typebox` | 🔴 致命 |
| **返回值格式** | `JSON.stringify({success, data})` 非 `{ content: [{ type: "text", text }] }` | 🔴 致命 |
| **无 Plugin 结构** | 缺少 `openclaw.plugin.json`、`package.json` 的 `openclaw` 字段 | 🔴 致命 |
| **功能缺失** | depth 遍历、timeRange 过滤、supersede 模式、archive、cleanup、ToolLimiter | 🟡 中等 |
| **无测试** | 全部删除，无新测试覆盖 | 🔴 严重 |
| **命名不规范** | `graph_memory`（下划线）应为 kebab-case | 🟡 轻微 |

---

## OpenClaw 接口规范对照

### Tool 注册（官方 Plugin SDK）

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";

export default definePluginEntry({
  id: "graph-memory",
  register(api) {
    api.registerTool({
      name: "graph_memory",
      description: "图记忆工具 - 让 AI 拥有真正的长期记忆能力",
      parameters: Type.Object({
        action: Type.String({ enum: ["recall", "commit", "purge", ...] }),
        params: Type.Object({ ... }),
      }),
      async execute(_id, params) {
        // 返回格式必须是:
        return { content: [{ type: "text", text: resultString }] };
      },
    });
  },
});
```

### SKILL.md 格式（官方要求）

```markdown
---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆，管理人设和任务"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# 正文指令...
```

**关键约束**：
- `metadata` 必须是**单行 JSON 对象**
- `description` 不能包含 `: `（冒号+空格），否则 YAML 解析**静默失败**
- `name` 必须 kebab-case，与文件夹名匹配
- **不支持** `arguments`、`allowed_tools`、`context: inline` 等多行 YAML 嵌套结构
- 所有 frontmatter 键值必须是**单行**

### Plugin Manifest

```json
{
  "id": "graph-memory",
  "name": "Graph Memory",
  "description": "让 AI 拥有真正的长期记忆能力",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

### package.json 扩展

```json
{
  "openclaw": {
    "extensions": ["./dist/plugin-entry.js"],
    "compat": {
      "pluginApi": ">=2026.3.24-beta.2",
      "minGatewayVersion": "2026.3.24-beta.2"
    },
    "build": {
      "openclawVersion": "2026.3.24-beta.2",
      "pluginSdkVersion": "2026.3.24-beta.2"
    }
  }
}
```

---

## 实施步骤

### Phase 1: 项目结构改造为 OpenClaw Plugin（🔴 P0 - 阻塞）

#### 1.1 添加 OpenClaw Plugin SDK 依赖

- [ ] 1.1.1 `npm install @sinclair/typebox`
- [ ] 1.1.2 更新 `ts/package.json` 添加 `openclaw` 字段（extensions、compat、build）
- [ ] 1.1.3 创建 `ts/openclaw.plugin.json` manifest 文件

#### 1.2 创建 Plugin Entry Point

- [ ] 1.2.1 创建 `ts/src/plugin-entry.ts`
  - 使用 `definePluginEntry` 包裹
  - 通过 `api.registerTool()` 注册 GraphMemoryTool
  - 工具名称: `graph_memory`
  - 描述: "图记忆工具 - 让 AI 拥有真正的长期记忆能力"
- [ ] 1.2.2 确保 entry point 导出为 ESM 格式
- [ ] 1.2.3 更新 `ts/tsconfig.json` 确保编译输出路径正确

#### 1.3 迁移 Tool Schema 到 TypeBox

- [ ] 1.3.1 创建 `ts/src/runtime/core/tools/builtin/graph_memory_schema.ts`
  - 用 `Type.Object` 定义 action 参数
  - 用 `Type.Object` 定义 params 嵌套结构
  - 覆盖所有 10 个 action 的参数类型
- [ ] 1.3.2 更新 `graph_memory_tool.ts` 的 `inputSchema` 字段为 TypeBox schema
- [ ] 1.3.3 修改 `handler` 方法签名匹配 OpenClaw 的 `execute(_id, params)` 格式
- [ ] 1.3.4 修改返回值格式为 `{ content: [{ type: "text", text: string }] }`

#### 1.4 更新 Tool Interface

- [ ] 1.4.1 更新 `ts/src/runtime/core/tools/tool_interface.ts`
  - 保持向后兼容（如其他模块引用）
  - 添加 OpenClaw 兼容的 `execute` 方法签名
  - 添加 `content` 返回类型定义

#### Phase 1 验收标准

- [ ] `npm run build` 编译通过
- [ ] `openclaw.plugin.json` 格式正确
- [ ] Plugin entry 使用 `definePluginEntry`
- [ ] Tool 使用 `api.registerTool` 注册
- [ ] Schema 使用 TypeBox
- [ ] 返回值格式为 `{ content: [{ type: "text", text }] }`

---

### Phase 2: SKILL.md 格式修复（🔴 P0 - 阻塞）

#### 2.1 修复 `skills/graph_memory/SKILL.md`

- [ ] 2.1.1 移除 `when_to_use` 多行值（合并到 `description`）
- [ ] 2.1.2 移除 `context: inline`（非 OpenClaw 标准字段）
- [ ] 2.1.3 移除 `allowed_tools` 多行数组
- [ ] 2.1.4 移除 `arguments` 多行嵌套结构
- [ ] 2.1.5 `name` 改为 `graph-memory`（kebab-case）
- [ ] 2.1.6 `description` 改为单行，不含 `: `
- [ ] 2.1.7 添加 `metadata` 单行 JSON
- [ ] 2.1.8 保留 `user_invocable: true`（改为 `user-invocable: true`，kebab-case）

**修复后格式**：

```yaml
---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆，管理人设和任务。使用 recall 检索、commit 写入、purge 删除"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---
```

#### 2.2 修复 `skills/graph_memory/persona/SKILL.md`

- [ ] 2.2.1 移除 `when_to_use`、`context`、`allowed_tools`、`arguments`
- [ ] 2.2.2 `name` 改为 `graph-memory-persona`
- [ ] 2.2.3 `description` 改为单行
- [ ] 2.2.4 添加 `metadata` 单行 JSON

#### 2.3 修复 `skills/graph_memory/task/SKILL.md`

- [ ] 2.3.1 移除 `when_to_use`、`context`、`allowed_tools`、`arguments`
- [ ] 2.3.2 `name` 改为 `graph-memory-task`
- [ ] 2.3.3 `description` 改为单行
- [ ] 2.3.4 添加 `metadata` 单行 JSON

#### 2.4 同步修复 `ts/bundled-skills/` 下三个文件

- [ ] 2.4.1 `ts/bundled-skills/graph_memory/SKILL.md`
- [ ] 2.4.2 `ts/bundled-skills/graph_memory/persona/SKILL.md`
- [ ] 2.4.3 `ts/bundled-skills/graph_memory/task/SKILL.md`

#### 2.5 重命名目录（kebab-case）

- [ ] 2.5.1 `skills/graph_memory/` → `skills/graph-memory/`
- [ ] 2.5.2 `skills/graph_memory/persona/` → `skills/graph-memory/persona/`
- [ ] 2.5.3 `skills/graph_memory/task/` → `skills/graph-memory/task/`
- [ ] 2.5.4 `ts/bundled-skills/graph_memory/` → `ts/bundled-skills/graph-memory/`
- [ ] 2.5.5 同步更新 README.md 和 README_EN.md 中的路径引用

#### Phase 2 验收标准

- [ ] 所有 SKILL.md 的 frontmatter 仅含单行键值
- [ ] `name` 全部 kebab-case
- [ ] `description` 不含 `: `
- [ ] `metadata` 为单行 JSON 对象
- [ ] 无 `arguments`、`allowed_tools`、`context: inline` 等非标准字段
- [ ] 目录名与 `name` 一致

---

### Phase 3: GraphDatabase 持久化（🔴 P0 - 核心价值）

#### 3.1 添加 SQLite 依赖

- [ ] 3.1.1 `npm install better-sqlite3`
- [ ] 3.1.2 `npm install @types/better-sqlite3 --save-dev`

#### 3.2 重写 GraphDatabase

- [ ] 3.2.1 修改构造函数接受 `dbPath` 参数
- [ ] 3.2.2 使用 `better-sqlite3` 创建/连接数据库
- [ ] 3.2.3 创建实体表（entities）：
  - `id TEXT PRIMARY KEY`
  - `name TEXT UNIQUE NOT NULL`
  - `type TEXT`
  - `mention_count INTEGER DEFAULT 1`
  - `created_at TEXT DEFAULT CURRENT_TIMESTAMP`
  - `updated_at TEXT DEFAULT CURRENT_TIMESTAMP`
- [ ] 3.2.4 创建关系表（relations）：
  - `id TEXT PRIMARY KEY`
  - `source_id TEXT NOT NULL`（外键 → entities.id）
  - `target_id TEXT NOT NULL`（外键 → entities.id）
  - `relation_type TEXT NOT NULL`
  - `confidence REAL DEFAULT 1.0`
  - `status TEXT DEFAULT 'active'`
  - `session_id TEXT`
  - `turn_id INTEGER`
  - `created_at TEXT DEFAULT CURRENT_TIMESTAMP`
  - `updated_at TEXT DEFAULT CURRENT_TIMESTAMP`
  - `date_bucket TEXT`
  - `superseded_by INTEGER`
- [ ] 3.2.5 创建索引：
  - `idx_entity_name ON entities(name)`
  - `idx_entity_type ON entities(type)`
  - `idx_relation_source ON relations(source_id)`
  - `idx_relation_target ON relations(target_id)`
  - `idx_relation_type ON relations(relation_type)`
  - `idx_relation_status ON relations(status)`
  - `idx_relation_session ON relations(session_id)`
  - `idx_relation_date ON relations(date_bucket)`

#### 3.3 实现 recall 的 depth 多跳遍历

- [ ] 3.3.1 实现 BFS/DFS 图遍历算法
- [ ] 3.3.2 depth=1: 直接匹配关键词的实体及其关系
- [ ] 3.3.3 depth=2: 扩展到相邻实体的关系
- [ ] 3.3.4 depth=N: 递归扩展到 N 层
- [ ] 3.3.5 限制最大 depth 为 5（防止爆炸）
- [ ] 3.3.6 去重已访问实体

#### 3.4 实现 recall 的 timeRange 过滤

- [ ] 3.4.1 解析 `timeRange.days` 参数
- [ ] 3.4.2 在 SQL 查询中添加 `created_at >= datetime('now', '-N days')` 条件
- [ ] 3.4.3 支持 `timeRange.from` 和 `timeRange.to` 范围查询

#### 3.5 实现 purge 的 supersede 模式

- [ ] 3.5.1 当 `mode === 'supersede'` 时：
  - 标记旧关系为 `superseded`
  - 设置 `superseded_by` 指向新关系 ID
  - 创建新关系（使用 `newRelation` 参数）
- [ ] 3.5.2 更新 `PurgeParams` 类型支持 `newRelation` 字段

#### 3.6 实现 memory_archive 归档功能

- [ ] 3.6.1 添加 `archive(days: number)` 方法
- [ ] 3.6.2 将 N 天前的非活跃关系标记为 `archived`
- [ ] 3.6.3 在 recall 中排除 `archived` 状态的关系（除非显式查询）

#### 3.7 实现 memory_cleanup 清理功能

- [ ] 3.7.1 添加 `cleanup(dryRun: boolean)` 方法
- [ ] 3.7.2 物理删除 `status = 'deleted'` 超过 90 天的关系
- [ ] 3.7.3 删除孤立节点（无任何关系连接的实体）
- [ ] 3.7.4 `dryRun=true` 时只返回将被删除的内容

#### 3.8 修复 isEntityDeleted 逻辑

- [ ] 3.8.1 当前逻辑有误：只要有一个关系被删就算实体被删
- [ ] 3.8.2 修正为：实体本身无 deleted 状态，通过关系状态判断
- [ ] 3.8.3 或者：在 entities 表中添加 `status` 字段

#### Phase 3 验收标准

- [ ] 数据持久化：写入后重启进程，数据仍然存在
- [ ] recall depth 遍历正确返回 N 层关系
- [ ] timeRange 过滤按时间正确筛选
- [ ] supersede 模式正确标记替代关系
- [ ] archive 正确归档旧数据
- [ ] cleanup 正确清理无效数据
- [ ] 编译通过，无类型错误

---

### Phase 4: ToolLimiter 迁移（🟡 P2 - 优化）

#### 4.1 创建 ToolLimiter

- [ ] 4.1.1 创建 `ts/src/runtime/core/tools/tool_limiter.ts`
- [ ] 4.1.2 移植 Python `ToolLimiter` 逻辑：
  - `ToolLimits` 配置类
  - `ToolCallCount` 计数类
  - `_classify_tool` 分类方法
  - `can_call` 检查方法
  - `record_call` 记录方法
  - `reset` 重置方法
- [ ] 4.1.3 默认限制值：
  - persona_query_max: 1
  - persona_update_max: 1
  - task_query_max: 4
  - task_update_max: 5
  - memory_query_max: 20
  - memory_update_max: 10

#### 4.2 集成到 GraphMemoryTool

- [ ] 4.2.1 在 Tool 构造函数中初始化 ToolLimiter
- [ ] 4.2.2 在 `execute` 方法中调用 `can_call` 检查
- [ ] 4.2.3 调用成功后调用 `record_call` 记录
- [ ] 4.2.4 每轮对话结束时调用 `reset` 重置计数

#### Phase 4 验收标准

- [ ] ToolLimiter 正确分类所有工具调用
- [ ] 超过限制时返回明确的拒绝消息
- [ ] 每轮对话计数正确重置

---

### Phase 5: 测试重建（🔴 P1 - 质量保障）

#### 5.1 GraphDatabase 测试

- [ ] 5.1.1 创建 `ts/tests/runtime/core/graph_memory/graph_database.test.ts`
- [ ] 5.1.2 commit 测试：创建实体和关系
- [ ] 5.1.3 recall 测试：按关键词检索、按 seedEntities 检索
- [ ] 5.1.4 recall depth 测试：1层、2层、3层遍历
- [ ] 5.1.5 recall timeRange 测试：按时间范围过滤
- [ ] 5.1.6 purge soft 测试：软删除
- [ ] 5.1.7 purge hard 测试：硬删除
- [ ] 5.1.8 purge supersede 测试：纠错替代
- [ ] 5.1.9 introspect 测试：返回统计
- [ ] 5.1.10 持久化测试：重启后数据保留
- [ ] 5.1.11 archive 测试：归档旧数据
- [ ] 5.1.12 cleanup 测试：清理无效数据
- [ ] 5.1.13 sessionFilter 测试：按会话过滤
- [ ] 5.1.14 并发测试：多线程安全
- [ ] 5.1.15 边界测试：空查询、超长字符串

#### 5.2 MemoryService 测试

- [ ] 5.2.1 创建 `ts/tests/runtime/core/graph_memory/memory_service.test.ts`
- [ ] 5.2.2 updatePersona merge 测试
- [ ] 5.2.3 updatePersona replace 测试
- [ ] 5.2.4 clearPersona 测试
- [ ] 5.2.5 createTask 测试
- [ ] 5.2.6 setTaskState 测试
- [ ] 5.2.7 deleteTask 测试
- [ ] 5.2.8 linkInfoToTask 测试
- [ ] 5.2.9 setSessionId/getSessionId 测试
- [ ] 5.2.10 任务状态转换测试（进行中→已暂停→进行中→已完成）
- [ ] 5.2.11 人设属性合并测试
- [ ] 5.2.12 错误处理测试：无效参数

#### 5.3 GraphMemoryTool 测试

- [ ] 5.3.1 创建 `ts/tests/runtime/core/tools/builtin/graph_memory_tool.test.ts`
- [ ] 5.3.2 metadata 测试：id、name、category
- [ ] 5.3.3 recall action 测试
- [ ] 5.3.4 commit action 测试
- [ ] 5.3.5 purge action 测试
- [ ] 5.3.6 introspect action 测试
- [ ] 5.3.7 persona_update action 测试
- [ ] 5.3.8 persona_clear action 测试
- [ ] 5.3.9 task_create action 测试
- [ ] 5.3.10 task_set_state action 测试
- [ ] 5.3.11 task_delete action 测试
- [ ] 5.3.12 task_link_info action 测试
- [ ] 5.3.13 未知 action 错误处理测试
- [ ] 5.3.14 返回值格式测试：`{ content: [{ type: "text", text }] }`
- [ ] 5.3.15 ToolLimiter 集成测试

#### 5.4 Plugin Entry 集成测试

- [ ] 5.4.1 创建 `ts/tests/plugin-entry.test.ts`
- [ ] 5.4.2 Plugin 注册测试
- [ ] 5.4.3 Tool 注册测试
- [ ] 5.4.4 Schema 验证测试

#### Phase 5 验收标准

- [ ] `npm test` 全部通过（50+ 用例）
- [ ] 无跳过（skip）的测试
- [ ] 覆盖率 > 80%

---

### Phase 6: 文档更新（🟢 P3 - 收尾）

#### 6.1 更新 README.md

- [ ] 6.1.1 更新标题：TrulyMEM → OpenClaw Graph Memory Plugin
- [ ] 6.1.2 更新安装方式：`openclaw plugins install`
- [ ] 6.1.3 更新使用示例
- [ ] 6.1.4 更新目录结构说明
- [ ] 6.1.5 更新 API 文档（反映 TypeBox schema）

#### 6.2 更新 README_EN.md

- [ ] 6.2.1 同步中文 README 的所有更新
- [ ] 6.2.2 确保英文表达准确

#### 6.3 更新迁移设计文档

- [ ] 6.3.1 更新 `docs/integration/waterflow-design.md`
- [ ] 6.3.2 添加 OpenClaw 接口适配说明
- [ ] 6.3.3 更新架构图中 Plugin SDK 部分

#### Phase 6 验收标准

- [ ] README.md 和 README_EN.md 内容一致
- [ ] 安装步骤可执行
- [ ] API 文档与实际代码一致

---

## 目标目录结构（重构后）

```
TrulyMEM-TrueHumanMEM/
├── ts/
│   ├── src/
│   │   ├── plugin-entry.ts                    # [NEW] OpenClaw Plugin 入口
│   │   └── runtime/core/
│   │       ├── graph_memory/
│   │       │   ├── index.ts
│   │       │   ├── types.ts
│   │       │   ├── graph_database.ts          # [REWRITE] SQLite 持久化
│   │       │   └── memory_service.ts
│   │       └── tools/
│   │           ├── builtin/
│   │           │   ├── graph_memory_tool.ts   # [UPDATE] OpenClaw 兼容
│   │           │   └── graph_memory_schema.ts # [NEW] TypeBox Schema
│   │           ├── tool_interface.ts          # [UPDATE] 添加 execute 签名
│   │           └── tool_limiter.ts            # [NEW] 调用限制器
│   ├── bundled-skills/
│   │   └── graph-memory/                      # [RENAMED] kebab-case
│   │       ├── SKILL.md                       # [FIXED] 单行 frontmatter
│   │       ├── persona/
│   │       │   └── SKILL.md                   # [FIXED]
│   │       └── task/
│   │           └── SKILL.md                   # [FIXED]
│   ├── tests/
│   │   └── runtime/core/
│   │       ├── graph_memory/
│   │       │   ├── graph_database.test.ts     # [NEW]
│   │       │   └── memory_service.test.ts     # [NEW]
│   │       └── tools/builtin/
│   │           └── graph_memory_tool.test.ts  # [NEW]
│   ├── package.json                           # [UPDATE] 添加 openclaw 字段
│   ├── tsconfig.json
│   └── openclaw.plugin.json                   # [NEW] Plugin Manifest
├── skills/
│   └── graph-memory/                          # [RENAMED] kebab-case
│       ├── SKILL.md                           # [FIXED]
│       ├── persona/
│       │   └── SKILL.md                       # [FIXED]
│       └── task/
│           └── SKILL.md                       # [FIXED]
├── docs/integration/waterflow-design.md       # [UPDATE]
├── README.md                                  # [UPDATE]
├── README_EN.md                               # [UPDATE]
├── .gitignore
└── LICENSE
```

---

## 依赖变更

```json
{
  "dependencies": {
    "yaml": "^2.8.3",
    "@sinclair/typebox": "^0.34.0",
    "better-sqlite3": "^11.0.0"
  },
  "devDependencies": {
    "@types/node": "^25.5.2",
    "@types/better-sqlite3": "^7.6.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

---

## 执行顺序与并行策略

```
Phase 1 (P0) ──────────────────────────────────────┐
  1.1 依赖 ─→ 1.2 Entry ─→ 1.3 Schema ─→ 1.4 Interface  │
                                                      ├── 必须最先完成
Phase 2 (P0) ──────────────────────────────────────┤     否则无法在 OpenClaw 中运行
  2.1-2.3 SKILL.md 修复（可并行）                     │
  2.4 bundled-skills 同步                              │
  2.5 目录重命名                                       │
                                                      │
Phase 3 (P0) ──────────────────────────────────────┤
  3.1 SQLite 依赖                                     │
  3.2 GraphDatabase 重写                               │
  3.3-3.7 功能补全（可部分并行）                        │
  3.8 逻辑修复                                        │
                                                      │
Phase 4 (P2) ──────────────────────────────────────┤     优化项，可延后
  4.1 ToolLimiter 创建                                │
  4.2 集成到 Tool                                     │
                                                      │
Phase 5 (P1) ──────────────────────────────────────┘     在 Phase 1-3 完成后执行
  5.1-5.4 测试重建（可并行编写）

Phase 6 (P3) ────────────────────────────────────────── 最后执行，文档收尾
  6.1-6.3 文档更新
```

---

## 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| better-sqlite3 原生模块编译失败 | 阻塞 Phase 3 | 使用预编译二进制或回退到 sql.js |
| OpenClaw Plugin SDK 版本不兼容 | 阻塞 Phase 1 | 锁定 `compat.pluginApi` 版本 |
| SKILL.md 描述中的中文冒号 | 静默加载失败 | 所有 description 用双引号包裹 |
| SQLite 并发写入冲突 | 数据损坏 | 使用 WAL 模式 + 连接池 |
| depth 遍历性能问题 | 响应缓慢 | 限制最大 depth=5，结果上限 100 |

---

## 验收总标准

- [ ] Phase 1-6 全部完成
- [ ] `npm run build` 编译通过，无错误无警告
- [ ] `npm test` 全部通过（50+ 用例）
- [ ] 作为 OpenClaw Plugin 可安装、可加载、可调用
- [ ] 数据持久化：写入后重启进程，数据仍然存在
- [ ] 所有 main 分支的核心功能均已实现
- [ ] SKILL.md 通过 OpenClaw 的 `openclaw skills check` 验证

# TrulyMEM → WaterFlow 迁移设计文档

**版本**: 1.0  
**日期**: 2026-04-15  
**目标**: 用 TypeScript 完全重写 TrulyMEM 的图记忆能力，集成到 WaterFlow

---

## 一、迁移策略

### 1.1 核心原则

- **完全重写**: 不保留 Python 代码，用 TypeScript 实现
- **架构一致**: 遵循 WaterFlow 的架构风格和设计模式
- **原生集成**: 作为 WaterFlow 的内置模块，而非外部依赖

### 1.2 迁移范围

| TrulyMEM (Python) | WaterFlow (TypeScript) | 说明 |
|-------------------|------------------------|------|
| `EmbeddedGraphDB` | `GraphDatabase` | SQLite 图数据库重写 |
| `GraphMemoryClient` | `MemoryService` | 记忆服务 |
| 12 个记忆工具 | `GraphMemoryTool` | WaterFlow Tool 接口 |
| System Prompt | 提示词模板 | 提示词管理 |
| TUI | ❌ 不迁移 | WaterFlow 无 TUI |

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WaterFlow Core                               │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐  │
│  │  Agent /   │───>│   Query     │───>│   ToolExecutor        │  │
│  │  Workflow  │    │   Engine    │    │                       │  │
│  └─────────────┘    └──────────────┘    └───────────┬────────────┘  │
│                                                       │              │
│                        ┌──────────────────────────────┘              │
│                        ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    GraphMemory Module (NEW)                       │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │
│  │  │ GraphMemoryTool │  │ GraphDatabase   │  │ MemoryService   │ │ │
│  │  │ (Tool Interface)│  │ (SQLite Graph)  │  │ (LLM Integration)│ │ │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │ │
│  │           │                    │                    │          │ │
│  │           └────────────────────┼────────────────────┘          │ │
│  │                                ▼                                 │ │
│  │                    ┌─────────────────────┐                      │ │
│  │                    │   GraphMemoryStore   │                      │ │
│  │                    │   (In-Memory Cache)  │                      │ │
│  │                    └─────────────────────┘                      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 位置 |
|------|------|------|
| `GraphMemoryTool` | WaterFlow Tool 接口，暴露记忆能力 | `runtime/core/tools/builtin/graph_memory/` |
| `GraphDatabase` | SQLite 图数据库实现 | `runtime/core/graph_memory/database/` |
| `MemoryService` | 封装业务逻辑 | `runtime/core/graph_memory/service/` |
| `GraphMemoryStore` | 内存缓存，加速查询 | `runtime/core/graph_memory/store/` |
| `SystemPrompt` | 提示词模板管理 | `runtime/core/graph_memory/prompts/` |

---

## 三、目录结构

### 3.1 新增目录

```
WaterFlow/ts/src/
├── runtime/core/
│   ├── graph_memory/                          # 新增: 图记忆模块
│   │   ├── index.ts                           # 模块导出
│   │   ├── types.ts                           # 类型定义
│   │   ├── database/                          # 图数据库实现
│   │   │   ├── index.ts
│   │   │   ├── graph_database.ts              # 主类
│   │   │   ├── entity_store.ts                # 实体存储
│   │   │   └── relation_store.ts              # 关系存储
│   │   ├── service/                           # 服务层
│   │   │   ├── index.ts
│   │   │   ├── memory_service.ts              # 记忆服务
│   │   │   ├── recall_service.ts              # 检索服务
│   │   │   └── task_service.ts                # 任务服务
│   │   ├── store/                             # 缓存层
│   │   │   ├── index.ts
│   │   │   └── memory_cache.ts
│   │   └── prompts/                           # 提示词
│   │       └── system_prompt.ts
│   │
│   └── tools/builtin/
│       └── graph_memory/                      # GraphMemory Tool
│           ├── index.ts
│           ├── graph_memory_tool.ts           # Tool 实现
│           ├── types.ts                       # Tool 参数类型
│           └── tool_registry.ts               # 自动注册
```

### 3.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `runtime/core/tools/builtin/index.ts` | 注册 GraphMemoryTool |
| `shared/types/index.ts` | 导出图记忆类型 |

---

## 四、核心类型定义

### 4.1 图数据库类型

```typescript
// src/runtime/core/graph_memory/types.ts

export interface Entity {
  id: string;
  name: string;
  type: string;
  mentionCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Relation {
  id: string;
  sourceId: string;
  targetId: string;
  relationType: string;
  confidence: number;
  status: RelationStatus;
  sessionId: string;
  turnId: number;
  createdAt: Date;
  updatedAt: Date;
  dateBucket: string;
}

export type RelationStatus = 'active' | 'deleted' | 'archived' | 'superseded';

export interface Triplet {
  subject: string;
  relation: string;
  object: string;
  confidence?: number;
}

export interface RecallParams {
  queryIntent: string;
  seedEntities?: string[];
  depth?: number;
  timeRange?: { days: number };
  sessionFilter?: string;
}

export interface CommitParams {
  triplets: Triplet[];
  entityTypes?: Record<string, string>;
  temporalTag?: string;
  sessionId?: string;
  turnId?: number;
}

export interface PurgeParams {
  criteria: {
    subject?: string;
    target?: string;
    relation?: string;
    sessionId?: string;
  };
  mode?: 'soft' | 'hard' | 'supersede';
  newRelation?: { relation: string; target: string };
}

export type TaskState = '进行中' | '已完成' | '已暂停' | '已取消';

export interface MemoryStats {
  entityCount: number;
  relationCount: number;
  sessionId?: string;
}
```

### 4.2 Tool 参数类型

```typescript
// src/runtime/core/tools/builtin/graph_memory/types.ts

export type GraphMemoryAction =
  | 'recall' | 'commit' | 'purge' | 'introspect' | 'archive' | 'cleanup'
  | 'persona_update' | 'persona_clear'
  | 'task_create' | 'task_set_state' | 'task_delete' | 'task_link_info';

export interface GraphMemoryToolInput {
  action: GraphMemoryAction;
  params: Record<string, unknown>;
}
```

---

## 五、核心实现

### 5.1 GraphDatabase 实现

```typescript
// src/runtime/core/graph_memory/database/graph_database.ts

export class GraphDatabase {
  private db: Database;
  
  constructor(dbPath: string) {
    this.db = new Database(dbPath);
    this.initialize();
  }

  private initialize(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        type TEXT,
        mention_count INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS relations (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        status TEXT DEFAULT 'active',
        session_id TEXT,
        turn_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        date_bucket TEXT
      )
    `);

    // 索引
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name);
      CREATE INDEX IF NOT EXISTS idx_relation_status ON relations(status);
    `);
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    const { queryIntent, seedEntities, sessionFilter } = params;
    const keywords = queryIntent.split(/[,\s]+/).filter(k => k.length > 0);
    const entities: Entity[] = [];
    const relations: Relation[] = [];
    const entityIds = new Set<string>();

    // 搜索实体
    for (const keyword of keywords) {
      const rows = this.db.exec(
        `SELECT * FROM entities WHERE LOWER(name) LIKE ? LIMIT 50`,
        [`%${keyword.toLowerCase()}%`]
      );
      for (const row of rows) {
        if (!entityIds.has(row.id)) {
          entityIds.add(row.id);
          entities.push(this.rowToEntity(row));
        }
      }
    }

    // 搜索关系
    if (entityIds.size > 0) {
      const placeholders = Array.from(entityIds).map(() => '?').join(',');
      let query = `
        SELECT r.*, e1.name as source_name, e2.name as target_name
        FROM relations r
        JOIN entities e1 ON r.source_id = e1.id
        JOIN entities e2 ON r.target_id = e2.id
        WHERE (r.source_id IN (${placeholders}) OR r.target_id IN (${placeholders}))
          AND r.status = 'active'
      `;
      const queryParams = [...entityIds, ...entityIds];

      if (sessionFilter) {
        query += ` AND r.session_id = ?`;
        queryParams.push(sessionFilter);
      }

      const rows = this.db.exec(query, queryParams);
      for (const row of rows) {
        relations.push(this.rowToRelation(row));
      }
    }

    return { entities, relations, message: `找到 ${entities.length} 个实体, ${relations.length} 条关系` };
  }

  async commit(params: CommitParams): Promise<{ createdEntities: number; createdRelations: number }> {
    const { triplets, sessionId, turnId } = params;
    let createdEntities = 0;
    let createdRelations = 0;

    for (const triplet of triplets) {
      const sourceId = this.upsertEntity(triplet.subject);
      const targetId = this.upsertEntity(triplet.object);
      
      this.db.exec(`
        INSERT INTO relations (id, source_id, target_id, relation_type, confidence, session_id, turn_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
      `, [this.generateId(), sourceId, targetId, triplet.relation, triplet.confidence || 1.0, sessionId, turnId || 0]);
      
      createdEntities += 2;
      createdRelations++;
    }

    return { createdEntities, createdRelations };
  }

  async purge(params: PurgeParams): Promise<{ deleted: number; mode: string }> {
    const { criteria, mode = 'soft' } = params;
    const conditions: string[] = ['status = ?'];
    const values: unknown[] = ['active'];

    if (criteria.subject) {
      conditions.push(`source_id IN (SELECT id FROM entities WHERE name = ?)`);
      values.push(criteria.subject);
    }

    const whereClause = conditions.join(' AND ');
    const result = this.db.exec(`UPDATE relations SET status = 'deleted' WHERE ${whereClause}`, values);
    
    return { deleted: result.length, mode };
  }

  async introspect(): Promise<MemoryStats> {
    const entityCount = this.db.exec(`SELECT COUNT(*) as c FROM entities`)[0]?.c || 0;
    const relationCount = this.db.exec(`SELECT COUNT(*) as c FROM relations WHERE status = 'active'`)[0]?.c || 0;
    return { entityCount, relationCount };
  }

  private upsertEntity(name: string): string {
    const existing = this.db.exec(`SELECT id FROM entities WHERE name = ?`, [name]);
    if (existing.length > 0) {
      this.db.exec(`UPDATE entities SET mention_count = mention_count + 1 WHERE name = ?`, [name]);
      return existing[0].id;
    }
    const id = this.generateId();
    this.db.exec(`INSERT INTO entities (id, name, type) VALUES (?, ?, ?)`, [id, name, 'unknown']);
    return id;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private rowToEntity(row: any): Entity {
    return {
      id: row.id, name: row.name, type: row.type || 'unknown',
      mentionCount: row.mention_count || 1,
      createdAt: new Date(row.created_at), updatedAt: new Date(row.updated_at)
    };
  }

  private rowToRelation(row: any): Relation {
    return {
      id: row.id, sourceId: row.source_id, targetId: row.target_id,
      relationType: row.relation_type, confidence: row.confidence || 1.0,
      status: row.status || 'active', sessionId: row.session_id || '',
      turnId: row.turn_id || 0,
      createdAt: new Date(row.created_at), updatedAt: new Date(row.updated_at),
      dateBucket: row.date_bucket || ''
    };
  }

  close(): void { this.db.close(); }
}
```

### 5.2 GraphMemoryTool 实现

```typescript
// src/runtime/core/tools/builtin/graph_memory/graph_memory_tool.ts

import type { Tool, ToolExecutionContext, ToolInputSchema } from '../tool_interface';
import { GraphDatabase } from '../../../graph_memory/database/graph_database';
import { MemoryService } from '../../../graph_memory/service/memory_service';

export class GraphMemoryTool implements Tool {
  readonly id = 'builtin:graph_memory';
  readonly name = 'GraphMemory';
  readonly description = `图记忆工具 - 让 AI 拥有真正的长期记忆能力

操作:
- recall: 检索记忆
- commit: 写入记忆
- purge: 删除记忆
- introspect: 查看状态
- persona_update/clear: 人设管理
- task_create/set_state/delete: 任务管理`;

  readonly category = 'analysis';
  readonly permissionLevel: 'safe' = 'safe';
  readonly inputSchema: ToolInputSchema = {
    type: 'object',
    properties: {
      action: {
        type: 'string',
        enum: ['recall', 'commit', 'purge', 'introspect', 'persona_update', 'persona_clear',
                'task_create', 'task_set_state', 'task_delete', 'task_link_info'],
        description: '记忆操作类型'
      },
      params: { type: 'object', description: '操作参数' }
    },
    required: ['action', 'params']
  };

  private db: GraphDatabase;
  private service: MemoryService;

  constructor(config: { dbPath: string; sessionId?: string }) {
    this.db = new GraphDatabase(config.dbPath);
    this.service = new MemoryService(this.db, config.sessionId);
  }

  async handler(params: Record<string, unknown>, context: ToolExecutionContext): Promise<string> {
    const action = params.action as string;
    const actionParams = params.params as Record<string, unknown>;

    try {
      const result = await this.executeAction(action, actionParams);
      return JSON.stringify({ success: true, data: result }, null, 2);
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: { type: 'execution_error', message: error instanceof Error ? error.message : String(error) }
      }, null, 2);
    }
  }

  private async executeAction(action: string, params: Record<string, unknown>): Promise<unknown> {
    switch (action) {
      case 'recall': return this.service.recall(params as any);
      case 'commit': return this.service.commit(params as any);
      case 'purge': return this.service.purge(params as any);
      case 'introspect': return this.service.introspect();
      case 'persona_update': return this.service.updatePersona(params);
      case 'persona_clear': return this.service.clearPersona(params);
      case 'task_create': return this.service.createTask(params);
      case 'task_set_state': return this.service.setTaskState(params);
      case 'task_delete': return this.service.deleteTask(params);
      default: throw new Error(`Unknown action: ${action}`);
    }
  }

  close(): void { this.db.close(); }
}
```

### 5.3 MemoryService 实现

```typescript
// src/runtime/core/graph_memory/service/memory_service.ts

import { GraphDatabase } from '../database/graph_database';
import type { RecallParams, CommitParams, PurgeParams } from '../types';

export class MemoryService {
  private db: GraphDatabase;
  private sessionId: string;

  constructor(db: GraphDatabase, sessionId?: string) {
    this.db = db;
    this.sessionId = sessionId || `session-${Date.now()}`;
  }

  async recall(params: RecallParams) {
    return this.db.recall({ ...params, sessionFilter: params.sessionFilter || this.sessionId });
  }

  async commit(params: CommitParams) {
    return this.db.commit({ ...params, sessionId: params.sessionId || this.sessionId });
  }

  async purge(params: PurgeParams) {
    return this.db.purge(params);
  }

  async introspect() {
    const stats = await this.db.introspect();
    return { ...stats, sessionId: this.sessionId };
  }

  async updatePersona(params: Record<string, unknown>) {
    const attributes = params.attributes as Array<{ attribute: string; value: string }>;
    const mode = params.mode as string || 'merge';

    if (mode === 'replace') {
      await this.db.purge({ criteria: { subject: 'AI' }, mode: 'soft' });
    }

    const triplets = attributes.map(attr => ({
      subject: 'AI', relation: attr.attribute, object: attr.value, confidence: 1.0
    }));

    await this.commit({ triplets });
    return { status: 'success', updatedAttributes: attributes.length };
  }

  async clearPersona(params: Record<string, unknown>) {
    if (params.confirm === false) return { status: 'cancelled', deletedCount: 0 };
    const result = await this.purge({ criteria: { subject: 'AI' }, mode: 'soft' });
    return { status: 'success', deletedCount: result.deleted };
  }

  async createTask(params: Record<string, unknown>) {
    const taskId = params.task_id as string;
    const description = params.description as string;
    const infoNodes = (params.info_nodes as string[]) || [];

    await this.commit({
      triplets: [
        { subject: taskId, relation: 'is_type', object: 'TaskNode' },
        { subject: taskId, relation: 'has_description', object: description },
        { subject: taskId, relation: 'HAS_STATE', object: 'State_进行中' }
      ]
    });

    if (infoNodes.length > 0) {
      await this.commit({
        triplets: infoNodes.map(node => ({ subject: taskId, relation: 'CONTAINS_INFO', object: node }))
      });
    }

    return { status: 'success', taskId };
  }

  async setTaskState(params: Record<string, unknown>) {
    const taskId = params.task_id as string;
    const state = params.state as string;

    await this.purge({ criteria: { subject: taskId, relation: 'HAS_STATE' }, mode: 'soft' });
    await this.commit({ triplets: [{ subject: taskId, relation: 'HAS_STATE', object: `State_${state}` }] });

    return { status: 'success', newState: state };
  }

  async deleteTask(params: Record<string, unknown>) {
    const taskId = params.task_id as string;
    await this.purge({ criteria: { subject: taskId }, mode: 'soft' });
    return { status: 'success', taskId };
  }
}
```

---

## 六、测试方案

### 6.1 测试文件结构

```
WaterFlow/ts/tests/
├── runtime/core/graph_memory/
│   ├── database/
│   │   └── graph_database.test.ts       # 15+ 测试
│   └── service/
│       └── memory_service.test.ts       # 12+ 测试
└── runtime/core/tools/builtin/
    └── graph_memory/
        └── graph_memory_tool.test.ts    # 15+ 测试
```

### 6.2 数据库测试

```typescript
// tests/runtime/core/graph_memory/database/graph_database.test.ts

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { GraphDatabase } from '../../../../../src/runtime/core/graph_memory/database/graph_database';
import * as fs from 'fs';

describe('GraphDatabase', () => {
  const testDbPath = '/tmp/test_graph_memory.db';
  let db: GraphDatabase;

  beforeEach(() => {
    if (fs.existsSync(testDbPath)) fs.unlinkSync(testDbPath);
    db = new GraphDatabase(testDbPath);
  });

  afterEach(() => {
    db.close();
    if (fs.existsSync(testDbPath)) fs.unlinkSync(testDbPath);
  });

  describe('commit', () => {
    it('should create entities and relations', async () => {
      const result = await db.commit({
        triplets: [
          { subject: '用户', relation: '喜欢', object: 'Python' },
          { subject: '用户', relation: '正在学习', object: 'TypeScript' }
        ]
      });
      expect(result.createdEntities).toBe(3);
      expect(result.createdRelations).toBe(2);
    });
  });

  describe('recall', () => {
    beforeEach(async () => {
      await db.commit({
        triplets: [
          { subject: '用户', relation: '喜欢', object: 'Python' },
          { subject: 'Python', relation: '是', object: '编程语言' }
        ]
      });
    });

    it('should recall by keyword', async () => {
      const result = await db.recall({ queryIntent: 'Python' });
      expect(result.entities.some(e => e.name === 'Python')).toBe(true);
    });

    it('should recall relations', async () => {
      const result = await db.recall({ queryIntent: '用户,Python' });
      expect(result.relations.length).toBeGreaterThan(0);
    });
  });

  describe('purge', () => {
    beforeEach(async () => {
      await db.commit({
        triplets: [{ subject: '旧信息', relation: 'is', object: '垃圾' }]
      });
    });

    it('should soft delete relations', async () => {
      const result = await db.purge({ criteria: { subject: '旧信息' }, mode: 'soft' });
      expect(result.deleted).toBeGreaterThan(0);
      expect(result.mode).toBe('soft');
    });
  });

  describe('introspect', () => {
    it('should return statistics', async () => {
      await db.commit({ triplets: [{ subject: 'A', relation: 'relates', object: 'B' }] });
      const stats = await db.introspect();
      expect(stats.entityCount).toBe(2);
      expect(stats.relationCount).toBe(1);
    });
  });
});
```

### 6.3 服务层测试

```typescript
// tests/runtime/core/graph_memory/service/memory_service.test.ts

import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryService } from '../../../../../src/runtime/core/graph_memory/service/memory_service';
import { GraphDatabase } from '../../../../../src/runtime/core/graph_memory/database/graph_database';

describe('MemoryService', () => {
  const testDbPath = '/tmp/test_memory_service.db';
  let db: GraphDatabase;
  let service: MemoryService;

  beforeEach(() => {
    db = new GraphDatabase(testDbPath);
    service = new MemoryService(db, 'test-session');
  });

  describe('persona management', () => {
    it('should update persona', async () => {
      const result = await service.updatePersona({
        attributes: [{ attribute: '角色', value: '猫娘' }],
        mode: 'replace'
      });
      expect(result.status).toBe('success');
      expect(result.updatedAttributes).toBe(1);
    });

    it('should clear persona', async () => {
      await service.updatePersona({ attributes: [{ attribute: '角色', value: '猫娘' }] });
      const result = await service.clearPersona({ confirm: true });
      expect(result.status).toBe('success');
    });
  });

  describe('task management', () => {
    it('should create task', async () => {
      const result = await service.createTask({
        task_id: 'Task_Test',
        description: '测试任务',
        info_nodes: ['info1']
      });
      expect(result.taskId).toBe('Task_Test');
    });

    it('should set task state', async () => {
      await service.createTask({ task_id: 'Task_State', description: '测试' });
      const result = await service.setTaskState({ task_id: 'Task_State', state: '已完成' });
      expect(result.newState).toBe('已完成');
    });
  });
});
```

### 6.4 Tool 接口测试

```typescript
// tests/runtime/core/tools/builtin/graph_memory/graph_memory_tool.test.ts

import { describe, it, expect, beforeEach } from 'vitest';
import { GraphMemoryTool } from '../../../../../src/runtime/core/tools/builtin/graph_memory/graph_memory_tool';
import * as fs from 'fs';

describe('GraphMemoryTool', () => {
  const testDbPath = '/tmp/test_graph_memory_tool.db';
  let tool: GraphMemoryTool;

  beforeEach(() => {
    if (fs.existsSync(testDbPath)) fs.unlinkSync(testDbPath);
    tool = new GraphMemoryTool({ dbPath: testDbPath, sessionId: 'test' });
  });

  it('should have correct metadata', () => {
    expect(tool.id).toBe('builtin:graph_memory');
    expect(tool.name).toBe('GraphMemory');
    expect(tool.category).toBe('analysis');
  });

  describe('recall', () => {
    it('should execute recall', async () => {
      await tool.handler({ action: 'commit', params: { triplets: [{ subject: 'Test', relation: 't', object: 'D' }] } }, mockContext());
      const result = await tool.handler({ action: 'recall', params: { query_intent: 'Test' } }, mockContext());
      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });
  });

  describe('commit', () => {
    it('should execute commit', async () => {
      const result = await tool.handler({
        action: 'commit',
        params: { triplets: [{ subject: '用户', relation: '喜欢', object: 'AI' }] }
      }, mockContext());
      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });
  });

  describe('error handling', () => {
    it('should return error for unknown action', async () => {
      const result = await tool.handler({ action: 'unknown', params: {} }, mockContext());
      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(false);
    });
  });
});

function mockContext() {
  return {
    toolCallId: 'test', workingDirectory: '/tmp', abortController: { signal: {} },
    config: { timeout: 5000 }, logger: { info: () => {}, warn: () => {}, error: () => {}, debug: () => {} }
  };
}
```

### 6.5 验证检查清单

```
[ ] GraphDatabase.commit - 创建实体和关系
[ ] GraphDatabase.recall - 按关键词检索
[ ] GraphDatabase.purge - 软删除
[ ] GraphDatabase.introspect - 返回统计

[ ] MemoryService.updatePersona - 人设更新
[ ] MemoryService.clearPersona - 人设清除
[ ] MemoryService.createTask - 创建任务
[ ] MemoryService.setTaskState - 设置状态
[ ] MemoryService.deleteTask - 删除任务

[ ] GraphMemoryTool recall action
[ ] GraphMemoryTool commit action
[ ] GraphMemoryTool persona_update action
[ ] GraphMemoryTool task_create action
[ ] GraphMemoryTool error handling
```

---

## 七、实现计划

| Phase | 任务 | 周期 | 测试 |
|-------|------|------|------|
| 1 | GraphDatabase 实现 | 2-3 天 | 15+ |
| 2 | MemoryService 实现 | 1-2 天 | 12+ |
| 3 | GraphMemoryTool 实现 | 1-2 天 | 15+ |
| 4 | 集成测试 | 1 天 | 8+ |

**总计**: 5-8 天，50+ 测试用例

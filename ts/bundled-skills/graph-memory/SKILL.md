---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆，管理人设和任务。作为 OpenClaw memory-core 的增强补充，不替代其核心功能"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory 图记忆系统

让 AI 拥有真正的长期记忆能力。

> **定位声明**：本工具是 **OpenClaw memory-core 的增强补充**，而非替代。memory-core 负责 session transcripts 和历史消息管理，GraphMemory 提供图数据库形式的结构化长期记忆。两者可并存运行。

## 与 memory-core 的关系

| 功能 | memory-core | GraphMemory (本工具) |
|------|-------------|---------------------|
| 对话历史 | ✅ 自动保存 messages | ❌ 不管理对话历史 |
| 结构化记忆 | ❌ 无 | ✅ 三元组图存储 |
| 人设管理 | ❌ 无 | ✅ persona_update/clear |
| 任务追踪 | ❌ 无 | ✅ task_create/set_state |
| 自动触发 | ✅ 自动索引检索 | ❌ LLM 可选调用 |

## 核心概念

### 实体 (Entity)
现实世界中的对象，如"用户"、"Python"、"WaterFlow"。

### 关系 (Relation)
连接两个实体的关系，格式为三元组：主体 - 关系 - 客体。

## 可用命令

### 1. recall - 检索记忆

从记忆图中检索相关信息。

**参数**:
- `queryIntent`: 搜索意图/关键词（必需，若无则需提供 seedEntities）
- `seedEntities`: 可选的种子实体名
- `depth`: 检索深度 1-5（默认 2）
- `sessionFilter`: 可选的会话ID过滤

### 2. commit - 写入记忆

将信息写入记忆图。

**参数**:
- `triplets`: 三元组数组，每个包含 subject, relation, object（必需）
- `sessionId`: 会话ID
- `turnId`: 轮次ID

### 3. purge - 删除记忆

从记忆图中删除信息。

**参数**:
- `criteria`: 删除条件 (subject, target, relation, sessionId)
- `mode`: 删除模式 (soft/hard/supersede)
- `newRelation`: 替代关系（supersede 模式必需）

### 4. introspect - 查看状态

查看当前记忆状态统计。

### 5. archive - 归档旧记忆

将 N 天前的非活跃关系标记为归档。

**参数**:
- `days`: 归档天数（默认 30）

### 6. cleanup - 清理无效数据

物理删除已删除超过 90 天的关系和孤立节点。

**参数**:
- `dry_run`: 仅预览不删除（默认 true）

## 使用原则

1. **选择性记忆**: 只记住重要和持久的信息
2. **结构化**: 使用三元组 (主体-关系-客体) 格式
3. **关联**: 通过关系连接相关实体
4. **定期清理**: 删除过时或错误的信息
5. **与 memory-core 配合**: 对话历史由 memory-core 管理，结构化事实由 GraphMemory 管理

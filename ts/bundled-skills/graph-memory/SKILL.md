---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆，管理人设和任务。使用 recall 检索、commit 写入、purge 删除"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory 图记忆操作

你可以通过以下操作与图记忆系统交互。

## 核心操作

### 1. recall - 检索记忆

从记忆图中检索相关信息。

**参数**:
- `queryIntent`: 搜索意图/关键词
- `seedEntities`: 可选的种子实体名
- `depth`: 检索深度
- `sessionFilter`: 可选的会话ID过滤

### 2. commit - 写入记忆

将信息写入记忆图。

**参数**:
- `triplets`: 三元组数组，每个包含 subject, relation, object
- `sessionId`: 会话ID
- `turnId`: 轮次ID

### 3. purge - 删除记忆

从记忆图中删除信息。

**参数**:
- `criteria`: 删除条件 (subject, target, relation, sessionId)
- `mode`: 删除模式 (soft/hard/supersede)
- `newRelation`: 可选的替代关系

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

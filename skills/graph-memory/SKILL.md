---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆，管理人设和任务。使用 recall 检索、commit 写入、purge 删除"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory 图记忆系统

让 AI 拥有真正的长期记忆能力。

## 核心概念

### 实体 (Entity)
现实世界中的对象，如"用户"、"Python"、"WaterFlow"。

### 关系 (Relation)
连接两个实体的关系，格式为三元组：主体 - 关系 - 客体。

## 可用命令

### 1. commit - 写入记忆

将信息写入记忆图。

**参数：**
- `triplets`: 三元组数组 `[{subject, relation, object}, ...]`
- `sessionId`: 会话 ID（可选）
- `turnId`: 轮次 ID（可选）

**示例：**
```
请记住：我喜欢编程，正在学习 TypeScript
```

AI 会执行：
```json
{
  "action": "commit",
  "params": {
    "triplets": [
      {"subject": "我", "relation": "喜欢", "object": "编程"},
      {"subject": "我", "relation": "正在学习", "object": "TypeScript"}
    ]
  }
}
```

### 2. recall - 检索记忆

从记忆图中检索相关信息。

**参数：**
- `queryIntent`: 搜索关键词
- `seedEntities`: 种子实体（可选）
- `depth`: 检索深度（默认 2）
- `sessionFilter`: 会话过滤（可选）

### 3. purge - 删除记忆

删除记忆图中的一些信息。

**参数：**
- `criteria`: 删除条件 `{subject, target, relation, sessionId}`
- `mode`: 删除模式 `soft`（标记删除）、`hard`（彻底删除）或 `supersede`（纠错替代）
- `newRelation`: 替代关系（supersede 模式）

### 4. introspect - 查看状态

查看当前记忆状态统计。

### 5. archive - 归档旧记忆

将 N 天前的非活跃关系标记为归档。

**参数：**
- `days`: 归档天数（默认 30）

### 6. cleanup - 清理无效数据

物理删除已删除超过 90 天的关系和孤立节点。

**参数：**
- `dry_run`: 仅预览不删除（默认 true）

### 7. persona_update - 更新人设

更新 AI 的角色/性格特征。

**参数：**
- `attributes`: 属性数组 `[{attribute, value}, ...]`
- `mode`: `merge`（合并）或 `replace`（替换）

### 8. persona_clear - 清除人设

清除 AI 的所有角色设定。

**参数：**
- `confirm`: 必须为 `true` 才能执行

### 9. task_create - 创建任务

创建长期任务节点。

**参数：**
- `task_id`: 唯一任务 ID
- `description`: 任务描述
- `info_nodes`: 相关信息节点（可选）

### 10. task_set_state - 设置任务状态

更新任务状态。

**参数：**
- `task_id`: 任务 ID
- `state`: 新状态（进行中/已完成/已暂停/已取消）

### 11. task_delete - 删除任务

删除任务。

**参数：**
- `task_id`: 任务 ID

### 12. task_link_info - 关联信息

将信息节点关联到任务。

**参数：**
- `task_id`: 任务 ID
- `info_node`: 信息节点

## 使用原则

1. **选择性记忆**：只记住重要和持久的信息
2. **结构化**：使用三元组格式存储关系
3. **定期清理**：删除过时或错误的信息
4. **关联思考**：利用关系进行联想记忆

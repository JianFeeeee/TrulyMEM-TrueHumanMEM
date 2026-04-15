---
name: graph_memory
description: 让 AI 拥有真正的长期记忆能力 - 检索、写入、删除记忆，管理人设和任务
when_to_use: 当需要 AI 记住持久信息、回忆过去交互、或管理长期任务时
version: 1.0.0
---

# GraphMemory 图记忆系统

让 AI 拥有真正的长期记忆能力。

## 这个技能做什么

这个技能教会 AI 如何使用图结构存储和检索记忆。AI 可以：
- 记住重要的信息（实体）
- 理解信息之间的关系（关系/三元组）
- 回忆相关的记忆
- 管理 AI 的人设（角色性格）
- 追踪长期任务

## 核心概念

### 实体 (Entity)
现实世界中的对象，如"用户"、"Python"、"WaterFlow"。每个实体有：
- 名称 (name)
- 类型 (type)
- 提及次数 (mentionCount)

### 关系 (Relation)
连接两个实体的关系，格式为三元组：
- 主体 (subject) - 关系 - 客体 (object)
- 例如："用户" 喜欢 "编程"

## 可用命令

### 1. commit - 写入记忆

将信息写入记忆图。

**参数：**
- `triplets`: 三元组数组，格式为 `[{subject, relation, object}, ...]`
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
- `sessionFilter`: 会话过滤（可选）

**示例：**
```
我之前说过我喜欢什么？
```

### 3. purge - 删除记忆

删除记忆图中的一些信息。

**参数：**
- `criteria`: 删除条件 `{subject, target, relation, sessionId}`
- `mode`: 删除模式 `soft`（标记删除）或 `hard`（彻底删除）

### 4. introspect - 查看状态

查看当前记忆状态统计。

**返回：**
- entityCount: 实体数量
- relationCount: 关系数量

### 5. persona_update - 更新人设

更新 AI 的角色/性格特征。

**参数：**
- `attributes`: 属性数组 `[{attribute, value}, ...]`
- `mode`: `merge`（合并）或 `replace`（替换）

**示例：**
```
我的角色是猫娘，性格活泼
```

### 6. persona_clear - 清除人设

清除 AI 的所有角色设定。

**参数：**
- `confirm`: 必须为 `true` 才能执行

### 7. task_create - 创建任务

创建长期任务节点。

**参数：**
- `task_id`: 唯一任务 ID
- `description`: 任务描述
- `info_nodes`: 相关信息节点（可选）

### 8. task_set_state - 设置任务状态

更新任务状态。

**参数：**
- `task_id`: 任务 ID
- `state`: 新状态 (`进行中`/`已完成`/`已暂停`/`已取消`)

### 9. task_delete - 删除任务

删除任务。

**参数：**
- `task_id`: 任务 ID

## 使用原则

1. **选择性记忆**：只记住重要和持久的信息
2. **结构化**：使用三元组格式存储关系
3. **定期清理**：删除过时或错误的信息
4. **关联思考**：利用关系进行联想记忆

## 关系类型参考

| 关系 | 含义 |
|------|------|
| 喜欢 | 偏好关系 |
| 是 | 类型关系 |
| 正在学习 | 进程关系 |
| 属于 | 归属关系 |
| 包含 | 组成关系 |
| has_description | 描述关系 |
| HAS_STATE | 状态关系 |

## 注意事项

- 每次交互后，AI 应该决定是否需要 commit 重要信息
- 使用 recall 来获取相关上下文，而不只是依赖当前对话
- persona 信息应该谨慎修改
- 任务可以跨会话追踪

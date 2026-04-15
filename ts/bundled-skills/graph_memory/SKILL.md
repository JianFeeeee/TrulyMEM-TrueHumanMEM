---
name: graph_memory
description: 图记忆工具 - 让 AI 拥有真正的长期记忆能力
when_to_use: 需要 AI 记住或回忆信息时
context: inline
allowed_tools:
  - builtin:graph_memory
arguments:
  - name: action
    type: string
    required: true
    enum: [recall, commit, purge, introspect]
    description: 记忆操作类型
  - name: params
    type: object
    required: true
    description: 操作参数
user_invocable: true
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

**示例**:
```
action: recall
params:
  queryIntent: "用户 喜欢 编程"
  seedEntities: ["用户"]
```

### 2. commit - 写入记忆

将信息写入记忆图。

**参数**:
- `triplets`: 三元组数组，每个包含 subject, relation, object
- `sessionId`: 会话ID
- `turnId`: 轮次ID

**示例**:
```
action: commit
params:
  triplets:
    - subject: "用户"
      relation: "喜欢"
      object: "Python"
    - subject: "用户"
      relation: "正在学习"
      object: "TypeScript"
```

### 3. purge - 删除记忆

从记忆图中删除信息。

**参数**:
- `criteria`: 删除条件 (subject, target, relation, sessionId)
- `mode`: 删除模式 (soft/hard/supersede)
- `newRelation`: 可选的替代关系

**示例**:
```
action: purge
params:
  criteria:
    subject: "旧信息"
  mode: "soft"
```

### 4. introspect - 查看状态

查看当前记忆状态统计。

**参数**: 无

**示例**:
```
action: introspect
params: {}
```

## 使用原则

1. **选择性记忆**: 只记住重要和持久的信息
2. **结构化**: 使用三元组 (主体-关系-客体) 格式
3. **关联**: 通过关系连接相关实体
4. **定期清理**: 删除过时或错误的信息

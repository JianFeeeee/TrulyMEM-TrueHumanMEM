---
context: inline
allowed-tools:
  - builtin:graph_memory
arguments:
  - name: action
    type: string
    required: true
    enum: [recall, commit, purge, introspect, persona_update, persona_clear, task_create, task_set_state, task_delete, task_link_info]
    description: 记忆操作类型
  - name: params
    type: object
    required: true
    description: 操作参数
user-invocable: true
---

# 图记忆工具 - 让 AI 拥有真正的长期记忆能力

**何时使用**: 需要 AI 记住、回忆、管理信息或任务时调用此技能。

你可以通过以下操作与图记忆系统交互。

## 核心操作

### 1. recall - 检索记忆

从记忆图中检索相关信息。支持广度优先搜索（BFS），自动扩展关联实体。

**参数**:
- `queryIntent`: 搜索意图/关键词
- `seedEntities`: 可选的种子实体名
- `depth`: 检索深度（默认 2，BFS 层数）
- `sessionFilter`: 可选的会话ID过滤

**示例**:
```
action: recall
params:
  queryIntent: "用户 喜欢 编程"
  seedEntities: ["用户"]
  depth: 2
```

### 2. commit - 写入记忆

将信息写入记忆图。使用三元组（主体-关系-客体）格式。

**参数**:
- `triplets`: 三元组数组，每个包含 subject, relation, object, confidence(可选)
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
- `mode`: 删除模式 (soft=标记删除/hard=物理删除/supersede=替代)

**示例**:
```
action: purge
params:
  criteria:
    subject: "旧信息"
  mode: "soft"
```

### 4. introspect - 查看状态

查看当前记忆状态统计（实体数、关系数）。

**参数**: 无

**示例**:
```
action: introspect
params: {}
```

## 人设管理

### 5. persona_update - 更新人设

更新 AI 的人设属性（性格、语气、角色等）。

**参数**:
- `attributes`: 属性数组，每个包含 attribute 和 value
- `mode`: merge(合并) 或 replace(替换)

**示例**:
```
action: persona_update
params:
  attributes:
    - attribute: "性格"
      value: "活泼可爱"
    - attribute: "语气词"
      value: "喵"
  mode: "replace"
```

### 6. persona_clear - 清除人设

清除所有人设，恢复默认身份。

**参数**:
- `confirm`: 必须为 true 才执行

**示例**:
```
action: persona_clear
params:
  confirm: true
```

## 任务管理

### 7. task_create - 创建任务

创建连续性任务节点，维持对话连贯性。

**参数**:
- `task_id`: 任务唯一ID
- `description`: 任务描述
- `info_nodes`: 可选的关联信息节点列表

**示例**:
```
action: task_create
params:
  task_id: "Task_成语接龙"
  description: "成语接龙游戏，当前成语：为所欲为"
  info_nodes: ["成语接龙_当前成语"]
```

### 8. task_set_state - 设置任务状态

更新任务状态（进行中/已完成/已暂停/已取消）。

**参数**:
- `task_id`: 任务ID
- `state`: 新状态

**示例**:
```
action: task_set_state
params:
  task_id: "Task_成语接龙"
  state: "已暂停"
```

### 9. task_delete - 删除任务

删除任务节点。

**参数**:
- `task_id`: 任务ID

**示例**:
```
action: task_delete
params:
  task_id: "Task_成语接龙"
```

### 10. task_link_info - 关联信息到任务

将记忆节点关联到任务节点，实现"由一件事回忆起相关事情"。

**参数**:
- `task_id`: 任务ID
- `info_node`: 信息节点名

**示例**:
```
action: task_link_info
params:
  task_id: "Task_成语接龙"
  info_node: "用户喜欢罗辑"
```

## 使用原则

1. **选择性记忆**: 只记住重要和持久的信息
2. **结构化**: 使用三元组 (主体-关系-客体) 格式
3. **关联**: 通过关系连接相关实体
4. **定期清理**: 删除过时或错误的信息
5. **BFS 搜索**: recall 支持广度优先搜索，depth 参数控制扩展层数
6. **工作记忆链**: 每轮对话必须查询和更新工作记忆链（TaskNode），这是维持对话连贯性的唯一机制
7. **人设优先**: 每轮对话必须先查询人设图，确保角色一致性

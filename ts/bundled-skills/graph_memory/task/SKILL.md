---
name: graph_memory_task
description: 管理连续性任务 - 创建、更新、删除任务节点
when_to_use: 需要创建或管理长期任务时
context: inline
allowed_tools:
  - builtin:graph_memory
arguments:
  - name: action
    type: string
    required: true
    enum: [task_create, task_set_state, task_delete, task_link_info]
    description: 操作类型
  - name: task_id
    type: string
    required: true
    description: 任务ID
  - name: description
    type: string
    description: 任务描述 (用于 create)
  - name: state
    type: string
    enum: [进行中, 已完成, 已暂停, 已取消]
    description: 任务状态 (用于 set_state)
  - name: info_nodes
    type: array
    description: 信息节点数组 (用于 create)
  - name: info_node
    type: string
    description: 信息节点 (用于 link_info)
user_invocable: true
---

# GraphMemory Task 任务管理

管理长期/连续性任务。

## 操作

### 1. task_create - 创建任务

创建新的任务节点。

**参数**:
- `task_id`: 唯一任务标识
- `description`: 任务描述
- `info_nodes`: 可选的相关信息节点

**示例**:
```
action: task_create
task_id: "Task_学习TypeScript"
description: "学习 TypeScript 并完成项目"
info_nodes: ["TypeScript文档", "教程链接"]
```

### 2. task_set_state - 设置状态

更新任务状态。

**参数**:
- `task_id`: 任务ID
- `state`: 新状态 (进行中/已完成/已暂停/已取消)

**示例**:
```
action: task_set_state
task_id: "Task_学习TypeScript"
state: "已完成"
```

### 3. task_delete - 删除任务

删除任务节点。

**参数**:
- `task_id`: 任务ID

**示例**:
```
action: task_delete
task_id: "Task_学习TypeScript"
```

### 4. task_link_info - 关联信息

将信息节点关联到任务。

**参数**:
- `task_id`: 任务ID
- `info_node`: 信息节点

**示例**:
```
action: task_link_info
task_id: "Task_学习TypeScript"
info_node: "新教程链接"
```

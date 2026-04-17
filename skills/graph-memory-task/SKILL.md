---
name: graph-memory-task
description: "管理连续性任务 - 创建、更新、删除任务节点。使用 task_create 创建、task_set_state 更新状态"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Task 任务管理

管理长期/连续性任务。

## 操作

### 1. task_create - 创建任务

创建新的任务节点。

**参数:**
- `task_id`: 唯一任务标识
- `description`: 任务描述
- `info_nodes`: 可选的相关信息节点

**示例:**
```
action: task_create
task_id: "Task_学习TypeScript"
description: "学习 TypeScript 并完成项目"
info_nodes: ["TypeScript文档", "教程链接"]
```

### 2. task_set_state - 设置状态

更新任务状态。

**参数:**
- `task_id`: 任务ID
- `state`: 新状态 (进行中/已完成/已暂停/已取消)

### 3. task_delete - 删除任务

删除任务节点。

**参数:**
- `task_id`: 任务ID

### 4. task_link_info - 关联信息

将信息节点关联到任务。

**参数:**
- `task_id`: 任务ID
- `info_node`: 信息节点

---
name: graph-memory-task
description: "管理连续性任务 - 创建、更新、删除任务节点。作为增强工具，通过 graph_memory 的 task_* 操作实现"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Task 任务管理

管理长期/连续性任务。

> **定位声明**：本 skill 通过 `graph_memory` 工具的 `task_create`/`task_set_state`/`task_delete`/`task_link_info` 操作实现。是 **OpenClaw 的增强功能**，提供任务追踪能力，不替代任何核心机制。

## 与主系统的关系

- **不强制**：不会每轮自动查询任务状态，由 LLM 根据用户请求决定
- **可选调用**：当用户提到"帮我记住这个任务"、"完成这个任务"等场景时触发
- **数据存储**：任务数据以三元组形式存储在图数据库中（subject=task_id）

## 操作

### 1. task_create - 创建任务

创建新的任务节点。

**参数:**
- `task_id`: 唯一任务标识（必需）
- `description`: 任务描述（必需）
- `info_nodes`: 可选的相关信息节点数组

**示例:**
```yaml
action: task_create
params:
  task_id: "Task_学习TypeScript"
  description: "学习 TypeScript 并完成项目"
  info_nodes: ["TypeScript文档", "教程链接"]
```

### 2. task_set_state - 设置状态

更新任务状态。

**参数:**
- `task_id`: 任务ID（必需）
- `state`: 新状态，`进行中`/`已完成`/`已暂停`/`已取消`（必需）

**示例:**
```yaml
action: task_set_state
params:
  task_id: "Task_学习TypeScript"
  state: "已完成"
```

### 3. task_delete - 删除任务

删除任务节点。

**参数:**
- `task_id`: 任务ID（必需）

### 4. task_link_info - 关联信息

将信息节点关联到任务。

**参数:**
- `task_id`: 任务ID（必需）
- `info_node`: 信息节点名称（必需）

## 使用建议

1. 任务ID应具有描述性（如 `Task_学习TypeScript`）
2. 任务描述应清晰说明目标和上下文
3. 定期使用 `recall` 查询任务状态，了解进行中的任务
4. 与 memory-core 配合：任务列表由 GraphMemory 管理，具体执行细节由对话上下文管理

---
name: graph-memory-task
description: "管理连续性任务 - AI 应主动追踪和维护任务状态，将任务信息作为长期记忆存储在图数据库中"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Task 任务管理

管理长期/连续性任务。

> **定位声明**：任务是 AI 长期记忆的一部分，存储在图数据库中。AI **应主动追踪**任务状态，在适当时候提醒用户或更新进度。

## 核心原则

**AI 必须在以下场景主动查询任务**：
1. 对话开始时（检索进行中的任务）
2. 用户询问进度或状态时
3. 用户提到"继续之前的..."、"那个任务怎么样了"等
4. 做计划或安排时（了解现有任务负荷）

**AI 必须在以下场景创建/更新任务**：
1. 用户明确创建任务（"帮我记住要做..."）
2. 用户完成或取消任务
3. 用户更新任务信息或进度
4. AI 自己承诺要完成某事（应创建任务跟踪）

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

## 任务查询模板

每次对话开始时，AI 应执行：
```yaml
action: recall
params:
  queryIntent: "任务 进行中 待办"
  seedEntities: ["Task"]
  depth: 2
```

## 使用建议

1. **主动追踪**：不要等用户问才查任务，主动在对话开始时检索进行中的任务
2. **及时更新**：任务状态变化时立即更新，避免信息过时
3. **ID规范**：任务ID应具有描述性（如 `Task_学习TypeScript`）
4. **定期提醒**：对于长期任务，在对话中适时提醒用户进度或截止日期
5. **关联信息**：将相关资源、链接、笔记关联到任务，形成完整上下文

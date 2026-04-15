---
name: graph_memory_task
description: 管理连续性任务 - 创建、更新、删除任务节点
when_to_use: 当需要创建或管理长期/跨会话任务时
version: 1.0.0
---

# GraphMemory Task 任务管理

管理长期/连续性任务。

## 这个技能做什么

这个技能让 AI 能够：
- 创建新任务
- 追踪任务进度
- 更新任务状态
- 关联任务相关信息
- 删除任务

## 可用命令

### 1. task_create - 创建任务

**参数：**
- `task_id`: 唯一任务标识
- `description`: 任务描述
- `info_nodes`: 相关信息节点（可选）

**示例：**
```
帮我创建一个任务：学习 TypeScript
```
会执行：
```json
{
  "action": "task_create",
  "params": {
    "task_id": "task_学习TypeScript",
    "description": "学习 TypeScript",
    "info_nodes": ["TypeScript文档", "教程链接"]
  }
}
```

### 2. task_set_state - 设置状态

**参数：**
- `task_id`: 任务 ID
- `state`: 新状态

**可用状态：**
- `进行中`: 任务正在处理
- `已完成`: 任务已完成
- `已暂停`: 任务暂停
- `已取消`: 任务取消

**示例：**
```
TypeScript 学习任务完成了
```
会执行：
```json
{
  "action": "task_set_state",
  "params": {
    "task_id": "task_学习TypeScript",
    "state": "已完成"
  }
}
```

### 3. task_delete - 删除任务

**参数：**
- `task_id`: 任务 ID

**示例：**
```
删除那个 TypeScript 任务
```
会执行：
```json
{
  "action": "task_delete",
  "params": {
    "task_id": "task_学习TypeScript"
  }
}
```

### 4. task_link_info - 关联信息

**参数：**
- `task_id`: 任务 ID
- `info_node`: 信息节点

**示例：**
```
给任务添加一个新资源
```
会执行：
```json
{
  "action": "task_link_info",
  "params": {
    "task_id": "task_学习TypeScript",
    "info_node": "新发现的教程"
  }
}
```

## 使用场景

- 跨会话追踪任务进度
- 记录任务相关信息
- 管理复杂工作流
- 任务状态持久化
- 长期项目追踪

## 任务状态流转

```
创建 (进行中) → 进行中 → 已完成
                      ↘ 已暂停
                      ↘ 已取消
```

## 最佳实践

1. **具体描述**：任务描述要清晰具体
2. **关联信息**：为任务添加相关资料链接
3. **及时更新**：状态改变时立即更新
4. **清理完成**：已完成的任务及时删除或归档

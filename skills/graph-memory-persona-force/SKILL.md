---
name: graph-memory-persona-force
description: "AI 人设强制查询最佳实践 - 指导 AI 在特定场景下主动查询人设图"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: false
---

# Graph Memory Persona Force - 人设强制查询 Skill

本 Skill 不是修改 OpenClaw 核心，而是作为**最佳实践指导**，帮助 AI 在合适的时机主动查询用户的长期记忆（人设图）。

## 何时查询人设？

当对话中出现以下信号时，AI **应当主动调用 graph_memory recall** 查询用户相关记忆：

### 1. 个人偏好信号
- "我喜欢..." / "我不喜欢..."
- "我更倾向于..." / "我讨厌..."
- "我习惯..." / "我总是..."
- **行动**：recall 查询 "偏好" 相关记忆

### 2. 重要决策信号
- "我决定..." / "我选了..."
- "我打算..." / "我准备..."
- "我确定用..." / "我最终选择..."
- **行动**：recall 查询 "决策" 相关记忆，commit 记录新决策

### 3. 目标/计划信号
- "我的目标是..." / "我想实现..."
- "我计划..." / "我希望..."
- **行动**：recall 查询 "目标" 相关记忆

### 4. 问题/困难信号
- "我遇到一个问题..." / "我不确定..."
- "我尝试了...但失败了" / "有什么建议..."
- **行动**：recall 查询历史 "解决方案"，看是否有类似经历

### 5. 情绪/状态信号
- "我最近..." / "我感觉..."
- "我很忙..." / "我没时间..."
- **行动**：recall 查询 "状态" 或 "情绪" 相关记忆

## 查询策略

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "用户偏好 决策",
    "seedEntities": ["用户", "我"],
    "depth": 2
  }
}
```

### 渐进式查询

1. **先查人设核心** (subject="AI" 或 "用户")
2. **再查相关实体** (seedEntities 包含关键词)
3. **最后查上下文** (working_memory_chain)

## 记录时机

当用户明确表达新的偏好、决策或目标时，**立即 commit**：

```json
{
  "action": "commit",
  "params": {
    "triplets": [
      {"subject": "用户", "relation": "偏好", "object": "Python"},
      {"subject": "用户", "relation": "决策", "object": "选择React作为前端框架"}
    ]
  }
}
```

## 示例对话

**用户**：我最近在学习 TypeScript，因为之前用 JavaScript 遇到太多类型问题了。

**AI 思考**：
1. 用户提到 "学习 TypeScript" → 可能是新偏好/目标
2. 用户提到 "之前用 JavaScript 遇到类型问题" → 历史决策原因
3. **行动**：recall 查询用户技术偏好

```json
{
  "action": "recall",
  "params": {
    "queryIntent": "技术偏好 JavaScript TypeScript",
    "seedEntities": ["用户", "JavaScript", "TypeScript"],
    "depth": 2
  }
}
```

## 与 graph-memory Skill 的关系

- `graph-memory`：提供工具能力（recall/commit/purge 等）
- `graph-memory-persona-force`：指导何时使用、如何使用（最佳实践）

两者配合使用，实现真正智能的长期记忆系统。

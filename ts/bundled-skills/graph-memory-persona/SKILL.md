---
name: graph-memory-persona
description: "管理 AI 人设 - 更新或清除 AI 角色特征。作为增强工具，通过 graph_memory 的 persona_update/clear 操作实现"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Persona 人设管理

管理 AI 的人设/角色特征。

> **定位声明**：本 skill 通过 `graph_memory` 工具的 `persona_update`/`persona_clear` 操作实现。是 **OpenClaw 的增强功能**，不替代任何核心机制。LLM 可自主选择是否查询/更新人设。

## 与主系统的关系

- **不强制**：不会每轮自动查询人设，由 LLM 根据上下文决定
- **可选调用**：当用户提到"记住我是..."、"你的角色是..."等场景时触发
- **数据存储**：人设数据以三元组形式存储在图数据库中（subject=AI）

## 操作

### 1. persona_update - 更新人设

更新 AI 的角色特征。

**参数:**
- `attributes`: 属性数组，每个包含 `attribute`（属性名）和 `value`（属性值）
- `mode`: 更新模式，`merge`（合并，默认）或 `replace`（替换）

**示例:**
```yaml
action: persona_update
params:
  attributes:
    - attribute: "角色"
      value: "猫娘"
    - attribute: "性格"
      value: "活泼"
  mode: "merge"
```

### 2. persona_clear - 清除人设

清除 AI 的所有角色特征。

**参数:**
- `confirm`: 必须为 `true` 才能执行清除（安全措施）

**示例:**
```yaml
action: persona_clear
params:
  confirm: true
```

## 使用建议

1. 人设信息应简洁、持久（如"用户喜欢Python"、"我是技术助手"）
2. 避免存储临时性、易变的信息到人设图
3. 与 memory-core 配合：人设由 GraphMemory 管理，对话风格由系统提示管理

---
name: persona
description: 管理 AI 人设 - 更新或清除 AI 角色特征
when_to_use: 需要修改 AI 的角色设定或清除人设时
context: inline
allowed-tools:
  - builtin:graph_memory
arguments:
  - name: action
    type: string
    required: true
    enum: [persona_update, persona_clear]
    description: 操作类型
  - name: attributes
    type: array
    description: 属性数组 (用于 update)
  - name: mode
    type: string
    enum: [merge, replace]
    default: merge
    description: 更新模式
  - name: confirm
    type: boolean
    description: 确认清除 (用于 clear)
user-invocable: true
---

# GraphMemory Persona 人设管理

管理 AI 的人设/角色特征。

## 操作

### 1. persona_update - 更新人设

更新 AI 的角色特征。

**参数**:
- `attributes`: 属性数组，每个包含 attribute 和 value
- `mode`: 更新模式
  - `merge`: 合并到现有属性
  - `replace`: 替换所有现有属性

**示例**:
```
action: persona_update
attributes:
  - attribute: "角色"
    value: "猫娘"
  - attribute: "性格"
    value: "活泼"
mode: "merge"
```

### 2. persona_clear - 清除人设

清除 AI 的所有角色特征。

**参数**:
- `confirm`: 确认为 true 才能执行清除

**示例**:
```
action: persona_clear
confirm: true
```

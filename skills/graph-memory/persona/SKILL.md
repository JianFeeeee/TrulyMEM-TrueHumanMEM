---
name: graph-memory-persona
description: "管理 AI 人设 - 更新或清除 AI 角色特征。使用 persona_update 更新、persona_clear 清除"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Persona 人设管理

管理 AI 的人设/角色特征。

## 操作

### 1. persona_update - 更新人设

更新 AI 的角色特征。

**参数:**
- `attributes`: 属性数组，每个包含 attribute 和 value
- `mode`: 更新模式（merge 合并或 replace 替换）

**示例:**
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

**参数:**
- `confirm`: 确认为 true 才能执行清除

**示例:**
```
action: persona_clear
confirm: true
```

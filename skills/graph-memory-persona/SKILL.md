---
name: graph-memory-persona
description: "管理 AI 人设 - AI 应主动查询和维护角色特征，将人设信息作为长期记忆存储在图数据库中"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory Persona 人设管理

管理 AI 的人设/角色特征。

> **定位声明**：人设是 AI 长期记忆的一部分，存储在图数据库中。AI **应主动查询**人设信息来指导自己的行为和回应风格。

## 核心原则

**AI 必须在以下场景主动查询人设**：
1. 对话开始时（检索用户偏好和 AI 角色设定）
2. 用户要求改变行为或风格时
3. 不确定如何回应时（查询是否有相关人设指导）
4. 用户提到"你之前说..."、"我告诉过你..."等暗示历史记忆的语句

**AI 必须在以下场景更新人设**：
1. 用户明确设定 AI 角色（"你是猫娘"、"你是技术专家"）
2. 用户描述自己的偏好（"我喜欢简洁的回答"）
3. 用户定义交互规则（"用中文回复我"、"不要道歉"）
4. 用户纠正 AI 的行为（"你太正式了，放松点"）

## 操作

### 1. persona_update - 更新人设

更新 AI 的角色特征或用户偏好。

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
    - attribute: "用户偏好_回复语言"
      value: "中文"
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

## 人设查询模板

每次对话开始时，AI 应执行：
```yaml
action: recall
params:
  queryIntent: "AI人设 用户偏好 角色设定"
  seedEntities: ["AI"]
  depth: 2
```

## 使用建议

1. **主动查询**：不要等用户提醒才查人设，主动在对话开始时检索
2. **及时更新**：用户一旦表达偏好或设定角色，立即写入
3. **分类存储**：使用前缀区分人设类型，如 `角色_`、`用户偏好_`、`行为规则_`
4. **持久化**：人设信息应简洁、持久，写入图数据库长期保存

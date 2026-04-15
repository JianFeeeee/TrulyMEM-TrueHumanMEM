---
name: graph_memory_persona
description: 管理 AI 人设 - 更新或清除 AI 角色特征
when_to_use: 当需要设置或修改 AI 的角色性格时
version: 1.0.0
---

# GraphMemory Persona 人设管理

管理 AI 的人设/角色特征。

## 这个技能做什么

这个技能让 AI 能够：
- 设置自己的角色/性格
- 更新人设信息
- 清除人设

## 可用命令

### 1. persona_update - 更新人设

**参数：**
- `attributes`: 属性数组 `[{attribute, value}, ...]`
- `mode`: 
  - `merge`: 合并到现有属性（默认）
  - `replace`: 替换所有现有属性

**示例：**
```
# 方式一：合并更新
记住我的角色是猫娘
```
会执行：
```json
{
  "action": "persona_update",
  "params": {
    "attributes": [
      {"attribute": "角色", "value": "猫娘"}
    ],
    "mode": "merge"
  }
}
```

```
# 方式二：完全替换
我是一个专业的技术作家
```
会执行：
```json
{
  "action": "persona_update",
  "params": {
    "attributes": [
      {"attribute": "职业", "value": "技术作家"}
    ],
    "mode": "replace"
  }
}
```

### 2. persona_clear - 清除人设

**参数：**
- `confirm`: 必须为 `true` 才能执行

**示例：**
```
清除我的人设
```
会执行：
```json
{
  "action": "persona_clear",
  "params": {
    "confirm": true
  }
}
```

## 使用场景

- 初始化 AI 角色
- 调整 AI 性格
- 清除错误的人设
- 角色切换
- 设置专业领域

## 常见人设属性

| 属性 | 说明 | 示例值 |
|------|------|--------|
| 角色 | AI 的角色 | "猫娘"、"助手"、"专家" |
| 性格 | 性格特征 | "活泼"、"严肃"、"幽默" |
| 职业 | 专业领域 | "技术作家"、"程序员" |
| 语言风格 | 说话方式 | "简洁"、"详细" |

# 提示词管理文档

本文档描述提示词管理模块。

## 概述

提示词管理模块（`core/prompts/`）负责加载和管理告诉 AI 如何使用记忆工具的系统提示词。

## 核心组件

| 组件 | 说明 |
|------|------|
| `PromptManager` | 提示词管理器，单例模式 |
| `system_prompt.md` | 主要系统提示词模板 |

## 使用方法

```python
from core.prompts import PromptManager

# 获取单例实例
prompt_manager = PromptManager()

# 获取系统提示词
system_prompt = prompt_manager.get_system_prompt()
```

## 系统提示词内容

系统提示词包含：

### 1. 核心身份

- **名称**: TrulyMEM (TrueHumanMEM)
- **能力**: 基于图数据库的长期记忆
- **理念**: 让 AI 的记忆方式更像人类

### 2. 核心能力

1. **长期记忆** - 图数据库存储实体关系
2. **人设管理** - 角色扮演和性格设定
3. **任务跟踪** - 工作记忆链

### 3. 记忆原则

- **必须写入**: 用户明确表达的偏好、分享的信息、计划
- **禁止写入**: AI 推断的内容（除非标注[推测]）
- **标注**: 推断内容必须标注 **[推测]**

### 4. 强制执行流程（每轮）

```
步骤 1: 查询人设图（最高优先级）
步骤 2: 查询工作记忆链
步骤 3: 处理对话
步骤 4: 更新工作记忆链
```

### 5. 工具系统

#### 记忆工具

| 工具 | 功能 |
|------|------|
| `memory_recall` | 检索记忆 |
| `memory_commit` | 写入记忆 |
| `memory_purge` | 删除记忆 |
| `memory_introspect` | 查看状态 |

#### 人设工具

| 工具 | 功能 |
|------|------|
| `persona_update` | 更新人设 |
| `persona_clear` | 清除人设 |

#### 任务工具

| 工具 | 功能 |
|------|------|
| `task_create` | 创建任务 |
| `task_set_state` | 设置状态 |
| `task_delete` | 删除任务 |
| `task_link_info` | 关联信息 |

### 6. 自主性原则

AI 可自主决定：
- 是否查询其他记忆
- 是否写入其他记忆
- 如何使用工具（强制要求外）

### 7. 对话风格

- 自然流畅
- 避免机械式工具调用
- 优先理解用户意图
- 适时使用记忆增强体验

## 文件结构

```
core/prompts/
├── __init__.py           # 导出 PromptManager
├── prompt_manager.py     # PromptManager 类
└── templates/
    └── system_prompt.md # 主要系统提示词
```

## 自定义

### 自定义系统提示词

修改 `core/prompts/templates/system_prompt.md` 自定义 AI 行为。

### 添加自定义提示词

1. 在 `core/prompts/templates/` 添加提示词模板文件
2. 修改 `PromptManager` 支持多个提示词
3. 使用 `set_prompt()` 切换提示词

## 缓存

- 系统提示词首次加载后缓存在内存中
- `get_system_prompt()` 返回缓存内容
- 缓存按进程，不持久化
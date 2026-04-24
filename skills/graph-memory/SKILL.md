---
name: graph-memory
description: "图记忆工具 - 检索、写入、删除记忆。AI 应优先使用图数据库管理长期记忆，将重要事实结构化存储"
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
user-invocable: true
---

# GraphMemory 图记忆系统

让 AI 拥有真正的长期记忆能力。

> **定位声明**：本工具是 AI 的**主要长期记忆系统**。memory-core 管理 session transcripts，GraphMemory 负责结构化长期记忆。AI 在对话中应优先将重要信息写入图数据库，而非依赖 message 历史。

## 与 memory-core 的关系

| 功能 | memory-core | GraphMemory (本工具) |
|------|-------------|---------------------|
| 对话历史 | ✅ 自动保存 messages | ❌ 不管理对话历史 |
| 结构化记忆 | ❌ 无 | ✅ **主要存储** |
| 人设管理 | ❌ 无 | ✅ **主要存储** |
| 任务追踪 | ❌ 无 | ✅ **主要存储** |
| 上下文压缩 | ❌ 无 | ✅ context_rewrite |
| 工作记忆链 | ❌ 无 | ✅ working_memory_chain |
| **语义搜索** | **❌ 无** | **✅ memory_search** |
| **记忆文件读取** | **❌ 无** | **✅ memory_get** |
| 自动触发 | ✅ 自动索引检索 | ❌ LLM 主动调用 |

## 核心概念

### 实体 (Entity)
现实世界中的对象，如"用户"、"Python"、"WaterFlow"。

### 关系 (Relation)
连接两个实体的关系，格式为三元组：主体 - 关系 - 客体。

## 可用命令

### 1. commit - 写入记忆

将信息写入记忆图。

**参数：**
- `triplets`: 三元组数组 `[{subject, relation, object}, ...]` （必需）
- `sessionId`: 会话 ID（可选）
- `turnId`: 轮次 ID（可选）

**示例：**
```
请记住：我喜欢编程，正在学习 TypeScript
```

AI 会执行：
```json
{
  "action": "commit",
  "params": {
    "triplets": [
      {"subject": "我", "relation": "喜欢", "object": "编程"},
      {"subject": "我", "relation": "正在学习", "object": "TypeScript"}
    ]
  }
}
```

### 2. recall - 检索记忆

从记忆图中检索相关信息。

**参数：**
- `queryIntent`: 搜索关键词（必需，若无则需提供 seedEntities）
- `seedEntities`: 种子实体数组（可选）
- `depth`: 检索深度 1-5（默认 2）
- `sessionFilter`: 会话过滤（可选）

### 3. purge - 删除记忆

删除记忆图中的一些信息。

**参数：**
- `criteria`: 删除条件 `{subject, target, relation, sessionId}`
- `mode`: 删除模式 `soft`（标记删除）、`hard`（彻底删除）或 `supersede`（纠错替代）
- `newRelation`: 替代关系（supersede 模式必需）

### 4. introspect - 查看状态

查看当前记忆状态统计（实体数、关系数）。

### 5. archive - 归档旧记忆

将 N 天前的非活跃关系标记为归档。

**参数：**
- `days`: 归档天数（默认 30）

### 6. cleanup - 清理无效数据

物理删除已删除超过 90 天的关系和孤立节点。

**参数：**
- `dry_run`: 仅预览不删除（默认 true，建议先预览再执行）

### 7. context_rewrite - 压缩上下文

当对话历史过长时，将历史对话压缩为关键记忆节点存入图数据库。

**参数：**
- `context`: 要压缩的长文本（必需）
- `maxEntities`: 最大提取实体数（默认 20）
- `summary`: 自定义摘要（可选）

**返回：**
- `extractedEntities`: 提取的实体数
- `extractedRelations`: 提取的关系数
- `summary`: 生成的摘要
- `compressed`: 是否成功压缩

### 8. working_memory_chain - 工作记忆链

检索当前会话的近期活跃关系和任务节点，形成工作记忆链。

**参数：**
- `maxDepth`: 检索深度 1-5（默认 3）
- `recentOnly`: 仅最近（默认 true）

### 9. task_node_create - 创建任务节点

创建一个新的 TaskNode 并自动链接到工作记忆链。

**参数：**
- `session_id`: 会话 ID（必需）
- `turn_id`: 轮次 ID（必需）
- `summary`: 摘要（必需）
- `key_facts`: 关键事实数组（必需）
- `raw_context`: 原始上下文（可选，会自动存档到文本文件）

### 10. task_node_get_recent - 获取最近节点

获取最近 N 个任务节点（按时间倒序）。

**参数：**
- `session_id`: 会话 ID（必需）
- `limit`: 限制数量（默认 5）

### 11. task_node_get_chain - 获取任务链

获取完整的工作记忆链（从指定节点或最新节点开始回溯）。

**参数：**
- `session_id`: 会话 ID（必需）
- `from_node_id`: 起始节点 ID（可选，默认最新）

### 12. memory_search - 语义搜索

基于 embedding 的语义向量搜索，查找与查询语义相似的文本片段。

**参数：**
- `query`: 搜索查询（必需）
- `limit`: 返回结果数量（可选，默认 10，最大 50）
- `corpus`: 搜索范围（可选，默认 'memory'）

**示例：**
```
搜索关于 OpenClaw 的记忆
```

AI 会执行：
```json
{
  "action": "memory_search",
  "params": {
    "query": "OpenClaw",
    "limit": 5
  }
}
```

返回结果包含相似度分数（0-1），按相关度排序。

### 13. memory_get - 精确读取记忆文件

按路径精确读取记忆文件的内容片段，支持行号范围。

**参数：**
- `path`: 文件路径（必需）
- `fromLine`: 起始行号（可选，1-based）
- `lines`: 读取行数（可选，默认全部，最大 500）

**示例：**
```
读取 MEMORY.md 第 1-20 行
```

AI 会执行：
```json
{
  "action": "memory_get",
  "params": {
    "path": "MEMORY.md",
    "fromLine": 1,
    "lines": 20
  }
}
```

## 使用原则

1. **优先使用图记忆**：对于重要事实、偏好、决策、任务等持久信息，**优先**使用 `commit` 写入图数据库，而非依赖 message 上下文
2. **主动检索**：在回答用户问题前，**先调用 `recall` 或 `memory_search`** 检索相关记忆，而非仅凭当前上下文推理
3. **结构化**：使用三元组格式存储关系，确保信息可被关联检索
4. **定期清理**：删除过时或错误的信息
5. **上下文压缩**：当对话过长时，使用 `context_rewrite` 将历史压缩为记忆节点
6. **工作记忆**：使用 `working_memory_chain` 获取当前会话的上下文链
7. **主动查询人设**：参考 `graph-memory-persona-force` Skill，在适当时候主动查询用户偏好和决策

## 记忆策略指南

### 什么时候写入图数据库？

**必须写入**：
- 用户明确说"请记住"、"记住这个"等
- 用户透露偏好、习惯、身份信息
- 做出重要决策或选择
- 创建任务或目标
- 关键知识点或学习成果

**建议写入**：
- 对话中重复出现的重要概念
- 用户纠正或补充的信息
- 项目相关的配置、路径、决策

**无需写入**：
- 临时性问候、寒暄
- 一次性问题（如"现在几点"）
- 已在图数据库中的重复信息

### 什么时候检索图数据库？

**必须检索**：
- 用户问"我之前说过..."、"你还记得..."
- 需要基于历史偏好做推荐或决策
- 继续之前的任务或话题

**建议检索**：
- 每次对话开始时，检索用户相关信息
- 做推荐前先了解用户偏好
- 涉及人设或性格相关的话题

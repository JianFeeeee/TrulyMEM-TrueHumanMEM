"""
记忆工具定义 - 优化版
精简描述，避免过拟合，保留AI自主性
"""

# 基础记忆工具
MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "memory_recall",
            "description": """检索记忆。支持关键词、时间范围、会话过滤。返回相关实体和关系。

【⚠️ 强制执行顺序 - 每轮必须严格遵守】
1. 步骤1（必须首先执行）: 查询人设图
   {"query_intent": "AI,人设,角色,性格,语气,说话风格", "depth": 2}
   
2. 步骤2（必须第二步执行）: 查询工作记忆链
   {"query_intent": "TaskNode,工作记忆,任务链", "depth": 2}

3. 步骤3: 根据需要查询其他记忆

【使用示例】
1. 查询用户偏好:
   {"query_intent": "用户,喜欢,偏好", "seed_entities": ["用户"]}

2. 查询特定主题:
   {"query_intent": "Python,编程,项目", "seed_entities": ["Python"]}

3. 查询最近7天的记忆:
   {"query_intent": "任务,工作", "time_range": {"days": 7}}

【重要】跳过步骤1或步骤2将导致系统错误！""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_intent": {
                        "type": "string",
                        "description": "查询意图，支持逗号分隔多个关键词"
                    },
                    "seed_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "种子实体（可选）"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "遍历深度，默认2"
                    },
                    "time_range": {
                        "type": "object",
                        "description": "时间范围（可选）",
                        "properties": {
                            "days": {"type": "integer", "description": "最近N天"}
                        }
                    },
                    "session_filter": {
                        "type": "string",
                        "description": "会话ID过滤（可选）"
                    }
                },
                "required": ["query_intent"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_commit",
            "description": """写入记忆。将三元组写入图数据库，支持批量写入。

【使用示例】
1. 记录用户偏好:
   {"triplets": [
     {"subject": "用户", "relation": "喜欢", "object": "Python编程", "confidence": 0.9},
     {"subject": "用户", "relation": "正在学习", "object": "机器学习"}
   ]}

2. 记录项目信息:
   {"triplets": [
     {"subject": "项目A", "relation": "使用技术", "object": "React"},
     {"subject": "项目A", "relation": "状态", "object": "开发中"}
   ]}

3. 记录游戏状态（配合工作记忆链）:
   {"triplets": [
     {"subject": "成语接龙_当前成语", "relation": "内容", "object": "画龙点睛"},
     {"subject": "成语接龙_当前成语", "relation": "游戏", "object": "成语接龙"}
   ]}

【重要】写入原则:
- 用户明确表达的信息 → 必须写入
- AI推理得到的信息 → 可以写入，但需标注[推测]
- 避免写入冗余或无意义的信息""",
            "parameters": {
                "type": "object",
                "properties": {
                    "triplets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subject": {"type": "string"},
                                "relation": {"type": "string"},
                                "object": {"type": "string"},
                                "confidence": {"type": "number"},
                                "subject_type": {"type": "string", "description": "主体的实体类型，如 Person、Project"},
                                "object_type": {"type": "string", "description": "客体的实体类型，如 Language、Technology"}
                            },
                            "required": ["subject", "relation", "object"]
                        },
                        "description": "三元组列表"
                    },
                    "entity_types": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "实体类型字典，如 {\"用户\": \"Person\", \"项目A\": \"Project\"}（可选）"
                    },
                    "temporal_tag": {
                        "type": "string",
                        "description": "时间标记（可选）"
                    }
                },
                "required": ["triplets"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_purge",
            "description": """删除记忆。支持条件删除和纠错替代。

【使用示例】
1. 软删除特定关系:
   {"criteria": {"subject_contains": "用户", "relation_type": "喜欢"}, "mode": "soft"}

2. 纠错替代（修正错误信息）:
   {
     "criteria": {"subject_contains": "用户", "relation_type": "年龄"},
     "mode": "supersede",
     "new_relation": {"relation": "年龄", "target": "25岁"}
   }

3. 删除特定会话的记忆:
   {"criteria": {"session_id": "session_123"}, "mode": "soft"}

4. 删除旧记忆:
   {"criteria": {"time_before": "2024-01-01"}, "mode": "soft"}

5. 删除残留在已归档任务上的状态关系:
   {"criteria": {"relation_type": "HAS_STATE", "source_type": "TaskNode", "source_has_status": "archived"}, "mode": "soft"}

6. 删除特定类型的节点关系:
   {"criteria": {"relation_type": "某种关系", "target_type": "某种类型"}, "mode": "soft"}

【重要】删除原则:
- 优先使用 supersede 模式修正错误
- 软删除不会物理删除数据
- 谨慎使用删除操作""",
            "parameters": {
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "object",
                        "properties": {
                            "subject_contains": {"type": "string"},
                            "relation_type": {"type": "string"},
                            "target_contains": {"type": "string"},
                            "source_type": {"type": "string", "description": "源实体类型过滤（如 TaskNode）"},
                            "target_type": {"type": "string", "description": "目标实体类型过滤"},
                            "source_has_status": {"type": "string", "description": "源实体状态过滤（如 archived）"},
                            "time_before": {"type": "string"},
                            "session_id": {"type": "string"}
                        },
                        "description": "删除条件"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["soft", "supersede"],
                        "description": "删除模式：soft=逻辑删除, supersede=纠错替代",
                        "default": "soft"
                    },
                    "new_relation": {
                        "type": "object",
                        "description": "新关系（supersede模式）",
                        "properties": {
                            "relation": {"type": "string"},
                            "target": {"type": "string"}
                        }
                    }
                },
                "required": ["criteria"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_introspect",
            "description": "查看记忆状态。返回会话统计、实体热点、关系分布。",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "会话ID（可选）"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_archive",
            "description": "归档旧记忆。将N天前的非活跃关系标记为归档状态。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "归档天数，默认30"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_cleanup",
            "description": "清理无效数据。物理删除已删除状态超过90天的关系和孤立节点。",
            "parameters": {
                "type": "object",
                "properties": {
                    "dry_run": {
                        "type": "boolean",
                        "description": "仅预览不删除",
                        "default": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_query_archived",
            "description": """查询已归档的记忆。

【使用场景】
- 想了解之前归档过哪些记忆
- 按关键词搜索归档内容
- 按时间范围查看最近归档的历史

【注意】
- 只返回 status=archived 的原始关系记录，不包含活跃的「归档摘要」
- days 和 keyword 可以单独使用，也可以组合使用
- 不加任何参数时返回所有归档记录

【示例】
```
# 不传参数：查全部归档
memory_query_archived({})

# 最近7天
memory_query_archived({"days": 7})

# 关键词过滤
memory_query_archived({"keyword": "任务"})

# 组合使用
memory_query_archived({"days": 30, "keyword": "配置"})
```
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "最近N天内的归档记录，不指定则不限时间"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "关键词，匹配实体名或关系类型"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "context_rewrite",
            "description": """压缩本轮对话的工具调用上下文。将冗长的JSON工具结果提炼为简洁摘要。

【使用场景】
- 本轮已执行 ≥5 次查询类工具调用，JSON细节已理解，不再需要原始格式
- 但需保留"我调用了什么工具、得到了什么结论"的元认知
- 继续携带原始JSON会干扰后续推理

【⚠️ 强制要求】
**context_rewrite 必须单独调用，不能和其他工具在同一轮一起调！**
- 正确方式：先调其他所有工具 → 收到工具结果 → 单独调 context_rewrite
- 错误方式：和其他工具一起调（会破坏对话历史结构）

【格式要求】
1. 必须标注调用了哪些工具
2. 必须标注是对几次工具调用的总结
3. 必须保留关键语义信息

【示例】
{
  "summary": "[工具调用总结: 本次总结了 2 次工具调用 | 调用工具: memory_recall, memory_recall]\\n\\n- 查询人设图：未找到人设，使用默认身份\\n- 查询工作记忆链：发现 Task_成语接龙，状态已暂停，当前成语为虎作伥"
}

【注意事项】
- 不可删除用户原始消息
- 不可歪曲工具返回的关键事实
- 仅在调用 ≥5 次查询类工具后使用""",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "压缩后的摘要文本，必须包含工具调用元信息"
                    }
                },
                "required": ["summary"]
            }
        }
    }
]

# 人设图管理工具
PERSONA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "persona_update",
            "description": """更新人设。修改AI的角色、性格、语气等属性。

【使用示例】
1. 切换为猫娘角色:
   {"attributes": [
     {"attribute": "扮演角色", "value": "猫娘"},
     {"attribute": "说话风格", "value": "可爱、卖萌、使用'喵'作为语气词"},
     {"attribute": "性格特点", "value": "活泼、粘人、忠诚"}
   ], "mode": "replace"}

2. 添加新属性（保留现有属性）:
   {"attributes": [
     {"attribute": "口头禅", "value": "喵呜~"}
   ], "mode": "merge"}

3. 设置专业角色:
   {"attributes": [
     {"attribute": "扮演角色", "value": "Python专家"},
     {"attribute": "说话风格", "value": "专业、简洁、代码示例丰富"},
     {"attribute": "性格特点", "value": "严谨、耐心、乐于助人"}
   ], "mode": "replace"}

【重要】人设更新后:
- 立即按照新人设回复
- 每句话都符合人设的语气、风格、特征
- 绝不主动跳出角色，除非用户明确要求""",
            "parameters": {
                "type": "object",
                "properties": {
                    "attributes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "attribute": {"type": "string", "description": "属性名（如：扮演角色、说话风格、性格特点）"},
                                "value": {"type": "string", "description": "属性值"}
                            },
                            "required": ["attribute", "value"]
                        },
                        "description": "人设属性列表"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["replace", "merge"],
                        "description": "更新模式：replace=替换, merge=合并",
                        "default": "merge"
                    }
                },
                "required": ["attributes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "persona_remove",
            "description": "删除单条人设属性。删除指定的属性（如说话风格、扮演角色等），保留其他人设不变。",
            "parameters": {
                "type": "object",
                "properties": {
                    "attribute": {
                        "type": "string",
                        "description": "要删除的属性名（如：扮演角色、说话风格、性格特点、口头禅）"
                    }
                },
                "required": ["attribute"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "persona_clear",
            "description": "清除人设。删除AI所有角色设定，恢复默认身份。注意：此操作不可逆。",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirm": {
                        "type": "boolean",
                        "description": "确认清除全部人设"
                    }
                },
                "required": ["confirm"]
            }
        }
    }
]

# 工作记忆链管理工具
WORKING_MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": """创建任务节点。用于跟踪连续性任务，维持对话连贯性。

【使用示例】
1. 创建成语接龙游戏任务:
   {
     "task_id": "Task_成语接龙",
     "description": "用户发起成语接龙游戏，当前成语：为所欲为",
     "info_nodes": ["成语接龙_当前成语"]
   }

2. 创建编程学习任务:
   {
     "task_id": "Task_Python学习",
     "description": "用户正在学习Python，当前主题：装饰器",
     "info_nodes": ["Python学习_当前主题"]
   }

3. 创建简单对话任务（每轮必须）:
   {
     "task_id": "Task_当前轮次",
     "description": "本轮对话的简要概述"
   }

【重要】工作记忆链机制:
- 每轮对话结束时必须创建任务节点
- 任务节点通过 NEXT_TASK 边形成时间链
- 任务节点通过 HAS_STATE 边指向状态节点
- 任务节点通过 CONTAINS_INFO 边指向信息节点
- **info_nodes 只能包含该任务专属的具体信息节点**（如"成语接龙_当前成语"），**严禁关联"用户"、"AI"、"系统"等全局通用实体**——这些实体不应通过任务中转
- 全局实体的信息直接用独立关系记录（如 用户--[特质]-->求知欲旺盛），不需要通过 Task 中转
- info_nodes 参数用于关联任务专属信息节点

【完整流程示例】
用户: "咱来玩成语接龙吧，我先开始，为所欲为"

AI操作步骤:
1. 查询人设图 → 获取当前人设
2. 查询工作记忆链 → 无进行中任务
3. 使用 memory_commit 记录游戏状态:
   {"triplets": [
     {"subject": "成语接龙_当前成语", "relation": "内容", "object": "为所欲为"},
     {"subject": "成语接龙_当前成语", "relation": "游戏", "object": "成语接龙"}
   ]}
4. 使用 task_create 创建任务节点:
   {"task_id": "Task_成语接龙", "description": "成语接龙游戏，当前成语：为所欲为", "info_nodes": ["成语接龙_当前成语"]}
5. 回复: "好的喵！我接：为虎作伥喵！" """,
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务ID（如：Task_001）"
                    },
                    "description": {
                        "type": "string",
                        "description": "任务概述"
                    },
                    "info_nodes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "关联的信息节点名称（可选）。⚠️ 只能放任务专属的具体信息节点（如\"成语接龙_当前成语\"），严禁放\"用户\"、\"AI\"、\"系统\"等全局通用实体"
                    }
                },
                "required": ["task_id", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_set_state",
            "description": """设置任务状态。支持：进行中、已完成、已暂停、已取消。

【使用示例】
1. 标记任务为进行中:
   {"task_id": "Task_成语接龙", "state": "进行中"}

2. 标记任务为已完成:
   {"task_id": "Task_成语接龙", "state": "已完成"}

3. 暂停任务（话题被打断时）:
   {"task_id": "Task_成语接龙", "state": "已暂停"}

4. 取消任务:
   {"task_id": "Task_成语接龙", "state": "已取消"}

【重要】状态转换场景:
- 进行中 → 已暂停: 话题被打断时
- 进行中 → 已完成: 任务完成时
- 已暂停 → 进行中: 任务恢复时
- 进行中 → 已取消: 任务被取消时

【完整流程示例】
用户: "关于刚才的成语接龙，我并不知道应该怎么接你的成语，请帮我接一下"

AI操作步骤:
1. 查询人设图 → 获取当前人设
2. 查询工作记忆链 → 发现 Task_成语接龙 状态为"已暂停"
3. 使用 task_set_state 恢复任务:
   {"task_id": "Task_成语接龙", "state": "进行中"}
4. 查询 Task_成语接龙 的信息节点 → 获取当前成语"为虎作伥"
5. 回复: "好的喵！上一个成语是'为虎作伥'，我帮你接：伥鬼害人喵！" """,
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["进行中", "已完成", "已暂停", "已取消"],
                        "description": "任务状态"
                    }
                },
                "required": ["task_id", "state"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_delete",
            "description": "删除任务节点。同时删除关联的信息节点。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    },
                    "delete_info_nodes": {
                        "type": "boolean",
                        "description": "是否删除关联的信息节点",
                        "default": True
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_link_info",
            "description": """关联信息节点。将记忆节点关联到任务节点，用于存储任务的具体信息。

【使用示例】
1. 关联游戏状态到任务:
   {"task_id": "Task_成语接龙", "info_node_names": ["成语接龙_当前成语", "成语接龙_上一个成语"]}

2. 关联学习主题到任务:
   {"task_id": "Task_Python学习", "info_node_names": ["Python学习_当前主题", "Python学习_学习进度"]}

3. 关联项目信息到任务:
   {"task_id": "Task_项目开发", "info_node_names": ["项目A_技术栈", "项目A_当前阶段"]}

【重要】使用场景:
- 先使用 memory_commit 创建信息节点
- 再使用 task_link_info 将信息节点关联到任务节点
- 信息节点通过 CONTAINS_INFO 边与任务节点连接

【完整流程示例】
用户: "咱来玩成语接龙吧，我先开始，为所欲为"

AI操作步骤:
1. 查询人设图 → 获取当前人设
2. 查询工作记忆链 → 无进行中任务
3. 使用 memory_commit 创建信息节点:
   {"triplets": [
     {"subject": "成语接龙_当前成语", "relation": "内容", "object": "为所欲为"},
     {"subject": "成语接龙_当前成语", "relation": "游戏", "object": "成语接龙"}
   ]}
4. 使用 task_create 创建任务节点:
   {"task_id": "Task_成语接龙", "description": "成语接龙游戏"}
5. 使用 task_link_info 关联信息节点:
   {"task_id": "Task_成语接龙", "info_node_names": ["成语接龙_当前成语"]}
6. 回复: "好的喵！我接：为虎作伥喵！" """,
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务ID"
                    },
                    "info_node_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "信息节点名称列表"
                    }
                },
                "required": ["task_id", "info_node_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_archive",
            "description": "归档已完成/过期的任务。将任务状态设为 archived，同时写入完成摘要到图数据库。\n\n【使用场景】\n1. 话题转变时归档旧任务\n2. 已完成的任务及时归档\n3. 长时间无更新的任务归档\n\n【注意】优先使用 task_archive 替代 task_set_state(state=archived)，因为它会自动写入完成摘要。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "要归档的任务ID"
                    },
                    "summary": {
                        "type": "string",
                        "description": "归档摘要，简述完成了什么或为什么归档。如果不填则自动生成。"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_query",
            "description": "查询最近的任务列表。按更新时间倒序排列。新对话开始时优先使用此工具获取所有进展中的任务，避免重复创建。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回的任务数量，默认10"
                    },
                    "state_filter": {
                        "type": "string",
                        "description": "按状态筛选：进行中、已完成、已暂停、已取消、archived"
                    }
                }
            }
        }
    }
]

# 所有工具
TOOLS = MEMORY_TOOLS + PERSONA_TOOLS + WORKING_MEMORY_TOOLS

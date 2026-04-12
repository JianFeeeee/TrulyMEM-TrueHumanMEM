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

【使用示例】
1. 查询人设图（每轮必须首先执行）:
   {"query_intent": "AI,人设,角色,性格,语气,说话风格", "depth": 2}

2. 查询工作记忆链（每轮必须第二步执行）:
   {"query_intent": "TaskNode,工作记忆,任务链", "depth": 2}

3. 查询用户偏好:
   {"query_intent": "用户,喜欢,偏好", "seed_entities": ["用户"]}

4. 查询特定主题:
   {"query_intent": "Python,编程,项目", "seed_entities": ["Python"]}

5. 查询最近7天的记忆:
   {"query_intent": "任务,工作", "time_range": {"days": 7}}

【重要】每轮对话必须按顺序执行:
- 步骤1: 查询人设图（最高优先级）
- 步骤2: 查询工作记忆链（维持对话连贯性）
- 步骤3: 根据需要查询其他记忆""",
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
                                "confidence": {"type": "number"}
                            },
                            "required": ["subject", "relation", "object"]
                        },
                        "description": "三元组列表"
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "实体类型（可选）"
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
            "name": "persona_clear",
            "description": "清除人设。删除AI的角色设定，恢复默认身份。",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirm": {
                        "type": "boolean",
                        "description": "确认清除",
                        "default": True
                    }
                },
                "required": []
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
- info_nodes 参数用于关联具体信息节点

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
                        "description": "关联的信息节点名称（可选）"
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
    }
]

# 所有工具
TOOLS = MEMORY_TOOLS + PERSONA_TOOLS + WORKING_MEMORY_TOOLS

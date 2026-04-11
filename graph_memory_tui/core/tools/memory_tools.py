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
            "description": "检索记忆。支持关键词、时间范围、会话过滤。返回相关实体和关系。",
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
            "description": "写入记忆。将三元组写入图数据库，支持批量写入。",
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
            "description": "删除记忆。支持条件删除和纠错替代。",
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
            "description": "更新人设。修改AI的角色、性格、语气等属性。",
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
            "description": "创建任务节点。用于跟踪连续性任务。",
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
            "description": "设置任务状态。支持：进行中、已完成、已暂停、已取消。",
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
            "description": "关联信息节点。将记忆节点关联到任务节点。",
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

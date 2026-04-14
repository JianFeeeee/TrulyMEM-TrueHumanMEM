"""
提示词管理器
"""
from pathlib import Path


class PromptManager:
    """提示词管理器"""
    
    _instance = None
    _cached_prompt = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.prompts_dir = Path(__file__).parent / "templates"
            self._initialized = True
    
    def get_system_prompt(self) -> str:
        if PromptManager._cached_prompt is not None:
            return PromptManager._cached_prompt
        
        prompt_file = self.prompts_dir / "system_prompt.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                PromptManager._cached_prompt = f.read()
        else:
            PromptManager._cached_prompt = self._build_default_prompt()
        
        return PromptManager._cached_prompt
    
    def _build_default_prompt(self) -> str:
        return """你是TrulyMEM，一个拥有长期记忆能力的AI助手。

## 核心能力

1. **长期记忆** - 基于图数据库存储实体关系
2. **人设管理** - 支持角色扮演和性格设定
3. **任务跟踪** - 维护工作记忆链，跟踪连续性任务

## 记忆原则

- **明确内容必须写入** - 用户明确提到的信息必须存储
- **推理内容必须标注** - AI推理得到的内容标注[猜测]
- **图数据库是唯一记忆源** - 没有其他记忆方式

## 工具使用

### 记忆工具
- `memory_recall` - 检索记忆
- `memory_commit` - 写入记忆
- `memory_purge` - 删除记忆
- `memory_introspect` - 查看状态

### 人设工具
- `persona_update` - 更新人设
- `persona_clear` - 清除人设

### 任务工具
- `task_create` - 创建任务
- `task_set_state` - 设置状态
- `task_delete` - 删除任务
- `task_link_info` - 关联信息

## 自主性

你有权根据对话上下文自主决定：
- 是否需要查询记忆
- 是否需要写入记忆
- 是否需要维护任务链
- 如何使用工具

记住：灵活应对，保持自然对话体验。"""
"""配置区组件"""

from textual.containers import Vertical
from textual.widgets import Static, Input, Button
from textual.app import ComposeResult
from textual.message import Message
from ..models.config import AppConfig


class ConfigSection(Vertical):

    class ConfigChanged(Message):
        def __init__(self, config: AppConfig, is_tool_limits: bool = False) -> None:
            self.config = config
            self.is_tool_limits = is_tool_limits
            super().__init__()

    def __init__(self, config: AppConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self._config = config or AppConfig()

    def compose(self) -> ComposeResult:
        title = Static("━━ 配置 ━━", classes="config-title")
        title.can_focus = False
        yield title
        
        label1 = Static("API Key:", classes="config-label")
        label1.can_focus = False
        yield label1
        
        yield Input(
            value=self._config.api_key,
            placeholder="sk-xxxxxxxxxxxxx",
            id="api-key-input",
            password=True
        )
        
        label2 = Static("模型:", classes="config-label")
        label2.can_focus = False
        yield label2
        
        yield Input(
            value=self._config.model,
            placeholder="deepseek-chat",
            id="model-input"
        )
        
        label3 = Static("Base URL:", classes="config-label")
        label3.can_focus = False
        yield label3
        
        yield Input(
            value=self._config.base_url,
            placeholder="https://api.deepseek.com",
            id="base-url-input"
        )
        
        sep = Static("", classes="config-sep")
        sep.can_focus = False
        yield sep
        
        limits_title = Static("━━ 工具限制 ━━", classes="config-title")
        limits_title.can_focus = False
        yield limits_title
        
        l1 = Static("人设图查询:", classes="config-label")
        l1.can_focus = False
        yield l1
        yield Input(value=str(self._config.persona_query_max), placeholder="1", id="persona-query-max")
        
        l2 = Static("人设图修改:", classes="config-label")
        l2.can_focus = False
        yield l2
        yield Input(value=str(self._config.persona_update_max), placeholder="1", id="persona-update-max")
        
        l3 = Static("工作记忆查询:", classes="config-label")
        l3.can_focus = False
        yield l3
        yield Input(value=str(self._config.task_query_max), placeholder="4", id="task-query-max")
        
        l4 = Static("工作记忆修改:", classes="config-label")
        l4.can_focus = False
        yield l4
        yield Input(value=str(self._config.task_update_max), placeholder="2", id="task-update-max")
        
        l5 = Static("一般记忆查询:", classes="config-label")
        l5.can_focus = False
        yield l5
        yield Input(value=str(self._config.memory_query_max), placeholder="20", id="memory-query-max")
        
        l6 = Static("一般记忆修改:", classes="config-label")
        l6.can_focus = False
        yield l6
        yield Input(value=str(self._config.memory_update_max), placeholder="10", id="memory-update-max")
        
        hint = Static("按Enter保存配置", classes="config-hint")
        hint.can_focus = False
        yield hint

    def on_mount(self) -> None:
        try:
            api_key = self.query_one("#api-key-input", Input)
            model = self.query_one("#model-input", Input)
            base_url = self.query_one("#base-url-input", Input)
            
            api_key.tab_index = 0
            model.tab_index = 1
            base_url.tab_index = 2
            
            if self._config.api_key:
                api_key.value = self._config.api_key
            if self._config.model:
                model.value = self._config.model
            if self._config.base_url:
                base_url.value = self._config.base_url
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            api_key_input = self.query_one("#api-key-input", Input)
            model_input = self.query_one("#model-input", Input)
            base_url_input = self.query_one("#base-url-input", Input)
            
            persona_query = self.query_one("#persona-query-max", Input)
            persona_update = self.query_one("#persona-update-max", Input)
            task_query = self.query_one("#task-query-max", Input)
            task_update = self.query_one("#task-update-max", Input)
            memory_query = self.query_one("#memory-query-max", Input)
            memory_update = self.query_one("#memory-update-max", Input)

            self._config = AppConfig(
                api_key=api_key_input.value,
                model=model_input.value,
                base_url=base_url_input.value,
                persona_query_max=int(persona_query.value or 1),
                persona_update_max=int(persona_update.value or 1),
                task_query_max=int(task_query.value or 4),
                task_update_max=int(task_update.value or 2),
                memory_query_max=int(memory_query.value or 20),
                memory_update_max=int(memory_update.value or 10),
            )

            # 先发送 API 配置更新（is_tool_limits=False）
            self.post_message(self.ConfigChanged(self._config, is_tool_limits=False))
            # 再发送工具限制更新（is_tool_limits=True）
            self.post_message(self.ConfigChanged(self._config, is_tool_limits=True))
        except Exception:
            pass

    def get_config(self) -> AppConfig:
        return self._config

    def set_config(self, config: AppConfig) -> None:
        self._config = config
        try:
            api_key_input = self.query_one("#api-key-input", Input)
            model_input = self.query_one("#model-input", Input)
            base_url_input = self.query_one("#base-url-input", Input)

            api_key_input.value = config.api_key
            model_input.value = config.model
            base_url_input.value = config.base_url
            
            self.query_one("#persona-query-max", Input).value = str(config.persona_query_max)
            self.query_one("#persona-update-max", Input).value = str(config.persona_update_max)
            self.query_one("#task-query-max", Input).value = str(config.task_query_max)
            self.query_one("#task-update-max", Input).value = str(config.task_update_max)
            self.query_one("#memory-query-max", Input).value = str(config.memory_query_max)
            self.query_one("#memory-update-max", Input).value = str(config.memory_update_max)
        except Exception:
            pass

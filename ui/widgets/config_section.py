"""配置区组件"""

from textual.containers import Vertical
from textual.widgets import Static, Input, Collapsible
from textual.app import ComposeResult
from textual.message import Message
from ..models.config import AppConfig


class ConfigSection(Vertical):
    """可折叠配置区"""

    class ConfigChanged(Message):
        """配置变更事件"""
        def __init__(self, config: AppConfig) -> None:
            self.config = config
            super().__init__()

    def __init__(self, config: AppConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self._config = config or AppConfig()

    def compose(self) -> ComposeResult:
        """构建配置区"""
        # 直接显示配置，不使用Collapsible
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
        
        hint = Static("按Enter保存配置", classes="config-hint")
        hint.can_focus = False
        yield hint

    def on_mount(self) -> None:
        """组件挂载时设置Tab顺序并加载配置"""
        try:
            api_key = self.query_one("#api-key-input", Input)
            model = self.query_one("#model-input", Input)
            base_url = self.query_one("#base-url-input", Input)
            
            # 设置Tab索引
            api_key.tab_index = 0
            model.tab_index = 1
            base_url.tab_index = 2
            
            # 如果配置有值，更新输入框
            if self._config.api_key:
                api_key.value = self._config.api_key
            if self._config.model:
                model.value = self._config.model
            if self._config.base_url:
                base_url.value = self._config.base_url
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """处理输入变更事件"""
        # 防抖：只在用户停止输入时更新
        pass  # 不在输入时实时更新，避免卡顿

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交事件（按Enter或Tab）"""
        # 只在提交时更新配置
        try:
            api_key_input = self.query_one("#api-key-input", Input)
            model_input = self.query_one("#model-input", Input)
            base_url_input = self.query_one("#base-url-input", Input)

            # 更新配置
            self._config = AppConfig(
                api_key=api_key_input.value,
                model=model_input.value,
                base_url=base_url_input.value
            )

            # 发送配置变更事件
            self.post_message(self.ConfigChanged(self._config))
        except Exception as e:
            pass

    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self._config

    def set_config(self, config: AppConfig) -> None:
        """设置配置"""
        self._config = config
        try:
            api_key_input = self.query_one("#api-key-input", Input)
            model_input = self.query_one("#model-input", Input)
            base_url_input = self.query_one("#base-url-input", Input)

            api_key_input.value = config.api_key
            model_input.value = config.model
            base_url_input.value = config.base_url
        except Exception:
            pass

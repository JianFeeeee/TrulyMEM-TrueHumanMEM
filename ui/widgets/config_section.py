"""配置区组件"""

from textual.containers import Vertical
from textual.widgets import Static, Input, Button, Checkbox
from textual.app import ComposeResult
from textual.message import Message
from ..models.config import AppConfig


class ConfigSection(Vertical):

    class ConfigChanged(Message):
        def __init__(self, config: AppConfig, is_tool_limits: bool = False) -> None:
            self.config = config
            self.is_tool_limits = is_tool_limits
            super().__init__()

    def __init__(self, config: AppConfig | None = None, is_admin: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._config = config or AppConfig()
        self._is_admin = is_admin

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
            placeholder="deepseek-v4-flash",
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
        
        l2 = Static("人设图修改:", classes="config-label")
        l2.can_focus = False
        yield l2
        yield Input(value=str(self._config.persona_update_max), placeholder="1", id="persona-update-max")
        
        l4 = Static("工作记忆修改:", classes="config-label")
        l4.can_focus = False
        yield l4
        yield Input(value=str(self._config.task_update_max), placeholder="5", id="task-update-max")
        
        l5 = Static("一般记忆查询:", classes="config-label")
        l5.can_focus = False
        yield l5
        yield Input(value=str(self._config.memory_query_max), placeholder="20", id="memory-query-max")
        
        l6 = Static("一般记忆修改:", classes="config-label")
        l6.can_focus = False
        yield l6
        yield Input(value=str(self._config.memory_update_max), placeholder="10", id="memory-update-max")
        
        sep2 = Static("", classes="config-sep")
        sep2.can_focus = False
        yield sep2

        # Web 登录 — 仅 admin 可见
        web_title = Static("━━ Web 登录 ━━", classes="config-title admin-section")
        web_title.can_focus = False
        yield web_title
        
        label_web_user = Static("用户名:", classes="config-label admin-section")
        label_web_user.can_focus = False
        yield label_web_user
        yield Input(
            value=self._config.web_username,
            placeholder="admin",
            id="web-username-input",
            classes="admin-section"
        )
        
        label_web_pwd = Static("密码:", classes="config-label admin-section")
        label_web_pwd.can_focus = False
        yield label_web_pwd
        yield Input(
            value=self._config.web_password,
            placeholder="修改密码",
            id="web-password-input",
            password=True,
            classes="admin-section"
        )
        
        hint = Static("按Enter保存配置", classes="config-hint admin-section")
        hint.can_focus = False
        yield hint

        sep3 = Static("", classes="config-sep admin-section")
        sep3.can_focus = False
        yield sep3

        # Web 服务 — 仅 admin 可见
        ws_title = Static("━━ Web 服务 ━━", classes="config-title admin-section")
        ws_title.can_focus = False
        yield ws_title

        ws_hint = Static("在侧边栏启用后将自动启动 Web 管理界面", classes="config-hint admin-section")
        ws_hint.can_focus = False
        yield ws_hint

        cb_web = Checkbox(
            "启用 Web 服务",
            value=self._config.enable_web,
            id="enable-web-checkbox",
            classes="admin-section"
        )
        yield cb_web

        label_web_port = Static("端口:", classes="config-label admin-section")
        label_web_port.can_focus = False
        yield label_web_port
        yield Input(
            value=str(self._config.web_port),
            placeholder="4096",
            id="web-port-input",
            type="integer",
            classes="admin-section"
        )

        sep4 = Static("", classes="config-sep admin-section")
        sep4.can_focus = False
        yield sep4

        # TUI 服务控制 — 仅 admin 可见
        tui_title = Static("━━ TUI 服务 ━━", classes="config-title admin-section")
        tui_title.can_focus = False
        yield tui_title

        tui_hint = Static("控制终端文本界面是否允许连接", classes="config-hint admin-section")
        tui_hint.can_focus = False
        yield tui_hint

        cb_tui = Checkbox(
            "启用 TUI 服务",
            value=self._config.enable_tui,
            id="enable-tui-checkbox",
            classes="admin-section"
        )
        yield cb_tui

    def on_mount(self) -> None:
        # 应用管理员区域的可见性
        self._apply_admin_visibility()
        
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

            web_user = self.query_one("#web-username-input", Input)
            web_pwd = self.query_one("#web-password-input", Input)
            web_user.tab_index = 7
            web_pwd.tab_index = 8

            web_port = self.query_one("#web-port-input", Input)
            web_port.tab_index = 9
        except Exception:
            pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """处理复选框状态变化"""
        try:
            # Web 服务开关
            if event.checkbox.id == "enable-web-checkbox":
                self._update_config_from_ui()
                # 发送配置更新消息
                self.post_message(self.ConfigChanged(self._config, is_tool_limits=False))
                
            # TUI 服务开关
            elif event.checkbox.id == "enable-tui-checkbox":
                self._update_config_from_ui()
                # 发送配置更新消息
                self.post_message(self.ConfigChanged(self._config, is_tool_limits=False))
        except Exception:
            pass

    def _update_config_from_ui(self) -> None:
        """从UI组件更新配置对象"""
        try:
            api_key_input = self.query_one("#api-key-input", Input)
            model_input = self.query_one("#model-input", Input)
            base_url_input = self.query_one("#base-url-input", Input)

            persona_update = self.query_one("#persona-update-max", Input)
            task_update = self.query_one("#task-update-max", Input)
            memory_query = self.query_one("#memory-query-max", Input)
            memory_update = self.query_one("#memory-update-max", Input)

            web_username = self.query_one("#web-username-input", Input)
            web_password = self.query_one("#web-password-input", Input)

            web_checkbox = self.query_one("#enable-web-checkbox", Checkbox)
            web_port_input = self.query_one("#web-port-input", Input)
            
            # TUI checkbox 可能不存在（非管理员）
            tui_checkbox = None
            try:
                tui_checkbox = self.query_one("#enable-tui-checkbox", Checkbox)
            except:
                pass

            self._config = AppConfig(
                api_key=api_key_input.value,
                model=model_input.value,
                base_url=base_url_input.value,
                persona_update_max=int(persona_update.value or 1),
                task_update_max=int(task_update.value or 5),
                memory_query_max=int(memory_query.value or 20),
                memory_update_max=int(memory_update.value or 10),
                web_username=web_username.value,
                web_password=web_password.value,
                enable_web=web_checkbox.value,
                web_port=int(web_port_input.value) if web_port_input.value else 4096,
                enable_tui=tui_checkbox.value if tui_checkbox else True,
            )
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            self._update_config_from_ui()

            # 先发送 API 配置更新（is_tool_limits=False）
            self.post_message(self.ConfigChanged(self._config, is_tool_limits=False))
            # 再发送工具限制更新（is_tool_limits=True）
            self.post_message(self.ConfigChanged(self._config, is_tool_limits=True))
        except Exception:
            pass

    def set_admin(self, is_admin: bool) -> None:
        """设置是否 admin 模式，动态显示/隐藏 admin 区域"""
        self._is_admin = is_admin
        self._apply_admin_visibility()

    def _apply_admin_visibility(self) -> None:
        """根据 _is_admin 显示/隐藏 admin 专用区域"""
        display_val = "block" if self._is_admin else "none"
        for widget in self.query(".admin-section"):
            widget.styles.display = display_val

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

            self.query_one("#persona-update-max", Input).value = str(config.persona_update_max)
            self.query_one("#task-update-max", Input).value = str(config.task_update_max)
            self.query_one("#memory-query-max", Input).value = str(config.memory_query_max)
            self.query_one("#memory-update-max", Input).value = str(config.memory_update_max)

            self.query_one("#web-username-input", Input).value = config.web_username
            self.query_one("#web-password-input", Input).value = config.web_password

            try:
                self.query_one("#enable-web-checkbox", Checkbox).value = config.enable_web
            except:
                pass
            self.query_one("#web-port-input", Input).value = str(config.web_port)
            
            # TUI checkbox
            try:
                self.query_one("#enable-tui-checkbox", Checkbox).value = config.enable_tui
            except:
                pass
        except Exception:
            pass

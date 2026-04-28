"""
TUI 登录页面
"""

import asyncio
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.widgets import Input, Button, Static, Label
from textual.screen import Screen
from core.embedded_db import EmbeddedGraphDB
from core.migrate import need_migration, run_migration, is_migrated


class LoginScreen(Screen):
    """登录界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._migrating = False
        self._migration_username = ""
        self._migration_password = ""
    
    def compose(self) -> ComposeResult:
        # 检测是否需要迁移
        migrating = need_migration()
        migrated = is_migrated()
        
        if migrating and not migrated:
            yield from self._compose_migration()
        else:
            yield from self._compose_login()
    
    def _compose_login(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="login_container"):
                    yield Static("🔐 TrulyMEM 登录", id="login_title")
                    yield Label("用户名:")
                    yield Input(placeholder="请输入用户名", id="username_input")
                    yield Label("密码:")
                    yield Input(placeholder="请输入密码", password=True, id="password_input")
                    yield Button("登录", id="login_button", variant="primary")
                    yield Static("", id="login_message")
    
    def _compose_migration(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="migration_container"):
                    yield Static("🔄 检测到旧版数据，需要迁移", id="migration_title")
                    yield Static("请设置管理员账号以完成迁移", id="migration_subtitle")
                    yield Label("用户名:")
                    yield Input(placeholder="请输入管理员用户名", id="mig_username_input")
                    yield Label("密码:")
                    yield Input(placeholder="请输入管理员密码", password=True, id="mig_password_input")
                    yield Button("开始迁移", id="migrate_button", variant="primary")
                    yield Static("", id="migration_message")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_button":
            self._handle_login()
        elif event.button.id == "migrate_button":
            self._handle_migration()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "username_input":
            self.query_one("#password_input", Input).focus()
        elif event.input.id == "password_input":
            self._handle_login()
        elif event.input.id == "mig_username_input":
            self.query_one("#mig_password_input", Input).focus()
        elif event.input.id == "mig_password_input":
            self._handle_migration()
    
    def _handle_login(self) -> None:
        username = self.query_one("#username_input", Input).value.strip()
        password = self.query_one("#password_input", Input).value
        
        if not username or not password:
            self.query_one("#login_message", Static).update("❌ 用户名和密码不能为空")
            return
        
        # 验证用户
        try:
            global_db_path = Path.home() / ".trulymem" / "trulymem.db"
            if not global_db_path.exists():
                self.query_one("#login_message", Static).update("❌ 全局数据库不存在，请先完成迁移")
                return
            
            db = EmbeddedGraphDB(db_path=str(global_db_path))
            user_info = db.get_web_user(username)
            
            if not user_info:
                self.query_one("#login_message", Static).update("❌ 用户不存在")
                db.close()
                return
            
            # 验证密码
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if db.verify_web_user(username, password):
                db.close()
                # 登录成功，通知应用
                self.app.on_login_success(username, user_info)
            else:
                self.query_one("#login_message", Static).update("❌ 密码错误")
                db.close()
        
        except Exception as e:
            self.query_one("#login_message", Static).update(f"❌ 登录失败: {str(e)}")
    
    def _handle_migration(self) -> None:
        username = self.query_one("#mig_username_input", Input).value.strip()
        password = self.query_one("#mig_password_input", Input).value
        
        if not username or not password:
            self.query_one("#migration_message", Static).update("❌ 用户名和密码不能为空")
            return
        
        self.query_one("#migration_message", Static).update("⏳ 正在迁移...")
        
        # 执行迁移（异步）
        asyncio.create_task(self._do_migration(username, password))
    
    async def _do_migration(self, username: str, password: str) -> None:
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, run_migration, username, password
            )
            
            if result.get("success"):
                self.query_one("#migration_message", Static).update("✅ 迁移成功！请登录")
                # 重新加载界面为登录界面
                await asyncio.sleep(1)
                self.app.pop_screen()
                self.app.push_screen(LoginScreen())
            else:
                self.query_one("#migration_message", Static).update(f"❌ 迁移失败: {result.get('error')}")
        except Exception as e:
            self.query_one("#migration_message", Static).update(f"❌ 迁移异常: {str(e)}")

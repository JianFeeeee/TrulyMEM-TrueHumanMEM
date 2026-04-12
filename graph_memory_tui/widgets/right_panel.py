"""右侧面板"""

from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.app import ComposeResult
from .config_section import ConfigSection
from .operation_log import OperationLog
from .cypher_query_box import CypherQueryBox
from ..models.config import AppConfig


class RightPanel(Container):
    """右侧边栏"""

    def __init__(self, config: AppConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self._is_collapsed = False
        self._config = config or AppConfig()

    def compose(self) -> ComposeResult:
        """构建右侧面板"""
        from textual.containers import ScrollableContainer
        
        yield Static("F2:隐藏侧边栏", classes="sidebar-title")
        with ScrollableContainer():
            yield ConfigSection(self._config)
            yield OperationLog()
            yield CypherQueryBox()

    def toggle(self) -> None:
        """切换折叠/展开"""
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.styles.width = 0
            self.styles.display = "none"
        else:
            self.styles.width = 70
            self.styles.display = "block"

    def is_collapsed(self) -> bool:
        """检查是否折叠"""
        return self._is_collapsed

    def get_config_section(self) -> ConfigSection:
        """获取配置区组件"""
        return self.query_one(ConfigSection)

    def get_operation_log(self) -> OperationLog:
        """获取操作日志组件"""
        return self.query_one(OperationLog)

    def get_cypher_query_box(self) -> CypherQueryBox:
        """获取Cypher查询框组件"""
        return self.query_one(CypherQueryBox)

    def update_title(self) -> None:
        """更新标题"""
        title = self.query_one(Static)
        title.update("F2:展开侧边栏" if self._is_collapsed else "F2:隐藏侧边栏")

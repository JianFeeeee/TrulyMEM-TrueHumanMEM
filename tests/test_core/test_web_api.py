"""Tests for Web API endpoints"""


def test_web_api_imports():
    """Web API 模块应能正常导入"""
    from core import web_api
    assert web_api is not None


def test_web_api_has_endpoints():
    """Web API 应定义关键端点"""
    from core.web_api import app
    rules = [r.rule for r in app.url_map.iter_rules()]
    expected_endpoints = [
        '/api/settings',
        '/api/message',
        '/api/tools/execute',
        '/api/status',
        '/api/history',
        '/api/check-auth',
    ]
    for endpoint in expected_endpoints:
        assert endpoint in rules, f"缺少端点: {endpoint}"


def test_web_api_static_files():
    """Web API 应正确配置静态文件路径"""
    from core.web_api import app
    assert app.static_folder is not None
    assert 'graph.html' in app.static_url_path or app.static_folder is not None


def test_ui_index_exists():
    """Web UI 的核心页面应存在"""
    import os
    from core.web_api import _ui_dir
    for page in ['graph.html', 'index.html']:
        path = os.path.join(_ui_dir, 'static', page)
        assert os.path.exists(path), f"缺少静态页面: {page}"
    for template in ['login.html', 'settings.html', 'setup.html']:
        path = os.path.join(_ui_dir, 'templates', template)
        assert os.path.exists(path), f"缺少模板: {template}"


def test_system_prompt_integration():
    """系统提示词应能被后端正确加载"""
    from core.prompts import PromptManager
    pm = PromptManager()
    prompt = pm.get_system_prompt()
    assert prompt is not None
    assert len(prompt) > 200

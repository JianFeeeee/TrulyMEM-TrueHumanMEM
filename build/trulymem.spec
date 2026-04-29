# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

project_root = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))
sys.path.insert(0, project_root)

datas = []
# UI 样式
ui_styles_dir = os.path.join(project_root, 'ui', 'styles')
if os.path.exists(ui_styles_dir):
    for root, dirs, files in os.walk(ui_styles_dir):
        for f in files:
            datas.append((os.path.join(root, f), 'ui/styles'))

# Prompt 模板
prompt_tmpl_dir = os.path.join(project_root, 'core', 'prompts', 'templates')
if os.path.exists(prompt_tmpl_dir):
    for root, dirs, files in os.walk(prompt_tmpl_dir):
        for f in files:
            datas.append((os.path.join(root, f), 'core/prompts/templates'))

# Web 静态文件
static_dir = os.path.join(project_root, 'ui', 'static')
if os.path.exists(static_dir):
    for root, dirs, files in os.walk(static_dir):
        for f in files:
            datas.append((os.path.join(root, f), 'ui/static'))

# Web 模板
templates_dir = os.path.join(project_root, 'ui', 'templates')
if os.path.exists(templates_dir):
    for root, dirs, files in os.walk(templates_dir):
        for f in files:
            datas.append((os.path.join(root, f), 'ui/templates'))

# Web API 脚本（以便子进程模式回退使用）
web_api_src = os.path.join(project_root, 'core', 'web_api.py')
if os.path.exists(web_api_src):
    datas.append((web_api_src, '.'))

# ——— TUI 主二进制 ———
a = Analysis(
    [os.path.join(project_root, 'trulymem_entry.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'textual', 'textual.app', 'textual.widgets', 'textual.css',
        'openai', 'openai._client',
        'neo4j',
        'sqlite3',
        'core', 'core.embedded_db', 'core.graph_client',
        'core.tool_executor', 'core.tool_limiter',
        'core.tools', 'core.tools.memory_tools',
        'core.prompts', 'core.prompts.prompt_manager',
        'core.server', 'core.client',
        'core.migrate',
        'ui', 'ui.app', 'ui.login_screen',
        'ui.models', 'ui.models.message', 'ui.models.config', 'ui.models.log_entry',
        'ui.widgets', 'ui.widgets.left_panel', 'ui.widgets.right_panel',
        'ui.widgets.input_box', 'ui.widgets.message_history', 'ui.widgets.status_bar',
        'ui.handlers',
        'ui.services', 'ui.services.config_manager', 'ui.services.config_service',
        'web_api',
        'flask', 'flask_cors', 'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TrulyMEM',
    icon='pic/TrulyMEM.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

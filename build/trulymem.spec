# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

project_root = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, project_root)

datas = []
# UI 样式
if os.path.exists(os.path.join(project_root, 'ui', 'styles')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'ui', 'styles')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('ui', 'styles', os.path.relpath(src, os.path.join(project_root, 'ui', 'styles')))
            datas.append((src, dst))

# Prompt 模板
if os.path.exists(os.path.join(project_root, 'core', 'prompts', 'templates')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'core', 'prompts', 'templates')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('core', 'prompts', 'templates', os.path.relpath(src, os.path.join(project_root, 'core', 'prompts', 'templates')))
            datas.append((src, dst))

# Web 静态文件
if os.path.exists(os.path.join(project_root, 'static')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'static')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('static', os.path.relpath(src, os.path.join(project_root, 'static')))
            datas.append((src, dst))

# Web 模板
if os.path.exists(os.path.join(project_root, 'templates')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'templates')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('templates', os.path.relpath(src, os.path.join(project_root, 'templates')))
            datas.append((src, dst))

# Web API 脚本（以便子进程模式回退使用）
web_api_src = os.path.join(project_root, 'web_api.py')
if os.path.exists(web_api_src):
    datas.append((web_api_src, '.'))

# ——— TUI 主二进制 ———
a = Analysis(
    ['trulymem_entry.py'],
    pathex=[project_root],
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
pyz = PYZ(a.pure, block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TrulyMEM',
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



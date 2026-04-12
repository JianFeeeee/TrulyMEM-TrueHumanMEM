# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

project_root = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, project_root)

datas = []
if os.path.exists(os.path.join(project_root, 'ui', 'styles')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'ui', 'styles')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('ui', 'styles', os.path.relpath(src, os.path.join(project_root, 'ui', 'styles')))
            datas.append((src, dst))

if os.path.exists(os.path.join(project_root, 'core', 'prompts', 'templates')):
    for root, dirs, files in os.walk(os.path.join(project_root, 'core', 'prompts', 'templates')):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join('core', 'prompts', 'templates', os.path.relpath(src, os.path.join(project_root, 'core', 'prompts', 'templates')))
            datas.append((src, dst))

a = Analysis(
    ['trulymem_entry.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'textual',
        'textual.app',
        'textual.widgets',
        'textual.css',
        'openai',
        'openai._client',
        'neo4j',
        'sqlite3',
        'graph_memory_tui',
        'core',
        'core.embedded_db',
        'core.graph_client',
        'core.tool_executor',
        'core.tool_limiter',
        'core.tools',
        'core.tools.memory_tools',
        'core.prompts',
        'core.prompts.prompt_manager',
        'ui',
        'ui.app',
        'ui.models',
        'ui.models.message',
        'ui.models.config',
        'ui.models.log_entry',
        'ui.widgets',
        'ui.widgets.left_panel',
        'ui.widgets.right_panel',
        'ui.widgets.input_box',
        'ui.widgets.message_history',
        'ui.widgets.status_bar',
        'ui.handlers',
        'ui.services',
        'ui.services.config_manager',
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
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('ui/styles', 'ui/styles'), ('core/prompts/templates', 'core/prompts/templates'), ('static', 'static'), ('templates', 'templates'), ('core/web_api.py', 'core/')]
binaries = []
hiddenimports = ['textual', 'textual.app', 'textual.widgets', 'textual.css', 'openai', 'openai._client', 'neo4j', 'sqlite3', 'core', 'core.embedded_db', 'core.graph_client', 'core.tool_executor', 'core.tool_limiter', 'core.tools', 'core.tools.memory_tools', 'core.prompts', 'core.prompts.prompt_manager', 'core.server', 'core.client', 'core.migrate', 'core.activity_recorder', 'ui', 'ui.app', 'ui.login_screen', 'ui.models', 'ui.models.message', 'ui.models.config', 'ui.models.log_entry', 'ui.widgets', 'ui.handlers', 'ui.services', 'ui.services.config_manager', 'ui.services.config_service', 'core.web_api', 'flask', 'flask_cors', 'werkzeug']
tmp_ret = collect_all('textual')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['trulymem_entry.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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

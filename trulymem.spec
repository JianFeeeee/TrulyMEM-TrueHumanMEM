# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['trulymem_entry.py'],
    pathex=[],
    binaries=[],
    datas=[('graph_memory_tui/styles/*.css', 'graph_memory_tui/styles'), ('graph_memory_tui/web/templates/*.html', 'graph_memory_tui/web/templates')],
    hiddenimports=['textual', 'openai', 'flask', 'neo4j'],
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

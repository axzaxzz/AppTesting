# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all source files
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/gui/modern_ui.html', 'src/gui'),
        ('config/settings.template.json', 'config'),
        ('ICON.ico', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'pywebview',
        'pywebview.platforms.winforms',
        'GitPython',
        'git',
        'watchdog',
        'watchdog.observers',
        'watchdog.observers.winapi',
        'click',
        'colorama',
        'yaml',
        'dateutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Wave.AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ICON.ico',
    version_file=None,
)

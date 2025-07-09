# main.spec

# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

# Helper function to include entire asset folders
def add_data_dir(source_dir):
    datas = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, '.')
            datas.append((rel_path, rel_path))
    return datas

# Collect all data folders
asset_dirs = ['assets']
all_datas = []
for d in asset_dirs:
    all_datas += add_data_dir(d)

# Collect hidden imports (in case of dynamic importing)
hidden_imports = collect_submodules('game_states') + collect_submodules('core') + collect_submodules('utils')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True if you want the console window to show up
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyGame'
)

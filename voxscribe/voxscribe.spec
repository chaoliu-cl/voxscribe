# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

project_root = Path(SPECPATH)

# Include optional assets if present
assets_dir = project_root / "assets"
optional_datas = []
if assets_dir.exists():
    optional_datas.append((str(assets_dir), "assets"))

# Some libraries (matplotlib, networkx, numpy, pandas) can need hidden imports
hiddenimports = []
hiddenimports += collect_submodules("matplotlib")
optional_datas += collect_data_files("faster_whisper")

block_cipher = None


a = Analysis(
    [str(project_root / "bootstrap.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=optional_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="VoxScribe",
    debug=False,
    icon=str(project_root / "assets" / "app.ico"),
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="VoxScribe",
)

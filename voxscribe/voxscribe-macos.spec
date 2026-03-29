# -*- mode: python ; coding: utf-8 -*-

import os
import re
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


project_root = Path(SPECPATH)


def read_app_version() -> str:
    init_file = project_root / "__init__.py"
    match = re.search(
        r'__version__\s*=\s*"([^"]+)"',
        init_file.read_text(encoding="utf-8"),
    )
    if not match:
        raise SystemExit(f"Unable to determine VoxScribe version from {init_file}")
    return match.group(1)


app_name = os.environ.get("VOXSCRIBE_APP_NAME", "VoxScribe")
app_version = os.environ.get("VOXSCRIBE_APP_VERSION", read_app_version())
bundle_id = os.environ.get("VOXSCRIBE_BUNDLE_ID", "io.github.chaoliu-cl.voxscribe")
target_arch = os.environ.get("VOXSCRIBE_TARGET_ARCH") or None
codesign_identity = os.environ.get("VOXSCRIBE_CODESIGN_IDENTITY") or None
entitlements_file = os.environ.get("VOXSCRIBE_ENTITLEMENTS_FILE") or None

icon_env = os.environ.get("VOXSCRIBE_MAC_ICON")
icon_path = Path(icon_env) if icon_env else project_root / "assets" / "app.icns"
if not icon_path.exists():
    icon_path = None

assets_dir = project_root / "assets"
optional_datas = []
if assets_dir.exists():
    optional_datas.append((str(assets_dir), "assets"))

optional_datas += collect_data_files("faster_whisper")
hiddenimports = collect_submodules("matplotlib")


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
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=target_arch,
    codesign_identity=codesign_identity,
    entitlements_file=entitlements_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=app_name,
)

app = BUNDLE(
    coll,
    name=f"{app_name}.app",
    icon=str(icon_path) if icon_path else None,
    bundle_identifier=bundle_id,
    version=app_version,
    info_plist={
        "CFBundleDisplayName": app_name,
        "CFBundleName": app_name,
        "CFBundleShortVersionString": app_version,
        "CFBundleVersion": app_version,
        "LSApplicationCategoryType": "public.app-category.productivity",
        "NSHumanReadableCopyright": "Copyright 2025 Chao Liu",
        "NSPrincipalClass": "NSApplication",
    },
)

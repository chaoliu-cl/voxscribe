VoxScribe Windows Build

Build type: one-dir (folder with exe + dependencies)
Console output: enabled
Python baseline: 3.11 - 3.14

Quick start (PowerShell)
1) Open PowerShell in this folder
2) Run: .\\build_exe.ps1
3) Run: .\\build_installer.ps1

The build script installs runtime and packaging dependencies from
`requirements-build.txt`, including `pyinstaller`.

Output
- .\\dist\\VoxScribe\\VoxScribe.exe

Assets (recommended)
- Place icons and sample data under .\\assets\\ and they will be bundled automatically.
- Example structure:
  assets\\app.ico
  assets\\samples\\example.wav
  assets\\splash.png
  (splash screen used at startup if present)

Icons
- Place the .ico at assets\\app.ico (used by both PyInstaller and the installer).

Models
- Do not bundle Whisper models by default (very large). Prefer first-run download to the cache
  (your code uses ~/.cache/voxscribe). If you want offline distribution later, provide a separate
  model pack and let the app detect it at startup.

Installer (Inno Setup)
- Install Inno Setup 6: https://jrsoftware.org/isdl.php
- Build installer: .\build_installer.ps1
- The script auto-detects `ISCC.exe` from PATH or common install locations and
  syncs the installer version from `__version__`.
- Output: .\Output\VoxScribe-Setup.exe

Microsoft Store (MSIX)
- Build the app first: .\build_exe.ps1
- Add required PNG assets under packaging\msix\assets (see packaging\msix\ASSETS_README.txt)
- Build MSIX: .\build_msix.ps1 -Publisher "CN=YOUR_PUBLISHER_ID" -PackageName "YOUR.PACKAGE.NAME"
- The MSIX version defaults to the package `__version__` with a trailing `.0`.
- For Store submission, use your Partner Center publisher ID and sign the MSIX.

VoxScribe Windows Build

Build type: one-dir (folder with exe + dependencies)
Console output: enabled

Quick start (PowerShell)
1) Open PowerShell in this folder
2) Run: .\\build_exe.ps1

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
- Output: .\Output\VoxScribe-Setup.exe

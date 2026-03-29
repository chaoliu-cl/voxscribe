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
- Build MSIX: .\build_msix.ps1
- Defaults are preconfigured for the VoxScribe Partner Center identity:
  Name=`ChaoLiu.VoxScribe`, Publisher=`CN=BF3179B5-D0C9-4D45-9E32-48C896F13BDB`,
  PublisherDisplayName=`Chao Liu`
- The MSIX version defaults to the package `__version__` with a trailing `.0`.
- If you do not pass `-CertPath`, the script creates or reuses a matching self-signed code-signing
  certificate in `CurrentUser\My`, signs the package, and exports the public `.cer` beside the MSIX assets.
- Output: .\dist\ChaoLiu.VoxScribe.msix and .\dist\ChaoLiu.VoxScribe.msixupload

macOS Universal Installer

Build type: native arm64 app + native x86_64 app wrapped in one .pkg installer
Python baseline: 3.11 - 3.14

Why this layout
- The VoxScribe dependency stack includes native extensions that are not always available as
  universal2 wheels.
- Instead of forcing a single universal2 .app, the macOS packaging flow builds a native app for
  Apple Silicon and a native app for Intel, then creates one installer package that automatically
  installs the correct payload for the current Mac.

Prerequisites
- macOS with the Command Line Tools installed (`iconutil`, `pkgbuild`, `productbuild`, `sips`)
- On Apple Silicon, Rosetta 2 installed for the Intel build:
  softwareupdate --install-rosetta
- A python.org-style universal2 Python is recommended when you want the same interpreter path to
  drive both architectures.

Quick start (Terminal)
1) Open Terminal in this folder
2) Run: chmod +x ./build_macos_universal.sh
3) Run: ./build_macos_universal.sh

Useful options
- `--python /path/to/python3`
  Uses the same interpreter path for both architectures.
- `--codesign-identity "Developer ID Application: ..."`
  Signs the `.app` bundles during the PyInstaller build.
- `--installer-sign-identity "Developer ID Installer: ..."`
  Signs the final `.pkg`.
- `--entitlements-file /path/to/entitlements.plist`
  Applies custom entitlements when signing the `.app` bundles.
- `--arm64-app /path/to/VoxScribe.app`
- `--x86_64-app /path/to/VoxScribe.app`
  Reuse prebuilt app bundles instead of building both locally.

Output
- `./dist/VoxScribe-macOS-universal.pkg`
- `./dist/macos/arm64/VoxScribe.app`
- `./dist/macos/x86_64/VoxScribe.app`

Notes
- The default bundle identifier is `io.github.chaoliu-cl.voxscribe`. Override it with
  `--bundle-id` if you need a different identifier for signing or distribution.
- If Intel wheels are unavailable for your chosen Python version, switch to a Python release with
  matching arm64 and x86_64 wheels for your dependencies.

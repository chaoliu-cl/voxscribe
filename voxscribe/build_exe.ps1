Param(
    [string]$Python = "python",
    [string]$Spec = "voxscribe.spec"
)

$ErrorActionPreference = "Stop"

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install pyinstaller

& $Python -m PyInstaller $Spec
Write-Host "Build complete. Output in .\\dist\\VoxScribe" -ForegroundColor Green

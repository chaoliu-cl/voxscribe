Param(
    [string]$Python = "python",
    [string]$Spec = "voxscribe.spec",
    [string]$SignToolPath = "",
    [string]$PfxPath = "",
    [string]$PfxPassword = "",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install pyinstaller

& $Python -m PyInstaller $Spec

if ($SignToolPath -and $PfxPath -and $PfxPassword) {
    $exePath = Join-Path (Join-Path (Get-Location) "dist\\VoxScribe") "VoxScribe.exe"
    if (Test-Path $exePath) {
        & $SignToolPath sign /f $PfxPath /p $PfxPassword /fd SHA256 /tr $TimestampUrl /td SHA256 $exePath
    } else {
        Write-Warning "Executable not found for signing: $exePath"
    }
}

Write-Host "Build complete. Output in .\\dist\\VoxScribe" -ForegroundColor Green

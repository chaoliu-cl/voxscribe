Param(
    [string]$InnoSetupPath = "C:\\Users\\psych\\Downloads\\InnoSetup\\ISCC.exe"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $InnoSetupPath)) {
    throw "Inno Setup not found at: $InnoSetupPath"
}

& $InnoSetupPath installer.iss
Write-Host "Installer build complete. Output in .\\Output" -ForegroundColor Green

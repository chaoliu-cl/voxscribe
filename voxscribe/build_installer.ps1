Param(
    [string]$InnoSetupPath = "C:\\Users\\psych\\Downloads\\InnoSetup\\ISCC.exe",
    [string]$SignToolPath = "",
    [string]$PfxPath = "",
    [string]$PfxPassword = "",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $InnoSetupPath)) {
    throw "Inno Setup not found at: $InnoSetupPath"
}

$argsList = @("installer.iss")
if ($SignToolPath -and $PfxPath -and $PfxPassword) {
    $argsList += "/DSignToolPath=$SignToolPath"
    $argsList += "/DSignPfxPath=$PfxPath"
    $argsList += "/DSignPfxPassword=$PfxPassword"
    $argsList += "/DSignTimestampUrl=$TimestampUrl"
}

& $InnoSetupPath @argsList
Write-Host "Installer build complete. Output in .\\Output" -ForegroundColor Green

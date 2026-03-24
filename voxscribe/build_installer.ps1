Param(
    [string]$InnoSetupPath = "",
    [string]$SignToolPath = "",
    [string]$PfxPath = "",
    [string]$PfxPassword = "",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

function Get-AppVersion {
    $versionFile = Join-Path $PSScriptRoot "__init__.py"
    $match = Select-String -Path $versionFile -Pattern '__version__\s*=\s*"([^"]+)"'
    if ($match -and $match.Matches.Count -gt 0) {
        return $match.Matches[0].Groups[1].Value
    }

    throw "Unable to determine application version from: $versionFile"
}

function Resolve-InnoSetupCompiler {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        if (Test-Path $RequestedPath) {
            return $RequestedPath
        }

        throw "Inno Setup not found at: $RequestedPath"
    }

    $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $commonPaths = @(
        "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 6\\ISCC.exe",
        (Join-Path $env:LOCALAPPDATA "Programs\\Inno Setup 6\\ISCC.exe"),
        "C:\\Users\\psych\\Downloads\\InnoSetup\\ISCC.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    throw "Inno Setup compiler not found. Install Inno Setup 6 or pass -InnoSetupPath."
}

$resolvedInnoSetupPath = Resolve-InnoSetupCompiler -RequestedPath $InnoSetupPath
$appVersion = Get-AppVersion
$distDir = Join-Path $PSScriptRoot "dist\\VoxScribe"

if (!(Test-Path $distDir)) {
    throw "Build output not found: $distDir. Run .\\build_exe.ps1 first."
}

$argsList = @("/DMyAppVersion=$appVersion", "installer.iss")
if ($SignToolPath -and $PfxPath -and $PfxPassword) {
    $argsList += "/DSignToolPath=$SignToolPath"
    $argsList += "/DSignPfxPath=$PfxPath"
    $argsList += "/DSignPfxPassword=$PfxPassword"
    $argsList += "/DSignTimestampUrl=$TimestampUrl"
}

Push-Location $PSScriptRoot
try {
    & $resolvedInnoSetupPath @argsList
    Write-Host "Installer build complete for version $appVersion. Output in .\\Output" -ForegroundColor Green
}
finally {
    Pop-Location
}

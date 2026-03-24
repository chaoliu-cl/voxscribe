Param(
    [string]$InputDir = ".\\dist\\VoxScribe",
    [string]$OutputMsix = ".\\dist\\VoxScribe.msix",
    [string]$PackageName = "VoxScribe",
    [string]$DisplayName = "VoxScribe",
    [string]$Publisher = "CN=YOUR_PUBLISHER_ID",
    [string]$PublisherDisplayName = "YOUR_PUBLISHER",
    [string]$Version = "",
    [string]$WindowsSdkBin = "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64",
    [string]$CertPath = "",
    [string]$CertPassword = ""
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

Push-Location $PSScriptRoot
try {
    if (-not $Version) {
        $Version = "$(Get-AppVersion).0"
    }

    $makeappx = Join-Path $WindowsSdkBin "makeappx.exe"
    $signtool = Join-Path $WindowsSdkBin "signtool.exe"

    if (!(Test-Path $makeappx)) {
        throw "makeappx.exe not found at: $makeappx"
    }

    if (!(Test-Path $InputDir)) {
        throw "Input folder not found: $InputDir"
    }

    $manifestTemplate = ".\\packaging\\msix\\AppxManifest.template.xml"
    if (!(Test-Path $manifestTemplate)) {
        throw "Manifest template not found: $manifestTemplate"
    }

    $assetsDir = ".\\packaging\\msix\\assets"
    if (!(Test-Path $assetsDir)) {
        throw "MSIX assets folder not found: $assetsDir (see packaging\\msix\\ASSETS_README.txt)"
    }

    $tempDir = New-Item -ItemType Directory -Force -Path ".\\packaging\\msix\\_build"

    Copy-Item -Recurse -Force $InputDir\\* $tempDir
    New-Item -ItemType Directory -Force -Path (Join-Path $tempDir "assets") | Out-Null
    Copy-Item -Recurse -Force $assetsDir\\* (Join-Path $tempDir "assets")

    $manifest = Get-Content $manifestTemplate -Raw
    $manifest = $manifest.Replace("__IDENTITY_NAME__", $PackageName)
    $manifest = $manifest.Replace("__DISPLAY_NAME__", $DisplayName)
    $manifest = $manifest.Replace("__PUBLISHER__", $Publisher)
    $manifest = $manifest.Replace("__PUBLISHER_DISPLAY__", $PublisherDisplayName)
    $manifest = $manifest.Replace("__VERSION__", $Version)
    Set-Content -Path (Join-Path $tempDir "AppxManifest.xml") -Value $manifest -Encoding UTF8

    & $makeappx pack /d $tempDir /p $OutputMsix /o

    if ($CertPath -and (Test-Path $CertPath)) {
        if ($CertPassword) {
            & $signtool sign /fd SHA256 /a /f $CertPath /p $CertPassword $OutputMsix
        } else {
            & $signtool sign /fd SHA256 /a /f $CertPath $OutputMsix
        }
        Write-Host "MSIX signed: $OutputMsix" -ForegroundColor Green
    } else {
        Write-Host "MSIX built (unsigned): $OutputMsix" -ForegroundColor Yellow
        Write-Host "For Microsoft Store submission, sign with your Partner Center certificate." -ForegroundColor Yellow
    }
}
finally {
    Pop-Location
}

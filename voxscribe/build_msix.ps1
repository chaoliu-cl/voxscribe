Param(
    [string]$InputDir = ".\\dist\\VoxScribe",
    [string]$OutputMsix = ".\\dist\\ChaoLiu.VoxScribe.msix",
    [string]$OutputUpload = "",
    [string]$PackageName = "ChaoLiu.VoxScribe",
    [string]$DisplayName = "VoxScribe",
    [string]$Publisher = "CN=BF3179B5-D0C9-4D45-9E32-48C896F13BDB",
    [string]$PublisherDisplayName = "Chao Liu",
    [string]$Version = "",
    [string]$Architecture = "x64",
    [string]$WindowsSdkBin = "",
    [string]$CertPath = "",
    [string]$CertPassword = "",
    [switch]$SkipAutoCertificate
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

function Resolve-WindowsSdkBin {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        $makeappx = Join-Path $RequestedPath "makeappx.exe"
        $signtool = Join-Path $RequestedPath "signtool.exe"
        if ((Test-Path $makeappx) -and (Test-Path $signtool)) {
            return $RequestedPath
        }

        throw "Windows SDK tools not found in: $RequestedPath"
    }

    $sdkRoot = "C:\\Program Files (x86)\\Windows Kits\\10\\bin"
    if (!(Test-Path $sdkRoot)) {
        throw "Windows SDK bin folder not found: $sdkRoot"
    }

    $candidateDirs = Get-ChildItem $sdkRoot -Directory |
        Where-Object { $_.Name -match '^10\.' } |
        Sort-Object { [Version]$_.Name } -Descending

    foreach ($candidate in $candidateDirs) {
        $candidateBin = Join-Path $candidate.FullName "x64"
        $makeappx = Join-Path $candidateBin "makeappx.exe"
        $signtool = Join-Path $candidateBin "signtool.exe"
        if ((Test-Path $makeappx) -and (Test-Path $signtool)) {
            return $candidateBin
        }
    }

    throw "Unable to locate makeappx.exe and signtool.exe under: $sdkRoot"
}

function New-OrReusePackageCertificate {
    param(
        [string]$Subject,
        [string]$FriendlyName,
        [string]$CerPath
    )

    $existing = Get-ChildItem Cert:\CurrentUser\My |
        Where-Object { $_.Subject -eq $Subject -and $_.FriendlyName -eq $FriendlyName } |
        Sort-Object NotAfter -Descending |
        Select-Object -First 1

    if (-not $existing) {
        $existing = New-SelfSignedCertificate `
            -Type Custom `
            -Subject $Subject `
            -FriendlyName $FriendlyName `
            -CertStoreLocation "Cert:\CurrentUser\My" `
            -KeyAlgorithm RSA `
            -KeyLength 2048 `
            -KeyExportPolicy Exportable `
            -HashAlgorithm SHA256 `
            -KeyUsage DigitalSignature `
            -TextExtension @(
                "2.5.29.37={text}1.3.6.1.5.5.7.3.3"
            ) `
            -NotAfter (Get-Date).AddYears(3)
    }

    Export-Certificate -Cert $existing -FilePath $CerPath -Force | Out-Null
    return $existing
}

function New-MsixUploadArchive {
    param(
        [string]$MsixPath,
        [string]$UploadPath
    )

    $zipPath = [System.IO.Path]::ChangeExtension($UploadPath, ".zip")
    if (Test-Path $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    Compress-Archive -LiteralPath $MsixPath -DestinationPath $zipPath -Force
    Move-Item -LiteralPath $zipPath -Destination $UploadPath -Force
}

function Assert-LastExitCode {
    param([string]$Action)

    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE"
    }
}

Push-Location $PSScriptRoot
try {
    if (-not $Version) {
        $Version = "$(Get-AppVersion).0"
    }

    if (-not $OutputUpload) {
        $OutputUpload = [System.IO.Path]::ChangeExtension($OutputMsix, ".msixupload")
    }

    $resolvedSdkBin = Resolve-WindowsSdkBin -RequestedPath $WindowsSdkBin
    $makeappx = Join-Path $resolvedSdkBin "makeappx.exe"
    $signtool = Join-Path $resolvedSdkBin "signtool.exe"

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

    $outputMsixDir = Split-Path -Parent $OutputMsix
    if ($outputMsixDir) {
        New-Item -ItemType Directory -Force -Path $outputMsixDir | Out-Null
    }

    $outputUploadDir = Split-Path -Parent $OutputUpload
    if ($outputUploadDir) {
        New-Item -ItemType Directory -Force -Path $outputUploadDir | Out-Null
    }

    $tempDir = Join-Path $PSScriptRoot "packaging\\msix\\_build"
    if (Test-Path $tempDir) {
        Remove-Item -LiteralPath $tempDir -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    Copy-Item -Recurse -Force (Join-Path $InputDir "*") $tempDir
    New-Item -ItemType Directory -Force -Path (Join-Path $tempDir "assets") | Out-Null
    Copy-Item -Recurse -Force (Join-Path $assetsDir "*") (Join-Path $tempDir "assets")

    $manifest = Get-Content $manifestTemplate -Raw
    $manifest = $manifest.Replace("__IDENTITY_NAME__", $PackageName)
    $manifest = $manifest.Replace("__DISPLAY_NAME__", $DisplayName)
    $manifest = $manifest.Replace("__PUBLISHER__", $Publisher)
    $manifest = $manifest.Replace("__PUBLISHER_DISPLAY__", $PublisherDisplayName)
    $manifest = $manifest.Replace("__VERSION__", $Version)
    $manifest = $manifest.Replace("__PROCESSOR_ARCHITECTURE__", $Architecture)
    Set-Content -Path (Join-Path $tempDir "AppxManifest.xml") -Value $manifest -Encoding UTF8

    if (Test-Path $OutputMsix) {
        Remove-Item -LiteralPath $OutputMsix -Force
    }
    if (Test-Path $OutputUpload) {
        Remove-Item -LiteralPath $OutputUpload -Force
    }

    & $makeappx pack /d $tempDir /p $OutputMsix /o
    Assert-LastExitCode -Action "MSIX packaging"

    if ($CertPath -and (Test-Path $CertPath)) {
        if ($CertPassword) {
            & $signtool sign /fd SHA256 /a /f $CertPath /p $CertPassword $OutputMsix
        }
        else {
            & $signtool sign /fd SHA256 /a /f $CertPath $OutputMsix
        }
        Assert-LastExitCode -Action "MSIX signing"
        Write-Host "MSIX signed with certificate file: $OutputMsix" -ForegroundColor Green
    }
    elseif (-not $SkipAutoCertificate) {
        $certificateName = "$PackageName Store Signing"
        $certificatePath = Join-Path $PSScriptRoot "packaging\\msix\\$PackageName.cer"
        $certificate = New-OrReusePackageCertificate -Subject $Publisher -FriendlyName $certificateName -CerPath $certificatePath
        & $signtool sign /fd SHA256 /sha1 $certificate.Thumbprint /s My $OutputMsix
        Assert-LastExitCode -Action "MSIX signing"
        Write-Host "MSIX signed with generated CurrentUser certificate: $OutputMsix" -ForegroundColor Green
        Write-Host "Public certificate exported to: $certificatePath" -ForegroundColor Green
    }
    else {
        Write-Host "MSIX built (unsigned): $OutputMsix" -ForegroundColor Yellow
        Write-Host "Pass -CertPath or omit -SkipAutoCertificate to sign it." -ForegroundColor Yellow
    }

    New-MsixUploadArchive -MsixPath $OutputMsix -UploadPath $OutputUpload
    Write-Host "Store submission archive ready: $OutputUpload" -ForegroundColor Green
}
finally {
    Pop-Location
}

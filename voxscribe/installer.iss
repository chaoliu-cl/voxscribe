#define MyAppName "VoxScribe"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppPublisher "VoxScribe"
#define MyAppExeName "VoxScribe.exe"
#define SignToolPath ""
#define SignPfxPath ""
#define SignPfxPassword ""
#define SignTimestampUrl "http://timestamp.digicert.com"

[Setup]
AppId={{D7B0F1C4-4D2E-4F5B-9C4C-5C0C1E7C1A10}
AppName={#MyAppName}
AppVerName={#MyAppName} {#MyAppVersion}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/chaoliu-cl/voxscribe
AppSupportURL=https://github.com/chaoliu-cl/voxscribe/issues
AppUpdatesURL=https://github.com/chaoliu-cl/voxscribe/releases
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultDirName={autopf64}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=VoxScribe-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoDescription=VoxScribe Installer
#if SignToolPath != ""
SignTool=mysig
SignedUninstaller=yes
#endif

[SignTools]
#if SignToolPath != ""
Name: "mysig"; Command: """{#SignToolPath}"" sign /f ""{#SignPfxPath}"" /p ""{#SignPfxPassword}"" /fd SHA256 /tr ""{#SignTimestampUrl}"" /td SHA256 $f"
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
#if SignToolPath != ""
Source: "dist\VoxScribe\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; SignTool: "mysig"
#else
Source: "dist\VoxScribe\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

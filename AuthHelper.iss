
#define MyAppName "Auth Helper"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Auth Helper"

[Setup]
AppId={{B7D0B6C8-82F5-4C2C-AFC4-5E66C7F13A91}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\Programs\AuthHelper
DefaultGroupName=Auth Helper

OutputDir=installer
OutputBaseFilename=AuthHelperSetup

PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

Compression=lzma
SolidCompression=yes

WizardStyle=modern
ChangesEnvironment=yes

Uninstallable=yes

[Files]
Source: "dist\AuthHelper\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "auth.cmd"; DestDir: "{app}"

[Code]

function PathContainsEntry(PathList, Entry: String): Boolean;
var
  Remaining: String;
  Current: String;
  SeparatorPos: Integer;
begin
  Result := False;
  Remaining := PathList;

  while Remaining <> '' do
  begin
    SeparatorPos := Pos(';', Remaining);

    if SeparatorPos > 0 then
    begin
      Current := Copy(Remaining, 1, SeparatorPos - 1);
      Delete(Remaining, 1, SeparatorPos);
    end
    else
    begin
      Current := Remaining;
      Remaining := '';
    end;

    Current := Trim(Current);

    if CompareText(Current, Entry) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;


procedure AddToPath(Entry: String);
var
  ExistingPath: String;
  NewPath: String;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', ExistingPath) then
    ExistingPath := '';

  if not PathContainsEntry(ExistingPath, Entry) then
  begin
    if ExistingPath = '' then
      NewPath := Entry
    else
      NewPath := ExistingPath + ';' + Entry;

    RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', NewPath);
  end;
end;


procedure RemoveFromPath(Entry: String);
var
  ExistingPath: String;
  Remaining: String;
  Current: String;
  SeparatorPos: Integer;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', ExistingPath) then
    Exit;

  Remaining := ExistingPath;
  ExistingPath := '';

  while Remaining <> '' do
  begin
    SeparatorPos := Pos(';', Remaining);

    if SeparatorPos > 0 then
    begin
      Current := Copy(Remaining, 1, SeparatorPos - 1);
      Delete(Remaining, 1, SeparatorPos);
    end
    else
    begin
      Current := Remaining;
      Remaining := '';
    end;

    Current := Trim(Current);

    if (Current <> '') and (CompareText(Current, Entry) <> 0) then
    begin
      if ExistingPath = '' then
        ExistingPath := Current
      else
        ExistingPath := ExistingPath + ';' + Current;
    end;
  end;

  RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', ExistingPath);
end;


procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    AddToPath(ExpandConstant('{app}'));
  end;
end;


procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    RemoveFromPath(ExpandConstant('{app}'));
  end;
end;

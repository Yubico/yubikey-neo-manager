!include "MUI2.nsh"

!define MUI_ICON "neoman.ico"

; The name of the installer
Name "YubiKey NEO Manager"

; The file to write
OutFile "../dist/yubikey-neo-manager-${NEOMAN_VERSION}.exe"

; The default installation directory
InstallDir "$PROGRAMFILES\Yubico\YubiKey NEO Manager"

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\Yubico\yubikey-neo-manager" "Install_Dir"

SetCompressor /SOLID lzma
ShowInstDetails show

Var MUI_TEMP
Var STARTMENU_FOLDER

;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------

; Pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_DEFAULTFOLDER "Yubico\YubiKey NEO Manager"
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Yubico\YubiKey NEO Manager"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;Languages
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------

Section "YubiKey NEO Manager"
  SectionIn RO
  SetOutPath $INSTDIR
  FILE "..\dist\YubiKey NEO Manager\*"
SectionEnd

Var MYTMP

# Last section is a hidden one.
Section
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Write the installation path into the registry
  WriteRegStr HKLM "Software\Yubico\yubikey-neo-manager" "Install_Dir" "$INSTDIR"

  # Windows Add/Remove Programs support
  StrCpy $MYTMP "Software\Microsoft\Windows\CurrentVersion\Uninstall\yubikey-neo-manager"
  WriteRegStr       HKLM $MYTMP "DisplayName"     "YubiKey NEO Manager"
  WriteRegExpandStr HKLM $MYTMP "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegExpandStr HKLM $MYTMP "InstallLocation" "$INSTDIR"
  WriteRegStr       HKLM $MYTMP "DisplayVersion"  "${NEOMAN_VERSION}"
  WriteRegStr       HKLM $MYTMP "Publisher"       "Yubico AB"
  WriteRegStr       HKLM $MYTMP "URLInfoAbout"    "http://www.yubico.com"
  WriteRegDWORD     HKLM $MYTMP "NoModify"        "1"
  WriteRegDWORD     HKLM $MYTMP "NoRepair"        "1"

!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
;Create shortcuts
  SetShellVarContext all
  SetOutPath "$SMPROGRAMS\$STARTMENU_FOLDER"
  CreateShortCut "YubiKey NEO Manager.lnk" "$INSTDIR\YubiKey NEO Manager.exe" "" "$INSTDIR\YubiKey NEO Manager.exe" 0
  CreateShortCut "Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 1
  WriteINIStr "$SMPROGRAMS\$STARTMENU_FOLDER\Yubico Web page.url" \
                   "InternetShortcut" "URL" "http://www.yubico.com/"
!insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\yubikey-neo-manager"
  DeleteRegKey HKLM "Software\Yubico\yubikey-neo-manager"

  ; Remove all
  DELETE "$INSTDIR\*"

  ; Remove shortcuts, if any
  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
  SetShellVarContext all

  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\Yubico Web page.url"
  Delete "$SMPROGRAMS\$MUI_TEMP\YubiKey NEO Manager.lnk"

  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"

  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."

    IfErrors startMenuDeleteLoopDone

    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey /ifempty HKCU "Software\Yubico\yubikey-neo-manager"

  ; Remove directories used
  RMDir "$INSTDIR"
SectionEnd

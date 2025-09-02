@echo off
REM WSMD Windows Installation Script
REM This script downloads and installs the appropriate WSMD executables 
REM from the GitHub releases page at https://github.com/Ragavaraaj/wsmd

echo ======================================
echo WSMD Installation Script for Windows
echo ======================================
echo Repository: https://github.com/Ragavaraaj/wsmd
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\wsmd
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo Installing to: %INSTALL_DIR%

REM Check for PowerShell
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: PowerShell is required for this installation script.
    exit /b 1
)

REM Determine the latest version
echo Looking for latest release...
for /f "tokens=*" %%a in ('powershell -Command "(Invoke-RestMethod -Uri https://api.github.com/repos/Ragavaraaj/wsmd/releases/latest).tag_name"') do set VERSION=%%a

if "%VERSION%"=="" (
    echo Error: Could not determine latest version
    exit /b 1
)

echo Using version: %VERSION%
echo Fetching release information...

REM Get the download URLs
for /f "tokens=*" %%a in ('powershell -Command "$release = Invoke-RestMethod -Uri \"https://api.github.com/repos/Ragavaraaj/wsmd/releases/tags/%VERSION%\"; $release.assets | Where-Object { $_.name -eq \"wsmd.exe\" } | Select-Object -ExpandProperty browser_download_url"') do set SERVER_URL=%%a
for /f "tokens=*" %%a in ('powershell -Command "$release = Invoke-RestMethod -Uri \"https://api.github.com/repos/Ragavaraaj/wsmd/releases/tags/%VERSION%\"; $release.assets | Where-Object { $_.name -eq \"wsmd_dashboard.exe\" } | Select-Object -ExpandProperty browser_download_url"') do set DASHBOARD_URL=%%a

if "%SERVER_URL%"=="" (
    echo Error: Could not find server executable in the release.
    exit /b 1
)

if "%DASHBOARD_URL%"=="" (
    echo Error: Could not find dashboard executable in the release.
    exit /b 1
)

REM Download server
echo Downloading WSMD Server...
powershell -Command "Invoke-WebRequest -Uri \"%SERVER_URL%\" -OutFile \"wsmd.exe\""
echo ✓ Downloaded server: wsmd.exe

REM Download dashboard
echo Downloading WSMD Dashboard...
powershell -Command "Invoke-WebRequest -Uri \"%DASHBOARD_URL%\" -OutFile \"wsmd_dashboard.exe\""
echo ✓ Downloaded dashboard: wsmd_dashboard.exe

REM Create desktop shortcuts
echo Creating desktop shortcuts...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$env:USERPROFILE\Desktop\WSMD Server.lnk\"); $Shortcut.TargetPath = \"%INSTALL_DIR%\wsmd.exe\"; $Shortcut.Save()"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$env:USERPROFILE\Desktop\WSMD Dashboard.lnk\"); $Shortcut.TargetPath = \"%INSTALL_DIR%\wsmd_dashboard.exe\"; $Shortcut.Save()"

echo.
echo ======================================
echo Installation complete!
echo ======================================
echo.
echo WSMD Server and Dashboard have been installed to: %INSTALL_DIR%
echo.
echo To start the server:
echo   Double-click the "WSMD Server" shortcut on your desktop
echo   Or navigate to %INSTALL_DIR% and run wsmd.exe
echo.
echo To start the dashboard:
echo   Double-click the "WSMD Dashboard" shortcut on your desktop
echo   Or navigate to %INSTALL_DIR% and run wsmd_dashboard.exe
echo.
echo Note: The server runs on port 8000 by default
echo Access the web interface at: http://localhost:8000
echo.

pause

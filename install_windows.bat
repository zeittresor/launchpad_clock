@echo off
setlocal EnableExtensions
REM Original source / updates: https://github.com/zeittresor
REM Project: Launchpad Clock
REM License: MIT

set "APP_NAME=Launchpad Clock"
set "APP_VERSION=0.9.4"

title %APP_NAME% v%APP_VERSION% - Installer

echo.
echo ============================================================
echo   %APP_NAME% v%APP_VERSION% - Windows Installer
echo ============================================================
echo.
echo Installing version: v%APP_VERSION%
echo.

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set PY=py -3
) else (
    where python >nul 2>nul
    if %ERRORLEVEL%==0 (
        set PY=python
    ) else (
        echo [ERROR] Python was not found.
        echo Please install Python 3.10+ and enable "Add Python to PATH".
        pause
        exit /b 1
    )
)

if not exist ".venv" (
    echo [1/4] Creating local virtual environment for %APP_NAME% v%APP_VERSION%...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] The virtual environment could not be created.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Local virtual environment already exists.
)

echo [2/4] Updating pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo [3/4] Installing dependencies for %APP_NAME% v%APP_VERSION%...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    echo Check your internet connection or install manually:
    echo .venv\Scripts\python.exe -m pip install PyQt6 mido python-rtmidi
    pause
    exit /b 1
)

echo [4/4] %APP_NAME% v%APP_VERSION% installation completed.
echo.
echo The GUI also starts without a connected Launchpad-style controller in live preview mode.
echo.
echo The app will start automatically in 10 seconds unless you choose N.
choice /C YN /N /T 10 /D Y /M "Start the app now? [Y/N] "
if errorlevel 2 (
    echo Start cancelled. You can run run_gui.bat later.
    exit /b 0
)

start "" "%~dp0run_gui.bat"
exit /b 0

@echo off
setlocal EnableExtensions
title Launchpad Clock v0.9.4
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment is missing. Starting installer...
    call install_windows.bat
)

echo Starting Launchpad Clock v0.9.4...
.venv\Scripts\python.exe -m launchpad_clock.gui_app
if errorlevel 1 (
    echo.
    echo [ERROR] The GUI exited with an error.
    pause
)

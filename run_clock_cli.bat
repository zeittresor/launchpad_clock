@echo off
setlocal EnableExtensions
title Launchpad Clock CLI v0.9.4
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment is missing. Starting installer...
    call install_windows.bat
)

.venv\Scripts\python.exe -m launchpad_clock
pause

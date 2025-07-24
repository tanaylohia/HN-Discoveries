@echo off
echo Starting HN Discoveries Dashboard...
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Run the deployment script
py deploy_local.py

pause
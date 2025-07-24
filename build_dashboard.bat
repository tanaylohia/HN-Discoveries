@echo off
echo Building Modern Dashboard...
echo.

cd modern-dashboard

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist node_modules (
    echo Installing dependencies...
    npm install
)

REM Build the dashboard
echo Building production version...
npm run build

echo.
echo [OK] Build complete! Files are in modern-dashboard/dist/
echo.
echo To deploy, copy the contents of modern-dashboard/dist/ to your web server.
pause
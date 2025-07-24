@echo off
echo Starting Modern Dashboard...
echo.

cd modern-dashboard

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

REM Copy latest data
echo Copying latest data...
if exist ..\reports\latest.json (
    if not exist reports mkdir reports
    copy ..\reports\latest.json reports\latest.json >nul
    echo [OK] Data copied
) else (
    echo [WARNING] No data found. Run 'py main.py --run-once' first.
)

echo.
echo Starting development server...
echo The dashboard will open in your browser automatically.
echo.

REM Start the dev server
call npm run dev
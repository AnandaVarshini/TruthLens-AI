@echo off
REM TruthLens AI - start the React frontend on http://localhost:5173
REM Run this from the project root (double-click or: start_frontend.bat)

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo node_modules not found - running npm install first...
    call npm install
    if errorlevel 1 (
        echo npm install failed. Check that Node.js is installed and on PATH.
        pause
        exit /b 1
    )
)

echo Starting TruthLens AI frontend on http://localhost:5173
echo The backend must also be running on http://localhost:8000
echo Press Ctrl+C to stop.
echo.

call npm run dev

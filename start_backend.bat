@echo off
REM TruthLens AI - start the FastAPI backend on http://localhost:8000
REM Run this from the project root (double-click or: start_backend.bat)

cd /d "%~dp0backend"

if exist "..\.venv\Scripts\python.exe" (
    set "PY=..\.venv\Scripts\python.exe"
) else if exist "..\venv\Scripts\python.exe" (
    set "PY=..\venv\Scripts\python.exe"
) else (
    set "PY=python"
)

echo Starting TruthLens AI backend with %PY%
echo API docs: http://localhost:8000/docs
echo Press Ctrl+C to stop.
echo.

"%PY%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

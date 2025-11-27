@echo off
REM CulinaAI Backend Server Startup Script
REM This script starts the FastAPI backend server for CulinaAI

echo.
echo ========================================
echo CulinaAI Backend Server
echo ========================================
echo.
echo Starting FastAPI server...
echo.

cd /d "C:\Users\Mega Pc\CulinaAI"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start the server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

REM If the above fails, show helpful message
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start server
    echo.
    echo Make sure:
    echo 1. Virtual environment is set up: .venv
    echo 2. All packages installed: pip install -r requirements.txt
    echo 3. Port 8000 is available
    echo.
    pause
)

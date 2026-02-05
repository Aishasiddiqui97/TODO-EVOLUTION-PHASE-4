@echo off
REM Start Chat API Server - Phase V MVP
REM Run this script to start the FastAPI server locally

echo.
echo ========================================
echo   Event-Driven Todo Chatbot - Chat API
echo ========================================
echo.

cd /d "%~dp0backend"

echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

echo.
echo Checking environment configuration...
if not exist .env (
    echo WARNING: .env file not found
    echo Creating from template...
    copy .env.example .env
    echo.
    echo Please edit backend\.env and add your OPENAI_API_KEY
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo Starting Chat API server...
echo.
echo Server will be available at:
echo   - API: http://localhost:8001
echo   - Docs: http://localhost:8001/docs
echo   - Health: http://localhost:8001/health
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

pause

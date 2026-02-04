@echo off
echo ========================================
echo    PHASE 4 CHATBOT STARTUP SCRIPT
echo ========================================

echo.
echo [1/4] Starting PostgreSQL Database...
docker-compose up -d db
timeout /t 10

echo.
echo [2/4] Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
timeout /t 5

echo.
echo [3/4] Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo [4/4] Opening Browser...
timeout /t 10
start http://localhost:3000

echo.
echo ========================================
echo    PHASE 4 CHATBOT IS NOW RUNNING!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Database: localhost:5432
echo.
echo Press any key to exit...
pause
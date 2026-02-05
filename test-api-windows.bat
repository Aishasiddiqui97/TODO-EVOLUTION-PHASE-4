@echo off
REM Quick Test Script for Chat API
REM Tests all endpoints to verify the implementation

echo.
echo ========================================
echo   Testing Chat API Endpoints
echo ========================================
echo.

set BASE_URL=http://localhost:8001

echo Test 1: Health Check
echo ---------------------
curl -s %BASE_URL%/health
echo.
echo.

echo Test 2: Root Endpoint
echo ----------------------
curl -s %BASE_URL%/
echo.
echo.

echo Test 3: Create Task
echo --------------------
curl -s -X POST %BASE_URL%/api/v1/tasks ^
  -H "Content-Type: application/json" ^
  -d "{\"title\": \"Test Task from Windows\", \"priority\": \"high\", \"tags\": [\"test\"]}"
echo.
echo.

echo Test 4: List Tasks
echo -------------------
curl -s %BASE_URL%/api/v1/tasks
echo.
echo.

echo Test 5: Chat Endpoint
echo ----------------------
curl -s -X POST %BASE_URL%/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Show me my tasks\"}"
echo.
echo.

echo ========================================
echo   Tests Complete!
echo ========================================
echo.
echo To view API documentation, open:
echo   %BASE_URL%/docs
echo.

pause

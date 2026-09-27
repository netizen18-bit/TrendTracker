@echo off
echo ========================================================
echo   Starting ContentPulse Development Environment
echo ========================================================
echo.

start "ContentPulse Backend (FastAPI)" cmd /k "cd backend && venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"
start "ContentPulse Frontend (React Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo Backend running on http://127.0.0.1:8000
echo Frontend running on http://localhost:3000
echo Demo Testbed Blog on http://127.0.0.1:8000/demo/blog
echo.
pause

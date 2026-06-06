@echo off

REM Use the script directory as the base path and activate the backend venv reliably.
echo Starting Backend...
start "Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && python app.py"

timeout /t 3 > nul

echo Starting Frontend...
start "Frontend" cmd /k "cd /d "%~dp0frontend\exam-seating" && npm run dev"

echo Project Started!
pause
@echo off
echo Starting Through the Ages AI Coach...
echo.

REM Start the backend in a new window
start "TtA Coach - Backend" cmd /k "cd /d "%~dp0backend" && C:\Users\svenftw\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn main:app --reload --port 8000"

REM Give the backend a moment to start
timeout /t 2 /nobreak > nul

REM Start the frontend in a new window
start "TtA Coach - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser.
echo Close the two server windows to stop.
pause

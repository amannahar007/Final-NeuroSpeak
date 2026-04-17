@echo off
title NeuroSpeak Control Panel
echo ==============================================
echo      Starting NeuroSpeak Services...
echo ==============================================

:: Start Backend
echo [Backend] Starting setup...
cd backend
if not exist "venv" (
    echo [Backend] Creating virtual environment...
    python -m venv venv
    echo [Backend] Activating environment...
    call venv\Scripts\activate.bat
    echo [Backend] Installing requirements...
    pip install -r requirements.txt
) else (
    echo [Backend] Virtual environment exists.
)
echo [Backend] Launching FastAPI + SocketIO Server...
start "NeuroSpeak Backend" cmd /k "title NeuroSpeak Backend && call venv\Scripts\activate.bat && python main.py"
cd ..

:: Start Dashboard
echo [Dashboard] Starting setup...
cd dashboard
if not exist "node_modules" (
    echo [Dashboard] Installing dependencies...
    call npm install
) else (
    echo [Dashboard] Dependencies already installed.
)
echo [Dashboard] Launching Vite Development Server...
start "NeuroSpeak Dashboard" cmd /k "title NeuroSpeak Dashboard && npm run dev"
cd ..

echo ==============================================
echo      All services started automatically!
echo      (Please wait a few seconds for servers to fully load)
echo ==============================================
timeout /t 5 /nobreak > NUL
start http://localhost:3000

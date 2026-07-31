@echo off
REM AI Employee - Silver Tier
REM Start All Watchers and Orchestrator

echo ================================================
echo AI Employee - Silver Tier
echo Starting All Services
echo ================================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    pause
    exit /b 1
)

echo Starting File System Watcher...
start "File Watcher" python watchers\filesystem_watcher.py
timeout /t 2 >nul

echo Starting Gmail Watcher...
start "Gmail Watcher" python watchers\gmail_watcher.py
timeout /t 2 >nul

REM WhatsApp Watcher - Skip (not authenticated yet)
echo Skipping WhatsApp Watcher (not authenticated)
echo   To authenticate: python watchers\whatsapp_watcher.py
timeout /t 2 >nul

echo Starting LinkedIn Watcher...
start "LinkedIn Watcher" python watchers\linkedin_watcher.py
timeout /t 2 >nul

echo Starting Orchestrator...
start "Orchestrator" python orchestrator.py

echo.
echo ================================================
echo All services started!
echo ================================================
echo.
echo Running services:
echo   [OK] File System Watcher
echo   [OK] Gmail Watcher
echo   [OK] LinkedIn Watcher
echo   [OK] Orchestrator
echo   [--] WhatsApp Watcher (not authenticated)
echo.
echo Check individual terminal windows for status
echo.
echo To stop all services, close each terminal window
echo ================================================
echo.
pause

@echo off
REM Start Orchestrator for AI Employee Bronze Tier
REM This script starts the orchestrator that coordinates tasks

cd /d "%~dp0"

echo ================================================
echo AI Employee - Bronze Tier
echo Orchestrator
echo ================================================
echo.
echo Vault: %CD%\AI_Employee_Vault
echo Monitoring: Needs_Action folder
echo.
echo Press Ctrl+C to stop
echo.
echo Tip: Open another terminal to run the watcher too
echo.

python orchestrator.py

pause

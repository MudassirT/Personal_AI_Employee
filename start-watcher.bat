@echo off
REM Start File System Watcher for AI Employee Bronze Tier
REM This script starts the file watcher that monitors the Inbox folder

cd /d "%~dp0"

echo ================================================
echo AI Employee - Bronze Tier
echo File System Watcher
echo ================================================
echo.
echo Vault: %CD%\AI_Employee_Vault
echo Monitoring: Inbox folder
echo.
echo Press Ctrl+C to stop
echo.

python watchers\filesystem_watcher.py

pause

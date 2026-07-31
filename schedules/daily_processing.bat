@echo off
REM AI Employee - Daily Processing
REM Scheduled task to process Needs_Action folder

echo ================================================
echo AI Employee - Daily Processing
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Process Needs_Action folder once
python orchestrator.py --process-once

echo.
echo Processing complete.
echo ================================================

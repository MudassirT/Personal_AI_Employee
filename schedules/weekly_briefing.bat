@echo off
REM AI Employee - Weekly Briefing
REM Scheduled task to generate CEO briefing

echo ================================================
echo AI Employee - Weekly Briefing
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Generate CEO briefing from completed tasks
qwen --cwd "AI_Employee_Vault" "Review completed tasks from this week and generate a CEO briefing in Briefings/ folder"

echo.
echo Briefing generated.
echo ================================================

@echo off
REM AI Employee - Silver Tier Test Script
REM This script tests all Silver Tier components

echo ================================================================
echo AI Employee - Silver Tier Test
echo ================================================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [TEST 1/6] Checking folder structure...
if exist "AI_Employee_Vault\Dashboard.md" (
    echo [PASS] Dashboard.md exists
) else (
    echo [FAIL] Dashboard.md missing
)

if exist "AI_Employee_Vault\Needs_Action" (
    echo [PASS] Needs_Action folder exists
) else (
    echo [FAIL] Needs_Action folder missing
)

if exist "AI_Employee_Vault\Plans" (
    echo [PASS] Plans folder exists
) else (
    echo [FAIL] Plans folder missing
)

if exist "AI_Employee_Vault\Pending_Approval" (
    echo [PASS] Pending_Approval folder exists
) else (
    echo [FAIL] Pending_Approval folder missing
)

echo.
echo [TEST 2/6] Checking watchers...
if exist "watchers\filesystem_watcher.py" (
    echo [PASS] File System Watcher exists
) else (
    echo [FAIL] File System Watcher missing
)

if exist "watchers\gmail_watcher.py" (
    echo [PASS] Gmail Watcher exists
) else (
    echo [FAIL] Gmail Watcher missing
)

if exist "watchers\whatsapp_watcher.py" (
    echo [PASS] WhatsApp Watcher exists
) else (
    echo [FAIL] WhatsApp Watcher missing
)

if exist "watchers\linkedin_watcher.py" (
    echo [PASS] LinkedIn Watcher exists
) else (
    echo [FAIL] LinkedIn Watcher missing
)

echo.
echo [TEST 3/6] Checking authentication...
if exist "watchers\credentials.json" (
    echo [PASS] Gmail credentials.json exists
) else (
    echo [FAIL] Gmail credentials.json missing
)

if exist "watchers\token.json" (
    echo [PASS] Gmail token.json exists (authenticated)
) else (
    echo [FAIL] Gmail token.json missing (not authenticated)
)

if exist "watchers\linkedin_session\Default" (
    echo [PASS] LinkedIn session exists (authenticated)
) else (
    echo [FAIL] LinkedIn session missing (not authenticated)
)

echo.
echo [TEST 4/6] Checking skills...
if exist ".qwen\skills\browsing-with-playwright" (
    echo [PASS] browsing-with-playwright skill exists
) else (
    echo [FAIL] browsing-with-playwright skill missing
)

if exist ".qwen\skills\approval-workflow" (
    echo [PASS] approval-workflow skill exists
) else (
    echo [FAIL] approval-workflow skill missing
)

if exist ".qwen\skills\linkedin-poster" (
    echo [PASS] linkedin-poster skill exists
) else (
    echo [FAIL] linkedin-poster skill missing
)

if exist ".qwen\skills\scheduler" (
    echo [PASS] scheduler skill exists
) else (
    echo [FAIL] scheduler skill missing
)

echo.
echo [TEST 5/6] Quick watcher test (File System)...
echo Dropping test file in Inbox...
echo Test content - Silver Tier Test > AI_Employee_Vault\Inbox\test_silver_tier.txt
timeout /t 2 >nul

if exist "AI_Employee_Vault\Needs_Action\FILE_*.md" (
    echo [PASS] File watcher created action file
) else (
    echo [INFO] File watcher may need to run - check manually
)

echo.
echo [TEST 6/6] Checking orchestrator...
if exist "orchestrator.py" (
    echo [PASS] Orchestrator exists
) else (
    echo [FAIL] Orchestrator missing
)

echo.
echo ================================================================
echo Test Summary
echo ================================================================
echo.
echo To run full integration test:
echo   1. Start all watchers: start-silver-tier.bat
echo   2. Drop a file in: AI_Employee_Vault\Inbox\
echo   3. Check: AI_Employee_Vault\Needs_Action\
echo   4. Process with: qwen --cwd "AI_Employee_Vault" "Process Needs_Action"
echo.
echo Authentication Status:
echo   - Gmail: Check watchers\token.json
echo   - LinkedIn: Check watchers\linkedin_session\
echo   - WhatsApp: Run 'python watchers\whatsapp_watcher.py' to auth
echo.
echo ================================================================

pause

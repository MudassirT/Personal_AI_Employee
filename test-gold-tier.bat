@echo off
REM AI Employee - Gold Tier Test Suite
REM Tests all Gold Tier components

echo ================================================
echo AI Employee - Gold Tier Test Suite
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0"

set ERRORS=0

echo [1/10] Checking vault structure...
if exist "AI_Employee_Vault\Dashboard.md" (echo   PASS: Dashboard exists) else (echo   FAIL: Dashboard missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Inbox" (echo   PASS: Inbox exists) else (echo   FAIL: Inbox missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Needs_Action" (echo   PASS: Needs_Action exists) else (echo   FAIL: Needs_Action missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\In_Progress" (echo   PASS: In_Progress exists) else (echo   FAIL: In_Progress missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Pending_Approval" (echo   PASS: Pending_Approval exists) else (echo   FAIL: Pending_Approval missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Approved" (echo   PASS: Approved exists) else (echo   FAIL: Approved missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Rejected" (echo   PASS: Rejected exists) else (echo   FAIL: Rejected missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Done" (echo   PASS: Done exists) else (echo   FAIL: Done missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Plans" (echo   PASS: Plans exists) else (echo   FAIL: Plans missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Logs" (echo   PASS: Logs exists) else (echo   FAIL: Logs missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Odoo" (echo   PASS: Odoo exists) else (echo   FAIL: Odoo missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Social" (echo   PASS: Social exists) else (echo   FAIL: Social missing & set /a ERRORS+=1)
if exist "AI_Employee_Vault\Audits" (echo   PASS: Audits exists) else (echo   FAIL: Audits missing & set /a ERRORS+=1)

echo.
echo [2/10] Checking watcher scripts...
if exist "watchers/filesystem_watcher.py" (echo   PASS: filesystem_watcher.py) else (echo   FAIL: filesystem_watcher.py missing & set /a ERRORS+=1)
if exist "watchers/gmail_watcher.py" (echo   PASS: gmail_watcher.py) else (echo   FAIL: gmail_watcher.py missing & set /a ERRORS+=1)
if exist "watchers/whatsapp_watcher.py" (echo   PASS: whatsapp_watcher.py) else (echo   FAIL: whatsapp_watcher.py missing & set /a ERRORS+=1)
if exist "watchers/linkedin_watcher.py" (echo   PASS: linkedin_watcher.py) else (echo   FAIL: linkedin_watcher.py missing & set /a ERRORS+=1)

echo.
echo [3/10] Checking Silver Tier skills...
if exist ".qwen\skills\approval-workflow\approval_workflow.py" (echo   PASS: approval-workflow skill) else (echo   FAIL: approval-workflow missing & set /a ERRORS+=1)
if exist ".qwen\skills\scheduler\scheduler.py" (echo   PASS: scheduler skill) else (echo   FAIL: scheduler skill missing & set /a ERRORS+=1)
if exist ".qwen\skills\linkedin-poster\linkedin_poster.py" (echo   PASS: linkedin-poster skill) else (echo   FAIL: linkedin-poster missing & set /a ERRORS+=1)
if exist ".qwen\skills\browsing-with-playwright" (echo   PASS: browsing-with-playwright skill) else (echo   FAIL: browsing-with-playwright missing & set /a ERRORS+=1)

echo.
echo [4/10] Checking Gold Tier skills...
if exist ".qwen\skills\facebook-instagram-poster\fb_ig_poster.py" (echo   PASS: facebook-instagram-poster skill) else (echo   FAIL: facebook-instagram-poster missing & set /a ERRORS+=1)
if exist ".qwen\skills\twitter-poster\twitter_poster.py" (echo   PASS: twitter-poster skill) else (echo   FAIL: twitter-poster missing & set /a ERRORS+=1)

echo.
echo [5/10] Checking MCP servers...
if exist "mcp-servers\email-sender\email_mcp_server.py" (echo   PASS: email-sender MCP) else (echo   FAIL: email-sender MCP missing & set /a ERRORS+=1)
if exist "mcp-servers\odoo-accounting\odoo_mcp_server.py" (echo   PASS: odoo-accounting MCP) else (echo   FAIL: odoo-accounting MCP missing & set /a ERRORS+=1)
if exist "mcp-servers\web-search\web_search_mcp.py" (echo   PASS: web-search MCP) else (echo   FAIL: web-search MCP missing & set /a ERRORS+=1)
if exist "mcp-servers\calendar\calendar_mcp.py" (echo   PASS: calendar MCP) else (echo   FAIL: calendar MCP missing & set /a ERRORS+=1)

echo.
echo [6/10] Checking orchestrator...
if exist "orchestrator.py" (echo   PASS: orchestrator.py) else (echo   FAIL: orchestrator.py missing & set /a ERRORS+=1)

echo.
echo [7/10] Checking error recovery module...
if exist "error_recovery.py" (echo   PASS: error_recovery.py) else (echo   FAIL: error_recovery.py missing & set /a ERRORS+=1)

echo.
echo [8/10] Checking audit logger...
if exist "audit_logger.py" (echo   PASS: audit_logger.py) else (echo   FAIL: audit_logger.py missing & set /a ERRORS+=1)

echo.
echo [9/10] Testing approval workflow...
python .qwen\skills\approval-workflow\approval_workflow.py --list-pending >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo   PASS: approval workflow runs) else (echo   FAIL: approval workflow error & set /a ERRORS+=1)

echo.
echo [10/10] Testing scheduler skill...
python .qwen\skills\scheduler\scheduler.py --list >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo   PASS: scheduler skill runs) else (echo   FAIL: scheduler skill error & set /a ERRORS+=1)

echo.
echo ================================================
if %ERRORS% EQU 0 (
    echo ALL TESTS PASSED! Gold Tier ready.
) else (
    echo TESTS FAILED: %ERRORS% error(s)
)
echo ================================================
echo.

if %ERRORS% GTR 0 exit /b 1
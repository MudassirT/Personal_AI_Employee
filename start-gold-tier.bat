@echo off
REM AI Employee - Gold Tier Startup
REM Starts all watchers, MCP servers, and the orchestrator with Ralph loop

echo ================================================
echo AI Employee - Gold Tier Startup
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0"

REM Check for required directories
if not exist "AI_Employee_Vault" (
    echo ERROR: AI_Employee_Vault not found!
    echo Run setup first.
    pause
    exit /b 1
)

echo Starting watchers...

REM Start filesystem watcher (always needed)
start "FileSystem Watcher" cmd /k python watchers/filesystem_watcher.py

REM Start Gmail watcher (if configured)
if exist "watchers/credentials.json" (
    start "Gmail Watcher" cmd /k python watchers/gmail_watcher.py
) else (
    echo WARNING: Gmail credentials not found. Skipping Gmail watcher.
)

REM Start WhatsApp watcher (if session exists)
if exist "watchers/whatsapp_session" (
    start "WhatsApp Watcher" cmd /k python watchers/whatsapp_watcher.py
) else (
    echo WARNING: WhatsApp session not found. Run auth first.
)

REM Start LinkedIn watcher (if session exists)
if exist "watchers/linkedin_session" (
    start "LinkedIn Watcher" cmd /k python watchers/linkedin_watcher.py
) else (
    echo WARNING: LinkedIn session not found. Run auth first.
)

echo.
echo Starting MCP servers...

REM Start Email MCP Server
start "Email MCP" cmd /k python mcp-servers/email-sender/email_mcp_server.py

REM Start Calendar MCP Server (if configured)
if exist "mcp-servers/calendar/credentials.json" (
    start "Calendar MCP" cmd /k python mcp-servers/calendar/calendar_mcp.py
) else (
    echo WARNING: Calendar credentials not found. Skipping Calendar MCP.
)

REM Start Odoo Accounting MCP (if configured)
if defined ODOO_URL (
    start "Odoo MCP" cmd /k python mcp-servers/odoo-accounting/odoo_mcp_server.py
) else (
    echo WARNING: ODOO_URL not set. Skipping Odoo MCP.
)

echo.
echo Starting Orchestrator with Ralph Wiggum Loop...

REM Start orchestrator in autonomous mode (50 iterations, 60s delay)
start "AI Employee Orchestrator" cmd /k python orchestrator.py --ralph-loop 50 --ralph-delay 60

echo.
echo ================================================
echo Gold Tier Started Successfully!
echo ================================================
echo.
echo Watchers running in separate windows.
echo Orchestrator running in autonomous mode.
echo.
echo Dashboard: AI_Employee_Vault/Dashboard.md
echo Logs: AI_Employee_Vault/Logs/
echo.
echo Press any key to close this window (watchers continue running)...
pause
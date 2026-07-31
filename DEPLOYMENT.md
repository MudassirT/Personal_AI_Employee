Deployment & Credentials Guide

Summary
-------
This document lists steps to deploy and authenticate the Silver Tier services:
- Watchers (File, Gmail, LinkedIn, WhatsApp)
- Orchestrator
- Email MCP server
- Scheduler

Quick Checklist
---------------
- [ ] Install Python 3.11+ and dependencies: `pip install -r requirements.txt`
- [ ] Install Playwright (if using LinkedIn/WhatsApp): `playwright install`
- [ ] Configure Gmail credentials (see `mcp-servers/email-sender/GET_CREDENTIALS.md`)
- [ ] Start Email MCP server: `python mcp-servers/email-sender/email_mcp_server.py`
- [ ] Authenticate WhatsApp: `python watchers/whatsapp_watcher.py` (scan QR)
- [ ] Authenticate LinkedIn: run the LinkedIn login script or run the watcher to capture session

Running services locally
------------------------
Start watchers:

```powershell
python watchers/filesystem_watcher.py
python watchers/gmail_watcher.py    # requires credentials.json in watchers/
python watchers/linkedin_watcher.py
python watchers/whatsapp_watcher.py # first-run: headless=False to scan QR
```

Start orchestrator:

```powershell
python orchestrator.py
```

Start Email MCP server:

```powershell
cd mcp-servers/email-sender
python email_mcp_server.py
```

Scheduler
---------
The repository includes `scripts/linkedin_scheduler.py` which can run daily
and post approved LinkedIn plans. To run once for testing:

```powershell
python scripts/linkedin_scheduler.py --once
```

Security
--------
- Never commit `credentials.json` or `token.json`.
- Use environment variables for SMTP credentials.
- Rotate credentials and monitor access logs.

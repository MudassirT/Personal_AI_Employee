# Silver Tier - Ready for Use!

## Quick Start

```bash
start-silver-tier.bat
```

This starts all **authenticated** watchers:
- ✅ File System Watcher
- ✅ Gmail Watcher
- ✅ LinkedIn Watcher
- ✅ Orchestrator

---

## What's Working

| Service | Status | Check Interval |
|---------|--------|----------------|
| **File System Watcher** | ✅ Ready | 30 seconds |
| **Gmail Watcher** | ✅ Ready | 2 minutes |
| **LinkedIn Watcher** | ✅ Ready | 15 minutes (headless) |
| **WhatsApp Watcher** | ⏳ Not Authenticated | - |
| **Orchestrator** | ✅ Ready | 1 minute |

---

## How to Use

### 1. Start All Services

Double-click:
```
start-silver-tier.bat
```

Or run manually:
```bash
python watchers\filesystem_watcher.py
python watchers\gmail_watcher.py
python watchers\linkedin_watcher.py
python orchestrator.py
```

### 2. Drop a File

Copy any file to:
```
AI_Employee_Vault\Inbox\your_file.txt
```

Within 30 seconds, an action file will be created in:
```
AI_Employee_Vault\Needs_Action\FILE_*.md
```

### 3. Check Gmail

The Gmail watcher automatically checks your unread emails every 2 minutes and creates:
```
AI_Employee_Vault\Needs_Action\EMAIL_*.md
```

### 4. Check LinkedIn

The LinkedIn watcher checks every 15 minutes (headless) for:
- Connection requests
- Messages
- Notifications

Creates:
```
AI_Employee_Vault\Needs_Action\LINKEDIN_*.md
```

### 5. Process with Qwen Code

```bash
qwen --cwd "AI_Employee_Vault" "Process all files in Needs_Action and create action plans"
```

---

## Current Action Items

Check what's waiting for processing:

```bash
dir AI_Employee_Vault\Needs_Action\*.md
```

You should see:
- `EMAIL_*.md` - From your Gmail unread emails
- `LINKEDIN_*.md` - From LinkedIn connection requests
- `FILE_*.md` - From file drops

---

## Authentication Status

| Service | Authenticated | How to Verify |
|---------|---------------|---------------|
| Gmail | ✅ Yes | `watchers\token.json` exists |
| LinkedIn | ✅ Yes | `watchers\linkedin_session\` exists |
| WhatsApp | ❌ No | Run `python watchers\whatsapp_watcher.py` to auth |

---

## Skills Available

All Silver Tier skills are ready:

| Skill | Purpose |
|-------|---------|
| **browsing-with-playwright** | Browser automation |
| **approval-workflow** | Human-in-the-loop approvals |
| **linkedin-poster** | LinkedIn posting |
| **scheduler** | Task scheduling |

---

## Test Commands

### Test File Watcher
```bash
echo Test > AI_Employee_Vault\Inbox\test.txt
# Wait 30 seconds
dir AI_Employee_Vault\Needs_Action\FILE_*.md
```

### Test Gmail Watcher
```bash
# Send yourself an email
# Wait 2 minutes
dir AI_Employee_Vault\Needs_Action\EMAIL_*.md
```

### Test LinkedIn Watcher
```bash
# Already running - checks every 15 minutes
dir AI_Employee_Vault\Needs_Action\LINKEDIN_*.md
```

### Test Qwen Code Integration
```bash
qwen --cwd "AI_Employee_Vault" "Summarize all items in Needs_Action"
```

---

## Logs

Check logs for each watcher:
```
AI_Employee_Vault\Logs\
├── FileWatcher.log
├── GmailWatcher.log
├── LinkedInWatcher.log
└── orchestrator.log
```

---

## To Stop Services

Close each terminal window, or press `Ctrl+C` in each.

---

## Next Steps

### Option 1: Authenticate WhatsApp
```bash
python watchers\whatsapp_watcher.py
```
Scan QR code with your phone.

### Option 2: Test Full Workflow
1. Start all: `start-silver-tier.bat`
2. Drop a file in `Inbox/`
3. Wait for action file in `Needs_Action/`
4. Process with Qwen Code

### Option 3: Start Gold Tier
- Odoo accounting integration
- Facebook/Instagram posting
- Twitter (X) integration

---

*Silver Tier Ready - AI Employee v0.2*

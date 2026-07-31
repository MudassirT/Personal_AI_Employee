# Silver Tier - Complete Setup Guide

## Overview

Silver Tier adds:
- ✅ Gmail Watcher (real-time email monitoring)
- ✅ LinkedIn Watcher (notifications and messages)
- ✅ WhatsApp Watcher (message monitoring)
- ✅ Approval Workflow (human-in-the-loop)
- ✅ Scheduler (automated tasks)
- ✅ Qwen Code integration

---

## Prerequisites

### 1. Python 3.13+
```bash
python --version
```

### 2. Playwright
```bash
pip install playwright
playwright install
```

### 3. Gmail API Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 4. Qwen Code
```bash
qwen --version
```

---

## Step 1: Gmail API Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name it "AI Employee"
4. Click "Create"

### 1.2 Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click "Enable"

### 1.3 Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "AI Employee Gmail"
5. Click "Create"
6. Download the `credentials.json` file

### 1.4 Place Credentials

Copy `credentials.json` to:
```
Personal_AI_Employee/watchers/credentials.json
```

### 1.5 Authenticate Gmail

```bash
cd watchers
python test_gmail_auth.py
```

This will:
1. Open a browser
2. Ask you to sign in to Google
3. Request Gmail API permissions
4. Save a token file for future use

**Success:** You should see "✓ Gmail API authentication successful!"

---

## Step 2: LinkedIn Setup

### 2.1 Install Playwright (if not done)

```bash
pip install playwright
playwright install
```

### 2.2 First Run - Login

```bash
python watchers/linkedin_watcher.py
```

This will:
1. Open a browser
2. Navigate to LinkedIn
3. **You need to log in manually**
4. Session is saved for future runs

**Note:** Keep the browser open until login completes.

---

## Step 3: WhatsApp Setup

### 3.1 First Run - QR Scan

```bash
python watchers/whatsapp_watcher.py
```

This will:
1. Open a browser
2. Navigate to WhatsApp Web
3. **Scan the QR code with your phone**
4. Session is saved for future runs

---

## Step 4: Start All Services

### Option A: Start All at Once

```bash
start-silver-tier.bat
```

This opens 5 terminal windows:
- File System Watcher
- Gmail Watcher
- WhatsApp Watcher
- LinkedIn Watcher
- Orchestrator

### Option B: Start Individually

```bash
# Terminal 1
python watchers/filesystem_watcher.py

# Terminal 2
python watchers/gmail_watcher.py

# Terminal 3
python watchers/whatsapp_watcher.py

# Terminal 4
python watchers/linkedin_watcher.py

# Terminal 5
python orchestrator.py
```

---

## Step 5: Test the System

### Test 1: File Drop

1. Copy a file to `AI_Employee_Vault/Inbox/`
2. Check `Needs_Action/` for action file
3. Check `Plans/` for plan file

### Test 2: Gmail

1. Send yourself an email with subject "Test"
2. Wait 2 minutes (Gmail checks every 2 min)
3. Check `Needs_Action/` for EMAIL_*.md file

### Test 3: LinkedIn

1. Have someone send you a LinkedIn message
2. Wait 5 minutes (LinkedIn checks every 5 min)
3. Check `Needs_Action/` for LINKEDIN_*.md file

### Test 4: WhatsApp

1. Send yourself a WhatsApp message with "urgent"
2. Wait 30 seconds
3. Check `Needs_Action/` for WHATSAPP_*.md file

### Test 5: Qwen Code Processing

```bash
qwen --cwd "AI_Employee_Vault" "Process all files in Needs_Action and summarize what actions are needed"
```

---

## Step 6: Configure Qwen Code MCP (Optional)

For email sending capability, configure MCP:

### 6.1 Create MCP Config

Create `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/full/path/to/mcp-servers/email-sender/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/full/path/to/watchers/credentials.json"
      }
    }
  }
}
```

### 6.2 Test Email Sending

```bash
qwen --cwd "AI_Employee_Vault" "Send a test email to yourself using the email MCP"
```

---

## Folder Structure

```
Personal_AI_Employee/
├── watchers/
│   ├── credentials.json          # ⭐ Gmail API credentials
│   ├── token.json                # ⭐ Gmail auth token (auto-created)
│   ├── base_watcher.py           # Base class
│   ├── filesystem_watcher.py     # File monitoring
│   ├── gmail_watcher.py          # Gmail monitoring
│   ├── whatsapp_watcher.py       # WhatsApp monitoring
│   ├── linkedin_watcher.py       # LinkedIn monitoring
│   └── test_gmail_auth.py        # Gmail auth test
├── mcp-servers/email-sender/
│   ├── README.md
│   └── requirements.txt
├── schedules/
│   ├── daily_processing.bat
│   └── weekly_briefing.bat
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/                    # Drop files here
│   ├── Needs_Action/             # Action items
│   ├── Plans/                    # Action plans
│   ├── Pending_Approval/         # Awaiting approval
│   ├── Approved/                 # Approved actions
│   ├── Done/                     # Completed
│   └── Logs/                     # System logs
├── orchestrator.py
├── start-silver-tier.bat         # ⭐ Start all services
└── SILVER_TIER_SETUP.md          # This file
```

---

## Troubleshooting

### Gmail Watcher Issues

**"credentials.json not found"**
```bash
# Make sure file is in watchers/ folder
dir watchers\credentials.json
```

**"Token expired"**
```bash
# Delete token and re-authenticate
del watchers\token.json
python watchers\test_gmail_auth.py
```

**"No unread messages"**
- Gmail watcher only checks unread messages
- Mark a test email as unread first

### LinkedIn Watcher Issues

**"Not logged in"**
- First run requires manual login
- Keep browser open until login completes
- Session is saved for future runs

**"No notifications found"**
- LinkedIn watcher needs actual notifications
- Have someone send you a message or connection request

### WhatsApp Watcher Issues

**"QR code not showing"**
- Refresh WhatsApp Web page manually
- Make sure phone has internet

**"Session expired"**
- Delete `whatsapp_session` folder
- Re-run and scan QR code again

### General Issues

**"Module not found: playwright"**
```bash
pip install playwright
playwright install
```

**"Qwen Code not found"**
```bash
# Ensure Qwen Code is installed
qwen --version
```

---

## Daily Operations

### Morning Check

1. Open Obsidian vault
2. Review `Dashboard.md`
3. Check `Needs_Action/` folder
4. Process with Qwen Code

### Weekly Tasks

```bash
# Run weekly briefing
qwen --cwd "AI_Employee_Vault" "Generate weekly CEO briefing from completed tasks"
```

### Monthly Audit

```bash
# Run subscription audit
qwen --cwd "AI_Employee_Vault" "Audit all subscriptions and flag unused services"
```

---

## Security Notes

⚠️ **Important:**
- Never commit `credentials.json` or `token.json` to Git
- Keep `.env` files secure
- Review all approval requests carefully
- Log out of sessions when done testing

---

## Next Steps

After Silver Tier is working:

1. **Gold Tier:**
   - Odoo accounting integration
   - Facebook/Instagram posting
   - Twitter (X) integration

2. **Platinum Tier:**
   - Cloud deployment
   - 24/7 operation
   - Multi-agent coordination

---

## Resources

- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Playwright Docs](https://playwright.dev/)
- [LinkedIn](https://www.linkedin.com/)
- [Qwen Code](https://claude.com/)

---

*Silver Tier Setup Guide - AI Employee v0.2*

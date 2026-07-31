# AI Employee - Silver Tier (Complete)

**Personal AI Employee Hackathon - Silver Tier Implementation**

A functional AI assistant with multiple watchers, social media automation, and human-in-the-loop approvals.

---

## What is Silver Tier?

Silver Tier builds on Bronze Tier by adding:

| # | Feature | Status |
|---|---------|--------|
| 1 | All Bronze requirements | ✅ Complete |
| 2 | Two or more Watcher scripts | ✅ Gmail + WhatsApp + LinkedIn + File |
| 3 | LinkedIn posting automation | ✅ LinkedIn Poster skill |
| 4 | Reasoning loop with Plan.md | ✅ Already in Bronze |
| 5 | MCP server for external action | ✅ Email Sender MCP |
| 6 | Human-in-the-loop approval | ✅ Approval Workflow skill |
| 7 | Task scheduling | ✅ Scheduler skill |
| 8 | All as Agent Skills | ✅ 4 skills created |

---

## Quick Start

### 1. Install Dependencies

```bash
# Gmail API dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Playwright (for LinkedIn and WhatsApp)
pip install playwright
playwright install
```

### 2. Setup Gmail API

**First time only:**

```bash
cd watchers
python test_gmail_auth.py
```

This will:
1. Open a browser
2. Ask you to sign in to Google
3. Save a token for future use

### 3. Start All Services

**Option A: Start everything at once (Windows)**

```bash
start-silver-tier.bat
```

**Option B: Start individually**

```bash
# Terminal 1 - File Watcher
python watchers/filesystem_watcher.py

# Terminal 2 - Gmail Watcher
python watchers/gmail_watcher.py

# Terminal 3 - WhatsApp Watcher (first run: scan QR)
python watchers/whatsapp_watcher.py

# Terminal 4 - LinkedIn Watcher (first run: login)
python watchers/linkedin_watcher.py

# Terminal 5 - Orchestrator
python orchestrator.py
```

---

## Watchers Overview

### 1. File System Watcher ✅
**Monitors:** `AI_Employee_Vault/Inbox/` folder
**Check Interval:** 30 seconds
**Creates:** `FILE_*.md` in `Needs_Action/`

### 2. Gmail Watcher ✅
**Monitors:** Unread Gmail messages
**Check Interval:** 2 minutes
**Creates:** `EMAIL_*.md` in `Needs_Action/`
**Setup Required:** Gmail API credentials

### 3. WhatsApp Watcher ✅
**Monitors:** WhatsApp Web messages with keywords
**Keywords:** urgent, asap, invoice, payment, help
**Check Interval:** 30 seconds
**Creates:** `WHATSAPP_*.md` in `Needs_Action/`
**Setup Required:** QR code scan (first run)

### 4. LinkedIn Watcher ✅ (NEW)
**Monitors:** LinkedIn notifications, messages, connection requests
**Check Interval:** 5 minutes
**Creates:** `LINKEDIN_*.md` in `Needs_Action/`
**Setup Required:** LinkedIn login (first run)

---

## Skills Overview

### 1. browsing-with-playwright ✅
Browser automation for web interaction.

### 2. approval-workflow ✅
Human-in-the-loop approval system.

### 3. linkedin-poster ✅
LinkedIn automation for posting content.

### 4. scheduler ✅
Task scheduling via Windows Task Scheduler or cron.

---

## Folder Structure

```
Personal_AI_Employee/
├── .qwen/skills/
│   ├── browsing-with-playwright/    # ✅ Bronze
│   ├── approval-workflow/           # ⭐ Silver
│   ├── linkedin-poster/             # ⭐ Silver
│   └── scheduler/                   # ⭐ Silver
├── mcp-servers/
│   └── email-sender/                # ⭐ Silver
├── watchers/
│   ├── credentials.json             # ⭐ Gmail API (you provide)
│   ├── token.json                   # ⭐ Gmail auth (auto-created)
│   ├── base_watcher.py              # ✅ Bronze
│   ├── filesystem_watcher.py        # ✅ Bronze
│   ├── gmail_watcher.py             # ✅ Silver
│   ├── whatsapp_watcher.py          # ✅ Silver
│   ├── linkedin_watcher.py          # ⭐ Silver (NEW)
│   └── test_gmail_auth.py           # ⭐ Auth helper
├── schedules/
│   ├── daily_processing.bat         # ⭐ Silver
│   └── weekly_briefing.bat          # ⭐ Silver
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/                       # Drop files here
│   ├── Needs_Action/                # Action items
│   ├── Plans/                       # Action plans
│   ├── Pending_Approval/            # Awaiting approval
│   ├── Approved/                    # Approved actions
│   ├── Done/                        # Completed
│   └── Logs/                        # System logs
├── orchestrator.py                  # ✅ Bronze (updated for Qwen)
├── start-silver-tier.bat            # ⭐ Start all services
├── SILVER_TIER_SETUP.md             # ⭐ Detailed setup guide
└── README_SILVER_TIER_COMPLETE.md   # This file
```

---

## Testing Checklist

### Test 1: File Drop ✅
1. Copy a file to `AI_Employee_Vault/Inbox/`
2. Wait 30 seconds
3. Check `Needs_Action/` for `FILE_*.md`

### Test 2: Gmail ✅
1. Send yourself an email with subject "Test"
2. Wait 2 minutes
3. Check `Needs_Action/` for `EMAIL_*.md`

### Test 3: WhatsApp ✅
1. Send yourself a WhatsApp message with "urgent"
2. Wait 30 seconds
3. Check `Needs_Action/` for `WHATSAPP_*.md`

### Test 4: LinkedIn ✅
1. Have someone send you a LinkedIn message
2. Wait 5 minutes
3. Check `Needs_Action/` for `LINKEDIN_*.md`

### Test 5: Qwen Code Processing ✅
```bash
qwen --cwd "AI_Employee_Vault" "Process all files in Needs_Action"
```

---

## Gmail API Setup (Detailed)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name: "AI Employee"
4. Click "Create"

### Step 2: Enable Gmail API

1. Go to "APIs & Services" > "Library"
2. Search: "Gmail API"
3. Click "Enable"

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "AI Employee Gmail"
5. Download `credentials.json`

### Step 4: Place Credentials

```
watchers/credentials.json
```

### Step 5: Authenticate

```bash
cd watchers
python test_gmail_auth.py
```

---

## LinkedIn Setup (Detailed)

### First Run - Login

```bash
python watchers/linkedin_watcher.py
```

1. Browser opens automatically
2. Navigate to LinkedIn login
3. **Log in manually**
4. Session saved to `linkedin_session/`

### Future Runs

Session is persisted - no login needed unless you log out.

---

## WhatsApp Setup (Detailed)

### First Run - QR Scan

```bash
python watchers/whatsapp_watcher.py
```

1. Browser opens automatically
2. WhatsApp Web QR code appears
3. **Scan with your phone**
4. Session saved to `whatsapp_session/`

### Future Runs

Session is persisted for ~2 weeks.

---

## Usage Examples

### Example 1: Email Processing Flow

1. Gmail Watcher detects new email
2. Creates `EMAIL_*.md` in `Needs_Action/`
3. Orchestrator creates `PLAN_*.md`
4. Qwen processes and drafts response
5. If sending needed → creates approval request
6. User approves → Email MCP sends

### Example 2: LinkedIn Post

1. Create draft in `Plans/`:
   ```markdown
   ---
   type: linkedin_post
   content: "Excited to announce our AI Employee!"
   ---
   ```
2. Move to `Pending_Approval/`
3. User moves to `Approved/`
4. LinkedIn Poster publishes

### Example 3: Approval Workflow

```bash
# Qwen creates approval request
qwen --cwd "AI_Employee_Vault" "Create approval to send invoice email"

# User reviews in Obsidian
# Moves file from Pending_Approval/ to Approved/

# Orchestrator executes
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail "credentials not found" | Ensure `credentials.json` in `watchers/` |
| Gmail "token expired" | Delete `token.json`, re-run `test_gmail_auth.py` |
| LinkedIn "not logged in" | Run watcher, log in when browser opens |
| WhatsApp "QR not showing" | Refresh page, check phone internet |
| Qwen "command not found" | Ensure Qwen Code is installed |
| Watcher exits immediately | Check `Logs/` folder for errors |

---

## Daily Operations

### Morning Check

1. Open Obsidian vault
2. Review `Dashboard.md`
3. Check `Needs_Action/` folder
4. Process with Qwen Code

### Weekly Tasks

```bash
qwen --cwd "AI_Employee_Vault" "Generate weekly CEO briefing"
```

### Monthly Audit

```bash
qwen --cwd "AI_Employee_Vault" "Audit subscriptions and flag unused"
```

---

## Security Notes

⚠️ **Important:**
- Never commit `credentials.json` or `token.json` to Git
- Keep `.env` files secure
- Review all approval requests carefully
- Log out of sessions when done testing

---

## Resources

- [Full Setup Guide](./SILVER_TIER_SETUP.md)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Playwright Docs](https://playwright.dev/)
- [Bronze Tier README](./README_BRONZE_TIER.md)
- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

---

*Silver Tier Complete - AI Employee v0.2*

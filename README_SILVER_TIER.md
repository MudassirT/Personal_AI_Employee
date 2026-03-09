# AI Employee - Silver Tier

**Personal AI Employee Hackathon - Silver Tier Implementation**

A functional AI assistant with multiple watchers, social media automation, and human-in-the-loop approvals.

---

## What is Silver Tier?

Silver Tier builds on Bronze Tier by adding:

| # | Feature | Status |
|---|---------|--------|
| 1 | All Bronze requirements | ✅ Complete |
| 2 | Two or more Watcher scripts | ✅ Gmail + WhatsApp + File System |
| 3 | LinkedIn posting automation | ✅ LinkedIn Poster skill |
| 4 | Reasoning loop with Plan.md | ✅ Already in Bronze |
| 5 | MCP server for external action | ✅ Email Sender MCP |
| 6 | Human-in-the-loop approval | ✅ Approval Workflow skill |
| 7 | Task scheduling | ✅ Scheduler skill |
| 8 | All as Agent Skills | ✅ 4 skills created |

---

## New Skills (Silver Tier)

### 1. browsing-with-playwright ✅
**Location:** `.qwen/skills/browsing-with-playwright/`

Browser automation for web interaction, form filling, and data extraction.

### 2. approval-workflow ✅ (NEW)
**Location:** `.qwen/skills/approval-workflow/`

Human-in-the-loop approval system for sensitive actions:
- Create approval requests in `/Pending_Approval/`
- User moves to `/Approved/` or `/Rejected/`
- Execute approved actions automatically

### 3. linkedin-poster ✅ (NEW)
**Location:** `.qwen/skills/linkedin-poster/`

LinkedIn automation using Playwright:
- Create business posts
- Post company updates
- Schedule content (future)

### 4. scheduler ✅ (NEW)
**Location:** `.qwen/skills/scheduler/`

Task scheduling via Windows Task Scheduler or cron:
- Daily: Process Needs_Action
- Weekly: Generate CEO Briefing
- Monthly: Subscription audit

---

## New Watchers (Silver Tier)

### WhatsApp Watcher ✅ (NEW)
**Location:** `watchers/whatsapp_watcher.py`

Monitors WhatsApp Web for:
- Unread messages
- Priority keywords: "urgent", "asap", "invoice", "payment", "help"
- Creates action files in Needs_Action

**First Run:**
```bash
python watchers/whatsapp_watcher.py
```
Scan QR code when browser opens. Session is saved for future runs.

### Gmail Watcher ✅
**Location:** `watchers/gmail_watcher.py`

Monitors Gmail for unread/important emails.

### File System Watcher ✅
**Location:** `watchers/filesystem_watcher.py`

Monitors Inbox folder for dropped files.

---

## New MCP Servers

### Email Sender 📧
**Location:** `mcp-servers/email-sender/`

Send emails via Gmail API or SMTP.

**Setup:**
```bash
cd mcp-servers/email-sender
pip install -r requirements.txt
```

**Configure:** Add to MCP settings:
```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/path/to/email-sender/email_mcp_server.py"]
    }
  }
}
```

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
│   ├── base_watcher.py              # ✅ Bronze
│   ├── filesystem_watcher.py        # ✅ Bronze
│   ├── gmail_watcher.py             # ✅ Bronze
│   └── whatsapp_watcher.py          # ⭐ Silver
├── schedules/
│   ├── daily_processing.bat         # ⭐ Silver
│   └── weekly_briefing.bat          # ⭐ Silver
├── AI_Employee_Vault/
│   ├── Pending_Approval/            # For HITL
│   ├── Approved/                    # Approved actions
│   ├── Rejected/                    # Rejected actions
│   └── ...
└── orchestrator.py
```

---

## Quick Start

### 1. Start All Watchers

Open three terminals:

```bash
# Terminal 1: File Watcher
python watchers/filesystem_watcher.py

# Terminal 2: WhatsApp Watcher (first run: scan QR)
python watchers/whatsapp_watcher.py

# Terminal 3: Gmail Watcher (requires API setup)
python watchers/gmail_watcher.py
```

### 2. Start Orchestrator

```bash
python orchestrator.py
```

### 3. Set Up Scheduler (Windows)

```powershell
# Open Task Scheduler
taskschd.msc

# Create tasks from:
# - schedules/daily_processing.bat (Daily at 8 AM)
# - schedules/weekly_briefing.bat (Monday at 9 AM)
```

---

## Usage Examples

### Example 1: WhatsApp Message Processing

1. WhatsApp Watcher detects message with "invoice"
2. Creates action file in `Needs_Action/`
3. Orchestrator creates plan
4. Qwen processes and drafts response
5. If sending required → creates approval request
6. User approves → Email MCP sends

### Example 2: LinkedIn Post

1. Create post draft in `Plans/`:
   ```markdown
   ---
   type: linkedin_post
   content: "Excited to announce our new AI Employee!"
   ---
   ```
2. Move to `Pending_Approval/` for review
3. User moves to `Approved/`
4. LinkedIn Poster publishes

### Example 3: Approval Workflow

```bash
# Qwen creates approval request
qwen --cwd "AI_Employee_Vault" "Create approval request to send invoice email"

# User reviews in Obsidian and moves to Approved/

# Orchestrator detects and executes
python orchestrator.py
```

---

## Silver Tier Checklist

- [ ] ✅ WhatsApp Watcher monitors messages
- [ ] ✅ Gmail Watcher monitors emails
- [ ] ✅ File Watcher monitors drop folder
- [ ] ✅ Approval workflow creates requests
- [ ] ✅ Email MCP can send emails
- [ ] ✅ LinkedIn Poster can create posts
- [ ] ✅ Scheduler triggers daily tasks
- [ ] ✅ All skills documented

---

## Testing

### Test WhatsApp Watcher

```bash
python watchers/whatsapp_watcher.py
# Send yourself a WhatsApp message with "urgent"
# Check Needs_Action folder for action file
```

### Test Approval Workflow

```bash
qwen --cwd "AI_Employee_Vault" "Create an approval request to send a test email"
# Check Pending_Approval folder
# Move file to Approved/
# Check if executed
```

### Test LinkedIn Poster

```bash
qwen --cwd "AI_Employee_Vault" "Create a LinkedIn post draft about our project"
# Check Plans folder for draft
```

### Test Scheduler

```bash
# Run daily processing manually
schedules/daily_processing.bat

# Check Logs folder for output
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| WhatsApp QR not scanning | Run with `headless=False`, wait longer |
| Email not sending | Check Gmail API credentials or SMTP settings |
| LinkedIn post fails | Ensure logged in, session saved |
| Scheduler not running | Check Task Scheduler history |

---

## Next Steps (Gold Tier)

After mastering Silver Tier:

- [ ] Odoo accounting integration
- [ ] Facebook/Instagram posting
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers
- [ ] Weekly CEO Briefing automation
- [ ] Error recovery system
- [ ] Cloud deployment

---

## Resources

- [Main Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Bronze Tier README](./README_BRONZE_TIER.md)
- [Silver Tier Skills Plan](./SILVER_TIER_SKILLS_PLAN.md)
- [Obsidian Help](https://help.obsidian.md/)
- [Playwright Docs](https://playwright.dev/)

---

*Silver Tier Implementation - AI Employee v0.2*

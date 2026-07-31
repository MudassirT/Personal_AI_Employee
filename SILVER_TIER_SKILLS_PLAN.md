# Silver Tier Skills Plan

## Overview

Silver Tier builds on Bronze Tier by adding:
- Multiple watchers (WhatsApp, Gmail)
- Social media automation (LinkedIn posting)
- Email sending capability
- Human-in-the-loop approval workflow
- Task scheduling

---

## Required Skills

### 1. browsing-with-playwright ✅ (Existing)
**Location:** `.qwen/skills/browsing-with-playwright/`

Browser automation for:
- WhatsApp Web monitoring
- LinkedIn posting
- Web form filling
- Data extraction

---

### 2. whatsapp-watcher (New)
**Location:** `watchers/whatsapp_watcher.py`

Uses Playwright to monitor WhatsApp Web for:
- Unread messages
- Keywords: "urgent", "asap", "invoice", "payment", "help"
- Creates action files in Needs_Action folder

**Dependencies:**
- Playwright (already installed via browsing-with-playwright)
- Persistent browser session for WhatsApp Web QR login

---

### 3. email-sender (New - MCP Server)
**Location:** `mcp-servers/email-sender/`

MCP server for sending emails via:
- Gmail API (OAuth 2.0)
- SMTP (fallback)

**Capabilities:**
- Send email
- Draft email
- Search emails
- Mark as read

**HITL Pattern:**
- Sensitive sends create approval request first
- User moves file to /Approved before sending

---

### 4. linkedin-poster (New - Agent Skill)
**Location:** `.qwen/skills/linkedin-poster/`

Uses Playwright to:
- Navigate to LinkedIn
- Create company updates
- Post business content
- Schedule posts (future)

**Workflow:**
1. Read content from Plans/ folder
2. Navigate to LinkedIn
3. Fill post composer
4. Take screenshot before posting
5. Create approval request
6. Post after approval

---

### 5. approval-workflow (New - Agent Skill)
**Location:** `.qwen/skills/approval-workflow/`

Human-in-the-loop approval system:

**Files:**
- `/Pending_Approval/` - Awaiting user review
- `/Approved/` - User approved, execute action
- `/Rejected/` - User rejected, archive

**Workflow:**
1. AI creates approval request in Pending_Approval/
2. User reviews and moves to Approved/ or Rejected/
3. Orchestrator detects and executes/rejects
4. Logs action and moves to Done/

---

### 6. scheduler (New - Agent Skill)
**Location:** `.qwen/skills/scheduler/`

Task scheduling via:
- Windows Task Scheduler (.bat files)
- Cron jobs (Linux/Mac)
- Python schedule library

**Scheduled Tasks:**
- Daily: Process Needs_Action folder
- Weekly: Generate CEO Briefing
- Monthly: Subscription audit

---

## Folder Structure for Silver Tier

```
Personal_AI_Employee/
├── .qwen/skills/
│   ├── browsing-with-playwright/    # ✅ Existing
│   ├── linkedin-poster/             # ⏳ New
│   ├── approval-workflow/           # ⏳ New
│   └── scheduler/                   # ⏳ New
├── mcp-servers/
│   └── email-sender/                # ⏳ New
├── watchers/
│   ├── base_watcher.py              # ✅ Existing
│   ├── filesystem_watcher.py        # ✅ Existing
│   ├── gmail_watcher.py             # ✅ Existing
│   └── whatsapp_watcher.py          # ⏳ New
├── AI_Employee_Vault/
│   ├── Pending_Approval/            # ✅ Existing
│   ├── Approved/                    # ✅ Existing
│   └── ...
└── schedules/                       # ⏳ New
    ├── daily_processing.bat
    └── weekly_briefing.bat
```

---

## Implementation Order

1. **whatsapp_watcher.py** - Uses existing Playwright skill
2. **approval-workflow skill** - Core HITL pattern
3. **email-sender MCP** - External action capability
4. **linkedin-poster skill** - Social media automation
5. **scheduler skill** - Task automation

---

## Testing Checklist

- [ ] WhatsApp Watcher detects messages
- [ ] Email MCP sends test email
- [ ] LinkedIn Poster creates post (draft mode)
- [ ] Approval workflow moves files correctly
- [ ] Scheduler triggers tasks on time

---

*Silver Tier Skills Plan - AI Employee v0.2*

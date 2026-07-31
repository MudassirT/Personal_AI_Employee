# Bronze Tier - Setup and Testing Guide

## Quick Start (5 Minutes)

### Step 1: Verify Prerequisites

```bash
# Check Python version (need 3.13+)
python --version

# Check Qwen Code
qwen --version
```

### Step 2: Open Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Navigate to: `Personal_AI_Employee/AI_Employee_Vault`
4. Click "Open"

You should see:
- Dashboard.md
- Company_Handbook.md
- Business_Goals.md

### Step 3: Start the Watcher

**Option A: Double-click** (Windows)
```
start-watcher.bat
```

**Option B: Terminal**
```bash
python watchers/filesystem_watcher.py
```

You should see:
```
File System Watcher starting...
Drop folder: ...\AI_Employee_Vault\Inbox
Vault: ...\AI_Employee_Vault
Drop files into the Inbox folder to trigger processing
Press Ctrl+C to stop
```

### Step 4: Start the Orchestrator

Open a **new terminal** and run:

**Option A: Double-click** (Windows)
```
start-orchestrator.bat
```

**Option B: Terminal**
```bash
python orchestrator.py
```

You should see:
```
==================================================
AI Employee Orchestrator
==================================================
Vault: ...\AI_Employee_Vault
Monitoring: Needs_Action folder
Press Ctrl+C to stop
```

### Step 5: Test the Workflow

1. **Copy** `test_document.md` to `AI_Employee_Vault/Inbox/`

2. **Watch** the terminal outputs - you should see:
   - File Watcher: "Created action file: FILE_..."
   - Orchestrator: "Processing: FILE_..."
   - Orchestrator: "Created plan: PLAN_..."

3. **Check** the folders:
   - `Needs_Action/` should have a new FILE_*.md file
   - `Plans/` should have a new PLAN_*.md file

4. **Check** `Dashboard.md` in Obsidian - it should update with activity

### Step 6: Process with Qwen Code

```bash
qwen --cwd "AI_Employee_Vault" "Read the file in Needs_Action and create a summary"
```

Qwen will:
1. Read the action file
2. Process the request
3. Write a response
4. Move the file to `Done/` when complete

---

## Testing Checklist

### Bronze Tier Requirements

- [ ] ✅ Obsidian vault created with proper folder structure
- [ ] ✅ Dashboard.md exists and updates correctly
- [ ] ✅ Company_Handbook.md exists with rules
- [ ] ✅ Business_Goals.md exists with objectives
- [ ] ✅ File System Watcher runs without errors
- [ ] ✅ Watcher creates action files in Needs_Action
- [ ] ✅ Orchestrator runs without errors
- [ ] ✅ Orchestrator creates plans in Plans/
- [ ] ✅ Qwen Code can read and write to vault
- [ ] ✅ Dashboard updates with activity

### Optional: Gmail Watcher

- [ ] Gmail API credentials configured
- [ ] `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`
- [ ] `credentials.json` in `watchers/` folder
- [ ] Gmail Watcher runs: `python watchers/gmail_watcher.py`
- [ ] Emails create action files in Needs_Action

---

## Troubleshooting

### "Python not found"
Install Python 3.13+ from [python.org](https://www.python.org/downloads/)

### "Qwen Code not found"
Ensure Qwen Code is installed and available in your PATH.

### "Module not found" for Gmail
Install dependencies:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Watcher exits immediately
Check the `Logs/` folder for error messages

### Files not being detected
1. Ensure watcher is running
2. Check file permissions
3. Try copying (not moving) the file

### Dashboard not updating
1. Ensure orchestrator is running
2. Check `Logs/orchestrator.log` for errors
3. Verify file write permissions

---

## File Structure Reference

```
Personal_AI_Employee/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Real-time summary
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # Q1 objectives
│   ├── Inbox/                   # Drop files here
│   ├── Needs_Action/            # Items to process
│   ├── Plans/                   # Action plans
│   ├── Done/                    # Completed tasks
│   ├── Pending_Approval/        # Awaiting approval
│   ├── Approved/                # Approved actions
│   ├── Briefings/               # CEO briefings
│   ├── Accounting/              # Financial records
│   └── Logs/                    # System logs
├── watchers/
│   ├── base_watcher.py          # Base class for watchers
│   ├── filesystem_watcher.py    # File system monitor
│   └── gmail_watcher.py         # Gmail monitor (optional)
├── orchestrator.py              # Main coordinator
├── start-watcher.bat            # Windows launcher
├── start-orchestrator.bat       # Windows launcher
├── test_document.md             # Test file
├── requirements.txt             # Python dependencies
├── README_BRONZE_TIER.md        # Full documentation
└── SETUP_AND_TEST.md            # This file
```

---

## Next Steps

Once Bronze Tier is working:

1. **Customize** Company_Handbook.md with your rules
2. **Update** Business_Goals.md with your objectives
3. **Test** with real documents and emails
4. **Consider** Silver Tier upgrades:
   - Gmail integration
   - WhatsApp monitoring
   - Email sending via MCP
   - Automated approvals

---

## Support Resources

- Main Blueprint: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- Full Documentation: `README_BRONZE_TIER.md`
- Obsidian Help: https://help.obsidian.md/

---

*Bronze Tier Setup Guide - AI Employee v0.1*

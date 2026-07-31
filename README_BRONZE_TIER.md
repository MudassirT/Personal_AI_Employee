# AI Employee - Bronze Tier

**Personal AI Employee Hackathon - Bronze Tier Implementation**

A local-first, autonomous AI employee that manages your personal and business affairs using Qwen Code and Obsidian.

---

## What is Bronze Tier?

Bronze Tier is the **Minimum Viable Deliverable** for the Personal AI Employee hackathon. It includes:

- ✅ Obsidian vault with Dashboard.md, Company_Handbook.md, and Business_Goals.md
- ✅ Working Watcher scripts (File System Watcher - no API setup required!)
- ✅ Qwen Code integration for reading/writing to the vault
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done, /Pending_Approval, /Approved
- ✅ Orchestrator for coordinating tasks

---

## Quick Start

### 1. Prerequisites

Ensure you have the following installed:

| Component | Version | Download |
|-----------|---------|----------|
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| Qwen Code | Latest | See installation instructions |
| Obsidian | v1.10.6+ | [obsidian.md](https://obsidian.md/download) |

### 2. Setup

```bash
# Navigate to the project directory
cd Personal_AI_Employee

# (Optional) Create Python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (optional for Bronze Tier)
pip install -r requirements.txt
```

### 3. Open the Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder
4. You should see Dashboard.md, Company_Handbook.md, and Business_Goals.md

### 4. Start the File System Watcher

```bash
python watchers/filesystem_watcher.py
```

This watcher monitors the `AI_Employee_Vault/Inbox` folder for new files.

### 5. Start the Orchestrator

Open a new terminal:

```bash
python orchestrator.py
```

The orchestrator monitors the `Needs_Action` folder and coordinates task processing.

---

## How It Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Drop Files    │────▶│  File Watcher    │────▶│  Needs_Action   │
│   in Inbox/     │     │  (Python)        │     │  (Markdown)     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Dashboard     │◀────│   Qwen Code      │◀────│   Orchestrator  │
│   (Obsidian)    │     │   (AI Brain)     │     │   (Python)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Workflow

1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. **File Watcher** detects the new file and creates an action file in `Needs_Action/`
3. **Orchestrator** picks up the action file and creates a plan in `Plans/`
4. **You trigger Qwen Code** to process the plan:
   ```bash
   qwen --cwd "AI_Employee_Vault" "Process all files in /Needs_Action"
   ```
5. **Qwen** reads the files, thinks, creates responses, and moves files to `Done/`
6. **Dashboard** is updated with the activity

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 objectives
├── Inbox/                    # Drop files here
├── Needs_Action/             # Items requiring attention
├── In_Progress/              # Currently being worked on
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Human-approved actions
├── Plans/                    # Generated action plans
├── Done/                     # Completed tasks
├── Briefings/                # CEO briefings
├── Accounting/               # Transaction logs
└── Logs/                     # System logs
```

---

## Usage Examples

### Example 1: Process a Document

1. Drop a PDF or text file into `Inbox/`
2. Watcher creates an action file in `Needs_Action/`
3. Run Qwen Code:
   ```bash
   qwen --cwd "AI_Employee_Vault" "Read and summarize the document in Needs_Action"
   ```

### Example 2: Process an Email (Manual)

1. Copy email content into a new file in `Inbox/`
2. Watcher processes it automatically
3. Qwen creates a draft response

### Example 3: Daily Briefing

```bash
qwen --cwd "AI_Employee_Vault" "Review all completed tasks this week and generate a CEO briefing in Briefings/"
```

---

## Ralph Wiggum Loop (Autonomous Mode)

For autonomous multi-step task processing, use the Ralph Wiggum pattern:

```bash
# Start autonomous processing
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" --max-iterations 10
```

This keeps Qwen working until all tasks are complete (up to 10 iterations).

---

## Gmail Watcher (Optional)

For automatic Gmail integration:

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to the `watchers/` folder

### Run

```bash
python watchers/gmail_watcher.py
```

First run will open a browser for authorization.

---

## Configuration

### Company Handbook

Edit `Company_Handbook.md` to customize:
- Communication guidelines
- Payment thresholds
- Task priorities
- Approval workflows

### Business Goals

Edit `Business_Goals.md` to set:
- Revenue targets
- Key metrics
- Active projects
- Subscription tracking

---

## Troubleshooting

### "Command not found: qwen"

Ensure Qwen Code is installed and available in your PATH.

### Watcher not detecting files

1. Ensure the watcher is running
2. Check the Logs folder for errors
3. Verify file permissions

### Qwen Code not reading files

1. Ensure you're in the vault directory
2. Check that files have `.md` extension
3. Verify YAML frontmatter is valid

---

## Next Steps (Silver Tier)

After mastering Bronze Tier, consider adding:

- [ ] Gmail Watcher with real API integration
- [ ] WhatsApp Watcher using Playwright
- [ ] MCP server for sending emails
- [ ] Human-in-the-loop approval workflow
- [ ] Scheduled tasks with cron/Task Scheduler
- [ ] LinkedIn posting automation

---

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit credentials** - Add `.env`, `credentials.json`, `token.json` to `.gitignore`
2. **Use environment variables** for API keys
3. **Review before approving** - Always check pending approvals carefully
4. **Audit logs** - Regularly review the Logs folder

---

## Resources

- [Main Hackathon Blueprint](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Obsidian Help](https://help.obsidian.md/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Support

For questions or issues:
- Check the Logs folder for error messages
- Review the Company_Handbook.md for rules
- Join the Wednesday Research Meeting on Zoom

---

*Bronze Tier Implementation - AI Employee v0.1*

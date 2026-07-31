# Personal AI Employee - Project Context

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI employee that manages personal and business affairs 24/7. The project uses a **local-first, agent-driven architecture** with human-in-the-loop oversight.

**Core Concept:** Transform AI from a reactive chatbot into a proactive business partner that:
- Monitors communications (Gmail, WhatsApp, LinkedIn)
- Manages tasks and projects
- Handles accounting and bank transactions
- Generates executive briefings ("Monday Morning CEO Briefing")
- Posts to social media platforms

## Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **The Memory/GUI** | Obsidian | Local Markdown dashboard & knowledge base |
| **The Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **The Hands** | MCP Servers | Model Context Protocol for external actions |
| **Browser Automation** | Playwright MCP | Web interaction, form filling, scraping |

### Folder Structure

```
Personal_AI_Employee/
├── .qwen/skills/           # Qwen skills (browsing-with-playwright)
├── skills-lock.json        # Skills version lock file
└── Personal AI Employee Hackathon 0_*.md  # Full architectural blueprint
```

### Obsidian Vault Structure (Expected)

```
Vault/
├── Dashboard.md            # Real-time summary
├── Company_Handbook.md     # Rules of engagement
├── Business_Goals.md       # Q1/Q2 objectives & metrics
├── Inbox/                  # Raw incoming items
├── Needs_Action/           # Items requiring attention
├── In_Progress/<agent>/    # Claimed tasks
├── Pending_Approval/       # Human-in-the-loop requests
├── Approved/               # User-approved actions
├── Done/                   # Completed tasks
├── Plans/                  # Generated action plans
├── Briefings/              # CEO briefings
└── Accounting/             # Transaction logs
```

## Key Concepts

### Watchers (Perception Layer)

Lightweight Python scripts that run continuously and create `.md` files in `/Needs_Action`:

- **Gmail Watcher:** Monitors unread/important emails
- **WhatsApp Watcher:** Uses Playwright to monitor WhatsApp Web
- **File System Watcher:** Watches drop folders for new files

### Ralph Wiggum Loop (Persistence)

A Stop hook pattern that keeps Claude Code working autonomously until tasks are complete:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in `/Done`?
5. If NO → Block exit, re-inject prompt (loop continues)
6. If YES → Allow exit

### Human-in-the-Loop (HITL)

For sensitive actions (payments, sending messages):
1. Claude creates approval request file in `/Pending_Approval`
2. User reviews and moves file to `/Approved` or `/Rejected`
3. Orchestrator executes approved actions via MCP

## Available Skills

### browsing-with-playwright

Browser automation via Playwright MCP server for web scraping, form submission, and UI testing.

**Server Management:**
```bash
# Start server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Operations:**
- Navigate URLs, take screenshots
- Fill forms, click elements, select dropdowns
- Execute JavaScript, wait for conditions
- Extract data via snapshots or custom code

See `.qwen/skills/browsing-with-playwright/SKILL.md` for detailed usage.

## Building & Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary AI engine |
| Obsidian | v1.10.6+ | Knowledge base |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Setup Checklist

1. Create Obsidian vault named `AI_Employee_Vault`
2. Verify Claude Code: `claude --version`
3. Install Playwright: `npx playwright install`
4. Set up Python virtual environment with `uv`
5. Configure MCP servers in `~/.config/claude-code/mcp.json`

### MCP Server Configuration

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": { "GMAIL_CREDENTIALS": "/path/to/credentials.json" }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": { "HEADLESS": "true" }
    }
  ]
}
```

## Development Conventions

### Coding Style
- Python: Use type hints, follow PEP 8
- All watchers inherit from `BaseWatcher` abstract class
- Markdown files use YAML frontmatter for metadata

### Testing Practices
- Verify MCP servers before use with `verify.py`
- Test watchers in isolation before integration
- Use logging for all watcher operations

### Security Rules
- Secrets never sync (`.env`, tokens, WhatsApp sessions, banking credentials)
- Cloud agents operate in draft-only mode
- Local instance handles approvals and final actions

## Hackathon Tiers

| Tier | Description | Time Estimate |
|------|-------------|---------------|
| **Bronze** | Foundation: 1 watcher, basic vault | 8-12 hours |
| **Silver** | Functional: 2+ watchers, MCP integration | 20-30 hours |
| **Gold** | Autonomous: Full integration, Odoo, multi-MCP | 40+ hours |
| **Platinum** | Production: Cloud deployment, 24/7 operation | 60+ hours |

## Key Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools:** `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Zoom Meetings:** Wednesdays 10:00 PM PKT (First: Jan 7, 2026)
- **YouTube:** https://www.youtube.com/@panaversity

## Common Commands

```bash
# Start Ralph loop for autonomous task processing
/ralph-loop "Process all files in /Needs_Action" --max-iterations 10

# Watcher pattern (Python)
python watchers/gmail_watcher.py
python watchers/whatsapp_watcher.py

# MCP client calls (Playwright)
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'
```

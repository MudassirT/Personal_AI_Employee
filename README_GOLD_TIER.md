# Gold Tier: Autonomous AI Employee

**Version:** 0.3  
**Tagline:** *Your business runs itself. Local-first, agent-driven, human-in-the-loop.*

---

## What's New in Gold Tier

Gold Tier builds on Silver Tier's watchers, skills, and approval workflow to add **full business automation**:

| Feature | Silver Tier | Gold Tier |
|---------|-------------|-----------|
| Email/Chat Monitoring | ✅ | ✅ |
| Approval Workflow | ✅ | ✅ |
| Task Scheduling | ✅ | ✅ |
| **Accounting (Odoo)** | ❌ | ✅ |
| **Social Media (FB/IG/Twitter)** | ❌ | ✅ |
| **Calendar Management** | ❌ | ✅ |
| **Web Search** | ❌ | ✅ |
| **Autonomous Loop (Ralph)** | ❌ | ✅ |
| **Error Recovery/Circuit Breakers** | ❌ | ✅ |
| **Audit Logging (Compliance)** | ❌ | ✅ |
| **Multi-MCP Architecture** | 1 server | 5+ servers |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Playwright: `pip install playwright && playwright install chromium`
- Google Cloud Project (for Calendar, Gmail)
- Odoo 17+ instance (for accounting)
- Meta Business Suite access (for Facebook/Instagram)
- Twitter/X account

### Installation

```bash
# 1. Clone and navigate
cd Personal_AI_Employee-main

# 2. Install all dependencies
pip install -r requirements.txt
pip install -r mcp-servers/email-sender/requirements.txt
pip install -r mcp-servers/odoo-accounting/requirements.txt
pip install -r mcp-servers/web-search/requirements.txt
pip install -r mcp-servers/calendar/requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Run setup
start-gold-tier.bat
```

### Configuration

#### 1. Odoo Accounting
```bash
# Set environment variables
set ODOO_URL=http://localhost:8069
set ODOO_DATABASE=mycompany
set ODOO_USERNAME=admin
set ODOO_PASSWORD=secure_password

# Or create .env in mcp-servers/odoo-accounting/
```

#### 2. Google Calendar/Gmail
```bash
# Place credentials in mcp-servers/calendar/credentials/
# Place credentials in mcp-servers/email-sender/credentials/
# Run first auth:
python mcp-servers/calendar/calendar_mcp.py
python mcp-servers/email-sender/email_mcp_server.py
```

#### 3. Social Media
```bash
# First-time authentication (opens browser)
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py --auth both
python .qwen/skills/twitter-poster/twitter_poster.py --auth
```

#### 4. Web Search (Optional)
```bash
# For Google Custom Search
set GOOGLE_API_KEY=your_key
set GOOGLE_CSE_ID=your_cse_id

# For Bing
set BING_API_KEY=your_key
```

---

## Running Gold Tier

### Option 1: Continuous Orchestrator (Recommended)
```bash
# Runs forever, processes tasks every 60s
python orchestrator.py
```

### Option 2: Autonomous Ralph Loop
```bash
# Processes queue autonomously for N iterations
python orchestrator.py --ralph-loop 50 --ralph-delay 30

# Parameters:
# --ralph-loop N    : Max iterations (default: 10)
# --ralph-delay S   : Seconds between iterations (default: 30)
```

### Option 3: Scheduled Tasks (Windows)
```bash
# Install scheduled tasks
schtasks /Create /TN "AI Employee Daily" /TR "C:\path\to\schedules\daily_processing.bat" /SC DAILY /ST 08:00
schtasks /Create /TN "AI Employee Weekly" /TR "C:\path\to\schedules\weekly_briefing.bat" /SC WEEKLY /D MON /ST 09:00
schtasks /Create /TN "AI Employee Monthly" /TR "C:\path\to\schedules\monthly_audit.bat" /SC MONTHLY /D 1 /ST 10:00
```

### Option 4: All Services (start-gold-tier.bat)
```bat
@echo off
echo Starting AI Employee Gold Tier...

start "File Watcher" python watchers/filesystem_watcher.py
start "Gmail Watcher" python watchers/gmail_watcher.py
start "WhatsApp Watcher" python watchers/whatsapp_watcher.py
start "LinkedIn Watcher" python watchers/linkedin_watcher.py
start "Orchestrator" python orchestrator.py

echo All services started!
echo Check logs in AI_Employee_Vault/Logs/
pause
```

---

## Vault Structure (Gold Tier)

```
AI_Employee_Vault/
├── Inbox/                      # Raw inputs (emails, files, messages)
├── Needs_Action/               # Parsed tasks awaiting processing
├── In_Progress/                # Currently being worked on
├── Pending_Approval/           # Human review required
├── Approved/                   # Approved for execution
├── Rejected/                   # Rejected items
├── Done/                       # Completed tasks
├── Plans/                      # Qwen Code execution plans
├── Odoo/                       # Accounting data
│   ├── Invoices/
│   ├── Payments/
│   ├── Reports/
│   └── Partners/
├── Social/                     # Social media assets
│   ├── Facebook/
│   │   ├── Posts/
│   │   ├── Scheduled/
│   │   └── History/
│   ├── Instagram/
│   │   ├── Posts/
│   │   ├── Stories/
│   │   ├── Reels/
│   │   └── History/
│   ├── Twitter/
│   │   ├── Tweets/
│   │   ├── Threads/
│   │   └── History/
│   └── Assets/
│       └── images/
├── Audits/                     # Compliance audit exports
└── Logs/
    ├── orchestrator.log
    ├── errors.log
    ├── degradation.log
    ├── audit_2026-01-15.jsonl
    └── component_health.json
```

---

## Core Workflows

### 1. Invoice Processing (Odoo)

```
Email received → Gmail Watcher → Needs_Action/invoice_*.md
     ↓
Orchestrator creates plan → Plans/PLAN_invoice_*.md
     ↓
Qwen Code reads plan, extracts data
     ↓
Approval requested → Pending_Approval/APPROVAL_create_invoice_*.md
     ↓
Human reviews → Moves to Approved/
     ↓
Orchestrator executes → Odoo MCP creates invoice
     ↓
Invoice posted → Payment registered → Done/
```

### 2. Social Media Campaign

```
Marketing request → Inbox/campaign_brief.md
     ↓
Orchestrator → Plans/PLAN_social_campaign_*.md
     ↓
Qwen Code drafts posts for FB/IG/Twitter
     ↓
Approval per post → Pending_Approval/social_post_*.md
     ↓
Human approves → Approved/Social/
     ↓
Skills execute → Facebook/Instagram/Twitter posted
     ↓
History logged → Social/Facebook/History/, etc.
```

### 3. Meeting Scheduling

```
Email: "Schedule meeting with client X"
     ↓
Gmail Watcher → Needs_Action/meeting_request.md
     ↓
Orchestrator + Calendar MCP → Check availability
     ↓
Proposed times → Pending_Approval/
     ↓
Human approves → Calendar event created
     ↓
Confirmation email sent via Email MCP
```

### 4. Expense Audit (Monthly)

```
Scheduler triggers → monthly_audit.bat
     ↓
Qwen Code: "Review all transactions, find subscriptions"
     ↓
Odoo MCP: Get bank transactions, vendor bills
     ↓
Report generated → Briefings/monthly_audit_*.md
     ↓
If issues found → Approval for cancellations
```

---

## Autonomous Mode: Ralph Wiggum Loop

The Ralph Loop enables **truly autonomous operation**:

```python
# In orchestrator.py
def run_ralph_loop(self, max_iterations=10, delay=30):
    for i in range(max_iterations):
        # 1. Scan for new tasks
        self.process_needs_action()
        
        # 2. Execute approved actions
        self.check_approved_actions()
        
        # 3. Trigger Qwen for plan execution
        self.trigger_qwen_processing()
        
        # 4. Check if queue empty
        if self.is_idle():
            break
            
        time.sleep(delay)
```

**Use cases:**
- Overnight batch processing
- Weekend autonomous operation
- CI/CD-style task pipelines
- Demo/presentation mode

**Safety features:**
- Max iteration limit
- Human approval gates
- Error circuit breakers
- Audit trail for every action

---

## Error Recovery & Resilience

### Circuit Breaker Pattern

Each external service has a circuit breaker:

```python
cb = CircuitBreaker("odoo", failure_threshold=5, recovery_timeout=300)

try:
    result = cb.call(odoo_client.create_invoice, data)
except CircuitOpenError:
    # Graceful degradation
    queue_for_later(data)
    notify_human("Odoo unavailable, invoice queued")
```

**States:**
- **Closed** (Normal) - Calls succeed
- **Open** (Failing) - Calls blocked, fast fail
- **Half-Open** (Testing) - Limited calls to test recovery

### Graceful Degradation Levels

| Level | Description | Functionality |
|-------|-------------|---------------|
| **None** | All systems operational | Full features |
| **Reduced** | Some services degraded | Core features only |
| **Minimal** | Major outage | Read-only, queue writes |
| **Maintenance** | Critical failure | Paused, manual only |

### Automatic Retry

- Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 retries)
- Jitter: ±25% to prevent thundering herd
- Dead letter queue for permanent failures

---

## Audit Logging & Compliance

### Immutable Audit Trail

Every action creates a hash-chained audit entry:

```json
{
  "event_id": "20260115103045_1234",
  "timestamp": "2026-01-15T10:30:45.123Z",
  "event_type": "invoice_created",
  "component": "odoo_mcp",
  "actor": "ai",
  "action": "create_invoice",
  "resource": "invoice_INV-2026-001",
  "result": "success",
  "details": {"amount": 1500, "partner": "Acme Corp"},
  "previous_hash": "a1b2c3d4...",
  "current_hash": "e5f6g7h8..."
}
```

### Verification

```bash
# Verify chain integrity
python -c "
from audit_logger import AuditLogger
logger = AuditLogger('AI_Employee_Vault')
result = logger.verify_chain('2026-01-01', '2026-01-31')
print('Verified:', result['verified'])
print('Errors:', result['errors'])
"
```

### Export for Auditors

```bash
# JSONL (full detail)
python audit_logger.py export audit_jan.jsonl --start 2026-01-01 --end 2026-01-31

# CSV (summary)
python audit_logger.py export audit_jan.csv --format csv --start 2026-01-01

# Compliance package
python audit_logger.py package compliance_2026_q1.zip --quarter 1
```

### Retention Policy

- **Default**: 7 years (2555 days) - SOX/GAAP compliant
- **Financial**: 7 years minimum
- **Operational**: 3 years
- **Debug logs**: 30 days

---

## MCP Server Architecture

Gold Tier uses **specialized MCP servers** for each domain:

```
┌────────────────────────────────────────────────────────────┐
│                    AI Employee Client                       │
│                        (Qwen Code)                           │
└──────────────────────┬─────────────────────────────────────┘
                       │ MCP Protocol (JSON-RPC)
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌───────────────┐ ┌───────────┐ ┌─────────────┐
│  Odoo MCP     │ │ Calendar  │ │  Web Search │
│  (Accounting) │ │ (Sched.)  │ │  (Research) │
└───────────────┘ └───────────┘ └─────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌───────────┐ ┌─────────────┐
│  Odoo ERP     │ │ Google    │ │  Search     │
│  (Local/Cloud)│ │ Calendar  │ │  APIs       │
└───────────────┘ └───────────┘ └─────────────┘

        ┌──────────────┐ ┌──────────────┐
        │   Email      │ │   Social     │
        │   MCP        │ │   MCP*       │
        └──────────────┘ └──────────────┘
               │               │
               ▼               ▼
        ┌───────────┐   ┌─────────────┐
        │  SMTP/    │   │  Playwright │
        │  IMAP     │   │  (Browser)  │
        └───────────┘   └─────────────┘

*Social MCP = skills using Playwright (no separate MCP server)
```

### Adding Custom MCP Servers

1. Create `mcp-servers/your-service/your_mcp.py`
2. Implement `list_tools()` and `call_tool()`
3. Add to `mcp.json` config
4. Restart client

---

## Monitoring & Observability

### Health Dashboard

```bash
# Component health
python -c "
from error_recovery import get_error_recovery
er = get_error_recovery('AI_Employee_Vault')
print(er.get_component_health())
"

# Error summary (24h)
python -c "
from error_recovery import get_error_recovery
er = get_error_recovery('AI_Employee_Vault')
print(er.get_error_summary(24))
"
```

### Key Metrics to Watch

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Orchestrator loop time | < 5s | 5-30s | > 30s |
| Error rate (1h) | 0 | 1-5 | > 5 |
| Circuit breakers open | 0 | 1 | > 1 |
| Pending approvals | < 5 | 5-20 | > 20 |
| Audit chain verified | ✅ | ⚠️ | ❌ |

### Log Locations

```
AI_Employee_Vault/Logs/
├── orchestrator.log       # Main process
├── errors.log             # All errors (JSONL)
├── degradation.log        # Degradation events
├── audit_YYYY-MM-DD.jsonl # Daily audit logs
├── component_health.json  # Current health
└── watchers/              # Per-watcher logs
```

---

## Security Considerations

### Credential Management

- **Never commit** credentials to git
- Use environment variables or `.env` files
- Rotate tokens quarterly
- Use service accounts where possible

### Network Security

- Run locally (no cloud exposure)
- MCP servers communicate via stdio
- No inbound ports required
- Outbound only to configured APIs

### Data Privacy

- All data stays in Obsidian vault
- No telemetry or analytics
- Audit logs contain operational metadata only
- PII in vault is user-controlled

---

## Troubleshooting

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Circuit breaker open" | Service down | Check service, wait for auto-recovery |
| "Audit chain broken" | Tampering or corruption | Restore from backup, investigate |
| "Playwright timeout" | Slow page load | Increase timeout, check network |
| "Odoo auth failed" | Token expired | Re-authenticate, check credentials |
| "No tasks processed" | Orchestrator stopped | Check logs, restart orchestrator |

### Debug Mode

```bash
# Verbose orchestrator
python orchestrator.py --interval 10 2>&1 | tee debug.log

# Single skill test
python .qwen/skills/twitter-poster/twitter_poster.py --content "Test" --headless false

# MCP server debug
python mcp-servers/odoo-accounting/odoo_mcp_server.py 2>&1 | tee mcp_debug.log
```

### Reset Procedures

```bash
# Reset circuit breakers
python -c "
from error_recovery import get_error_recovery
er = get_error_recovery('AI_Employee_Vault')
for cb in er.circuit_breakers.values():
    cb.reset()
print('All circuit breakers reset')
"

# Clear audit chain (DANGEROUS - only for testing)
rm AI_Employee_Vault/Audits/audit_*.jsonl
rm AI_Employee_Vault/Logs/audit_*.jsonl

# Re-authenticate all services
rm watchers/*/session/state.json
rm watchers/*/token.json
# Re-run auth for each
```

---

## Performance Tuning

### Orchestrator Intervals

| Workload | Check Interval | Ralph Delay |
|----------|---------------|-------------|
| Light (personal) | 120s | 60s |
| Standard (SMB) | 60s | 30s |
| Heavy (enterprise) | 30s | 15s |

### Resource Limits

```python
# In orchestrator.py
MAX_CONCURRENT_WATCHERS = 4
QWEN_TIMEOUT = 300  # 5 minutes
MCP_TIMEOUT = 60
PLAYWRIGHT_TIMEOUT = 120
```

### Scaling

- **Horizontal**: Multiple orchestrator instances (different vaults)
- **Vertical**: Increase timeouts, add memory
- **MCP**: Run on separate machines, connect via network MCP

---

## Migration from Silver Tier

```bash
# 1. Backup
cp -r AI_Employee_Vault AI_Employee_Vault_backup

# 2. Pull latest code
git pull

# 3. Install new dependencies
pip install -r requirements.txt
pip install -r mcp-servers/odoo-accounting/requirements.txt
pip install -r mcp-servers/web-search/requirements.txt
pip install -r mcp-servers/calendar/requirements.txt
playwright install chromium

# 4. Create new vault folders
mkdir AI_Employee_Vault/Odoo
mkdir AI_Employee_Vault/Social
mkdir AI_Employee_Vault/Audits

# 5. Configure new services
# Edit .env files for Odoo, Calendar, Search APIs

# 6. Authenticate new services
python mcp-servers/calendar/calendar_mcp.py
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py --auth both
python .qwen/skills/twitter-poster/twitter_poster.py --auth

# 7. Test
test-gold-tier.bat

# 8. Run
start-gold-tier.bat
```

---

## Roadmap

### Gold Tier v0.3 (Current)
- ✅ Odoo Accounting MCP
- ✅ Facebook/Instagram/Twitter Skills
- ✅ Calendar MCP
- ✅ Web Search MCP
- ✅ Ralph Wiggum Loop
- ✅ Circuit Breakers
- ✅ Audit Logging

### Gold Tier v0.4 (Planned)
- [ ] Multi-user support
- [ ] Plugin marketplace for skills
- [ ] Advanced ML categorization
- [ ] Mobile app for approvals
- [ ] Kubernetes deployment
- [ ] Grafana/Prometheus metrics

### Platinum Tier (Future)
- [ ] Multi-agent coordination
- [ ] Cross-organization workflows
- [ ] Advanced RAG with vector DB
- [ ] Voice interface
- [ ] Compliance certifications (SOC2, ISO27001)

---

## Support & Community

- **Documentation**: This README + inline code docs
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@example.com

---

## License

MIT License - See LICENSE file

---

*Gold Tier Implementation - AI Employee v0.3*  
*Built with ❤️ for autonomous business operations*
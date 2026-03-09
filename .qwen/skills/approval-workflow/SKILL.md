---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions.
  Creates approval requests, monitors for user approval, and executes
  approved actions. Use for email sending, payments, social media posts,
  and any action requiring human oversight.
---

# Approval Workflow

Human-in-the-loop (HITL) pattern for sensitive actions.

## Overview

For sensitive actions, the AI Employee creates an approval request file
instead of acting directly. The user reviews and approves/rejects by
moving the file between folders.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/    # Awaiting user review
├── Approved/            # User approved, execute action
├── Rejected/            # User rejected, archive
└── Done/                # Completed actions
```

## Workflow

### Step 1: Create Approval Request

When a sensitive action is needed, create a file in `/Pending_Approval/`:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #1234
amount: 500.00
created: 2026-03-09T10:30:00Z
expires: 2026-03-10T10:30:00Z
status: pending
---

# Approval Request

## Action Details
- **Type:** Send Email
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Amount:** $500.00

## Content
[Email body or action details]

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Created by AI Employee at 2026-03-09T10:30:00Z*
```

### Step 2: User Review

User reviews the file in Obsidian and:
- **Approves:** Move file to `/Approved/`
- **Rejects:** Move file to `/Rejected/`

### Step 3: Execute Action

Orchestrator detects approved files and executes:

```python
# In orchestrator.py
def check_approved_actions(self):
    files = list(self.approved.glob('*.md'))
    for f in files:
        execute_approved_action(f)
        f.rename(self.done / f.name)
```

### Step 4: Log and Archive

After execution:
- Log action in `/Logs/`
- Move file to `/Done/`

---

## Approval Thresholds

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email replies | Known contacts | New contacts, bulk |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move |

---

## Python Implementation

### Create Approval Request

```python
from pathlib import Path
from datetime import datetime, timedelta

def create_approval_request(vault_path: str, action_type: str, 
                            details: dict) -> Path:
    """Create approval request file."""
    
    pending_dir = Path(vault_path) / 'Pending_Approval'
    pending_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'APPROVAL_{action_type}_{timestamp}.md'
    
    # Create content
    content = f'''---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

# Approval Request

## Action Details
'''
    
    for key, value in details.items():
        content += f'- **{key}:** {value}\n'
    
    content += f'''

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Created by AI Employee at {datetime.now().isoformat()}*
'''
    
    filepath = pending_dir / filename
    filepath.write_text(content)
    
    return filepath
```

### Check for Approved Actions

```python
def process_approved_actions(vault_path: str) -> list:
    """Process approved actions and return executed actions."""
    
    approved_dir = Path(vault_path) / 'Approved'
    done_dir = Path(vault_path) / 'Done'
    executed = []
    
    for filepath in approved_dir.glob('*.md'):
        try:
            # Read approval details
            content = filepath.read_text()
            details = parse_approval_content(content)
            
            # Execute the action
            result = execute_action(details)
            
            if result['success']:
                # Move to Done
                filepath.rename(done_dir / filepath.name)
                executed.append({
                    'file': filepath.name,
                    'action': details.get('action'),
                    'result': 'success'
                })
            else:
                executed.append({
                    'file': filepath.name,
                    'action': details.get('action'),
                    'result': f'failed: {result["error"]}'
                })
                
        except Exception as e:
            executed.append({
                'file': filepath.name,
                'result': f'error: {str(e)}'
            })
    
    return executed
```

### Execute Action Based on Type

```python
def execute_action(details: dict) -> dict:
    """Execute action based on type."""
    
    action_type = details.get('action', '')
    
    if action_type == 'send_email':
        return send_email_action(details)
    elif action_type == 'post_linkedin':
        return post_linkedin_action(details)
    elif action_type == 'payment':
        return payment_action(details)
    else:
        return {'success': False, 'error': f'Unknown action: {action_type}'}


def send_email_action(details: dict) -> dict:
    """Send email action."""
    # Use email MCP or SMTP
    try:
        # Implementation depends on your email setup
        result = send_email(
            to=details.get('to'),
            subject=details.get('subject'),
            body=details.get('body')
        )
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def post_linkedin_action(details: dict) -> dict:
    """Post to LinkedIn action."""
    # Use LinkedIn poster skill
    try:
        result = post_to_linkedin(
            content=details.get('content'),
            image=details.get('image')
        )
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

## Qwen Code Usage

### Create Approval Request

```bash
qwen --cwd "AI_Employee_Vault" "Create an approval request to send an email to client@example.com with subject 'Project Update' and body 'The project is on track.'"
```

### Check Pending Approvals

```bash
qwen --cwd "AI_Employee_Vault" "List all pending approval requests and summarize what actions are waiting"
```

### Process Approved Actions

```bash
qwen --cwd "AI_Employee_Vault" "Check the Approved folder and execute all approved actions, then move them to Done"
```

---

## Monitoring Script

```python
# approval_monitor.py
import time
from pathlib import Path

def monitor_approvals(vault_path: str, check_interval: int = 30):
    """Monitor for approved actions and execute them."""
    
    approved_dir = Path(vault_path) / 'Approved'
    
    print(f"Monitoring {approved_dir} for approved actions...")
    
    while True:
        approved_files = list(approved_dir.glob('*.md'))
        
        if approved_files:
            print(f"Found {len(approved_files)} approved action(s)")
            for f in approved_files:
                print(f"  - {f.name}")
                execute_and_archive(f, vault_path)
        
        time.sleep(check_interval)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not detected | Ensure file has .md extension |
| Action fails | Check logs in /Logs/ folder |
| Approval stuck | Verify file was moved to Approved/ |
| Duplicate execution | Check file was moved to Done/ |

---

## Security Notes

⚠️ **Important:**
- Never auto-approve payments to new recipients
- Always require approval for bulk emails
- Review all social media posts before posting
- Log all actions for audit trail

---

*Approval Workflow Skill - AI Employee v0.2*

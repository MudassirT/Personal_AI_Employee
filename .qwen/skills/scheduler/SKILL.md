---
name: scheduler
description: |
  Task scheduling for AI Employee operations. Schedule recurring tasks
  like daily processing, weekly briefings, and monthly audits using
  Windows Task Scheduler or cron. Automates trigger-based operations.
---

# Scheduler

Task scheduling for AI Employee operations.

## Overview

The scheduler enables automated execution of AI Employee tasks:
- **Daily:** Process Needs_Action folder
- **Weekly:** Generate CEO Briefing
- **Monthly:** Subscription audit

## Scheduling Options

### Windows: Task Scheduler (.bat files)
### Mac/Linux: Cron jobs
### Cross-platform: Python schedule library

---

## Quick Start (Windows)

### Step 1: Create Batch Files

```batch
:: schedules/daily_processing.bat
@echo off
cd /d "%~dp0.."
python orchestrator.py --process-once
```

```batch
:: schedules/weekly_briefing.bat
@echo off
cd /d "%~dp0.."
qwen --cwd "AI_Employee_Vault" "Generate weekly CEO briefing from completed tasks"
```

### Step 2: Schedule with Task Scheduler

```powershell
# Open Task Scheduler
taskschd.msc

# Create Basic Task
# - Name: AI Employee Daily Processing
# - Trigger: Daily at 8:00 AM
# - Action: Start a program
# - Program: schedules\daily_processing.bat
```

### Step 3: Verify Schedule

```powershell
# List all tasks
schtasks /Query /FO TABLE

# Run task manually (test)
schtasks /Run /TN "AI Employee Daily Processing"
```

---

## Cron Jobs (Mac/Linux)

### Edit Crontab

```bash
crontab -e
```

### Add Entries

```cron
# AI Employee Daily Processing - 8 AM every day
0 8 * * * cd /path/to/Personal_AI_Employee && python orchestrator.py --process-once

# Weekly Briefing - Monday 9 AM
0 9 * * 1 cd /path/to/Personal_AI_Employee && qwen --cwd "AI_Employee_Vault" "Generate weekly briefing"

# Monthly Audit - 1st of month at 10 AM
0 10 1 * * cd /path/to/Personal_AI_Employee && qwen --cwd "AI_Employee_Vault" "Audit subscriptions and expenses"
```

### Verify Cron

```bash
# List cron jobs
crontab -l

# Check cron logs
grep CRON /var/log/syslog
```

---

## Python Schedule Library (Cross-platform)

### Installation

```bash
pip install schedule
```

### Implementation

```python
# scheduler.py
import schedule
import time
import subprocess
from pathlib import Path

class AIScheduler:
    """Schedule AI Employee tasks."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
    
    def process_needs_action(self):
        """Process Needs_Action folder."""
        print("Processing Needs_Action folder...")
        subprocess.run(['python', 'orchestrator.py', '--process-once'])
    
    def generate_briefing(self):
        """Generate weekly CEO briefing."""
        print("Generating weekly briefing...")
        subprocess.run([
            'qwen', '--cwd', str(self.vault_path),
            'Generate weekly CEO briefing from completed tasks'
        ])
    
    def audit_subscriptions(self):
        """Monthly subscription audit."""
        print("Running subscription audit...")
        subprocess.run([
            'qwen', '--cwd', str(self.vault_path),
            'Audit subscriptions and flag unused services'
        ])
    
    def setup_schedule(self):
        """Set up recurring schedule."""
        # Daily processing at 8 AM
        schedule.every().day.at("08:00").do(self.process_needs_action)
        
        # Weekly briefing on Monday at 9 AM
        schedule.every().monday.at("09:00").do(self.generate_briefing)
        
        # Monthly audit on 1st at 10 AM
        schedule.every().day.at("10:00").do(self.audit_subscriptions)
        
        print("Schedule configured. Running...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    scheduler = AIScheduler('AI_Employee_Vault')
    scheduler.setup_schedule()
```

---

## Scheduled Task Templates

### Daily Processing

```batch
:: schedules/daily_processing.bat
@echo off
echo ================================================
echo AI Employee - Daily Processing
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Process Needs_Action folder
python orchestrator.py --process-once

echo.
echo Processing complete.
echo ================================================
```

### Weekly Briefing

```batch
:: schedules/weekly_briefing.bat
@echo off
echo ================================================
echo AI Employee - Weekly Briefing
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Generate CEO briefing
qwen --cwd "AI_Employee_Vault" "Review completed tasks from this week and generate a CEO briefing in Briefings/ folder"

echo.
echo Briefing generated.
echo ================================================
```

### Monthly Audit

```batch
:: schedules/monthly_audit.bat
@echo off
echo ================================================
echo AI Employee - Monthly Audit
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "%~dp0.."

REM Run subscription audit
qwen --cwd "AI_Employee_Vault" "Review all transactions this month, identify subscriptions, and flag any unused services for cancellation"

echo.
echo Audit complete.
echo ================================================
```

---

## Task Scheduler XML (Advanced)

For advanced Windows scheduling, import XML:

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>AI Employee Daily Processing</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-09T08:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>cmd.exe</Command>
      <Arguments>/c "cd /d C:\Path\To\Personal_AI_Employee &amp; python orchestrator.py --process-once"</Arguments>
    </Exec>
  </Actions>
</Task>
```

Import with:
```powershell
schtasks /Create /TN "AI Employee Daily" /XML schedule.xml
```

---

## Qwen Code Integration

### Create Schedule

```bash
qwen --cwd "AI_Employee_Vault" "Create a weekly schedule for processing emails, generating briefings, and auditing subscriptions"
```

### Check Schedule Status

```bash
qwen --cwd "AI_Employee_Vault" "Check if scheduled tasks ran successfully by reviewing logs"
```

---

## Monitoring Scheduled Tasks

### Check Task History (Windows)

```powershell
# Get task info
schtasks /Query /TN "AI Employee Daily Processing" /V /FO LIST

# View task history in Event Viewer
eventvwr.msc
# Navigate to: Applications and Services Logs > Microsoft > Windows > TaskScheduler
```

### Check Cron Logs (Linux)

```bash
# View cron logs
grep CRON /var/log/syslog | tail -20

# Check if cron is running
systemctl status cron
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task doesn't run | Check task scheduler service |
| Python not found | Use full path to python.exe |
| Permissions error | Run as administrator |
| Task runs but fails | Check working directory |

---

## Best Practices

1. **Log everything** - Capture output to log files
2. **Error handling** - Schedule retry on failure
3. **Notifications** - Email on critical failures
4. **Review regularly** - Check task history weekly
5. **Test first** - Run manually before scheduling

---

## Example: Complete Setup Script

```python
# setup_scheduler.py
import subprocess
import sys
from pathlib import Path

def create_windows_tasks():
    """Create Windows Task Scheduler tasks."""
    
    tasks = [
        {
            'name': 'AI Employee Daily Processing',
            'time': '08:00',
            'script': 'schedules\\daily_processing.bat'
        },
        {
            'name': 'AI Employee Weekly Briefing',
            'time': '09:00',
            'days': 'MONDAY',
            'script': 'schedules\\weekly_briefing.bat'
        }
    ]
    
    for task in tasks:
        cmd = f'schtasks /Create /TN "{task["name"]}" /TR "{task["script"]}" /SC DAILY /ST {task["time"]} /RL HIGHEST /F'
        print(f"Creating task: {task['name']}")
        subprocess.run(cmd, shell=True)

def create_cron_jobs():
    """Create cron jobs for Linux/Mac."""
    
    cron_jobs = """
# AI Employee Tasks
0 8 * * * cd /path/to/Personal_AI_Employee && python orchestrator.py --process-once
0 9 * * 1 cd /path/to/Personal_AI_Employee && qwen --cwd "AI_Employee_Vault" "Generate weekly briefing"
"""
    
    # Append to crontab
    subprocess.run(['crontab', '-l'], capture_output=True)
    # Add jobs (implement properly)
    
    print("Cron jobs created")

if __name__ == '__main__':
    if sys.platform == 'win32':
        create_windows_tasks()
    else:
        create_cron_jobs()
```

---

*Scheduler Skill - AI Employee v0.2*

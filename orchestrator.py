"""
<<<<<<< HEAD
Orchestrator - Master process for the AI Employee (Gold Tier Enhanced).
=======
Orchestrator - Master process for the AI Employee.
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process items
3. Updates the Dashboard with activity
4. Manages the overall workflow
<<<<<<< HEAD
5. Error recovery and graceful degradation
6. Ralph Wiggum loop for autonomous task completion

Usage:
    python orchestrator.py                    # Continuous mode
    python orchestrator.py --process-once     # Single run (scheduled)
    python orchestrator.py --ralph-loop 10    # Autonomous mode (10 iterations)
=======

For Bronze Tier: Simple file-based orchestration that prepares tasks
for Qwen Code processing.

Usage:
    python orchestrator.py
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
"""

import os
import sys
import time
import logging
import subprocess
<<<<<<< HEAD
import json
import signal
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_APPROVAL = "needs_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class TaskRecord:
    """Record of a task execution."""
    task_id: str
    source_file: str
    file_type: str
    status: TaskStatus
    created: str
    started: Optional[str] = None
    completed: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    plan_file: Optional[str] = None
    approval_file: Optional[str] = None


class CircuitBreaker:
    """Circuit breaker for external service failures."""
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == "open":
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                self.state = "half-open"
                self.failure_count = 0
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class ErrorRecoveryManager:
    """Manages error recovery and graceful degradation."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_history: List[Dict] = []
        self.max_error_history = 100
    
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        return self.circuit_breakers[name]
    
    def record_error(self, component: str, error: Exception, context: Dict = None):
        """Record an error for analysis."""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        # Log to file
        log_file = self.logs_dir / "errors.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(error_record) + "\n")
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """Get error summary for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            e for e in self.error_history
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        by_component = {}
        by_type = {}
        for e in recent_errors:
            by_component[e["component"]] = by_component.get(e["component"], 0) + 1
            by_type[e["error_type"]] = by_type.get(e["error_type"], 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "by_component": by_component,
            "by_type": by_type,
            "recent": recent_errors[-10:]  # Last 10 errors
        }
    
    def should_retry(self, component: str, error: Exception) -> bool:
        """Determine if an operation should be retried."""
        # Don't retry if circuit breaker is open
        cb = self.get_circuit_breaker(component)
        if cb.state == "open":
            return False
        
        # Don't retry certain error types
        non_retryable = [
            "AuthenticationError", "PermissionError", 
            "ValidationError", "ConfigurationError"
        ]
        if type(error).__name__ in non_retryable:
            return False
        
        return True
    
    def degrade_gracefully(self, component: str, fallback_action: str = None):
        """Handle graceful degradation when a component fails."""
        self.log_degradation(component, fallback_action)
        
        # Create a notification for manual intervention
        self._create_degradation_notice(component, fallback_action)
    
    def log_degradation(self, component: str, fallback: str):
        """Log degradation event."""
        log_file = self.logs_dir / "degradation.log"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "fallback": fallback,
            "action": "graceful_degradation"
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _create_degradation_notice(self, component: str, fallback: str):
        """Create a notice file for manual intervention."""
        notice_dir = self.vault_path / "Needs_Action"
        notice_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        notice_file = notice_dir / f"DEGRADATION_{component}_{timestamp}.md"
        
        content = f"""---
type: degradation_notice
component: {component}
fallback: {fallback or 'Manual intervention required'}
created: {datetime.now().isoformat()}
priority: high
---

# System Degradation Notice

## Component: {component}
**Status:** Failed - Running in degraded mode

## Fallback Action:
{fallback or 'Requires manual intervention'}

## Impact:
This component is temporarily unavailable. The system will continue
processing other tasks, but {component}-related actions will be queued
or require manual handling.

## Resolution:
1. Check error logs in `/Logs/errors.log`
2. Verify {component} service is running
3. Check credentials and connectivity
4. Restart the affected watcher/service

---
*Generated by Error Recovery Manager*
"""
        notice_file.write_text(content)


class RalphWiggumLoop:
    """Autonomous task processing loop (Ralph Wiggum pattern)."""
    
    def __init__(self, orchestrator, max_iterations: int = 10, 
                 iteration_delay: int = 30, progress_threshold: int = 0):
        self.orchestrator = orchestrator
        self.max_iterations = max_iterations
        self.iteration_delay = iteration_delay
        self.progress_threshold = progress_threshold
        self.iteration = 0
        self.tasks_completed = 0
        self.logger = orchestrator.logger
    
    def run(self) -> Dict[str, Any]:
        """Run the autonomous loop."""
        self.logger.info(f"Starting Ralph Wiggum Loop: max {self.max_iterations} iterations")
        
        results = {
            "iterations": 0,
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "approvals_created": 0,
            "errors": []
        }
        
        for self.iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"=== Ralph Loop Iteration {self.iteration}/{self.max_iterations} ===")
            
            iteration_results = self._run_iteration()
            
            results["iterations"] += 1
            results["tasks_processed"] += iteration_results.get("processed", 0)
            results["tasks_completed"] += iteration_results.get("completed", 0)
            results["tasks_failed"] += iteration_results.get("failed", 0)
            results["approvals_created"] += iteration_results.get("approvals", 0)
            results["errors"].extend(iteration_results.get("errors", []))
            
            # Check if we made progress
            if iteration_results.get("processed", 0) == 0:
                self.logger.info("No tasks processed this iteration. Checking for pending approvals...")
                if not self._has_pending_work():
                    self.logger.info("No pending work. Stopping early.")
                    break
            
            # Wait before next iteration
            if self.iteration < self.max_iterations:
                self.logger.info(f"Waiting {self.iteration_delay}s before next iteration...")
                time.sleep(self.iteration_delay)
        
        self.logger.info(f"Ralph Wiggum Loop completed: {results}")
        return results
    
    def _run_iteration(self) -> Dict[str, int]:
        """Run a single iteration of the loop."""
        results = {"processed": 0, "completed": 0, "failed": 0, "approvals": 0, "errors": []}
        
        try:
            # Process Needs_Action
            self.orchestrator.update_dashboard()
            files = self.orchestrator.get_needs_action_files()
            
            if files:
                self.logger.info(f"Processing {len(files)} files in Needs_Action")
                self.orchestrator.process_needs_action()
                results["processed"] = len(files)
            
            # Check for approved actions
            self.orchestrator.check_approved_actions()
            
            # Trigger Qwen Code for processing (if available)
            # This would be the autonomous part - triggering AI to process plans
            qwen_triggered = self._trigger_qwen_processing()
            if qwen_triggered:
                results["completed"] += 1
            
        except Exception as e:
            error_msg = f"Iteration {self.iteration} error: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            results["failed"] += 1
            self.orchestrator.error_recovery.record_error("ralph_loop", e, {"iteration": self.iteration})
        
        return results
    
    def _trigger_qwen_processing(self) -> bool:
        """Trigger Qwen Code to process plans. Returns True if triggered."""
        try:
            # Check if there are plans ready for processing
            plans = list(self.orchestrator.plans.glob("PLAN_*_ready_for_qwen.md"))
            if not plans:
                # Check for any plan files
                plans = list(self.orchestrator.plans.glob("PLAN_*.md"))
            
            if plans:
                # Create a trigger file for Qwen
                trigger_file = self.orchestrator.vault_path / ".qwen_trigger"
                trigger_file.write_text(f"Process all plans in Plans/ at {datetime.now().isoformat()}")
                self.logger.info(f"Created Qwen trigger for {len(plans)} plans")
                return True
        except Exception as e:
            self.logger.debug(f"Qwen trigger check failed: {e}")
        return False
    
    def _has_pending_work(self) -> bool:
        """Check if there's pending work."""
        # Check Needs_Action
        if list(self.orchestrator.needs_action.glob("*.md")):
            return True
        # Check Approved
        if list(self.orchestrator.approved.glob("*.md")):
            return True
        # Check Pending_Approval (waiting for human)
        if list(self.orchestrator.pending_approval.glob("*.md")):
            return True
        return False
=======
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73


class Orchestrator:
    """
<<<<<<< HEAD
    Main orchestrator for the AI Employee system (Gold Tier).
    
    Coordinates between watchers, Qwen Code, and the Obsidian vault.
    Includes error recovery, circuit breakers, and autonomous mode.
=======
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the Obsidian vault.
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.running = False
        
        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.plans = self.vault_path / 'Plans'
        self.logs_dir = self.vault_path / 'Logs'
        
        # Files
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        self.goals = self.vault_path / 'Business_Goals.md'
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Setup logging
        self.logger = self._setup_logging()
        
<<<<<<< HEAD
        # Error recovery manager
        self.error_recovery = ErrorRecoveryManager(vault_path)
        
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        # Statistics
        self.stats = {
            'tasks_processed': 0,
            'tasks_pending_approval': 0,
            'tasks_completed_today': 0,
<<<<<<< HEAD
            'last_activity': None,
            'errors_recovered': 0,
            'degradations': 0
        }
        
        # Task tracking
        self.task_records: Dict[str, TaskRecord] = {}
        self._load_task_records()
=======
            'last_activity': None
        }
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.needs_action,
            self.in_progress,
            self.done,
            self.pending_approval,
            self.approved,
            self.plans,
<<<<<<< HEAD
            self.logs_dir,
            self.vault_path / 'Odoo',
            self.vault_path / 'Social',
            self.vault_path / 'Audits'
=======
            self.logs_dir
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('Orchestrator')
        logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self.logs_dir / 'orchestrator.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
<<<<<<< HEAD
    def _load_task_records(self):
        """Load task records from disk."""
        records_file = self.logs_dir / "task_records.json"
        if records_file.exists():
            try:
                with open(records_file) as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v['status'] = TaskStatus(v['status'])
                        self.task_records[k] = TaskRecord(**v)
            except Exception as e:
                self.logger.error(f"Failed to load task records: {e}")
    
    def _save_task_records(self):
        """Save task records to disk."""
        records_file = self.logs_dir / "task_records.json"
        try:
            data = {}
            for k, v in self.task_records.items():
                d = asdict(v)
                d['status'] = v.status.value
                data[k] = d
            with open(records_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save task records: {e}")
    
    def _create_task_record(self, filepath: Path) -> TaskRecord:
        """Create a new task record."""
        content = filepath.read_text(encoding='utf-8')
        file_type = self._extract_metadata(content, 'type', 'unknown')
        
        task_id = f"{file_type}_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = TaskRecord(
            task_id=task_id,
            source_file=filepath.name,
            file_type=file_type,
            status=TaskStatus.PENDING,
            created=datetime.now().isoformat()
        )
        self.task_records[task_id] = record
        self._save_task_records()
        return record
    
    def _update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """Update task record status."""
        if task_id in self.task_records:
            record = self.task_records[task_id]
            record.status = status
            if status == TaskStatus.IN_PROGRESS and not record.started:
                record.started = datetime.now().isoformat()
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                record.completed = datetime.now().isoformat()
            for k, v in kwargs.items():
                if hasattr(record, k):
                    setattr(record, k, v)
            self._save_task_records()
    
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    def count_files(self, directory: Path) -> int:
        """Count .md files in a directory."""
        if not directory.exists():
            return 0
        return len(list(directory.glob('*.md')))
    
    def get_needs_action_files(self) -> List[Path]:
        """Get list of files in Needs_Action folder."""
        if not self.needs_action.exists():
            return []
        return sorted(self.needs_action.glob('*.md'), 
                     key=lambda f: f.stat().st_mtime)
    
    def update_dashboard(self):
        """Update the Dashboard.md with current statistics."""
        try:
            # Count files in each directory
            inbox_count = self.count_files(self.vault_path / 'Inbox')
            needs_action_count = self.count_files(self.needs_action)
            in_progress_count = self.count_files(self.in_progress)
            pending_approval_count = self.count_files(self.pending_approval)
            done_today = self.count_files(self.done)  # Simplified
            
            # Update stats
            self.stats['tasks_pending_approval'] = pending_approval_count
            
            # Read current dashboard
            if self.dashboard.exists():
                content = self.dashboard.read_text(encoding='utf-8')
                
                # Update counts
                content = self._update_table_value(content, 'Tasks in Inbox', str(inbox_count))
                content = self._update_table_value(content, 'Tasks Needing Action', str(needs_action_count))
                content = self._update_table_value(content, 'Tasks In Progress', str(in_progress_count))
                content = self._update_table_value(content, 'Pending Approval', str(pending_approval_count))
                content = self._update_table_value(content, 'Tasks Completed Today', str(done_today))
                
                # Update last activity
                if self.stats['last_activity']:
                    content = content.replace(
                        '**Last Activity:** --',
                        f"**Last Activity:** {self.stats['last_activity']}"
                    )
                
                # Update pending approvals section
                pending_section = self._generate_pending_approvals()
                content = self._replace_section(content, 'Pending Approvals', pending_section)
                
                # Write updated dashboard
                self.dashboard.write_text(content, encoding='utf-8')
                
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
<<<<<<< HEAD
            self.error_recovery.record_error("dashboard", e)
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    
    def _update_table_value(self, content: str, label: str, value: str) -> str:
        """Update a value in a markdown table."""
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if f'| {label}' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    parts[2] = f' {value} '
                    line = '|'.join(parts)
            new_lines.append(line)
        return '\n'.join(new_lines)
    
    def _replace_section(self, content: str, section_title: str, new_content: str) -> str:
        """Replace content under a section header."""
        lines = content.split('\n')
        new_lines = []
        in_section = False
        
        for line in lines:
            if line.strip().startswith('##') and section_title.lower() in line.lower():
                new_lines.append(line)
                new_lines.append('')
                new_lines.append(new_content)
                in_section = True
            elif in_section and line.strip().startswith('##'):
                in_section = False
                new_lines.append(line)
            elif not in_section:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _generate_pending_approvals(self) -> str:
        """Generate pending approvals section content."""
        files = list(self.pending_approval.glob('*.md'))
        if not files:
            return '*No pending approvals*\n'
        
        lines = []
        for f in files:
            lines.append(f'- 📄 [{f.name}](file://{f})')
        return '\n'.join(lines)
    
    def log_activity(self, action: str, details: str):
        """Log an activity to the dashboard and logs."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stats['last_activity'] = timestamp
        
        # Add to dashboard recent activity
        try:
            if self.dashboard.exists():
                content = self.dashboard.read_text(encoding='utf-8')
                
                activity_line = f'- [{timestamp}] {action}: {details}'
                
                # Find Recent Activity section and add line
                lines = content.split('\n')
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if '## Recent Activity' in line:
                        new_lines.append('')
                        new_lines.append(activity_line)
                
                content = '\n'.join(new_lines)
                self.dashboard.write_text(content, encoding='utf-8')
        except Exception as e:
            self.logger.error(f'Error logging to dashboard: {e}')
        
        # Also log to file
        self.logger.info(f'{action}: {details}')
    
    def process_needs_action(self):
        """
<<<<<<< HEAD
        Process files in Needs_Action folder with error recovery.
=======
        Process files in Needs_Action folder.
        
        For Bronze Tier: This prepares files for Claude Code processing
        and provides instructions for the user.
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        """
        files = self.get_needs_action_files()
        
        if not files:
            self.logger.debug('No files in Needs_Action')
            return
        
        self.logger.info(f'Found {len(files)} file(s) to process')
        
        for filepath in files:
<<<<<<< HEAD
            task_record = self._create_task_record(filepath)
            self._update_task_status(task_record.task_id, TaskStatus.IN_PROGRESS)
            
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
            try:
                self.logger.info(f'Processing: {filepath.name}')
                
                # Read the file to understand its type
                content = filepath.read_text(encoding='utf-8')
                
                # Extract metadata from frontmatter
                file_type = self._extract_metadata(content, 'type', 'unknown')
                priority = self._extract_metadata(content, 'priority', 'normal')
                
                # Log activity
                self.log_activity('Processing', f'{file_type} from {filepath.name}')
                
<<<<<<< HEAD
                # Move to In_Progress
                in_progress_path = self.in_progress / filepath.name
                filepath.rename(in_progress_path)
                
                # Create a plan file
                self._create_plan(filepath, content, task_record)
                
                # Update stats
                self.stats['tasks_processed'] += 1
                self._update_task_status(task_record.task_id, TaskStatus.COMPLETED, 
                                       plan_file=task_record.plan_file)
                
            except Exception as e:
                self.logger.error(f'Error processing {filepath.name}: {e}')
                self.error_recovery.record_error("process_needs_action", e, {"file": filepath.name})
                
                # Move back to Needs_Action for retry
                if filepath.exists():
                    filepath.rename(self.needs_action / filepath.name)
                elif (self.in_progress / filepath.name).exists():
                    (self.in_progress / filepath.name).rename(self.needs_action / filepath.name)
                
                self._update_task_status(task_record.task_id, TaskStatus.FAILED, 
                                       error=str(e), retry_count=task_record.retry_count + 1)
                
                # Check if should retry
                if task_record.retry_count < task_record.max_retries:
                    self.logger.info(f"Will retry {filepath.name} (attempt {task_record.retry_count + 1}/{task_record.max_retries})")
                else:
                    self.logger.error(f"Max retries exceeded for {filepath.name}")
=======
                # For Bronze Tier: Create a plan file
                self._create_plan(filepath, content)
                
                # Update stats
                self.stats['tasks_processed'] += 1
                
            except Exception as e:
                self.logger.error(f'Error processing {filepath.name}: {e}')
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    
    def _extract_metadata(self, content: str, key: str, default: str = '') -> str:
        """Extract metadata from YAML frontmatter."""
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            
            if in_frontmatter and ':' in line:
                k, v = line.split(':', 1)
                if k.strip() == key:
                    return v.strip()
        
        return default
    
<<<<<<< HEAD
    def _create_plan(self, filepath: Path, content: str, task_record: TaskRecord):
        """
        Create a plan file for Qwen Code to process.
=======
    def _create_plan(self, filepath: Path, content: str):
        """
        Create a plan file for Qwen Code to process.

        For Bronze Tier, this is a simple instruction file.
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_filename = f'PLAN_{filepath.stem}_{timestamp}.md'
<<<<<<< HEAD
            
            plan_content = f'''---
created: {datetime.now().isoformat()}
source_file: {filepath.name}
task_id: {task_record.task_id}
=======

            plan_content = f'''---
created: {datetime.now().isoformat()}
source_file: {filepath.name}
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
status: ready_for_qwen
---

# Action Plan

## Source
File: {filepath.name}
<<<<<<< HEAD
Task ID: {task_record.task_id}
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Instructions for Qwen Code

1. Read the source file: {filepath.name}
2. Understand the context and required actions
3. Create appropriate responses or action items
4. Update the Dashboard with progress
<<<<<<< HEAD
5. For sensitive actions: Create approval request in /Pending_Approval
6. Move completed items to /Done folder
=======
5. Move completed items to /Done folder
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73

---

## Source File Content

{content}

---

## Processing Steps

- [ ] Read and understand the source file
- [ ] Identify required actions
- [ ] Execute or draft responses
- [ ] Request approval if needed (create file in /Pending_Approval)
- [ ] Update Dashboard
- [ ] Move to /Done when complete

---
<<<<<<< HEAD
*Generated by Orchestrator (Gold Tier)*
=======
*Generated by Orchestrator*
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
'''
            
            plan_filepath = self.plans / plan_filename
            plan_filepath.write_text(plan_content, encoding='utf-8')
            
<<<<<<< HEAD
            task_record.plan_file = plan_filename
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
            self.logger.info(f'Created plan: {plan_filename}')
            
        except Exception as e:
            self.logger.error(f'Error creating plan: {e}')
<<<<<<< HEAD
            self.error_recovery.record_error("create_plan", e, {"source": filepath.name})
    
    def check_approved_actions(self):
        """Check for approved actions that need execution with error recovery."""
=======
    
    def check_approved_actions(self):
        """Check for approved actions that need execution."""
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        files = list(self.approved.glob('*.md'))
        
        if files:
            self.logger.info(f'Found {len(files)} approved action(s) to execute')
<<<<<<< HEAD
            for f in files:
                try:
                    self.log_activity('Approved', f.name)
                    # Move to Done after processing
                    f.rename(self.done / f.name)
                except Exception as e:
                    self.logger.error(f'Error moving approved file: {e}')
                    self.error_recovery.record_error("check_approved", e, {"file": f.name})
    
    def run_ralph_loop(self, max_iterations: int = 10, delay: int = 30):
        """Run the Ralph Wiggum autonomous loop."""
        loop = RalphWiggumLoop(self, max_iterations, delay)
        results = loop.run()
        
        # Print summary
        print("\n" + "=" * 50)
        print("RALPH WIGGUM LOOP COMPLETE")
        print("=" * 50)
        print(f"Iterations: {results['iterations']}")
        print(f"Tasks Processed: {results['tasks_processed']}")
        print(f"Tasks Completed: {results['tasks_completed']}")
        print(f"Tasks Failed: {results['tasks_failed']}")
        print(f"Approvals Created: {results['approvals_created']}")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
            for e in results['errors'][-5:]:
                print(f"  - {e}")
        print("=" * 50)
        
        return results
    
    def run(self):
        """Main orchestration loop with error recovery."""
        self.running = True
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator Starting (Gold Tier)')
=======
            # For Bronze Tier, just log that approval was received
            for f in files:
                self.log_activity('Approved', f.name)
                # Move to Done after processing
                try:
                    f.rename(self.done / f.name)
                except Exception as e:
                    self.logger.error(f'Error moving approved file: {e}')
    
    def run(self):
        """Main orchestration loop."""
        self.running = True
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator Starting')
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        self.logger.info(f'Vault Path: {self.vault_path}')
        self.logger.info(f'Check Interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
<<<<<<< HEAD
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        consecutive_errors = 0
        max_consecutive_errors = 10
        
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        try:
            while self.running:
                try:
                    # Update dashboard
                    self.update_dashboard()
                    
                    # Process Needs_Action folder
                    self.process_needs_action()
                    
                    # Check for approved actions
                    self.check_approved_actions()
                    
<<<<<<< HEAD
                    # Reset consecutive error counter on success
                    consecutive_errors = 0
                    
                except Exception as e:
                    consecutive_errors += 1
                    self.logger.error(f'Orchestration loop error ({consecutive_errors}/{max_consecutive_errors}): {e}')
                    self.error_recovery.record_error("orchestration_loop", e)
                    
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.critical(f"Too many consecutive errors ({consecutive_errors}). Entering degraded mode.")
                        self.error_recovery.degrade_gracefully(
                            "orchestrator", 
                            "Orchestrator paused. Check logs and restart manually."
                        )
                        break
=======
                except Exception as e:
                    self.logger.error(f'Error in orchestration loop: {e}')
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        finally:
            self.running = False
            self.logger.info('Orchestrator stopped')
    
<<<<<<< HEAD
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    def stop(self):
        """Stop the orchestrator."""
        self.running = False


def run_qwen_task(vault_path: str, prompt: str):
    """
    Run a Qwen Code task on the vault.
<<<<<<< HEAD
=======

    This is a helper function to trigger Qwen Code processing.

    Args:
        vault_path: Path to the vault
        prompt: Task prompt for Qwen
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    """
    cmd = [
        'qwen',
        '--cwd', vault_path,
        prompt
    ]

    try:
<<<<<<< HEAD
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
=======
        result = subprocess.run(cmd, capture_output=True, text=True)
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
        return result.stdout
    except FileNotFoundError:
        print("Qwen Code not found. Please ensure Qwen Code is installed.")
        return None
<<<<<<< HEAD
    except subprocess.TimeoutExpired:
        return "Qwen Code timed out after 5 minutes"
=======
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73


def main():
    """Main entry point."""
<<<<<<< HEAD
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator (Gold Tier)')
    parser.add_argument('vault_path', nargs='?', default=None, help='Path to Obsidian vault')
    parser.add_argument('--process-once', action='store_true', help='Process once and exit (for scheduled tasks)')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')
    parser.add_argument('--ralph-loop', type=int, metavar='N', help='Run autonomous Ralph Wiggum loop for N iterations')
    parser.add_argument('--ralph-delay', type=int, default=30, help='Delay between Ralph loop iterations (seconds)')
    parser.add_argument('--error-summary', action='store_true', help='Show error summary and exit')
    args = parser.parse_args()

    # Get vault path
    if args.vault_path:
        vault_path = args.vault_path
=======
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73
    else:
        # Default: sibling directory
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'

<<<<<<< HEAD
    # Create orchestrator
    orchestrator = Orchestrator(
        vault_path=str(vault_path),
        check_interval=args.interval
    )

    if args.error_summary:
        summary = orchestrator.error_recovery.get_error_summary(24)
        print(json.dumps(summary, indent=2))
        return

    if args.ralph_loop:
        # Autonomous mode
        print("=" * 50)
        print("AI Employee Orchestrator - Ralph Wiggum Loop")
        print("=" * 50)
        print(f"Vault: {vault_path}")
        print(f"Max Iterations: {args.ralph_loop}")
        print(f"Iteration Delay: {args.ralph_delay}s")
        print()
        
        orchestrator.run_ralph_loop(args.ralph_loop, args.ralph_delay)
    
    elif args.process_once:
        # Single run mode for scheduled tasks
        print("=" * 50)
        print("AI Employee Orchestrator - Single Run Mode")
        print("=" * 50)
        print(f"Vault: {vault_path}")
        print()
        
        orchestrator.update_dashboard()
        orchestrator.process_needs_action()
        orchestrator.check_approved_actions()
        
        print("Processing complete.")
    else:
        # Continuous run mode
        print("=" * 50)
        print("AI Employee Orchestrator (Gold Tier)")
        print("=" * 50)
        print(f"Vault: {vault_path}")
        print(f"Monitoring: Needs_Action folder")
        print(f"Check Interval: {args.interval}s")
        print("Press Ctrl+C to stop")
        print()
        print("Modes:")
        print(f"  Single run:     python orchestrator.py --process-once")
        print(f"  Autonomous:     python orchestrator.py --ralph-loop 10")
        print(f"  Error summary:  python orchestrator.py --error-summary")
        print()
        print("To process tasks with Qwen Code, run:")
        print(f"  qwen --cwd \"{vault_path}\" \"Process all files in /Needs_Action\"")
        print()

        orchestrator.run()


if __name__ == '__main__':
    main()
=======
    # Create and run orchestrator
    orchestrator = Orchestrator(
        vault_path=str(vault_path),
        check_interval=60  # Check every minute
    )

    print("=" * 50)
    print("AI Employee Orchestrator")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"Monitoring: Needs_Action folder")
    print("Press Ctrl+C to stop")
    print()
    print("To process tasks with Qwen Code, run:")
    print(f"  qwen --cwd \"{vault_path}\" \"Process all files in /Needs_Action\"")
    print()

    orchestrator.run()


if __name__ == '__main__':
    main()
>>>>>>> f3afea3cffaff1ce88817baa189802c7ef46fd73

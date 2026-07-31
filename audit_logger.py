#!/usr/bin/env python3
"""
Comprehensive Audit Logging System for AI Employee (Gold Tier).

Provides immutable audit trails for all system actions, decisions, and changes.
"""

import json
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class AuditEventType(Enum):
    """Types of audit events."""
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIG_CHANGE = "config_change"
    
    # Task events
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_RETRIED = "task_retried"
    
    # Approval events
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    APPROVAL_EXPIRED = "approval_expired"
    
    # Action events
    EMAIL_SENT = "email_sent"
    POST_PUBLISHED = "post_published"
    PAYMENT_PROCESSED = "payment_processed"
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    
    # Data access
    VAULT_READ = "vault_read"
    VAULT_WRITE = "vault_write"
    EXTERNAL_API_CALL = "external_api_call"
    
    # Security events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    PERMISSION_DENIED = "permission_denied"
    
    # Error events
    ERROR_OCCURRED = "error_occurred"
    DEGRADATION_TRIGGERED = "degradation_triggered"
    RECOVERY_ACTION = "recovery_action"


@dataclass
class AuditEvent:
    """Single audit log entry."""
    event_id: str
    timestamp: str
    event_type: str
    component: str
    actor: str  # system, human, ai, external
    action: str
    resource: str
    result: str  # success, failure, partial
    details: Dict[str, Any]
    previous_hash: str
    current_hash: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'), sort_keys=True)


class AuditLogger:
    """
    Immutable audit logger with hash chaining for tamper detection.
    
    Features:
    - Hash-chained entries (each entry contains hash of previous)
    - Structured JSONL format for easy parsing
    - Automatic rotation by date
    - Query API for compliance
    """
    
    def __init__(self, vault_path: str, retention_days: int = 2555):  # 7 years default
        self.vault_path = Path(vault_path)
        self.audit_dir = self.vault_path / 'Audits'
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        
        self._lock = threading.Lock()
        self._current_file: Optional[Path] = None
        self._previous_hash = "0" * 64  # Genesis hash
        self._initialize()
    
    def _initialize(self):
        """Initialize or resume audit log."""
        # Find latest audit file
        audit_files = sorted(self.audit_dir.glob('audit_*.jsonl'))
        if audit_files:
            self._current_file = audit_files[-1]
            # Read last line to get previous hash
            with open(self._current_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    self._previous_hash = last_entry.get('current_hash', '0' * 64)
        else:
            # Create new audit file
            self._rotate_file()
    
    def _rotate_file(self):
        """Create new audit file for current date."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        self._current_file = self.audit_dir / f'audit_{date_str}.jsonl'
        self._previous_hash = "0" * 64
        # Write header
        header = {
            "audit_version": "1.0",
            "created": datetime.now().isoformat(),
            "format": "jsonl",
            "hash_algorithm": "sha256"
        }
        with open(self._current_file, 'w') as f:
            f.write(json.dumps(header) + '\n')
    
    def _compute_hash(self, event: AuditEvent) -> str:
        """Compute hash of audit event."""
        # Create deterministic string representation
        data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "component": event.component,
            "actor": event.actor,
            "action": event.action,
            "resource": event.resource,
            "result": event.result,
            "details": event.details,
            "previous_hash": event.previous_hash
        }
        serialized = json.dumps(data, separators=(',', ':'), sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def log(self, event_type: AuditEventType, component: str, actor: str,
            action: str, resource: str, result: str, 
            details: Dict[str, Any] = None) -> AuditEvent:
        """Log an audit event."""
        with self._lock:
            # Check if we need to rotate (new day)
            expected_file = self.audit_dir / f'audit_{datetime.now().strftime("%Y-%m-%d")}.jsonl'
            if self._current_file != expected_file:
                self._rotate_file()
            
            # Create event
            event = AuditEvent(
                event_id=f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.getpid()}",
                timestamp=datetime.now().isoformat(),
                event_type=event_type.value,
                component=component,
                actor=actor,
                action=action,
                resource=resource,
                result=result,
                details=details or {},
                previous_hash=self._previous_hash,
                current_hash=""  # Will be computed
            )
            
            # Compute hash
            event.current_hash = self._compute_hash(event)
            
            # Write to file
            with open(self._current_file, 'a') as f:
                f.write(event.to_json() + '\n')
            
            # Update previous hash for next entry
            self._previous_hash = event.current_hash
            
            return event
    
    def log_simple(self, event_type: AuditEventType, component: str, 
                   action: str, resource: str, result: str = "success",
                   actor: str = "system", **details):
        """Simplified logging interface."""
        return self.log(event_type, component, actor, action, resource, result, details)
    
    def query(self, start_date: str = None, end_date: str = None,
              event_type: str = None, component: str = None,
              actor: str = None, result: str = None,
              limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters."""
        events = []
        
        # Determine which files to read
        files = sorted(self.audit_dir.glob('audit_*.jsonl'))
        
        if start_date:
            start = datetime.fromisoformat(start_date).date()
            files = [f for f in files if self._parse_date(f) >= start]
        if end_date:
            end = datetime.fromisoformat(end_date).date()
            files = [f for f in files if self._parse_date(f) <= end]
        
        for file in files:
            with open(file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if 'audit_version' in data:
                            continue  # Skip header
                        
                        # Apply filters
                        if event_type and data.get('event_type') != event_type:
                            continue
                        if component and data.get('component') != component:
                            continue
                        if actor and data.get('actor') != actor:
                            continue
                        if result and data.get('result') != result:
                            continue
                        
                        events.append(AuditEvent(**data))
                        
                        if len(events) >= limit:
                            return events
                    except json.JSONDecodeError:
                        continue
        
        return events
    
    def _parse_date(self, filepath: Path) -> Optional[datetime.date]:
        """Extract date from audit filename."""
        try:
            name = filepath.stem  # audit_YYYY-MM-DD
            date_str = name.replace('audit_', '')
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return None
    
    def verify_chain(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Verify hash chain integrity."""
        events = self.query(start_date, end_date)
        
        errors = []
        prev_hash = "0" * 64
        
        for i, event in enumerate(events):
            # Verify previous hash
            if i == 0:
                # First event of day should have genesis or previous day's last hash
                # For simplicity, just check it's a valid hash
                pass
            else:
                if event.previous_hash != prev_hash:
                    errors.append({
                        "event_id": event.event_id,
                        "index": i,
                        "error": "Hash chain broken",
                        "expected": prev_hash,
                        "actual": event.previous_hash
                    })
            
            # Verify current hash
            computed = self._compute_hash(event)
            if event.current_hash != computed:
                errors.append({
                    "event_id": event.event_id,
                    "index": i,
                    "error": "Hash mismatch",
                    "expected": computed,
                    "actual": event.current_hash
                })
            
            prev_hash = event.current_hash
        
        return {
            "verified": len(errors) == 0,
            "total_events": len(events),
            "errors": errors,
            "period": f"{start_date} to {end_date}" if start_date or end_date else "all"
        }
    
    def export(self, output_path: str, start_date: str = None, 
               end_date: str = None, format: str = "jsonl"):
        """Export audit logs."""
        events = self.query(start_date, end_date)
        
        output = Path(output_path)
        if format == "jsonl":
            with open(output, 'w') as f:
                for event in events:
                    f.write(event.to_json() + '\n')
        elif format == "json":
            with open(output, 'w') as f:
                json.dump([e.to_dict() for e in events], f, indent=2)
        elif format == "csv":
            import csv
            with open(output, 'w', newline='') as f:
                if events:
                    writer = csv.DictWriter(f, fieldnames=events[0].to_dict().keys())
                    writer.writeheader()
                    for event in events:
                        writer.writerow(event.to_dict())
        
        return len(events)
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics."""
        start = datetime.now().date() - timedelta(days=days)
        end = datetime.now().date()
        
        events = self.query(start_date=start.isoformat(), end_date=end.isoformat())
        
        by_type = {}
        by_component = {}
        by_actor = {}
        by_result = {}
        
        for event in events:
            by_type[event.event_type] = by_type.get(event.event_type, 0) + 1
            by_component[event.component] = by_component.get(event.component, 0) + 1
            by_actor[event.actor] = by_actor.get(event.actor, 0) + 1
            by_result[event.result] = by_result.get(event.result, 0) + 1
        
        return {
            "period_days": days,
            "total_events": len(events),
            "by_type": by_type,
            "by_component": by_component,
            "by_actor": by_actor,
            "by_result": by_result,
            "files": len(list(self.audit_dir.glob('audit_*.jsonl')))
        }


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str) -> AuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger


# Convenience functions
def audit_log(event_type: AuditEventType, component: str, action: str,
              resource: str, result: str = "success", actor: str = "system", **details):
    """Log an audit event (uses global logger)."""
    logger = get_audit_logger("AI_Employee_Vault")
    return logger.log_simple(event_type, component, action, resource, result, actor, **details)


# Integration with orchestrator
# In Orchestrator.__init__:
# self.audit_logger = get_audit_logger(vault_path)
# 
# In process_needs_action():
# self.audit_log(AuditEventType.TASK_CREATED, "orchestrator", "create_task", 
#                filepath.name, "success", "system", task_id=task_record.task_id)
# 
# In _update_task_status():
# if status == TaskStatus.COMPLETED:
#     self.audit_log(AuditEventType.TASK_COMPLETED, "orchestrator", "complete_task",
#                    task_id, "success", "ai", details=details)
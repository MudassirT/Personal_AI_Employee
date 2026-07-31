"""
Error Recovery and Graceful Degradation System for AI Employee.

Provides circuit breakers, error tracking, automatic retry, and graceful degradation.
"""

import json
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict


class DegradationLevel(Enum):
    NONE = "none"
    REDUCED = "reduced"      # Some features disabled
    MINIMAL = "minimal"      # Only critical functions
    MAINTENANCE = "maintenance"  # System paused


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    timestamp: str
    component: str
    error_type: str
    message: str
    traceback: str
    context: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[str] = None


@dataclass
class ComponentHealth:
    """Health status of a system component."""
    name: str
    status: str  # healthy, degraded, failed
    last_check: str
    error_count: int = 0
    last_error: Optional[str] = None
    degradation_level: DegradationLevel = DegradationLevel.NONE


class CircuitBreaker:
    """Circuit breaker pattern for external service failures."""
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: int = 300, half_open_requests: int = 3):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self.half_open_successes = 0
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "half-open"
                self.half_open_successes = 0
            else:
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        if self.state == "half-open":
            self.half_open_successes += 1
            if self.half_open_successes >= self.half_open_requests:
                self.state = "closed"
                self.half_open_successes = 0
        else:
            self.state = "closed"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def reset(self):
        """Manually reset the circuit breaker."""
        self.failure_count = 0
        self.success_count = 0
        self.state = "closed"
        self.half_open_successes = 0
        self.last_failure_time = None
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": self.last_failure_time
        }


class ErrorRecoveryManager:
    """Manages error recovery and graceful degradation."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.error_log = self.logs_dir / 'errors.jsonl'
        self.health_log = self.logs_dir / 'component_health.json'
        self.degradation_file = self.logs_dir / 'degradation_state.json'
        
        self.errors: List[ErrorRecord] = []
        self.components: Dict[str, ComponentHealth] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.degradation_level = DegradationLevel.NONE
        
        self._load_state()
    
    def _load_state(self):
        """Load persisted state."""
        # Load errors
        if self.error_log.exists():
            with open(self.error_log, 'r') as f:
                for line in f:
                    try:
                        self.errors.append(ErrorRecord(**json.loads(line)))
                    except:
                        pass
        
        # Load component health
        if self.health_log.exists():
            with open(self.health_log, 'r') as f:
                data = json.load(f)
                for name, health in data.items():
                    self.components[name] = ComponentHealth(**health)
        
        # Load degradation state
        if self.degradation_file.exists():
            with open(self.degradation_file, 'r') as f:
                data = json.load(f)
                self.degradation_level = DegradationLevel(data.get('level', 'none'))
    
    def _save_state(self):
        """Persist state to disk."""
        # Save errors (last 1000)
        with open(self.error_log, 'w') as f:
            for error in self.errors[-1000:]:
                f.write(json.dumps(asdict(error)) + '\n')
        
        # Save component health
        with open(self.health_log, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.components.items()}, f, indent=2)
        
        # Save degradation state
        with open(self.degradation_file, 'w') as f:
            json.dump({"level": self.degradation_level.value, "updated": datetime.now().isoformat()}, f)
    
    def record_error(self, component: str, error: Exception, context: Dict = None):
        """Record an error occurrence."""
        error_record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            component=component,
            error_type=type(error).__name__,
            message=str(error),
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        self.errors.append(error_record)
        
        # Update component health
        if component not in self.components:
            self.components[component] = ComponentHealth(
                name=component,
                status="healthy",
                last_check=datetime.now().isoformat()
            )
        
        comp = self.components[component]
        comp.error_count += 1
        comp.last_error = str(error)
        comp.last_check = datetime.now().isoformat()
        
        # Check if component should be degraded
        if comp.error_count >= 10 and comp.status == "healthy":
            comp.status = "degraded"
            comp.degradation_level = DegradationLevel.REDUCED
            self._trigger_degradation(component, DegradationLevel.REDUCED)
        elif comp.error_count >= 50 and comp.status == "degraded":
            comp.status = "failed"
            comp.degradation_level = DegradationLevel.MAINTENANCE
            self._trigger_degradation(component, DegradationLevel.MAINTENANCE)
        
        self._save_state()
        
        # Print error summary
        print(f"\n[ERROR] {component}: {type(error).__name__}: {error}")
        if context:
            print(f"  Context: {context}")
    
    def record_success(self, component: str):
        """Record a successful operation."""
        if component in self.components:
            comp = self.components[component]
            comp.last_check = datetime.now().isoformat()
            # Gradually recover
            if comp.error_count > 0:
                comp.error_count = max(0, comp.error_count - 1)
            if comp.status == "degraded" and comp.error_count == 0:
                comp.status = "healthy"
                comp.degradation_level = DegradationLevel.NONE
            self._save_state()
    
    def get_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, **kwargs)
        return self.circuit_breakers[name]
    
    def _trigger_degradation(self, component: str, level: DegradationLevel):
        """Trigger graceful degradation."""
        print(f"\n[DEGRADATION] Component '{component}' degraded to {level.value}")
        
        # Update global degradation level
        if level.value == "maintenance":
            self.degradation_level = DegradationLevel.MAINTENANCE
        elif level.value == "reduced" and self.degradation_level != DegradationLevel.MAINTENANCE:
            self.degradation_level = DegradationLevel.REDUCED
        
        self._save_state()
        
        # Log to degradation log
        degradation_log = self.logs_dir / 'degradation.log'
        with open(degradation_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {component}: {level.value}\n")
    
    def degrade_gracefully(self, component: str, message: str):
        """Force graceful degradation of a component."""
        if component in self.components:
            self.components[component].status = "failed"
            self.components[component].degradation_level = DegradationLevel.MAINTENANCE
            self._trigger_degradation(component, DegradationLevel.MAINTENANCE)
        
        # Create maintenance notice
        notice_file = self.vault_path / 'MAINTENANCE_NOTICE.md'
        with open(notice_file, 'w') as f:
            f.write(f"""# System Maintenance Notice

**Component:** {component}
**Status:** Degraded / Maintenance Mode
**Message:** {message}
**Time:** {datetime.now().isoformat()}

## Impact
- {component} functionality is temporarily unavailable
- Other components may continue to operate
- Manual intervention required

## Recovery
1. Check logs in `/Logs/errors.jsonl`
2. Resolve underlying issue
3. Restart orchestrator
4. System will auto-recover on next successful operation
""")
    
    def is_degraded(self, component: str = None) -> bool:
        """Check if system or component is degraded."""
        if component:
            return self.components.get(component, ComponentHealth("", "healthy", "")).status != "healthy"
        return self.degradation_level != DegradationLevel.NONE
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """Get error summary for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors 
                        if datetime.fromisoformat(e.timestamp) > cutoff]
        
        by_component = defaultdict(int)
        by_type = defaultdict(int)
        
        for e in recent_errors:
            by_component[e.component] += 1
            by_type[e.error_type] += 1
        
        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "by_component": dict(by_component),
            "by_type": dict(by_type),
            "components_status": {k: v.status for k, v in self.components.items()},
            "degradation_level": self.degradation_level.value,
            "circuit_breakers": {k: v.get_status() for k, v in self.circuit_breakers.items()}
        }
    
    def get_component_health(self) -> Dict:
        """Get health status of all components."""
        return {k: asdict(v) for k, v in self.components.items()}


class RalphWiggumLoop:
    """
    Autonomous task processing loop (Ralph Wiggum pattern).
    
    Keeps processing until all tasks are complete or max iterations reached.
    """
    
    def __init__(self, orchestrator, max_iterations: int = 10, delay: int = 30):
        self.orchestrator = orchestrator
        self.max_iterations = max_iterations
        self.delay = delay
        self.results = {
            "iterations": 0,
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "approvals_created": 0,
            "errors": []
        }
    
    def run(self) -> Dict:
        """Run the autonomous loop."""
        print(f"\n🤖 Starting Ralph Wiggum Loop: {self.max_iterations} iterations")
        
        for iteration in range(1, self.max_iterations + 1):
            self.results["iterations"] = iteration
            print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            
            try:
                # Update dashboard
                self.orchestrator.update_dashboard()
                
                # Process Needs_Action
                initial_count = len(self.orchestrator.get_needs_action_files())
                self.orchestrator.process_needs_action()
                processed = initial_count - len(self.orchestrator.get_needs_action_files())
                self.results["tasks_processed"] += processed
                
                if processed > 0:
                    print(f"  Processed {processed} new task(s)")
                
                # Check for completed tasks (moved to Done)
                # This is a simplification - in practice you'd track task records
                
                # Check for approved actions
                self.orchestrator.check_approved_actions()
                
                # Check if there's anything left to do
                pending = len(self.orchestrator.get_needs_action_files())
                in_progress = len(list(self.orchestrator.in_progress.glob('*.md')))
                pending_approval = len(list(self.orchestrator.pending_approval.glob('*.md')))
                approved = len(list(self.orchestrator.approved.glob('*.md')))
                
                print(f"  Queue: {pending} pending, {in_progress} in progress, "
                      f"{pending_approval} awaiting approval, {approved} approved")
                
                # If nothing to do, we can stop early
                if pending == 0 and in_progress == 0 and pending_approval == 0 and approved == 0:
                    print("  ✓ No more tasks to process. Stopping early.")
                    break
                
            except Exception as e:
                error_msg = f"Iteration {iteration} error: {e}"
                self.results["errors"].append(error_msg)
                print(f"  ✗ Error: {e}")
                traceback.print_exc()
            
            # Wait before next iteration (unless last iteration)
            if iteration < self.max_iterations:
                print(f"  Waiting {self.delay}s before next iteration...")
                time.sleep(self.delay)
        
        return self.results


# Global instance getter
_error_recovery_manager: Optional[ErrorRecoveryManager] = None


def get_error_recovery(vault_path: str) -> ErrorRecoveryManager:
    """Get global error recovery manager instance."""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager(vault_path)
    return _error_recovery_manager


# Add to orchestrator
# In Orchestrator.__init__:
# self.error_recovery = get_error_recovery(vault_path)
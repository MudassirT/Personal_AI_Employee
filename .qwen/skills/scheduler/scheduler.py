#!/usr/bin/env python3
"""
Scheduler Skill for AI Employee

Provides task scheduling for automated AI Employee operations.
Supports Windows Task Scheduler, cron (Linux/Mac), and Python schedule library.
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class AIScheduler:
    """Schedule AI Employee tasks."""
    
    def __init__(self, vault_path: str = 'AI_Employee_Vault', project_root: Optional[str] = None):
        self.vault_path = Path(vault_path)
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Task definitions
        self.tasks = {
            'daily_processing': {
                'name': 'Daily Processing',
                'description': 'Process Needs_Action folder and create plans',
                'command': 'python orchestrator.py --process-once',
                'schedule': 'daily',
                'time': '08:00',
                'enabled': True
            },
            'weekly_briefing': {
                'name': 'Weekly CEO Briefing',
                'description': 'Generate weekly briefing from completed tasks',
                'command': f'qwen --cwd "{self.vault_path}" "Review completed tasks from this week and generate a CEO briefing in Briefings/ folder"',
                'schedule': 'weekly',
                'day': 'monday',
                'time': '09:00',
                'enabled': True
            },
            'monthly_audit': {
                'name': 'Monthly Subscription Audit',
                'description': 'Audit subscriptions and expenses',
                'command': f'qwen --cwd "{self.vault_path}" "Review all transactions this month, identify subscriptions, and flag any unused services for cancellation"',
                'schedule': 'monthly',
                'day': 1,
                'time': '10:00',
                'enabled': True
            }
        }
    
    def _log(self, message: str):
        """Log message to scheduler log."""
        log_file = self.logs_dir / 'scheduler.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{timestamp}] {message}\n')
        print(f'[{timestamp}] {message}')
    
    def run_task(self, task_name: str) -> Dict[str, Any]:
        """Run a specific task by name."""
        if task_name not in self.tasks:
            return {'success': False, 'error': f'Unknown task: {task_name}'}
        
        task = self.tasks[task_name]
        if not task.get('enabled', True):
            return {'success': False, 'error': f'Task {task_name} is disabled'}
        
        self._log(f'Running task: {task["name"]}')
        
        try:
            # Change to project root directory
            result = subprocess.run(
                task['command'],
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self._log(f'Task {task_name} completed successfully')
                return {
                    'success': True,
                    'task': task_name,
                    'output': result.stdout
                }
            else:
                self._log(f'Task {task_name} failed: {result.stderr}')
                return {
                    'success': False,
                    'task': task_name,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            error = f'Task {task_name} timed out after 5 minutes'
            self._log(error)
            return {'success': False, 'task': task_name, 'error': error}
        except Exception as e:
            error = f'Task {task_name} error: {str(e)}'
            self._log(error)
            return {'success': False, 'task': task_name, 'error': str(e)}
    
    def run_daily_processing(self) -> Dict[str, Any]:
        """Run daily processing task."""
        return self.run_task('daily_processing')
    
    def run_weekly_briefing(self) -> Dict[str, Any]:
        """Run weekly briefing task."""
        return self.run_task('weekly_briefing')
    
    def run_monthly_audit(self) -> Dict[str, Any]:
        """Run monthly audit task."""
        return self.run_task('monthly_audit')
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks."""
        return [
            {
                'id': task_id,
                'name': task['name'],
                'description': task['description'],
                'schedule': task['schedule'],
                'time': task.get('time'),
                'day': task.get('day'),
                'enabled': task.get('enabled', True)
            }
            for task_id, task in self.tasks.items()
        ]
    
    def enable_task(self, task_name: str) -> bool:
        """Enable a task."""
        if task_name in self.tasks:
            self.tasks[task_name]['enabled'] = True
            self._log(f'Enabled task: {task_name}')
            return True
        return False
    
    def disable_task(self, task_name: str) -> bool:
        """Disable a task."""
        if task_name in self.tasks:
            self.tasks[task_name]['enabled'] = False
            self._log(f'Disabled task: {task_name}')
            return True
        return False
    
    def create_windows_tasks(self) -> List[str]:
        """Create Windows Task Scheduler tasks."""
        created = []
        
        for task_id, task in self.tasks.items():
            if not task.get('enabled', True):
                continue
            
            task_name = f'AI Employee - {task["name"]}'
            script_path = self.project_root / 'schedules' / f'{task_id}.bat'
            
            # Create batch file if it doesn't exist
            if not script_path.exists():
                self._create_batch_file(task_id, task, script_path)
            
            # Build schtasks command
            if task['schedule'] == 'daily':
                cmd = f'schtasks /Create /TN "{task_name}" /TR "{script_path}" /SC DAILY /ST {task["time"]} /RL HIGHEST /F'
            elif task['schedule'] == 'weekly':
                cmd = f'schtasks /Create /TN "{task_name}" /TR "{script_path}" /SC WEEKLY /D {task["day"].upper()} /ST {task["time"]} /RL HIGHEST /F'
            elif task['schedule'] == 'monthly':
                cmd = f'schtasks /Create /TN "{task_name}" /TR "{script_path}" /SC MONTHLY /D {task["day"]} /ST {task["time"]} /RL HIGHEST /F'
            else:
                continue
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    created.append(task_name)
                    self._log(f'Created Windows task: {task_name}')
                else:
                    self._log(f'Failed to create Windows task {task_name}: {result.stderr}')
            except Exception as e:
                self._log(f'Error creating Windows task {task_name}: {e}')
        
        return created
    
    def _create_batch_file(self, task_id: str, task: Dict[str, Any], script_path: Path):
        """Create a batch file for Windows Task Scheduler."""
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f'''@echo off
REM AI Employee - {task['name']}
REM Auto-generated by scheduler skill

echo ================================================
echo AI Employee - {task['name']}
echo ================================================
echo Time: %DATE% %TIME%
echo.

cd /d "{self.project_root}"

{task['command']}

echo.
echo {task['name']} complete.
echo ================================================
'''
        script_path.write_text(content)
        self._log(f'Created batch file: {script_path}')
    
    def get_cron_entries(self) -> str:
        """Generate cron entries for Linux/Mac."""
        lines = ['# AI Employee Scheduled Tasks', '# Generated by scheduler skill', '']
        
        for task_id, task in self.tasks.items():
            if not task.get('enabled', True):
                continue
            
            if task['schedule'] == 'daily':
                time_parts = task['time'].split(':')
                lines.append(f'{time_parts[1]} {time_parts[0]} * * * cd {self.project_root} && {task["command"]}')
            elif task['schedule'] == 'weekly':
                time_parts = task['time'].split(':')
                day_num = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].index(task['day'].lower())
                lines.append(f'{time_parts[1]} {time_parts[0]} * * {day_num} cd {self.project_root} && {task["command"]}')
            elif task['schedule'] == 'monthly':
                time_parts = task['time'].split(':')
                lines.append(f'{time_parts[1]} {time_parts[0]} {task["day"]} * * cd {self.project_root} && {task["command"]}')
        
        return '\n'.join(lines)
    
    def run_python_schedule(self, check_interval: int = 60):
        """Run tasks using Python schedule library (cross-platform)."""
        try:
            import schedule
        except ImportError:
            self._log('schedule library not installed. Run: pip install schedule')
            return
        
        self._log('Starting Python scheduler...')
        
        # Schedule tasks
        for task_id, task in self.tasks.items():
            if not task.get('enabled', True):
                continue
            
            if task['schedule'] == 'daily':
                schedule.every().day.at(task['time']).do(self.run_task, task_id)
                self._log(f'Scheduled daily: {task["name"]} at {task["time"]}')
            elif task['schedule'] == 'weekly':
                getattr(schedule.every(), task['day'].lower()).at(task['time']).do(self.run_task, task_id)
                self._log(f'Scheduled weekly: {task["name"]} on {task["day"]} at {task["time"]}')
            elif task['schedule'] == 'monthly':
                # schedule library doesn't have native monthly, run daily and check date
                schedule.every().day.at(task['time']).do(self._check_and_run_monthly, task_id)
                self._log(f'Scheduled monthly check: {task["name"]} on day {task["day"]} at {task["time"]}')
        
        self._log('Scheduler running. Press Ctrl+C to stop.')
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self._log('Scheduler stopped by user')
    
    def _check_and_run_monthly(self, task_id: str):
        """Check if today is the monthly run day and execute if so."""
        if datetime.now().day == self.datetime.now().day == self.tasks[task_id]['day']:
            self.run_task(task_id)


def main():
    """CLI entry point for scheduler skill."""
    parser = argparse.ArgumentParser(description='AI Employee Scheduler Skill')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Vault path')
    parser.add_argument('--root', help='Project root directory')
    parser.add_argument('--run', help='Run specific task (daily_processing, weekly_briefing, monthly_audit)')
    parser.add_argument('--list', action='store_true', help='List all scheduled tasks')
    parser.add_argument('--enable', help='Enable a task')
    parser.add_argument('--disable', help='Disable a task')
    parser.add_argument('--create-windows', action='store_true', help='Create Windows Task Scheduler tasks')
    parser.add_argument('--cron', action='store_true', help='Output cron entries for Linux/Mac')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon using Python schedule library')
    parser.add_argument('--interval', type=int, default=60, help='Daemon check interval (seconds)')
    
    args = parser.parse_args()
    
    scheduler = AIScheduler(args.vault, args.root)
    
    if args.run:
        result = scheduler.run_task(args.run)
        if result['success']:
            print(f'SUCCESS: {args.run}')
            if result.get('output'):
                print(result['output'])
        else:
            print(f'FAILED: {args.run}')
            if result.get('error'):
                print(f'Error: {result["error"]}')
            sys.exit(1)
    
    elif args.list:
        tasks = scheduler.list_tasks()
        for task in tasks:
            status = 'ENABLED' if task['enabled'] else 'DISABLED'
            schedule_info = f"{task['schedule']} at {task.get('time', 'N/A')}"
            if task.get('day'):
                schedule_info += f" on {task['day']}"
            print(f"  {task['id']}: {task['name']} [{status}] - {schedule_info}")
            print(f"    {task['description']}")
    
    elif args.enable:
        if scheduler.enable_task(args.enable):
            print(f'Enabled: {args.enable}')
        else:
            print(f'Unknown task: {args.enable}')
            sys.exit(1)
    
    elif args.disable:
        if scheduler.disable_task(args.disable):
            print(f'Disabled: {args.disable}')
        else:
            print(f'Unknown task: {args.disable}')
            sys.exit(1)
    
    elif args.create_windows:
        created = scheduler.create_windows_tasks()
        if created:
            print('Created Windows tasks:')
            for task in created:
                print(f'  - {task}')
        else:
            print('No tasks created')
    
    elif args.cron:
        print(scheduler.get_cron_entries())
    
    elif args.daemon:
        scheduler.run_python_schedule(args.interval)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
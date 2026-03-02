"""
Orchestrator - Master process for the AI Employee.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process items
3. Updates the Dashboard with activity
4. Manages the overall workflow

For Bronze Tier: Simple file-based orchestration that prepares tasks
for Qwen Code processing.

Usage:
    python orchestrator.py
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the Obsidian vault.
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
        
        # Statistics
        self.stats = {
            'tasks_processed': 0,
            'tasks_pending_approval': 0,
            'tasks_completed_today': 0,
            'last_activity': None
        }
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.needs_action,
            self.in_progress,
            self.done,
            self.pending_approval,
            self.approved,
            self.plans,
            self.logs_dir
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
        Process files in Needs_Action folder.
        
        For Bronze Tier: This prepares files for Claude Code processing
        and provides instructions for the user.
        """
        files = self.get_needs_action_files()
        
        if not files:
            self.logger.debug('No files in Needs_Action')
            return
        
        self.logger.info(f'Found {len(files)} file(s) to process')
        
        for filepath in files:
            try:
                self.logger.info(f'Processing: {filepath.name}')
                
                # Read the file to understand its type
                content = filepath.read_text(encoding='utf-8')
                
                # Extract metadata from frontmatter
                file_type = self._extract_metadata(content, 'type', 'unknown')
                priority = self._extract_metadata(content, 'priority', 'normal')
                
                # Log activity
                self.log_activity('Processing', f'{file_type} from {filepath.name}')
                
                # For Bronze Tier: Create a plan file
                self._create_plan(filepath, content)
                
                # Update stats
                self.stats['tasks_processed'] += 1
                
            except Exception as e:
                self.logger.error(f'Error processing {filepath.name}: {e}')
    
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
    
    def _create_plan(self, filepath: Path, content: str):
        """
        Create a plan file for Qwen Code to process.

        For Bronze Tier, this is a simple instruction file.
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_filename = f'PLAN_{filepath.stem}_{timestamp}.md'

            plan_content = f'''---
created: {datetime.now().isoformat()}
source_file: {filepath.name}
status: ready_for_qwen
---

# Action Plan

## Source
File: {filepath.name}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Instructions for Qwen Code

1. Read the source file: {filepath.name}
2. Understand the context and required actions
3. Create appropriate responses or action items
4. Update the Dashboard with progress
5. Move completed items to /Done folder

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
*Generated by Orchestrator*
'''
            
            plan_filepath = self.plans / plan_filename
            plan_filepath.write_text(plan_content, encoding='utf-8')
            
            self.logger.info(f'Created plan: {plan_filename}')
            
        except Exception as e:
            self.logger.error(f'Error creating plan: {e}')
    
    def check_approved_actions(self):
        """Check for approved actions that need execution."""
        files = list(self.approved.glob('*.md'))
        
        if files:
            self.logger.info(f'Found {len(files)} approved action(s) to execute')
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
        self.logger.info(f'Vault Path: {self.vault_path}')
        self.logger.info(f'Check Interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
        try:
            while self.running:
                try:
                    # Update dashboard
                    self.update_dashboard()
                    
                    # Process Needs_Action folder
                    self.process_needs_action()
                    
                    # Check for approved actions
                    self.check_approved_actions()
                    
                except Exception as e:
                    self.logger.error(f'Error in orchestration loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        finally:
            self.running = False
            self.logger.info('Orchestrator stopped')
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False


def run_qwen_task(vault_path: str, prompt: str):
    """
    Run a Qwen Code task on the vault.

    This is a helper function to trigger Qwen Code processing.

    Args:
        vault_path: Path to the vault
        prompt: Task prompt for Qwen
    """
    cmd = [
        'qwen',
        '--cwd', vault_path,
        prompt
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        print("Qwen Code not found. Please ensure Qwen Code is installed.")
        return None


def main():
    """Main entry point."""
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default: sibling directory
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'

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

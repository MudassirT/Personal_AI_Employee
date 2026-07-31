"""
Approval Workflow Skill - Human-in-the-loop approval system for sensitive actions.

Creates approval requests in Pending_Approval/, monitors Approved/ folder for execution,
and moves completed actions to Done/.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json


class ApprovalWorkflow:
    """Manages human-in-the-loop approval workflow."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.rejected_dir = self.vault_path / 'Rejected'
        self.done_dir = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for d in [self.pending_dir, self.approved_dir, self.rejected_dir, self.done_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def create_approval_request(self, action_type: str, details: Dict[str, Any], 
                                expires_hours: int = 24) -> Path:
        """Create an approval request file in Pending_Approval/."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'APPROVAL_{action_type}_{timestamp}.md'
        filepath = self.pending_dir / filename
        
        expires = datetime.now() + timedelta(hours=expires_hours)
        
        content = f'''---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {expires.isoformat()}
status: pending
---

# Approval Request

## Action Details
- **Type:** {action_type}
'''
        
        for key, value in details.items():
            content += f'- **{key}:** {value}\n'
        
        content += f'''
## Content
{details.get('body', details.get('content', '[No content provided]'))}

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Created by AI Employee at {datetime.now().isoformat()}*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self._log_action('CREATE', f'Created approval request: {filename}')
        return filepath
    
    def list_pending_approvals(self) -> List[Dict[str, Any]]:
        """List all pending approval requests."""
        approvals = []
        for filepath in sorted(self.pending_dir.glob('*.md')):
            content = filepath.read_text(encoding='utf-8')
            approval = self._parse_approval_file(content, filepath.name)
            approvals.append(approval)
        return approvals
    
    def list_approved_actions(self) -> List[Dict[str, Any]]:
        """List all approved actions ready for execution."""
        approved = []
        for filepath in sorted(self.approved_dir.glob('*.md')):
            content = filepath.read_text(encoding='utf-8')
            approval = self._parse_approval_file(content, filepath.name)
            approved.append(approval)
        return approved
    
    def process_approved_actions(self) -> List[Dict[str, Any]]:
        """Process all approved actions and move to Done/."""
        results = []
        
        for filepath in sorted(self.approved_dir.glob('*.md')):
            try:
                content = filepath.read_text(encoding='utf-8')
                details = self._parse_approval_content(content)
                
                # Execute the action
                result = self._execute_action(details)
                
                if result['success']:
                    # Move to Done
                    dest = self.done_dir / filepath.name
                    filepath.rename(dest)
                    self._log_action('EXECUTE', f'Executed and archived: {filepath.name}')
                else:
                    self._log_action('ERROR', f'Failed to execute: {filepath.name} - {result["error"]}')
                
                results.append({
                    'file': filepath.name,
                    'action': details.get('action'),
                    'result': result
                })
                
            except Exception as e:
                self._log_action('ERROR', f'Error processing {filepath.name}: {e}')
                results.append({
                    'file': filepath.name,
                    'action': 'unknown',
                    'result': {'success': False, 'error': str(e)}
                })
        
        return results
    
    def _execute_action(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an approved action based on its type."""
        action_type = details.get('action', '')
        
        if action_type == 'send_email':
            return self._send_email(details)
        elif action_type == 'post_linkedin':
            return self._post_linkedin(details)
        elif action_type == 'payment':
            return self._process_payment(details)
        elif action_type == 'delete_file':
            return self._delete_file(details)
        else:
            return {'success': False, 'error': f'Unknown action type: {action_type}'}
    
    def _send_email(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using email MCP or SMTP."""
        try:
            # Try to use email MCP server if available
            import subprocess
            
            to = details.get('to', '')
            subject = details.get('subject', '')
            body = details.get('body', details.get('content', ''))
            
            # For now, log the email (in production, call MCP or SMTP)
            log_entry = {
                'type': 'email_sent',
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat(),
                'status': 'logged_for_mcp'
            }
            
            log_file = self.logs_dir / f'email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            log_file.write_text(json.dumps(log_entry, indent=2))
            
            return {
                'success': True, 
                'result': 'Email logged for MCP processing',
                'details': log_entry
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _post_linkedin(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Post to LinkedIn using linkedin-poster skill."""
        try:
            content = details.get('content', details.get('body', ''))
            
            # Log for linkedin-poster skill
            log_entry = {
                'type': 'linkedin_post',
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'status': 'queued_for_poster_skill'
            }
            
            log_file = self.logs_dir / f'linkedin_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            log_file.write_text(json.dumps(log_entry, indent=2))
            
            return {
                'success': True,
                'result': 'LinkedIn post queued for poster skill',
                'details': log_entry
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_payment(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment (placeholder - requires payment integration)."""
        return {
            'success': False, 
            'error': 'Payment processing not implemented - requires payment gateway integration'
        }
    
    def _delete_file(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file from the vault."""
        try:
            filepath = details.get('filepath', '')
            if filepath:
                target = self.vault_path / filepath
                if target.exists():
                    target.unlink()
                    return {'success': True, 'result': f'Deleted {filepath}'}
            return {'success': False, 'error': 'No filepath provided or file not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_approval_file(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse approval file content."""
        details = self._parse_approval_content(content)
        details['filename'] = filename
        return details
    
    def _parse_approval_content(self, content: str) -> Dict[str, Any]:
        """Parse approval request frontmatter and body."""
        details = {}
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                details[key.strip()] = value.strip()
        
        # Extract body content (after frontmatter)
        body_start = False
        body_lines = []
        for line in lines:
            if body_start:
                body_lines.append(line)
            elif line.strip() == '---' and not in_frontmatter:
                body_start = True
        
        if body_lines:
            details['body'] = '\n'.join(body_lines).strip()
        
        return details
    
    def _log_action(self, action: str, details: str):
        """Log action to log file."""
        log_file = self.logs_dir / 'approval_workflow.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{timestamp}] {action}: {details}\n')


def main():
    """CLI entry point for approval workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Approval Workflow Skill')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Vault path')
    parser.add_argument('--create', action='store_true', help='Create approval request')
    parser.add_argument('--action', help='Action type (send_email, post_linkedin, payment, delete_file)')
    parser.add_argument('--list-pending', action='store_true', help='List pending approvals')
    parser.add_argument('--list-approved', action='store_true', help='List approved actions')
    parser.add_argument('--process', action='store_true', help='Process approved actions')
    parser.add_argument('--details', help='JSON string of action details')
    
    args = parser.parse_args()
    
    workflow = ApprovalWorkflow(args.vault)
    
    if args.create and args.action:
        details = json.loads(args.details) if args.details else {}
        filepath = workflow.create_approval_request(args.action, details)
        print(f'Created: {filepath}')
    
    elif args.list_pending:
        pending = workflow.list_pending_approvals()
        for p in pending:
            print(f"- {p['filename']}: {p.get('action', 'unknown')} (created: {p.get('created', 'unknown')})")
    
    elif args.list_approved:
        approved = workflow.list_approved_actions()
        for a in approved:
            print(f"- {a['filename']}: {a.get('action', 'unknown')}")
    
    elif args.process:
        results = workflow.process_approved_actions()
        for r in results:
            status = 'SUCCESS' if r['result']['success'] else 'FAILED'
            print(f"[{status}] {r['file']}: {r['action']} - {r['result']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
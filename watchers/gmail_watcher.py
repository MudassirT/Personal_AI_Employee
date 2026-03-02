"""
Gmail Watcher - Monitors Gmail for new unread/important emails.

This watcher connects to the Gmail API, checks for new messages,
and creates action files in the Needs_Action folder for Claude to process.

Setup Requirements:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json to this directory
4. First run will open browser for authorization

Usage:
    python gmail_watcher.py
"""

import os
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher

# Gmail API imports (install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib)
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import client_config
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """
    Gmail Watcher - Monitors Gmail for new messages.
    
    Features:
    - Monitors unread and important emails
    - Filters by keywords (optional)
    - Creates markdown action files with email content
    - Tracks processed message IDs to avoid duplicates
    """
    
    # OAuth scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Keywords that indicate high priority
    PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'important', 'deadline']
    
    def __init__(self, vault_path: str, credentials_path: Optional[str] = None, 
                 check_interval: int = 120):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail credentials JSON (default: ./credentials.json)
            check_interval: Seconds between checks (default: 120)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not installed")
        
        super().__init__(vault_path, check_interval)
        
        # Default credentials path
        self.credentials_path = credentials_path or Path(__file__).parent / 'credentials.json'
        self.token_path = Path(__file__).parent / 'token.json'
        
        # Gmail service
        self.service = None
        
        # Load processed IDs from disk for persistence
        self.load_processed_from_disk()
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful
        """
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        self.logger.error(
                            f'Credentials file not found: {self.credentials_path}\n'
                            'Please download credentials.json from Google Cloud Console'
                        )
                        return False
                    
                    # Run OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save token for future use
                self.token_path.write_text(creds.to_json())
                self.logger.info('Authentication successful')
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            return True
            
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread/important emails.
        
        Returns:
            List of new email message dicts
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Query for unread, important messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                msg_id = msg['id']
                if not self.is_processed(msg_id):
                    new_messages.append(msg)
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            # Try to re-authenticate on error
            self.service = None
            return []
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create markdown action file for email.
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path to created file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg['payload'].get('headers', [])
            header_dict = {}
            for h in headers:
                header_dict[h['name']] = h['value']
            
            # Extract body
            body = self._extract_body(msg['payload'])
            
            # Determine priority
            priority = self._determine_priority(header_dict, body)
            
            # Get sender info
            from_email = header_dict.get('From', 'Unknown')
            subject = header_dict.get('Subject', 'No Subject')
            
            # Create filename
            safe_subject = self._sanitize_filename(subject[:50])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'EMAIL_{timestamp}_{safe_subject}.md'
            
            # Create content
            content = f'''---
type: email
message_id: {message['id']}
from: {from_email}
to: {header_dict.get('To', 'Unknown')}
subject: {subject}
received: {datetime.now().isoformat()}
priority: {priority}
status: unread
---

# Email: {subject}

## Sender
**From:** {from_email}  
**To:** {header_dict.get('To', 'Unknown')}  
**Date:** {header_dict.get('Date', 'Unknown')}

---

## Email Content

{body}

---

## Suggested Actions

- [ ] Read and understand the email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create follow-up task
- [ ] Archive after processing

## Notes

<!-- Add your notes here -->

---
*Created by Gmail Watcher at {datetime.now().isoformat()}*
'''
            
            # Write file
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.mark_processed(message['id'])
            self.save_processed_to_disk()
            
            # Also mark as read in Gmail (optional)
            # self._mark_as_read(message['id'])
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from payload.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Email body text
        """
        body = ""
        
        # Check for multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        # Could add HTML stripping here
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        else:
            # Single part
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        
        # Truncate if too long
        if len(body) > 5000:
            body = body[:5000] + "\n\n... [truncated]"
        
        return body.strip() or "[No text content]"
    
    def _determine_priority(self, headers: Dict[str, str], body: str) -> str:
        """
        Determine email priority based on content.
        
        Args:
            headers: Email headers
            body: Email body
            
        Returns:
            Priority level: 'high', 'normal', or 'low'
        """
        # Check subject and body for priority keywords
        text = (headers.get('Subject', '') + ' ' + body).lower()
        
        for keyword in self.PRIORITY_KEYWORDS:
            if keyword in text:
                return 'high'
        
        # Check importance header
        if headers.get('Importance', '').lower() == 'high':
            return 'high'
        
        return 'normal'
    
    def _sanitize_filename(self, text: str) -> str:
        """
        Sanitize text for use in filename.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized filename-safe string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()
    
    def _mark_as_read(self, message_id: str):
        """
        Mark email as read in Gmail.
        
        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f'Marked message {message_id} as read')
        except Exception as e:
            self.logger.error(f'Error marking as read: {e}')


def main():
    """Main entry point."""
    import sys
    
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default: sibling directory
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Create and run watcher
    watcher = GmailWatcher(
        vault_path=str(vault_path),
        check_interval=120  # Check every 2 minutes
    )
    
    print(f"Gmail Watcher starting...")
    print(f"Vault: {vault_path}")
    print("Press Ctrl+C to stop")
    print()
    
    watcher.run()


if __name__ == '__main__':
    main()

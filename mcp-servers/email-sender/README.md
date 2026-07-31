# Email Sender MCP Server

Model Context Protocol (MCP) server for sending emails via Gmail API or SMTP.

## Overview

This MCP server provides email capabilities for the AI Employee:
- Send emails
- Draft emails
- Search emails
- Mark as read

## Installation

```bash
cd mcp-servers/email-sender
pip install -r requirements.txt
```

## Configuration

### Gmail API (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to this folder

### SMTP (Fallback)

Create `.env` file:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your-app-password
```

## Usage

### Start Server

```bash
python email_mcp_server.py
```

### Configure in Claude Code/Qwen Code

Add to MCP configuration:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/path/to/email-sender/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

## Tools

### send_email

Send an email.

```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email body text",
  "attachments": []
}
```

### draft_email

Create a draft email (doesn't send).

```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email body text"
}
```

### search_emails

Search for emails.

```json
{
  "query": "from:client is:unread",
  "maxResults": 10
}
```

### mark_read

Mark emails as read.

```json
{
  "messageIds": ["msg_id_1", "msg_id_2"]
}
```

## Implementation

```python
# email_mcp_server.py
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# MCP Server implementation
class EmailMCPServer:
    """Email MCP Server."""
    
    def __init__(self):
        self.use_gmail_api = False
        self.credentials_path = os.getenv('GMAIL_CREDENTIALS')
        
        if self.credentials_path and Path(self.credentials_path).exists():
            self.use_gmail_api = True
            self.setup_gmail_api()
        else:
            self.setup_smtp()
    
    def setup_gmail_api(self):
        """Setup Gmail API."""
        from google.oauth2.credentials import Credentials
        from google.oauth2 import client_config
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        self.scopes = ['https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        self.service = None
    
    def setup_smtp(self):
        """Setup SMTP."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
    
    def send_email(self, to: str, subject: str, body: str, 
                   attachments: list = None) -> dict:
        """Send an email."""
        try:
            if self.use_gmail_api:
                return self._send_gmail_api(to, subject, body, attachments)
            else:
                return self._send_smtp(to, subject, body, attachments)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_smtp(self, to: str, subject: str, body: str,
                   attachments: list = None) -> dict:
        """Send email via SMTP."""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = to
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                with open(filepath, 'rb') as f:
                    part = MIMEText(f.read())
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={Path(filepath).name}'
                    )
                    msg.attach(part)
        
        # Send
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.smtp_username, self.smtp_password)
        server.send_message(msg)
        server.quit()
        
        return {'success': True, 'message_id': 'sent'}
    
    def _send_gmail_api(self, to: str, subject: str, body: str,
                        attachments: list = None) -> dict:
        """Send email via Gmail API."""
        # Implementation using Gmail API
        # See Gmail API documentation for full implementation
        pass
    
    def draft_email(self, to: str, subject: str, body: str) -> dict:
        """Create a draft email."""
        # Similar to send but save as draft
        pass
    
    def search_emails(self, query: str, max_results: int = 10) -> dict:
        """Search for emails."""
        if self.use_gmail_api:
            # Use Gmail API search
            pass
        else:
            return {'success': False, 'error': 'Search requires Gmail API'}
    
    def mark_read(self, message_ids: list) -> dict:
        """Mark emails as read."""
        if self.use_gmail_api:
            # Use Gmail API to mark as read
            pass
        else:
            return {'success': False, 'error': 'Mark read requires Gmail API'}


# MCP Protocol handlers
def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle MCP tool call."""
    server = EmailMCPServer()
    
    if tool_name == 'send_email':
        return server.send_email(**arguments)
    elif tool_name == 'draft_email':
        return server.draft_email(**arguments)
    elif tool_name == 'search_emails':
        return server.search_emails(**arguments)
    elif tool_name == 'mark_read':
        return server.mark_read(**arguments)
    else:
        return {'success': False, 'error': f'Unknown tool: {tool_name}'}


if __name__ == '__main__':
    # Run MCP server
    print("Email MCP Server running...")
    # Implement MCP protocol communication
```

## Requirements

```txt
# requirements.txt
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
```

## Security Notes

⚠️ **Important:**
- Never commit credentials
- Use app passwords for SMTP
- Rotate credentials regularly
- Log all sent emails

## Testing

```bash
# Test send email
python -c "
from email_mcp_server import EmailMCPServer
server = EmailMCPServer()
result = server.send_email('test@example.com', 'Test', 'Hello World')
print(result)
"
```

---

*Email Sender MCP Server - AI Employee v0.2*

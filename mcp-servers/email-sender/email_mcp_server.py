"""
Email MCP Server

Simple HTTP JSON interface to call email tools (send_email, draft_email,
search_emails, mark_read). Supports Gmail API if `GMAIL_CREDENTIALS` or
`credentials.json` is present; otherwise falls back to SMTP using env vars.

Usage:
    python email_mcp_server.py

POST /tool
Body: {"tool": "send_email", "args": { ... }}

Health: GET /health
"""

import os
import json
import base64
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger('EmailMCP')
logging.basicConfig(level=logging.INFO)


class EmailMCPServer:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly',
    ]

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS')
        self.token_path = Path(__file__).parent / 'token.json'
        self.use_gmail_api = False
        self.service = None

        # SMTP fallback configuration from environment
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

        # Try to setup Gmail API if credentials provided
        if self.credentials_path and Path(self.credentials_path).exists():
            try:
                self._setup_gmail_api()
                self.use_gmail_api = True
                logger.info('Gmail API configured')
            except Exception as e:
                logger.warning(f'Gmail API setup failed: {e}; falling back to SMTP')
                self.use_gmail_api = False

    def _setup_gmail_api(self):
        """Initialize Gmail API service using OAuth2 flow."""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None

        # Try load saved token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)

        # If no valid creds, run auth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None

            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                # Save token
                with open(self.token_path, 'w', encoding='utf-8') as f:
                    f.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(self, to: str, subject: str, body: str, attachments: list = None) -> Dict[str, Any]:
        """Send an email via Gmail API or SMTP fallback."""
        attachments = attachments or []

        if self.use_gmail_api and self.service:
            try:
                message = MIMEMultipart()
                message['To'] = to
                message['Subject'] = subject
                message.attach(MIMEText(body, 'plain'))

                # attachments not implemented for Gmail API in this minimal server
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                sent = self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
                return {'success': True, 'message_id': sent.get('id')}
            except Exception as e:
                logger.exception('Gmail API send failed')
                return {'success': False, 'error': str(e)}

        # SMTP fallback
        try:
            import smtplib

            msg = MIMEMultipart()
            msg['From'] = self.smtp_username or 'noreply@example.com'
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach files (simple inline attach as text)
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as f:
                        part = MIMEText(f.read().decode(errors='replace'))
                        part.add_header('Content-Disposition', f'attachment; filename={Path(filepath).name}')
                        msg.attach(part)
                except Exception:
                    logger.warning(f'Could not attach {filepath}')

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            return {'success': True, 'message_id': 'smtp_sent'}
        except Exception as e:
            logger.exception('SMTP send failed')
            return {'success': False, 'error': str(e)}

    def draft_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Create an email draft (Gmail API only)."""
        if self.use_gmail_api and self.service:
            try:
                from googleapiclient.errors import HttpError

                msg = MIMEMultipart()
                msg['To'] = to
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

                draft = self.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
                return {'success': True, 'draft_id': draft.get('id')}
            except Exception as e:
                logger.exception('Draft creation failed')
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Drafts require Gmail API'}

    def search_emails(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search emails via Gmail API."""
        if not (self.use_gmail_api and self.service):
            return {'success': False, 'error': 'Search requires Gmail API'}

        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            msgs = results.get('messages', [])
            items = []
            for m in msgs:
                items.append({'id': m.get('id')})
            return {'success': True, 'messages': items}
        except Exception as e:
            logger.exception('Search failed')
            return {'success': False, 'error': str(e)}

    def mark_read(self, message_ids: list) -> Dict[str, Any]:
        """Mark messages as read (Gmail API only)."""
        if not (self.use_gmail_api and self.service):
            return {'success': False, 'error': 'Mark read requires Gmail API'}

        results = []
        try:
            for mid in message_ids:
                res = self.service.users().messages().modify(userId='me', id=mid, body={'removeLabelIds': ['UNREAD']}).execute()
                results.append({'id': mid, 'status': 'modified'})
            return {'success': True, 'results': results}
        except Exception as e:
            logger.exception('Mark read failed')
            return {'success': False, 'error': str(e)}


def handle_tool_call(server: EmailMCPServer, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
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
    except TypeError as e:
        return {'success': False, 'error': f'Argument error: {e}'}


class SimpleHandler(BaseHTTPRequestHandler):
    server_instance: EmailMCPServer = None

    def _send_json(self, obj: Dict[str, Any], code: int = 200):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/health':
            self._send_json({'status': 'ok', 'use_gmail_api': bool(self.server_instance.use_gmail_api)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/tool':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body)
            tool = payload.get('tool')
            args = payload.get('args', {})
            if not tool:
                self._send_json({'success': False, 'error': 'Missing tool name'}, code=400)
                return

            result = handle_tool_call(self.server_instance, tool, args)
            self._send_json(result)
        except json.JSONDecodeError:
            self._send_json({'success': False, 'error': 'Invalid JSON'}, code=400)


def run_http_server(host: str = '127.0.0.1', port: int = 8765):
    server = EmailMCPServer()
    SimpleHandler.server_instance = server
    httpd = HTTPServer((host, port), SimpleHandler)
    logger.info(f'Email MCP Server listening on http://{host}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down')
        httpd.server_close()


if __name__ == '__main__':
    run_http_server()

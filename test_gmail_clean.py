"""
Quick test - Fetch and display unread Gmail messages with clean text
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from pathlib import Path
import base64
import re
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def extract_clean_text(payload):
    """Extract plain text from Gmail payload, preferring plain text over HTML."""
    plain_text = ""
    html_text = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    data = part['body']['data']
                    plain_text += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    data = part['body']['data']
                    html_text += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    else:
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            content = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            if '<html' in content.lower() or '<!DOCTYPE' in content.lower():
                html_text = content
            else:
                plain_text = content
    
    if plain_text:
        return plain_text.strip()
    elif html_text:
        # Strip HTML
        text = re.sub(r'<[^>]+>', '', html_text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    return ""

def main():
    creds_path = Path('watchers/credentials.json')
    token_path = Path('watchers/token.json')
    
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Get unread messages
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=5
    ).execute()
    
    messages = results.get('messages', [])
    
    print(f"Found {len(messages)} unread message(s)\n")
    
    for msg in messages:
        msg_detail = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='full'
        ).execute()
        
        headers = msg_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        
        # Extract clean text
        body = extract_clean_text(msg_detail['payload'])
        
        print(f"From: {from_addr}")
        print(f"Subject: {subject}")
        print(f"Content (first 200 chars):\n{body[:200]}...")
        print("-" * 80)

if __name__ == '__main__':
    main()

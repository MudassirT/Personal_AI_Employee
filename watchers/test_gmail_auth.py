"""
Test Gmail API Authentication

Run this script first to authenticate with Gmail API.
It will open a browser for you to grant permission.
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds_path = Path(__file__).parent / 'credentials.json'
    token_path = Path(__file__).parent / 'token.json'
    
    if not creds_path.exists():
        print(f"ERROR: credentials.json not found at {creds_path}")
        print("Please create Gmail API credentials first:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json to the watchers folder")
        return
    
    creds = None
    
    # Load existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print(f"Loaded existing token from {token_path}")
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            print("Opening browser for authentication...")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("Authentication successful!")
            
            # Save token for future use
            token_path.write_text(creds.to_json())
            print(f"Token saved to {token_path}")
    
    # Test Gmail API
    print("\nTesting Gmail API...")
    service = build('gmail', 'v1', credentials=creds)
    
    # Get unread messages
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=5
    ).execute()
    
    messages = results.get('messages', [])
    
    print(f"\nFound {len(messages)} unread message(s)")
    
    for msg in messages[:3]:  # Show first 3
        msg_detail = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject']
        ).execute()
        
        headers = msg_detail['payload']['headers']
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        
        print(f"  - From: {from_addr}")
        print(f"    Subject: {subject}")
        print()

    print("[OK] Gmail API authentication successful!")
    print("\nYou can now run: python gmail_watcher.py")


if __name__ == '__main__':
    main()

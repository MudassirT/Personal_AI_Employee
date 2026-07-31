#!/usr/bin/env python3
"""
Simple Gmail Watcher using IMAP/SMTP (App Password)
No OAuth required - uses App Password authentication
"""

import imaplib
import email
import smtplib
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging


class SimpleGmailWatcher:
    """Gmail watcher using IMAP with App Password."""
    
    def __init__(self, vault_path: str = "AI_Employee_Vault", 
                 gmail_user: str = None, app_password: str = None,
                 check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.gmail_user = gmail_user or os.getenv("GMAIL_USER")
        self.app_password = app_password or os.getenv("GMAIL_APP_PASSWORD")
        self.check_interval = check_interval
        
        # Directories
        self.inbox_dir = self.vault_path / "Inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger()
        
        # State file for last checked email UID
        self.state_file = self.vault_path / ".gmail_watcher_state.json"
        self.last_uid = self._load_state()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("SimpleGmailWatcher")
        logger.setLevel(logging.INFO)
        log_file = self.logs_dir / "gmail_watcher.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        return logger
    
    def _load_state(self) -> int:
        """Load last processed email UID."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f).get("last_uid", 0)
            except:
                pass
        return 0
    
    def _save_state(self, uid: int):
        """Save last processed email UID."""
        with open(self.state_file, "w") as f:
            json.dump({"last_uid": uid, "updated": datetime.now().isoformat()}, f)
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """Connect to Gmail IMAP."""
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(self.gmail_user, self.app_password)
        return mail
    
    def fetch_new_emails(self) -> list:
        """Fetch new emails since last check."""
        new_emails = []
        
        try:
            mail = self.connect()
            mail.select("INBOX")
            
            # Search for emails newer than last UID
            if self.last_uid > 0:
                _, messages = mail.search(None, f'UID {self.last_uid + 1}:*')
            else:
                # First run: get last 50 emails
                _, messages = mail.search(None, "ALL")
            
            uids = messages[0].split()
            
            for uid in uids[-50:]:  # Process max 50 per run
                uid_int = int(uid)
                if uid_int <= self.last_uid:
                    continue
                
                _, msg_data = mail.fetch(uid, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Parse email
                parsed = self._parse_email(msg)
                parsed["uid"] = uid_int
                new_emails.append(parsed)
                self.last_uid = uid_int
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
        
        return new_emails
    
    def _parse_email(self, msg) -> dict:
        """Parse email message into dict."""
        # Headers
        subject = msg.get("Subject", "")
        from_addr = msg.get("From", "")
        date_str = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")
        
        # Body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        
        return {
            "subject": subject,
            "from": from_addr,
            "date": date_str,
            "message_id": message_id,
            "body": body.strip()[:5000],  # Limit size
            "received_at": datetime.now().isoformat()
        }
    
    def save_email_to_vault(self, email_data: dict) -> Path:
        """Save email as markdown file in Inbox."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_subject = "".join(c for c in email_data["subject"] if c.isalnum() or c in " -_")[:50]
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.inbox_dir / filename
        
        content = f"""---
type: email
from: "{email_data['from']}"
subject: "{email_data['subject']}"
date: "{email_data['date']}"
message_id: "{email_data['message_id']}"
uid: {email_data['uid']}
received_at: "{email_data['received_at']}"
---

# Email Received

**From:** {email_data['from']}
**Subject:** {email_data['subject']}
**Date:** {email_data['date']}
**Message-ID:** {email_data['message_id']}

---

## Body

{email_data['body']}

---
*Saved by Simple Gmail Watcher at {email_data['received_at']}*
"""
        filepath.write_text(content, encoding="utf-8")
        return filepath
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.gmail_user
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.gmail_user, self.app_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def run_once(self) -> int:
        """Check for new emails once."""
        if not self.gmail_user or not self.app_password:
            self.logger.error("GMAIL_USER and GMAIL_APP_PASSWORD must be set")
            return 0
        
        self.logger.info("Checking for new emails...")
        emails = self.fetch_new_emails()
        
        count = 0
        for email_data in emails:
            filepath = self.save_email_to_vault(email_data)
            self.logger.info(f"Saved email: {filepath.name}")
            count += 1
        
        if count > 0:
            self._save_state(self.last_uid)
            self.logger.info(f"Processed {count} new email(s)")
        else:
            self.logger.info("No new emails")
        
        return count
    
    def run_continuous(self):
        """Run continuous monitoring."""
        self.logger.info(f"Starting Gmail watcher (interval: {self.check_interval}s)")
        
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.logger.error(f"Error in watcher loop: {e}")
            
            time.sleep(self.check_interval)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Gmail Watcher (App Password)")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Vault path")
    parser.add_argument("--user", help="Gmail address")
    parser.add_argument("--password", help="App Password (16 chars)")
    parser.add_argument("--interval", type=int, default=60, help="Check interval (seconds)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    watcher = SimpleGmailWatcher(
        vault_path=args.vault,
        gmail_user=args.user,
        app_password=args.password,
        check_interval=args.interval
    )
    
    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} email(s)")
    else:
        watcher.run_continuous()


if __name__ == "__main__":
    main()
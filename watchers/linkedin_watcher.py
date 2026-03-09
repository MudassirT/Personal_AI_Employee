"""
LinkedIn Watcher - Monitors LinkedIn for notifications and messages.

This watcher uses Playwright to automate LinkedIn and monitor for:
- New connection requests
- Messages
- Important notifications

IMPORTANT:
- Requires LinkedIn login on first run
- Session is persisted in the session folder
- Be aware of LinkedIn's terms of service

Usage:
    python linkedin_watcher.py
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: playwright install")


class LinkedInWatcher(BaseWatcher):
    """
    LinkedIn Watcher - Monitors LinkedIn for notifications and messages.
    
    Features:
    - Monitors new connection requests
    - Monitors messages
    - Monitors important notifications
    - Creates markdown action files
    - Persists session to avoid repeated logins
    """
    
    # Keywords that indicate high priority notifications
    PRIORITY_KEYWORDS = [
        'message', 'connection', 'job', 'opportunity', 'hiring',
        'interview', 'position', 'role', 'urgent', 'important'
    ]
    
    # LinkedIn URLs
    LINKEDIN_URL = 'https://www.linkedin.com'
    LINKEDIN_FEED = 'https://www.linkedin.com/feed/'
    LINKEDIN_NETWORK = 'https://www.linkedin.com/mynetwork/'
    LINKEDIN_MESSAGING = 'https://www.linkedin.com/messaging/'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 check_interval: int = 900, headless: bool = True):
        """
        Initialize LinkedIn Watcher.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: ./linkedin_session)
            check_interval: Seconds between checks (default: 900 = 15 min)
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed")
        
        super().__init__(vault_path, check_interval)
        
        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(__file__).parent / 'linkedin_session'
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        
        # Track processed items
        self.processed_notifications: set = set()
        self.load_processed_from_disk()
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new LinkedIn notifications and messages.
        
        Returns:
            List of new notification dicts
        """
        notifications = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto(self.LINKEDIN_URL, wait_until='domcontentloaded', timeout=60000)
                
                # Check if logged in
                if 'login' in page.url:
                    self.logger.warning('Not logged in to LinkedIn')
                    self.logger.info('Please log in manually when browser opens')
                    try:
                        # Wait for user to log in (max 2 minutes)
                        page.wait_for_url(self.LINKEDIN_FEED, timeout=120000)
                        self.logger.info('Login successful')
                    except Exception as e:
                        self.logger.error('Login timeout or failed')
                        browser.close()
                        return []
                
                # Navigate to feed to check notifications
                page.goto(self.LINKEDIN_FEED, wait_until='domcontentloaded', timeout=60000)
                time.sleep(5)
                
                # Check for notification bell
                try:
                    notification_bell = page.query_selector('[aria-label*="notification"]')
                    if notification_bell:
                        badge = notification_bell.query_selector('[aria-label*="unread"]')
                        if badge:
                            self.logger.info('Found unread notifications')
                            notifications.append({
                                'type': 'notification',
                                'content': 'You have unread LinkedIn notifications',
                                'priority': 'normal',
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    self.logger.debug(f'No notification bell found: {e}')
                
                # Check for connection requests
                try:
                    page.goto(self.LINKEDIN_NETWORK, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(3)
                    
                    # Look for connection requests
                    connection_requests = page.query_selector_all('[aria-label*="invitation"]')
                    if connection_requests:
                        self.logger.info(f'Found {len(connection_requests)} connection request(s)')
                        notifications.append({
                            'type': 'connection_request',
                            'content': f'You have {len(connection_requests)} new connection request(s)',
                            'priority': 'high',
                            'count': len(connection_requests),
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    self.logger.debug(f'Error checking connections: {e}')
                
                # Check for messages
                try:
                    page.goto(self.LINKEDIN_MESSAGING, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(3)
                    
                    # Look for unread messages
                    unread_chats = page.query_selector_all('[aria-label*="unread"]')
                    if unread_chats:
                        self.logger.info(f'Found {len(unread_chats)} unread message(s)')
                        
                        for chat in unread_chats[:5]:  # Limit to 5
                            try:
                                text = chat.inner_text()
                                # Extract sender name if possible
                                name_elem = chat.query_selector('[aria-label*="from"]')
                                sender = name_elem.get_attribute('aria-label', '').replace('from ', '') if name_elem else 'Unknown'
                                
                                notifications.append({
                                    'type': 'message',
                                    'content': text[:200],  # Truncate
                                    'sender': sender,
                                    'priority': 'high',
                                    'timestamp': datetime.now().isoformat()
                                })
                            except Exception as e:
                                self.logger.debug(f'Error processing chat: {e}')
                except Exception as e:
                    self.logger.debug(f'Error checking messages: {e}')
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
        
        return notifications
    
    def create_action_file(self, notification: Dict[str, Any]) -> Optional[Path]:
        """
        Create markdown action file for LinkedIn notification.
        
        Args:
            notification: Notification dict from check_for_updates
            
        Returns:
            Path to created file
        """
        try:
            # Create filename
            notif_type = notification.get('type', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'LINKEDIN_{timestamp}_{notif_type.upper()}.md'
            
            # Create content
            content = f'''---
type: linkedin_{notif_type}
notification_type: {notif_type}
received: {notification.get('timestamp', datetime.now().isoformat())}
priority: {notification.get('priority', 'normal')}
status: unread
---

# LinkedIn Notification

## Type
**{notif_type.replace('_', ' ').title()}**

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Priority
{notification.get('priority', 'normal').upper()}

---

## Content

{notification.get('content', 'No content')}

{f"**Sender:** {notification.get('sender', 'Unknown')}" if notification.get('sender') else ""}
{f"**Count:** {notification.get('count', 1)}" if notification.get('count') else ""}

---

## Suggested Actions

- [ ] Review the notification
- [ ] Take appropriate action
- [ ] Respond if needed
- [ ] Mark as processed

## Notes

<!-- Add your notes here -->

---
*Created by LinkedIn Watcher at {datetime.now().isoformat()}*
'''
            
            # Write file
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            notif_id = f"{notif_type}_{notification.get('timestamp', '')}"
            self.mark_processed(notif_id)
            self.save_processed_to_disk()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def send_message(self, contact_name: str, message: str) -> bool:
        """
        Send a LinkedIn message to a contact.
        
        Args:
            contact_name: Contact name
            message: Message text to send
            
        Returns:
            True if sent successfully
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(self.LINKEDIN_MESSAGING, wait_until='networkidle')
                time.sleep(2)
                
                # Search for contact
                try:
                    search_box = page.query_selector('[aria-label*="Search"]')
                    if search_box:
                        search_box.fill(contact_name)
                        time.sleep(2)
                        
                        # Click on contact
                        contact_elem = page.query_selector(f'[aria-label*="{contact_name}"]')
                        if contact_elem:
                            contact_elem.click()
                            time.sleep(2)
                            
                            # Find message input
                            message_input = page.query_selector('[role="textbox"]')
                            if message_input:
                                message_input.fill(message)
                                time.sleep(1)
                                
                                # Find send button
                                send_button = page.query_selector('[aria-label*="Send"]')
                                if send_button:
                                    send_button.click()
                                    self.logger.info(f'Message sent to {contact_name}')
                                    browser.close()
                                    return True
                except Exception as e:
                    self.logger.debug(f'Error sending message: {e}')
                
                browser.close()
                self.logger.warning(f'Could not send message to {contact_name}')
                return False
                
        except Exception as e:
            self.logger.error(f'Error sending message: {e}')
            return False


def main():
    """Main entry point."""
    import sys

    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    # Check if session exists (user has already authenticated)
    session_path = Path(__file__).parent / 'linkedin_session'
    session_exists = session_path.exists() and (session_path / 'Default').exists()
    
    # Use headless mode if session exists, otherwise show browser
    headless = session_exists
    check_interval = 900  # Check every 15 minutes

    # Create and run watcher
    watcher = LinkedInWatcher(
        vault_path=str(vault_path),
        check_interval=check_interval,
        headless=headless
    )

    print("=" * 50)
    print("LinkedIn Watcher")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"Session: {watcher.session_path}")
    print(f"Check interval: {check_interval}s ({check_interval//60} min)")
    print(f"Headless mode: {headless}")
    print()
    
    if not session_exists:
        print("FIRST RUN: Log in to LinkedIn when browser opens")
        print("Session will be saved for future runs")
    else:
        print("Using saved session (headless mode)")
    
    print()
    print("Press Ctrl+C to stop")
    print()
    
    watcher.run()


if __name__ == '__main__':
    main()

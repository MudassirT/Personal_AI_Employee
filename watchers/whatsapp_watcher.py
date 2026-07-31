"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages.

This watcher uses Playwright to automate WhatsApp Web and monitor
for unread messages containing priority keywords.

IMPORTANT: 
- Requires QR code login on first run
- Session is persisted in the session folder
- Be aware of WhatsApp's terms of service

Usage:
    python whatsapp_watcher.py
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


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Watcher - Monitors WhatsApp Web for new messages.
    
    Features:
    - Monitors unread messages
    - Filters by priority keywords
    - Creates markdown action files
    - Persists session to avoid repeated QR scans
    """
    
    # Keywords that indicate high priority messages
    PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important', 'deadline']
    
    # WhatsApp Web selectors (may change with updates)
    SELECTORS = {
        'chat_list': '[data-testid="chat-list"]',
        'chat': 'div[role="row"]',
        'unread_indicator': 'span[aria-label*="unread"]',
        'message_text': 'span[aria-label^="message"]',
        'contact_name': 'span[title]',
    }
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None,
                 check_interval: int = 30, headless: bool = True):
        """
        Initialize WhatsApp Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: ./whatsapp_session)
            check_interval: Seconds between checks (default: 30)
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed")
        
        super().__init__(vault_path, check_interval)
        
        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(__file__).parent / 'whatsapp_session'
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        
        # Track processed messages
        self.processed_chats: set = set()
        self.load_processed_from_disk()
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread messages on WhatsApp Web.
        
        Returns:
            List of new message dicts with chat info and text
        """
        messages = []
        
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
                
                # Navigate to WhatsApp Web
                self.logger.info('Navigating to WhatsApp Web...')
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector(self.SELECTORS['chat_list'], timeout=30000)
                    self.logger.info('WhatsApp Web loaded successfully')
                except Exception as e:
                    self.logger.warning(f'Chat list not found: {e}')
                    # Might need QR scan
                    self.logger.info('Please scan QR code if prompted')
                    try:
                        page.wait_for_selector(self.SELECTORS['chat_list'], timeout=60000)
                    except Exception:
                        self.logger.error('Failed to load WhatsApp Web')
                        browser.close()
                        return []
                
                # Give page time to render
                time.sleep(3)
                
                # Find all chats
                chats = page.query_selector_all(self.SELECTORS['chat'])
                self.logger.info(f'Found {len(chats)} chats')
                
                for chat in chats:
                    try:
                        # Get chat text content
                        text = chat.inner_text()
                        
                        # Check for unread indicator
                        is_unread = 'unread' in chat.get_attribute('aria-label', '').lower()
                        
                        # Extract contact name
                        contact_elem = chat.query_selector(self.SELECTORS['contact_name'])
                        contact_name = contact_elem.get_attribute('title', '') if contact_elem else 'Unknown'
                        
                        # Check for priority keywords
                        text_lower = text.lower()
                        has_keyword = any(kw in text_lower for kw in self.PRIORITY_KEYWORDS)
                        
                        # Process if unread or has priority keyword
                        if is_unread or has_keyword:
                            chat_id = f'{contact_name}_{int(time.time())}'
                            
                            # Skip if already processed
                            if chat_id not in self.processed_chats:
                                messages.append({
                                    'chat_id': chat_id,
                                    'contact': contact_name,
                                    'text': text,
                                    'is_unread': is_unread,
                                    'has_keyword': has_keyword,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f'New message from {contact_name}')
                    
                    except Exception as e:
                        self.logger.debug(f'Error processing chat: {e}')
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
        
        return messages
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create markdown action file for WhatsApp message.
        
        Args:
            message: Message dict from check_for_updates
            
        Returns:
            Path to created file
        """
        try:
            # Determine priority
            priority = 'high' if message['has_keyword'] else 'normal'
            
            # Create filename
            safe_contact = self._sanitize_filename(message['contact'])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'WHATSAPP_{timestamp}_{safe_contact}.md'
            
            # Create content
            content = f'''---
type: whatsapp_message
contact: {message['contact']}
chat_id: {message['chat_id']}
received: {message['timestamp']}
priority: {priority}
status: unread
is_unread: {str(message['is_unread'])}
---

# WhatsApp Message

## Contact
**From:** {message['contact']}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Priority:** {priority.upper()}

---

## Message Content

{message['text']}

---

## Suggested Actions

- [ ] Read and understand the message
- [ ] Reply to contact
- [ ] Take necessary action
- [ ] Mark as processed

## Notes

<!-- Add your notes here -->

---
*Created by WhatsApp Watcher at {datetime.now().isoformat()}*
'''
            
            # Write file
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.mark_processed(message['chat_id'])
            self.save_processed_to_disk()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()[:30]
    
    def send_message(self, contact: str, message: str) -> bool:
        """
        Send a WhatsApp message to a contact.
        
        Args:
            contact: Contact name or phone number
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
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for chat list
                page.wait_for_selector(self.SELECTORS['chat_list'], timeout=30000)
                
                # Search for contact
                search_box = page.query_selector('[data-testid="search"]')
                if search_box:
                    search_box.fill(contact)
                    time.sleep(2)
                    
                    # Click on contact
                    contact_elem = page.query_selector(f'{self.SELECTORS["chat"]} span[title="{contact}"]')
                    if contact_elem:
                        contact_elem.click()
                        time.sleep(2)
                        
                        # Find message input
                        message_input = page.query_selector('[data-testid="compose-input"]')
                        if message_input:
                            message_input.fill(message)
                            time.sleep(1)
                            
                            # Find send button
                            send_button = page.query_selector('[data-testid="compose-btn-send"]')
                            if send_button:
                                send_button.click()
                                self.logger.info(f'Message sent to {contact}')
                                browser.close()
                                return True
                
                browser.close()
                self.logger.warning(f'Could not send message to {contact}')
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
    
    # Create and run watcher
    watcher = WhatsAppWatcher(
        vault_path=str(vault_path),
        check_interval=30,
        headless=False  # Show browser for QR scan on first run
    )
    
    print("=" * 50)
    print("WhatsApp Watcher")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"Session: {watcher.session_path}")
    print("Monitoring WhatsApp Web for priority messages")
    print()
    print("FIRST RUN: Scan QR code when browser opens")
    print("Session will be saved for future runs")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    watcher.run()


if __name__ == '__main__':
    main()

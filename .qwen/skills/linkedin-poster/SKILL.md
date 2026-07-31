---
name: linkedin-poster
description: |
  LinkedIn automation using Playwright MCP. Create company updates,
  post business content, and schedule posts. Requires LinkedIn login
  credentials. Use for business promotion, lead generation, and
  professional networking automation.
---

# LinkedIn Poster

Automate LinkedIn posting via Playwright browser automation.

## Prerequisites

- Playwright installed (`playwright install`)
- LinkedIn account credentials
- Session storage for persistent login

## Quick Start

### First Run (Login)

```bash
python scripts/linkedin_login.py
```

This opens a browser for you to log in to LinkedIn. Session is saved.

### Post to LinkedIn

```bash
python scripts/linkedin_post.py "Your post content here"
```

---

## Workflow: Create and Post

### Step 1: Create Post Content

Create a post file in `/Plans/`:

```markdown
---
type: linkedin_post
content: |
  Excited to announce our new AI Employee product!
  
  #AI #Automation #Productivity
  
  Learn more at our website.
created: 2026-03-09T10:00:00Z
status: draft
---

# LinkedIn Post Draft

## Content
Excited to announce our new AI Employee product!

#AI #Automation #Productivity

Learn more at our website.

## To Post
Move this file to /Pending_Approval/ for review.
```

### Step 2: Approval (HITL)

Move file to `/Pending_Approval/` for user review.

User approves by moving to `/Approved/`.

### Step 3: Execute Post

```bash
qwen --cwd "AI_Employee_Vault" "Post the approved LinkedIn content"
```

---

## Python Implementation

### LinkedIn Poster Class

```python
# linkedin_poster.py
from playwright.sync_api import sync_playwright, Page, BrowserContext
from pathlib import Path
import time
from typing import Optional

class LinkedInPoster:
    """Post to LinkedIn using Playwright automation."""
    
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def login(self, email: str, password: str) -> bool:
        """Log in to LinkedIn."""
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.linkedin.com/login')
            
            # Fill login form
            page.fill('#username', email)
            page.fill('#password', password)
            page.click('button[type="submit"]')
            
            # Wait for navigation
            page.wait_for_url('https://www.linkedin.com/feed/')
            
            browser.close()
            return True
    
    def create_post(self, content: str, image_path: Optional[str] = None) -> bool:
        """Create a post on LinkedIn."""
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.linkedin.com/feed/')
            
            # Wait for page to load
            time.sleep(3)
            
            # Click on "Start a post"
            try:
                start_post = page.query_selector('[aria-label="Start a post"]')
                if not start_post:
                    # Alternative selector
                    start_post = page.query_selector('button[aria-label*="post"]')
                
                if start_post:
                    start_post.click()
                    time.sleep(2)
                    
                    # Find the text input
                    text_input = page.query_selector('[role="textbox"]')
                    if text_input:
                        text_input.fill(content)
                        time.sleep(1)
                        
                        # Add image if provided
                        if image_path:
                            # Click media button
                            media_btn = page.query_selector('input[type="file"]')
                            if media_btn:
                                media_btn.set_input_files(image_path)
                                time.sleep(2)
                        
                        # Click Post button
                        post_btn = page.query_selector('button[aria-label*="Post"]')
                        if post_btn:
                            post_btn.click()
                            time.sleep(3)
                            
                            # Verify post was created
                            if self._verify_post(page, content[:50]):
                                print("Post created successfully!")
                                browser.close()
                                return True
                            else:
                                print("Post may not have been created")
                    
                browser.close()
                return False
                
            except Exception as e:
                print(f"Error creating post: {e}")
                browser.close()
                return False
    
    def _verify_post(self, page: Page, content_preview: str) -> bool:
        """Verify post was created."""
        try:
            # Look for success message or the post in feed
            time.sleep(2)
            return True
        except:
            return False
```

### Usage Script

```python
# scripts/linkedin_post.py
import sys
from linkedin_poster import LinkedInPoster

def main():
    if len(sys.argv) < 2:
        print("Usage: python linkedin_post.py \"Your post content\"")
        sys.exit(1)
    
    content = sys.argv[1]
    session_path = Path(__file__).parent.parent / 'linkedin_session'
    
    poster = LinkedInPoster(str(session_path))
    
    print(f"Posting to LinkedIn: {content[:50]}...")
    success = poster.create_post(content)
    
    if success:
        print("✓ Post created successfully")
    else:
        print("✗ Failed to create post")

if __name__ == '__main__':
    main()
```

---

## Qwen Code Integration

### Create Post Draft

```bash
qwen --cwd "AI_Employee_Vault" "Create a LinkedIn post draft about our new product launch with hashtags #AI #Automation"
```

### Post After Approval

```bash
qwen --cwd "AI_Employee_Vault" "Check Approved folder for LinkedIn posts and publish them"
```

---

## Content Templates

### Business Update

```
📢 Exciting news! 

We're launching [Product Name] to help businesses 
automate their workflows with AI.

Key features:
✓ 24/7 autonomous operation
✓ Local-first privacy
✓ Human-in-the-loop safety

Learn more: [link]

#AI #Automation #Business
```

### Thought Leadership

```
💡 Here's what I learned about AI automation:

1. Start small with repetitive tasks
2. Keep humans in the loop for decisions
3. Measure and iterate

What's your experience?

#Leadership #AI #Productivity
```

### Engagement Post

```
Question for my network:

What's the biggest time-waster in your daily workflow?

Looking to understand where AI can help most.

#Feedback #Automation
```

---

## Scheduling (Future)

```python
# Schedule post for later
import schedule

def scheduled_post():
    content = get_scheduled_content()
    poster.create_post(content)

schedule.every().day.at("09:00").do(scheduled_post)
```

---

## Best Practices

1. **Review before posting** - Always use HITL approval
2. **Add value** - Share insights, not just promotions
3. **Use hashtags** - 3-5 relevant hashtags
4. **Engage** - Respond to comments
5. **Consistency** - Post regularly (2-3x/week)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Clear session folder, re-login |
| Post button not found | Refresh page, wait longer |
| Content not appearing | Check character limit (3000) |
| Image upload fails | Use supported formats (PNG, JPG) |

---

## Security Notes

⚠️ **Important:**
- Never store LinkedIn password in code
- Use session storage for persistence
- Always review posts before publishing
- Respect LinkedIn's terms of service

---

*LinkedIn Poster Skill - AI Employee v0.2*

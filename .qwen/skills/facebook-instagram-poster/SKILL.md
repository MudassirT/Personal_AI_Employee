---
name: facebook-instagram-poster
description: |
  Facebook and Instagram posting automation using Playwright.
  Supports creating posts, stories, reels, and managing multiple pages.
  Requires manual login on first run; session is saved for future use.
---

# Facebook & Instagram Poster

Automated posting to Facebook Pages and Instagram Business accounts using Playwright browser automation.

## Overview

This skill enables the AI Employee to:
- Post to Facebook Pages (text, images, links)
- Post to Instagram (feed posts, stories, reels)
- Schedule posts for future publication
- Manage multiple pages/accounts
- Track posting history and engagement

## Prerequisites

1. **Playwright installed**: `pip install playwright && playwright install chromium`
2. **Facebook/Instagram Business accounts** with Pages set up
3. **Meta Business Suite** access for Instagram integration

## Setup

### First Run - Authentication

```bash
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py --auth
```

This will:
1. Open a browser window
2. Navigate to Facebook login
3. Prompt you to log in manually
4. Save session cookies for future runs

**Note**: You must have Admin or Editor access to the Facebook Pages you want to post to.

### Session Storage

Sessions are stored in:
- `watchers/facebook_session/` - Facebook cookies
- `watchers/instagram_session/` - Instagram cookies

## Usage

### Create Facebook Post

```bash
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py \
  --platform facebook \
  --page "Your Page Name" \
  --content "Hello from AI Employee! 🤖" \
  --image "path/to/image.jpg"
```

### Create Instagram Post

```bash
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py \
  --platform instagram \
  --content "New blog post! Check it out 👇" \
  --image "path/to/image.jpg" \
  --hashtags "#AI #Automation #Tech"
```

### Schedule a Post

```bash
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py \
  --platform facebook \
  --page "Your Page Name" \
  --content "Scheduled post!" \
  --schedule "2026-01-15 10:00"
```

## Qwen Code Integration

### Post to Facebook

```bash
qwen --cwd "AI_Employee_Vault" "Create a Facebook post about our new AI Employee launch on the company page"
```

### Post to Instagram

```bash
qwen --cwd "AI_Employee_Vault" "Create an Instagram post with image from Social/launch_image.jpg and caption about our automation features"
```

### Schedule Posts

```bash
qwen --cwd "AI_Employee_Vault" "Schedule Facebook and Instagram posts for next Monday 9 AM announcing our weekly update"
```

## Approval Workflow Integration

For sensitive posts, the skill creates approval requests:

1. AI creates draft in `Plans/social_post_*.md`
2. Moves to `Pending_Approval/` for review
3. Human reviews and moves to `Approved/`
4. Skill detects approval and publishes

## File Structure

```
AI_Employee_Vault/
├── Social/
│   ├── Facebook/
│   │   ├── Posts/
│   │   ├── Scheduled/
│   │   └── History/
│   ├── Instagram/
│   │   ├── Posts/
│   │   ├── Stories/
│   │   ├── Reels/
│   │   └── History/
│   └── Assets/
│       └── images/
├── Plans/
│   └── social_post_*.md
├── Pending_Approval/
│   └── social_*.md
└── Logs/
    └── social_poster.log
```

## Post Template (Plans/social_post_*.md)

```markdown
---
type: social_post
platform: facebook|instagram|both
page: "Page Name"
content: |
  Your post content here
  Multiple lines supported
image: "Social/Assets/images/launch.jpg"
hashtags: "#AI #Automation #Tech"
schedule: "2026-01-15 10:00"  # Optional
status: draft
created: "2026-01-10T10:30:00Z"
---

# Social Media Post Plan

## Platform: Facebook
**Page:** Company Page
**Content:** Your post content
**Image:** Social/Assets/images/launch.jpg
**Hashtags:** #AI #Automation #Tech
**Schedule:** 2026-01-15 10:00 (or immediate)

## Approval Required
Move this file to `/Approved/` to publish.
```

## Error Handling

| Error | Solution |
|-------|----------|
| "Not logged in" | Run `--auth` to re-authenticate |
| "Page not found" | Verify page name matches exactly |
| "Image upload failed" | Check file path and format (JPG/PNG) |
| "Rate limited" | Wait 30+ minutes; check Meta Business Suite |

## Security Notes

- Never commit session files to git
- Use 2FA on Facebook/Instagram accounts
- Limit page roles to Editor (not Admin) for automation
- Regularly audit posted content

## Troubleshooting

### Session Expired
```bash
rm -rf watchers/facebook_session watchers/instagram_session
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py --auth
```

### Headless Mode Issues
By default, runs in headless mode. For debugging:
```bash
python .qwen/skills/facebook-instagram-poster/fb_ig_poster.py --headless false ...
```

### Multiple Pages
Specify exact page name as it appears in Meta Business Suite.

## Integration with Other Skills

- **approval-workflow**: For human review before posting
- **scheduler**: For automated recurring posts
- **linkedin-poster**: For cross-platform campaigns
- **orchestrator**: For end-to-end workflow automation

---

*Facebook/Instagram Poster Skill - AI Employee v0.3 (Gold Tier)*
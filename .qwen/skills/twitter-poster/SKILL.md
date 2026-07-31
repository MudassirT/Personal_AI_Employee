---
name: twitter-poster
description: |
  Twitter (X) posting automation using Playwright.
  Supports tweets, threads, media, and approval workflow.
  Requires manual login on first run; session saved for future use.
---

# Twitter (X) Poster

Automated posting to X (formerly Twitter) using Playwright browser automation.

## Overview

This skill enables the AI Employee to:
- Post single tweets with text and media (images, videos)
- Post tweet threads (multi-tweet conversations)
- Schedule tweets (future enhancement)
- Track posting history and engagement
- Integrate with approval workflow

## Prerequisites

1. **Playwright installed**: `pip install playwright && playwright install chromium`
2. **Twitter/X account** with verified phone/email
3. **Developer access** not required (uses web automation)

## Setup

### First Run - Authentication

```bash
python .qwen/skills/twitter-poster/twitter_poster.py --auth
```

This will:
1. Open a browser window to x.com/login
2. Prompt you to log in manually
3. Save session cookies for future runs

**Note**: You must complete login within the browser. 2FA is supported.

### Session Storage

Session is saved in: `watchers/twitter_session/state.json`

## Usage

### Post a Single Tweet

```bash
python .qwen/skills/twitter-poster/twitter_poster.py \
  --content "Just launched our AI Employee! 🤖 Automating business tasks 24/7" \
  --media "Social/Assets/images/launch.png" \
  --hashtags "#AI #Automation #Productivity"
```

### Post a Thread

```bash
python .qwen/skills/twitter-poster/twitter_poster.py \
  --content "1/5 Building an AI Employee that runs your business..." \
  --thread "2/5 It watches Gmail, WhatsApp, LinkedIn..." \
  --thread "3/5 Creates approval requests for sensitive actions..." \
  --thread "4/5 Integrates with Odoo for accounting..." \
  --thread "5/5 Runs 24/7 locally or in cloud. Open source! 🚀"
```

### Create Approval Plan

```bash
python .qwen/skills/twitter-poster/twitter_poster.py \
  --create-plan \
  --content "Big announcement coming tomorrow! 🎉" \
  --hashtags "#AI #Startup"
```

### Process Approved Tweets

```bash
python .qwen/skills/twitter-poster/twitter_poster.py --process-approved
```

## Qwen Code Integration

### Post a Tweet

```bash
qwen --cwd "AI_Employee_Vault" "Post a tweet about our new feature launch with the launch image"
```

### Post a Thread

```bash
qwen --cwd "AI_Employee_Vault" "Create a tweet thread explaining how our AI Employee works"
```

### Schedule via Approval Workflow

```bash
qwen --cwd "AI_Employee_Vault" "Create a tweet plan for tomorrow's product launch announcement"
# Review in Pending_Approval/
# Move to Approved/Social/ to publish
```

## File Structure

```
AI_Employee_Vault/
├── Plans/
│   └── Social/
│       └── tweet_plan_*.md
├── Pending_Approval/
│   └── Social/
│       └── tweet_plan_*.md
├── Approved/
│   └── Social/
│       └── tweet_plan_*.md
├── Done/
│   └── Social/
│       └── tweet_plan_*.md
├── Social/
│   └── Assets/
│       └── images/
└── Logs/
    └── twitter_poster.log
```

## Tweet Plan Template (Plans/Social/tweet_plan_*.md)

```markdown
---
type: tweet
content: |
  Your tweet content here
  Multiple lines supported
media: ["Social/Assets/images/photo.jpg"]
thread: ["Thread tweet 2", "Thread tweet 3"]
hashtags: "#AI #Automation"
schedule: "2026-01-15 10:00"
status: draft
created: "2026-01-10T10:30:00Z"
---

# Tweet Plan

## Content
Your tweet content here
**Hashtags:** #AI #Automation
**Media:** 1 file(s)
**Thread:** 2 additional tweets
**Schedule:** 2026-01-15 10:00 (or immediate)

## Approval Required
Move this file to `/Approved/Social/` to publish.
```

## Error Handling

| Error | Solution |
|-------|----------|
| "Not authenticated" | Run `--auth` to re-authenticate |
| "Selector not found" | Twitter UI changed; update selectors |
| "Rate limited" | Wait 15+ minutes; check X.com manually |
| "Media upload failed" | Check file size (<512MB video, <5MB image) |
| "Session expired" | Delete `watchers/twitter_session/` and re-auth |

## Security Notes

- **Never commit session files** to git
- Enable 2FA on Twitter account
- Use dedicated automation account if possible
- Regularly audit posted content
- Monitor for unusual activity

## Rate Limits

Twitter/X imposes rate limits:
- **Tweets**: ~300 per 3 hours
- **Media uploads**: ~50 per 15 minutes
- **Follow/Unfollow**: ~400 per day

The skill adds delays between posts but doesn't enforce limits. Monitor usage.

## Integration with Other Skills

- **approval-workflow**: For human review before posting
- **scheduler**: For recurring tweet campaigns
- **linkedin-poster**, **facebook-instagram-poster**: Cross-platform campaigns
- **orchestrator**: End-to-end workflow automation

## Troubleshooting

### Session Issues
```bash
# Clear and re-authenticate
rm -rf watchers/twitter_session
python .qwen/skills/twitter-poster/twitter_poster.py --auth
```

### Debug Mode
```bash
# Run with visible browser
python .qwen/skills/twitter-poster/twitter_poster.py --headless false --content "Test"
```

### Selector Updates
If Twitter changes UI, update selectors in `twitter_poster.py`:
- Tweet textarea: `[data-testid="tweetTextarea_0"]`
- Tweet button: `[data-testid="tweetButton"]`
- File input: `input[data-testid="fileInput"]`

## Limitations

- No official API (uses web automation)
- UI changes can break selectors
- Rate limits apply
- No direct DM support
- Scheduling requires external cron + approval workflow

## Future Enhancements

- [ ] Tweet scheduling via approval workflow + cron
- [ ] Reply/quote tweet support
- [ ] DM automation (with approval)
- [ ] Analytics tracking
- [ ] Multiple account support
- [ ] X Premium features (longer posts, formatting)

---

*Twitter (X) Poster Skill - AI Employee v0.3 (Gold Tier)*
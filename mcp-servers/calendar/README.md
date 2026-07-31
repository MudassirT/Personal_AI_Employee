# Calendar MCP Server

MCP server for Google Calendar integration with the AI Employee.

## Features

- List upcoming events
- Create new events with attendees
- Update existing events
- Delete events
- Free/busy scheduling queries

## Prerequisites

1. **Google Cloud Project** with Calendar API enabled
2. **OAuth 2.0 credentials** (Desktop app type)
3. **Calendar access** - User must grant calendar permissions

## Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 Client ID** (Application type: Desktop app)
5. Download credentials as `credentials.json`

### 2. Install Dependencies

```bash
cd mcp-servers/calendar
pip install -r requirements.txt
```

### 3. First Authentication

```bash
python calendar_mcp.py
```

This will:
1. Open browser for Google OAuth consent
2. Save token to `token.json` for future use
3. Keep running as MCP server

### 4. MCP Configuration

Add to your MCP settings (`~/.config/claude-code/mcp.json`):

```json
{
  "mcpServers": {
    "calendar": {
      "command": "python",
      "args": ["mcp-servers/calendar/calendar_mcp.py"],
      "cwd": "C:/path/to/Personal_AI_Employee-main"
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `calendar_list_events` | List upcoming events (default: next 7 days) |
| `calendar_create_event` | Create new event with optional attendees |
| `calendar_update_event` | Modify existing event |
| `calendar_delete_event` | Delete an event |
| `calendar_freebusy` | Check free/busy schedule |

## Usage Examples

### List Events
```json
{
  "name": "calendar_list_events",
  "arguments": {"days_ahead": 14, "max_results": 50}
}
```

### Create Event
```json
{
  "name": "calendar_create_event",
  "arguments": {
    "summary": "Team Meeting",
    "start_time": "2026-01-15T10:00:00Z",
    "end_time": "2026-01-15T11:00:00Z",
    "description": "Weekly team sync",
    "location": "Conference Room A",
    "attendees": ["alice@example.com", "bob@example.com"]
  }
}
```

### Check Availability
```json
{
  "name": "calendar_freebusy",
  "arguments": {
    "start_time": "2026-01-15T09:00:00Z",
    "end_time": "2026-01-15T17:00:00Z"
  }
}
```

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Use dedicated Google account for automation if possible
- Regularly review OAuth consent screen settings
- Token refresh is automatic

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" | Delete `token.json` and re-authenticate |
| "Calendar API not enabled" | Enable in Google Cloud Console |
| "Insufficient permissions" | Check OAuth scopes include `calendar.events` |
| Rate limiting | Implement exponential backoff |

## Integration with AI Employee

The orchestrator can use this MCP server for:
- Scheduling meetings from email requests
- Creating calendar events from task approvals
- Checking availability before committing to meetings
- Automated weekly planning

---

*Calendar MCP Server - AI Employee v0.3 (Gold Tier)*
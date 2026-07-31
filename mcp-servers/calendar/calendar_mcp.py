#!/usr/bin/env python3
"""
Calendar MCP Server

Provides calendar management capabilities via Google Calendar API,
Outlook Calendar, or CalDAV.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)


class CalendarClient:
    """Multi-provider calendar client."""
    
    def __init__(self):
        self.provider = os.getenv("CALENDAR_PROVIDER", "google").lower()
        
        # Google Calendar
        self.google_creds_path = os.getenv("GOOGLE_CALENDAR_CREDS", "credentials/calendar_creds.json")
        self.google_token_path = os.getenv("GOOGLE_CALENDAR_TOKEN", "credentials/calendar_token.json")
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        # State
        self._service = None
    
    def _get_google_service(self):
        """Get authenticated Google Calendar service."""
        if self._service:
            return self._service
        
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            if os.path.exists(self.google_token_path):
                creds = Credentials.from_authorized_user_file(self.google_token_path, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.google_creds_path):
                        raise Exception(f"Credentials file not found: {self.google_creds_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(self.google_creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(self.google_token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self._service = build('calendar', 'v3', credentials=creds)
            return self._service
            
        except ImportError:
            raise Exception("Google Calendar libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    
    async def list_events(self, days_ahead: int = 7, max_results: int = 20) -> List[Dict]:
        """List upcoming calendar events."""
        if self.provider == "google":
            return await self._list_google_events(days_ahead, max_results)
        return [{"error": f"Provider {self.provider} not implemented"}]
    
    async def _list_google_events(self, days_ahead: int, max_results: int) -> List[Dict]:
        service = self._get_google_service()
        
        now = datetime.utcnow().isoformat() + 'Z'
        future = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            timeMax=future,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = []
        for event in events_result.get('items', []):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            events.append({
                "id": event.get('id'),
                "summary": event.get('summary', 'No title'),
                "description": event.get('description', ''),
                "start": start,
                "end": end,
                "location": event.get('location', ''),
                "attendees": [a.get('email') for a in event.get('attendees', [])],
                "html_link": event.get('htmlLink', '')
            })
        return events
    
    async def create_event(self, summary: str, start_time: str, end_time: str,
                          description: str = "", location: str = "",
                          attendees: List[str] = None) -> Dict:
        """Create a new calendar event."""
        if self.provider == "google":
            return await self._create_google_event(summary, start_time, end_time, 
                                                   description, location, attendees)
        return {"error": f"Provider {self.provider} not implemented"}
    
    async def _create_google_event(self, summary: str, start_time: str, end_time: str,
                                   description: str, location: str, 
                                   attendees: List[str] = None) -> Dict:
        service = self._get_google_service()
        
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
        
        return {
            "id": created_event.get('id'),
            "summary": created_event.get('summary'),
            "html_link": created_event.get('htmlLink'),
            "status": "created"
        }
    
    async def update_event(self, event_id: str, **updates) -> Dict:
        """Update an existing event."""
        if self.provider == "google":
            return await self._update_google_event(event_id, updates)
        return {"error": f"Provider {self.provider} not implemented"}
    
    async def _update_google_event(self, event_id: str, updates: Dict) -> Dict:
        service = self._get_google_service()
        
        # Get existing event
        event = service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
        
        # Apply updates
        for key, value in updates.items():
            if key in ['summary', 'description', 'location']:
                event[key] = value
            elif key == 'start_time':
                event['start']['dateTime'] = value
            elif key == 'end_time':
                event['end']['dateTime'] = value
        
        updated = service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event).execute()
        return {"id": updated.get('id'), "status": "updated"}
    
    async def delete_event(self, event_id: str) -> Dict:
        """Delete a calendar event."""
        if self.provider == "google":
            service = self._get_google_service()
            service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            return {"id": event_id, "status": "deleted"}
        return {"error": f"Provider {self.provider} not implemented"}
    
    async def get_free_busy(self, start_time: str, end_time: str, 
                            calendars: List[str] = None) -> Dict:
        """Get free/busy information."""
        if self.provider == "google":
            return await self._get_google_freebusy(start_time, end_time, calendars)
        return {"error": f"Provider {self.provider} not implemented"}
    
    async def _get_google_freebusy(self, start_time: str, end_time: str, 
                                   calendars: List[str] = None) -> Dict:
        service = self._get_google_service()
        
        calendars = calendars or [self.calendar_id]
        
        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": cal} for cal in calendars]
        }
        
        result = service.freebusy().query(body=body).execute()
        
        freebusy = {}
        for cal_id, data in result.get('calendars', {}).items():
            freebusy[cal_id] = {
                "busy": data.get('busy', []),
                "errors": data.get('errors', [])
            }
        return freebusy


calendar_client: Optional[CalendarClient] = None


async def get_calendar_client() -> CalendarClient:
    global calendar_client
    if calendar_client is None:
        calendar_client = CalendarClient()
    return calendar_client


server = Server("calendar")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=[
        Tool(
            name="calendar_list_events",
            description="List upcoming calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "default": 7},
                    "max_results": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="calendar_create_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO format datetime"},
                    "end_time": {"type": "string", "description": "ISO format datetime"},
                    "description": {"type": "string", "default": ""},
                    "location": {"type": "string", "default": ""},
                    "attendees": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["summary", "start_time", "end_time"]
            }
        ),
        Tool(
            name="calendar_update_event",
            description="Update an existing calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "location": {"type": "string"}
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="calendar_delete_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"}
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="calendar_freebusy",
            description="Get free/busy schedule",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "calendars": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["start_time", "end_time"]
            }
        ),
    ])


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        client = await get_calendar_client()
        
        if name == "calendar_list_events":
            events = await client.list_events(arguments.get("days_ahead", 7), 
                                              arguments.get("max_results", 20))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(events, indent=2))])
        
        elif name == "calendar_create_event":
            result = await client.create_event(
                arguments["summary"],
                arguments["start_time"],
                arguments["end_time"],
                arguments.get("description", ""),
                arguments.get("location", ""),
                arguments.get("attendees")
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "calendar_update_event":
            event_id = arguments.pop("event_id")
            result = await client.update_event(event_id, **arguments)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "calendar_delete_event":
            result = await client.delete_event(arguments["event_id"])
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "calendar_freebusy":
            result = await client.get_free_busy(
                arguments["start_time"],
                arguments["end_time"],
                arguments.get("calendars")
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
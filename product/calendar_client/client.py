"""
Google Calendar API client for reading events and creating tasks.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import pytz

from googleapiclient.discovery import Resource

from .auth import get_calendar_service
from config import get_settings
from models import CalendarEvent, Attendee, PrepTask


class CalendarClient:
    """Client for interacting with Google Calendar API."""
    
    def __init__(self):
        self.service: Resource = get_calendar_service()
        self.settings = get_settings()
    
    def get_upcoming_events(
        self, 
        hours_ahead: Optional[int] = None,
        max_results: int = 50
    ) -> List[CalendarEvent]:
        """
        Get upcoming calendar events.
        
        Args:
            hours_ahead: How many hours ahead to look (default from settings)
            max_results: Maximum number of events to return
            
        Returns:
            List of parsed calendar events
        """
        if hours_ahead is None:
            hours_ahead = self.settings.calendar_lookahead_hours
        
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(hours=hours_ahead)).isoformat() + "Z"
        
        events_result = self.service.events().list(
            calendarId=self.settings.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        return [self._parse_event(event) for event in events]
    
    def get_event_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Parsed calendar event or None
        """
        try:
            event = self.service.events().get(
                calendarId=self.settings.calendar_id,
                eventId=event_id
            ).execute()
            return self._parse_event(event)
        except Exception:
            return None
    
    def create_prep_task(self, prep_task: PrepTask) -> Optional[str]:
        """
        Create a preparation task event on the calendar.
        
        Args:
            prep_task: PrepTask with task details
            
        Returns:
            Created event ID or None on failure
        """
        event_body = {
            "summary": prep_task.title,
            "description": prep_task.description,
            "start": {
                "dateTime": prep_task.start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": prep_task.end_time.isoformat(),
                "timeZone": "UTC",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 5},
                ],
            },
            # Color: Sage (green-ish) to distinguish from regular meetings
            "colorId": "2",
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.settings.calendar_id,
                body=event_body
            ).execute()
            return created_event.get("id")
        except Exception as e:
            print(f"Failed to create prep task: {e}")
            return None
    
    def check_prep_task_exists(self, meeting_event_id: str) -> bool:
        """
        Check if a prep task already exists for a meeting.
        
        Searches for events with the meeting ID in the description.
        
        Args:
            meeting_event_id: Original meeting event ID
            
        Returns:
            True if prep task exists
        """
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(hours=48)).isoformat() + "Z"
        
        events_result = self.service.events().list(
            calendarId=self.settings.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=f"PREP:{meeting_event_id}",  # Search for prep task marker
            singleEvents=True,
        ).execute()
        
        return len(events_result.get("items", [])) > 0
    
    def _parse_event(self, event: dict) -> CalendarEvent:
        """
        Parse raw Google Calendar event into CalendarEvent model.
        
        Args:
            event: Raw event from Google Calendar API
            
        Returns:
            Parsed CalendarEvent
        """
        # Parse start/end times
        start = event.get("start", {})
        end = event.get("end", {})
        
        start_time = self._parse_datetime(start)
        end_time = self._parse_datetime(end)
        
        # Parse attendees
        attendees = []
        for att in event.get("attendees", []):
            attendees.append(Attendee(
                email=att.get("email", ""),
                name=att.get("displayName"),
                is_organizer=att.get("organizer", False),
                response_status=att.get("responseStatus"),
            ))
        
        # Extract meeting link from conference data or description
        meeting_link = None
        conf_data = event.get("conferenceData", {})
        entry_points = conf_data.get("entryPoints", [])
        for ep in entry_points:
            if ep.get("entryPointType") == "video":
                meeting_link = ep.get("uri")
                break
        
        return CalendarEvent(
            event_id=event.get("id", ""),
            title=event.get("summary", "No Title"),
            description=event.get("description"),
            start_time=start_time,
            end_time=end_time,
            location=event.get("location"),
            attendees=attendees,
            organizer_email=event.get("organizer", {}).get("email"),
            meeting_link=meeting_link,
            is_recurring=event.get("recurringEventId") is not None,
        )
    
    def _parse_datetime(self, dt_dict: dict) -> datetime:
        """Parse datetime from Google Calendar format."""
        if "dateTime" in dt_dict:
            dt_str = dt_dict["dateTime"]
            # Handle timezone
            if dt_str.endswith("Z"):
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return datetime.fromisoformat(dt_str)
        elif "date" in dt_dict:
            # All-day event
            return datetime.strptime(dt_dict["date"], "%Y-%m-%d")
        return datetime.utcnow()

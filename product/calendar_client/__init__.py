"""
Google Calendar integration for Kairo.
"""

from .auth import get_credentials, get_calendar_service
from .client import CalendarClient
from .watcher import CalendarWatcher

__all__ = [
    "get_credentials",
    "get_calendar_service", 
    "CalendarClient",
    "CalendarWatcher",
]

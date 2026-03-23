"""
Database module for Kairo.

Provides database connection and models for internal data storage.
"""

from .connection import get_engine, get_session_local, get_db
from .models import (
    Base,
    Client,
    Contact,
    Deal,
    Activity,
    Document,
    MeetingNote,
    HealthMetrics,
    PrepTaskLog,
)

__all__ = [
    "get_engine",
    "get_session_local",
    "get_db",
    "Base",
    "Client",
    "Contact",
    "Deal",
    "Activity",
    "Document",
    "MeetingNote",
    "HealthMetrics",
    "PrepTaskLog",
]

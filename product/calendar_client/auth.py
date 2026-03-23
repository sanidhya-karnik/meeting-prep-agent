"""
Google OAuth authentication for Calendar API.
"""

import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from config import get_settings

# OAuth scopes for calendar access
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",  # Read calendar events
    "https://www.googleapis.com/auth/calendar.events",     # Create/modify events (for tasks)
]


def get_credentials() -> Credentials:
    """
    Get or refresh Google OAuth credentials.
    
    On first run, opens browser for authentication.
    Subsequently uses stored token.
    
    Returns:
        Valid Google OAuth credentials
    """
    settings = get_settings()
    creds = None
    
    token_path = Path(settings.token_path)
    credentials_path = Path(settings.credentials_path)
    
    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # Run OAuth flow
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Google OAuth credentials not found at {credentials_path}. "
                    "Please download from Google Cloud Console and save as credentials.json"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds


def get_calendar_service() -> Resource:
    """
    Get authenticated Google Calendar API service.
    
    Returns:
        Google Calendar API service resource
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    return service

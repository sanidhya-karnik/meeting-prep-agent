"""
Configuration management for Kairo.

Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # External Research (Required)
    tavily_api_key: str = Field(..., description="Tavily API key for web research")
    
    # Internal Database (Optional)
    database_url: Optional[str] = Field(
        default=None, 
        description="PostgreSQL connection string for internal search"
    )
    
    # Calendar Settings
    poll_interval_seconds: int = Field(
        default=300,
        description="How often to poll calendar (seconds)"
    )
    calendar_lookahead_hours: int = Field(
        default=48,
        description="How far ahead to look for meetings (hours)"
    )
    prep_task_minutes_before: int = Field(
        default=30,
        description="Minutes before meeting to create prep task"
    )
    calendar_id: str = Field(
        default="primary",
        description="Google Calendar ID to monitor"
    )
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Paths
    credentials_path: str = Field(
        default="credentials.json",
        description="Path to Google OAuth credentials"
    )
    token_path: str = Field(
        default="token.json",
        description="Path to store OAuth token"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()


def internal_search_enabled() -> bool:
    """Check if internal database search is configured."""
    settings = get_settings()
    return settings.database_url is not None and len(settings.database_url) > 0

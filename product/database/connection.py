"""
Database connection management.
"""

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config import get_settings, internal_search_enabled

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create SQLAlchemy engine."""
    global _engine
    
    if _engine is None:
        settings = get_settings()
        if settings.database_url:
            _engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
    
    return _engine


def get_session_local():
    """Get session factory."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        if engine:
            _SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
            )
    
    return _SessionLocal


def get_db() -> Optional[Session]:
    """
    Get database session.
    
    Usage:
        db = get_db()
        if db:
            # use db
            db.close()
    """
    SessionLocal = get_session_local()
    if SessionLocal:
        return SessionLocal()
    return None

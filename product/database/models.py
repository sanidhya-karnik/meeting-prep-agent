"""
SQLAlchemy models for internal database.

These models represent the expected schema for internal data search.
Actual table structures may vary - the search queries in internal.py
use raw SQL to be flexible with different schemas.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, 
    ForeignKey, Boolean, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Client(Base):
    """Company/organization record."""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100))
    company_size = Column(String(50))
    headquarters = Column(String(255))
    website = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_date = Column(DateTime)
    
    # Relationships
    contacts = relationship("Contact", back_populates="client")
    deals = relationship("Deal", back_populates="client")
    activities = relationship("Activity", back_populates="client")


class Contact(Base):
    """Individual contact at a company."""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    role = Column(String(100))
    department = Column(String(100))
    sentiment = Column(String(50))  # Champion, Supportive, Neutral, Detractor
    notes = Column(Text)
    linkedin_url = Column(String(500))
    is_primary = Column(Boolean, default=False)
    last_contact_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")


class Deal(Base):
    """Sales opportunity/deal."""
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String(255), nullable=False)
    stage = Column(String(50))  # Discovery, Proposal, Negotiation, Closed Won, Closed Lost
    deal_type = Column(String(50))
    value = Column(Float)
    currency = Column(String(10), default="USD")
    close_date = Column(DateTime)
    probability = Column(Integer)  # 0-100
    owner = Column(String(255))
    competitor = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="deals")


class Activity(Base):
    """Interaction/activity with a client."""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    activity_type = Column(String(50))  # Call, Email, Meeting, Demo, etc.
    subject = Column(String(500))
    description = Column(Text)
    participants = Column(Text)  # Comma-separated emails
    duration_minutes = Column(Integer)
    activity_date = Column(DateTime, index=True)
    next_steps = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="activities")


class Document(Base):
    """Internal document (proposal, contract, etc.)."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    title = Column(String(500), nullable=False)
    doc_type = Column(String(50))  # Proposal, Contract, Presentation, etc.
    content = Column(Text)  # Full text content for search
    file_path = Column(String(1000))
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MeetingNote(Base):
    """Notes from past meetings."""
    __tablename__ = "meeting_notes"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    title = Column(String(500), nullable=False)
    company = Column(String(255), index=True)
    attendees = Column(Text)  # Comma-separated names/emails
    notes = Column(Text)
    action_items = Column(JSON)
    meeting_date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HealthMetrics(Base):
    """Customer health indicators."""
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    engagement_score = Column(Integer)  # 0-100
    nps_score = Column(Integer)  # -100 to 100
    support_tickets_open = Column(Integer, default=0)
    last_login = Column(DateTime)
    usage_trend = Column(String(20))  # up, down, stable
    risk_level = Column(String(20))  # low, medium, high
    recorded_at = Column(DateTime, default=datetime.utcnow)


class PrepTaskLog(Base):
    """Log of created preparation tasks."""
    __tablename__ = "prep_task_log"
    
    id = Column(Integer, primary_key=True)
    meeting_event_id = Column(String(255), unique=True, index=True)
    meeting_title = Column(String(500))
    meeting_time = Column(DateTime)
    prep_task_event_id = Column(String(255))
    research_summary = Column(Text)
    sources_used = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

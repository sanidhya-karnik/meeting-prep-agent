"""
Database initialization script.

Creates tables and optionally seeds sample data for testing.
"""

import sys
from datetime import datetime, timedelta

from sqlalchemy import create_engine

from config import get_settings, internal_search_enabled
from .models import (
    Base, Client, Contact, Deal, Activity, 
    Document, MeetingNote, HealthMetrics
)


def init_database(seed_sample_data: bool = False):
    """
    Initialize database schema.
    
    Args:
        seed_sample_data: If True, insert sample data for testing
    """
    settings = get_settings()
    
    if not settings.database_url:
        print("Error: DATABASE_URL not configured")
        print("Set DATABASE_URL in your .env file to initialize the database")
        sys.exit(1)
    
    print(f"Connecting to database...")
    engine = create_engine(settings.database_url)
    
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
    
    if seed_sample_data:
        print("Seeding sample data...")
        seed_data(engine)
        print("Sample data inserted!")
    
    print("Database initialization complete.")


def seed_data(engine):
    """Insert sample data for testing."""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create sample client
        acme = Client(
            name="Acme Corp",
            industry="Technology",
            company_size="500-1000",
            headquarters="San Francisco, CA",
            website="https://acme-corp.example.com",
            notes="Enterprise software company, strong growth trajectory",
            last_activity_date=datetime.utcnow() - timedelta(days=3),
        )
        session.add(acme)
        session.flush()
        
        # Create contacts
        contacts = [
            Contact(
                client_id=acme.id,
                name="John Smith",
                email="john.smith@acme-corp.example.com",
                role="VP Engineering",
                department="Engineering",
                sentiment="Champion",
                notes="Primary technical decision maker. Very hands-on, wants to see demos.",
                is_primary=True,
                last_contact_date=datetime.utcnow() - timedelta(days=5),
            ),
            Contact(
                client_id=acme.id,
                name="Lisa Park",
                email="lisa.park@acme-corp.example.com",
                role="CFO",
                department="Finance",
                sentiment="Neutral",
                notes="Focused on ROI and total cost of ownership. Has not attended recent calls.",
                is_primary=False,
                last_contact_date=datetime.utcnow() - timedelta(days=14),
            ),
            Contact(
                client_id=acme.id,
                name="Mike Chen",
                email="mike.chen@acme-corp.example.com",
                role="IT Director",
                department="IT",
                sentiment="Supportive",
                notes="Concerned about integration with existing ERP. Wants detailed security docs.",
                is_primary=False,
                last_contact_date=datetime.utcnow() - timedelta(days=7),
            ),
        ]
        session.add_all(contacts)
        
        # Create deal
        deal = Deal(
            client_id=acme.id,
            name="Acme Corp Enterprise License",
            stage="Negotiation",
            deal_type="New Business",
            value=450000,
            currency="USD",
            close_date=datetime.utcnow() + timedelta(days=30),
            probability=75,
            owner="Sarah Chen",
            competitor="TechRival Inc",
            notes="Strong interest from engineering team. CFO needs ROI justification.",
        )
        session.add(deal)
        
        # Create activities
        activities = [
            Activity(
                client_id=acme.id,
                activity_type="Call",
                subject="Technical Requirements Discussion",
                description="Reviewed integration requirements with John and Mike. Key concerns: API rate limits, SSO support, data migration timeline.",
                participants="john.smith@acme-corp.example.com, mike.chen@acme-corp.example.com",
                duration_minutes=45,
                activity_date=datetime.utcnow() - timedelta(days=7),
                next_steps="Send technical architecture document. Schedule follow-up demo.",
            ),
            Activity(
                client_id=acme.id,
                activity_type="Email",
                subject="Proposal v3 Sent",
                description="Sent revised proposal with Net 30 payment terms and 99.9% SLA guarantee.",
                participants="john.smith@acme-corp.example.com, lisa.park@acme-corp.example.com",
                duration_minutes=0,
                activity_date=datetime.utcnow() - timedelta(days=3),
                next_steps="Schedule call to review proposal with CFO.",
            ),
        ]
        session.add_all(activities)
        
        # Create documents
        documents = [
            Document(
                client_id=acme.id,
                title="Acme Corp - Enterprise Proposal v3",
                doc_type="Proposal",
                content="3-year enterprise license proposal for Acme Corp. Includes: Core platform, Analytics module, API access, Premium support. Total value: $450,000. Payment terms: Net 30. SLA: 99.9% uptime guarantee.",
            ),
            Document(
                client_id=acme.id,
                title="Acme Corp - Technical Requirements",
                doc_type="Requirements",
                content="Technical requirements gathered from John Smith and Mike Chen. Key items: REST API integration, SAML SSO, Data encryption at rest and in transit, SOC 2 compliance required.",
            ),
        ]
        session.add_all(documents)
        
        # Create meeting notes
        meeting_notes = [
            MeetingNote(
                client_id=acme.id,
                title="Q4 Planning Discussion",
                company="Acme Corp",
                attendees="John Smith, Mike Chen, Sarah Chen",
                notes="Discussed Q4 implementation timeline. John wants to go live by end of Q1 next year. Mike raised security questionnaire - need to complete before legal review. Action: Send completed security questionnaire by EOW.",
                action_items=["Complete security questionnaire", "Schedule legal review", "Prepare implementation timeline"],
                meeting_date=datetime.utcnow() - timedelta(days=14),
            ),
        ]
        session.add_all(meeting_notes)
        
        # Create health metrics
        health = HealthMetrics(
            client_id=acme.id,
            engagement_score=85,
            nps_score=42,
            support_tickets_open=0,
            usage_trend="up",
            risk_level="low",
        )
        session.add(health)
        
        # Second sample client
        globex = Client(
            name="Globex Industries",
            industry="Manufacturing",
            company_size="1000-5000",
            headquarters="Chicago, IL",
            website="https://globex.example.com",
            notes="Large manufacturing company exploring digital transformation",
        )
        session.add(globex)
        session.flush()
        
        globex_contact = Contact(
            client_id=globex.id,
            name="David Wilson",
            email="d.wilson@globex.example.com",
            role="VP Operations",
            sentiment="Neutral",
            notes="Evaluating multiple vendors. Price-sensitive.",
            is_primary=True,
        )
        session.add(globex_contact)
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        session.close()


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    settings = get_settings()
    
    if not settings.database_url:
        print("Error: DATABASE_URL not configured")
        return
    
    confirm = input("This will DELETE all data. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return
    
    engine = create_engine(settings.database_url)
    Base.metadata.drop_all(engine)
    print("All tables dropped.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Kairo database")
    parser.add_argument(
        "--seed", 
        action="store_true", 
        help="Seed sample data for testing"
    )
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="Drop all tables (dangerous!)"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        drop_all_tables()
    else:
        init_database(seed_sample_data=args.seed)

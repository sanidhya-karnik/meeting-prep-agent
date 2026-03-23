"""
Internal database research using PostgreSQL.

Searches internal databases for relevant context about meetings,
attendees, and companies.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from config import get_settings, internal_search_enabled
from models import InternalSearchResult, CalendarEvent


class InternalResearcher:
    """
    Searches internal PostgreSQL database for meeting context.
    
    Looks for:
    - Previous interactions with attendees
    - Company history and notes
    - Related documents and proposals
    - Past meeting notes
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.Session = None
        
        if internal_search_enabled():
            self._init_connection()
    
    def _init_connection(self):
        """Initialize database connection."""
        try:
            self.engine = create_engine(self.settings.database_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(f"Failed to connect to internal database: {e}")
            self.engine = None
    
    @property
    def is_available(self) -> bool:
        """Check if internal search is available."""
        return self.engine is not None
    
    def search_by_email(self, email: str) -> List[InternalSearchResult]:
        """
        Search for records related to an email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            List of search results
        """
        if not self.is_available:
            return []
        
        results = []
        
        try:
            with self.Session() as session:
                # Search contacts table
                contact_results = self._search_contacts(session, email)
                results.extend(contact_results)
                
                # Search activity/interaction history
                activity_results = self._search_activities(session, email)
                results.extend(activity_results)
                
                # Search notes/documents
                doc_results = self._search_documents(session, email)
                results.extend(doc_results)
                
        except SQLAlchemyError as e:
            print(f"Database search error: {e}")
        
        return results
    
    def search_by_company(self, company_name: str) -> List[InternalSearchResult]:
        """
        Search for records related to a company.
        
        Args:
            company_name: Company name or domain to search for
            
        Returns:
            List of search results
        """
        if not self.is_available:
            return []
        
        results = []
        
        try:
            with self.Session() as session:
                # Search clients/accounts table
                client_results = self._search_clients(session, company_name)
                results.extend(client_results)
                
                # Search deals/opportunities
                deal_results = self._search_deals(session, company_name)
                results.extend(deal_results)
                
                # Search meeting notes
                notes_results = self._search_meeting_notes(session, company_name)
                results.extend(notes_results)
                
        except SQLAlchemyError as e:
            print(f"Database search error: {e}")
        
        return results
    
    def search_for_event(self, event: CalendarEvent) -> List[InternalSearchResult]:
        """
        Comprehensive search for all context related to a calendar event.
        
        Args:
            event: Calendar event to research
            
        Returns:
            Combined search results
        """
        if not self.is_available:
            return []
        
        all_results = []
        
        # Search by each attendee
        for attendee in event.attendees:
            if attendee.email:
                results = self.search_by_email(attendee.email)
                all_results.extend(results)
        
        # Search by each company
        for company in event.companies:
            results = self.search_by_company(company)
            all_results.extend(results)
        
        # Search by meeting title keywords
        title_results = self._search_by_keywords(event.title)
        all_results.extend(title_results)
        
        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result.source, result.title)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results[:20]  # Limit to top 20 results
    
    def _search_contacts(self, session, email: str) -> List[InternalSearchResult]:
        """Search contacts table for email."""
        results = []
        
        query = text("""
            SELECT name, role, company, notes, last_contact_date
            FROM contacts
            WHERE email ILIKE :email
            LIMIT 5
        """)
        
        try:
            rows = session.execute(query, {"email": f"%{email}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="contacts",
                    title=f"{row.name} ({row.role or 'Unknown Role'})",
                    content=row.notes or f"Contact at {row.company or 'Unknown Company'}",
                    relevance_score=0.9,
                    metadata={
                        "company": row.company,
                        "role": row.role,
                    },
                    timestamp=row.last_contact_date,
                ))
        except SQLAlchemyError:
            pass  # Table might not exist
        
        return results
    
    def _search_activities(self, session, email: str) -> List[InternalSearchResult]:
        """Search activity history for interactions with email."""
        results = []
        
        query = text("""
            SELECT activity_type, subject, description, activity_date
            FROM activities
            WHERE participants ILIKE :email
            ORDER BY activity_date DESC
            LIMIT 5
        """)
        
        try:
            rows = session.execute(query, {"email": f"%{email}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="activities",
                    title=f"{row.activity_type}: {row.subject}",
                    content=row.description or "",
                    relevance_score=0.8,
                    timestamp=row.activity_date,
                ))
        except SQLAlchemyError:
            pass
        
        return results
    
    def _search_documents(self, session, email: str) -> List[InternalSearchResult]:
        """Search documents mentioning email."""
        results = []
        
        query = text("""
            SELECT title, content, doc_type, created_at
            FROM documents
            WHERE content ILIKE :email OR title ILIKE :email
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        try:
            rows = session.execute(query, {"email": f"%{email}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="documents",
                    title=row.title,
                    content=row.content[:500] if row.content else "",
                    relevance_score=0.7,
                    metadata={"doc_type": row.doc_type},
                    timestamp=row.created_at,
                ))
        except SQLAlchemyError:
            pass
        
        return results
    
    def _search_clients(self, session, company: str) -> List[InternalSearchResult]:
        """Search clients/accounts table."""
        results = []
        
        query = text("""
            SELECT name, industry, company_size, notes, last_activity_date
            FROM clients
            WHERE name ILIKE :company
            LIMIT 3
        """)
        
        try:
            rows = session.execute(query, {"company": f"%{company}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="clients",
                    title=row.name,
                    content=row.notes or f"{row.industry or ''} company, {row.company_size or 'unknown'} size",
                    relevance_score=0.95,
                    metadata={
                        "industry": row.industry,
                        "size": row.company_size,
                    },
                    timestamp=row.last_activity_date,
                ))
        except SQLAlchemyError:
            pass
        
        return results
    
    def _search_deals(self, session, company: str) -> List[InternalSearchResult]:
        """Search deals/opportunities related to company."""
        results = []
        
        query = text("""
            SELECT d.name, d.stage, d.value, d.close_date, d.notes
            FROM deals d
            JOIN clients c ON d.client_id = c.id
            WHERE c.name ILIKE :company
            ORDER BY d.close_date DESC
            LIMIT 5
        """)
        
        try:
            rows = session.execute(query, {"company": f"%{company}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="deals",
                    title=f"Deal: {row.name} ({row.stage})",
                    content=f"Value: ${row.value:,.0f}. {row.notes or ''}",
                    relevance_score=0.85,
                    metadata={
                        "stage": row.stage,
                        "value": row.value,
                    },
                    timestamp=row.close_date,
                ))
        except SQLAlchemyError:
            pass
        
        return results
    
    def _search_meeting_notes(self, session, company: str) -> List[InternalSearchResult]:
        """Search past meeting notes related to company."""
        results = []
        
        query = text("""
            SELECT title, notes, meeting_date, attendees
            FROM meeting_notes
            WHERE company ILIKE :company OR notes ILIKE :company
            ORDER BY meeting_date DESC
            LIMIT 5
        """)
        
        try:
            rows = session.execute(query, {"company": f"%{company}%"}).fetchall()
            for row in rows:
                results.append(InternalSearchResult(
                    source="meeting_notes",
                    title=row.title,
                    content=row.notes[:500] if row.notes else "",
                    relevance_score=0.8,
                    metadata={"attendees": row.attendees},
                    timestamp=row.meeting_date,
                ))
        except SQLAlchemyError:
            pass
        
        return results
    
    def _search_by_keywords(self, text_query: str) -> List[InternalSearchResult]:
        """Generic keyword search across multiple tables."""
        if not self.is_available:
            return []
        
        # Extract meaningful keywords (simple approach)
        keywords = [w for w in text_query.split() if len(w) > 3]
        if not keywords:
            return []
        
        results = []
        
        try:
            with self.Session() as session:
                for keyword in keywords[:3]:  # Limit keywords
                    # Search documents
                    doc_query = text("""
                        SELECT title, content, created_at
                        FROM documents
                        WHERE title ILIKE :keyword OR content ILIKE :keyword
                        LIMIT 3
                    """)
                    
                    rows = session.execute(doc_query, {"keyword": f"%{keyword}%"}).fetchall()
                    for row in rows:
                        results.append(InternalSearchResult(
                            source="documents",
                            title=row.title,
                            content=row.content[:300] if row.content else "",
                            relevance_score=0.5,
                            timestamp=row.created_at,
                        ))
        except SQLAlchemyError:
            pass
        
        return results

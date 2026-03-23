"""
Pydantic schemas for Kairo Production.

Defines data models for meetings, research results, and briefings.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Attendee(BaseModel):
    """Meeting attendee information."""
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    is_organizer: bool = False
    response_status: Optional[str] = None  # accepted, declined, tentative, needsAction


class CalendarEvent(BaseModel):
    """Parsed calendar event."""
    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[Attendee] = Field(default_factory=list)
    organizer_email: Optional[str] = None
    meeting_link: Optional[str] = None
    is_recurring: bool = False
    
    @property
    def companies(self) -> List[str]:
        """Extract unique companies from attendee emails."""
        domains = set()
        for attendee in self.attendees:
            if attendee.email and "@" in attendee.email:
                domain = attendee.email.split("@")[1]
                # Filter out common email providers
                if domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                    company = domain.split(".")[0].title()
                    domains.add(company)
        return list(domains)
    
    @property
    def external_attendees(self) -> List[Attendee]:
        """Get attendees from external organizations."""
        # This would need the user's domain to filter properly
        return [a for a in self.attendees if not a.is_organizer]


class InternalSearchResult(BaseModel):
    """Result from internal database search."""
    source: str  # e.g., "crm", "documents", "emails"
    title: str
    content: str
    relevance_score: float = 0.0
    metadata: dict = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class ExternalSearchResult(BaseModel):
    """Result from external web search."""
    title: str
    url: str
    content: str
    source: str  # e.g., "news", "company_info", "linkedin"
    published_date: Optional[str] = None
    relevance_score: float = 0.0


class PersonResearch(BaseModel):
    """Research results for a specific person."""
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    background: Optional[str] = None
    recent_news: List[ExternalSearchResult] = Field(default_factory=list)
    internal_notes: List[InternalSearchResult] = Field(default_factory=list)


class CompanyResearch(BaseModel):
    """Research results for a company."""
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    recent_news: List[ExternalSearchResult] = Field(default_factory=list)
    internal_history: List[InternalSearchResult] = Field(default_factory=list)


class ResearchResults(BaseModel):
    """Combined research results for a meeting."""
    event_id: str
    meeting_context: Optional[str] = None
    companies: List[CompanyResearch] = Field(default_factory=list)
    people: List[PersonResearch] = Field(default_factory=list)
    internal_results: List[InternalSearchResult] = Field(default_factory=list)
    external_results: List[ExternalSearchResult] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AttendeeProfile(BaseModel):
    """Structured attendee profile for briefing."""
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    background: Optional[str] = None
    news_mentions: List[dict] = Field(default_factory=list)  # [{title, url}]


class CompanyContext(BaseModel):
    """Structured company context for briefing."""
    name: str
    description: Optional[str] = None
    recent_news: List[dict] = Field(default_factory=list)  # [{title, url, summary}]


class NewsItem(BaseModel):
    """A news item with link."""
    headline: str
    url: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None


class MeetingBriefing(BaseModel):
    """Generated meeting briefing."""
    event_id: str
    event_title: str
    event_time: datetime
    
    # Briefing content
    executive_summary: str
    attendee_profiles: List[AttendeeProfile] = Field(default_factory=list)
    company_context: List[CompanyContext] = Field(default_factory=list)
    key_talking_points: List[str] = Field(default_factory=list)
    potential_questions: List[str] = Field(default_factory=list)
    recent_news: List[NewsItem] = Field(default_factory=list)
    internal_context: Optional[str] = None
    
    # Metadata
    sources_used: List[str] = Field(default_factory=list)
    reference_links: List[dict] = Field(default_factory=list)  # [{title, url}]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_task_description(self) -> str:
        """Format briefing as professional calendar task description."""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append(f"MEETING BRIEFING: {self.event_title}")
        lines.append(f"Scheduled: {self.event_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
        lines.append("=" * 50)
        lines.append("")
        
        # Executive Summary
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 30)
        lines.append(self.executive_summary)
        lines.append("")
        
        # Attendee Profiles
        if self.attendee_profiles:
            lines.append("ATTENDEES")
            lines.append("-" * 30)
            for profile in self.attendee_profiles[:5]:
                # Name and role
                header = profile.name
                if profile.role and profile.company:
                    header += f" | {profile.role} at {profile.company}"
                elif profile.company:
                    header += f" | {profile.company}"
                lines.append(header)
                
                # LinkedIn
                if profile.linkedin_url:
                    lines.append(f"  LinkedIn: {profile.linkedin_url}")
                
                # Background
                if profile.background:
                    bg = profile.background[:200].replace('\n', ' ')
                    lines.append(f"  Background: {bg}...")
                
                lines.append("")
        
        # Company Context
        if self.company_context:
            lines.append("COMPANY INTELLIGENCE")
            lines.append("-" * 30)
            for ctx in self.company_context[:3]:
                lines.append(f"{ctx.name}")
                if ctx.description:
                    desc = ctx.description[:200].replace('\n', ' ')
                    lines.append(f"  {desc}")
                
                if ctx.recent_news:
                    lines.append("  Recent News:")
                    for news in ctx.recent_news[:3]:
                        title = news.get("title", "")[:80]
                        url = news.get("url", "")
                        if url:
                            lines.append(f"    - {title}")
                            lines.append(f"      {url}")
                        else:
                            lines.append(f"    - {title}")
                lines.append("")
        
        # Recent News
        if self.recent_news:
            lines.append("RECENT DEVELOPMENTS")
            lines.append("-" * 30)
            for news in self.recent_news[:5]:
                lines.append(f"- {news.headline}")
                if news.url:
                    lines.append(f"  {news.url}")
                if news.summary:
                    summary = news.summary[:150].replace('\n', ' ')
                    lines.append(f"  {summary}")
            lines.append("")
        
        # Talking Points
        if self.key_talking_points:
            lines.append("SUGGESTED TALKING POINTS")
            lines.append("-" * 30)
            for i, point in enumerate(self.key_talking_points[:5], 1):
                lines.append(f"{i}. {point}")
            lines.append("")
        
        # Questions to Ask
        if self.potential_questions:
            lines.append("QUESTIONS TO CONSIDER")
            lines.append("-" * 30)
            for q in self.potential_questions[:5]:
                lines.append(f"- {q}")
            lines.append("")
        
        # Internal Context
        if self.internal_context:
            lines.append("INTERNAL CONTEXT")
            lines.append("-" * 30)
            lines.append(self.internal_context[:500])
            lines.append("")
        
        # Reference Links
        if self.reference_links:
            lines.append("REFERENCE LINKS")
            lines.append("-" * 30)
            for ref in self.reference_links[:10]:
                lines.append(f"- {ref.get('title', 'Link')}")
                lines.append(f"  {ref.get('url', '')}")
            lines.append("")
        
        # Footer
        lines.append("=" * 50)
        lines.append(f"Generated by Kairo | {self.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("=" * 50)
        
        return "\n".join(lines)


class PrepTask(BaseModel):
    """Calendar prep task to be created."""
    event_id: str  # Reference to original meeting
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    created: bool = False
    task_event_id: Optional[str] = None  # ID of created task event

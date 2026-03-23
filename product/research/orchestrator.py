"""
Research orchestrator that combines internal and external research.

Coordinates research from multiple sources and generates meeting briefings.
"""

from typing import Optional, List, Set
from datetime import datetime

from config import get_settings, internal_search_enabled
from models.schemas import (
    CalendarEvent,
    ResearchResults,
    MeetingBriefing,
    AttendeeProfile,
    CompanyContext,
    NewsItem,
    InternalSearchResult,
)
from .internal import InternalResearcher
from .external import ExternalResearcher


class ResearchOrchestrator:
    """
    Orchestrates research from multiple sources and generates briefings.
    
    Workflow:
    1. Parse meeting context from calendar event
    2. Search internal database (if available)
    3. Search external sources via Tavily
    4. Combine and synthesize results
    5. Generate meeting briefing
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.internal = InternalResearcher()
        self.external = ExternalResearcher()
    
    def research_meeting(self, event: CalendarEvent) -> ResearchResults:
        """
        Perform comprehensive research for a meeting.
        
        Args:
            event: Calendar event to research
            
        Returns:
            Combined research results
        """
        results = ResearchResults(event_id=event.event_id)
        
        # Extract meeting context from title/description
        results.meeting_context = self._extract_meeting_context(event)
        
        # Internal research (if database is configured)
        if self.internal.is_available:
            internal_results = self.internal.search_for_event(event)
            results.internal_results = internal_results
        
        # External research via Tavily
        external_data = self.external.research_event(event)
        
        results.people = external_data.get("people", [])
        results.companies = external_data.get("companies", [])
        results.external_results = external_data.get("context", [])
        
        return results
    
    def generate_briefing(
        self, 
        event: CalendarEvent, 
        research: ResearchResults
    ) -> MeetingBriefing:
        """
        Generate a meeting briefing from research results.
        
        Args:
            event: Calendar event
            research: Collected research results
            
        Returns:
            Generated meeting briefing
        """
        # Build all components
        executive_summary = self._generate_executive_summary(event, research)
        attendee_profiles = self._build_attendee_profiles(research)
        company_context = self._build_company_context(research)
        recent_news = self._extract_recent_news(research)
        talking_points = self._generate_talking_points(event, research)
        potential_questions = self._generate_questions(event, research)
        internal_context = self._summarize_internal_context(research) if research.internal_results else None
        reference_links = self._collect_reference_links(research)
        sources_used = self._get_sources_used(research)
        
        # Create briefing with all fields
        briefing = MeetingBriefing(
            event_id=event.event_id,
            event_title=event.title,
            event_time=event.start_time,
            executive_summary=executive_summary,
            attendee_profiles=attendee_profiles,
            company_context=company_context,
            key_talking_points=talking_points,
            recent_news=recent_news,
            internal_context=internal_context,
            potential_questions=potential_questions,
            reference_links=reference_links,
            sources_used=sources_used,
        )
        
        return briefing
    
    def _extract_meeting_context(self, event: CalendarEvent) -> str:
        """Extract meeting context from title and description."""
        context_parts = [f"Meeting: {event.title}"]
        
        if event.description:
            desc = event.description.replace("<br>", "\n")
            desc = desc[:500]
            context_parts.append(f"Description: {desc}")
        
        if event.location:
            context_parts.append(f"Location: {event.location}")
        
        if event.companies:
            context_parts.append(f"Companies involved: {', '.join(event.companies)}")
        
        return "\n".join(context_parts)
    
    def _generate_executive_summary(
        self, 
        event: CalendarEvent, 
        research: ResearchResults
    ) -> str:
        """Generate a concise executive summary."""
        parts = []
        
        # Simple meeting overview
        attendee_count = len(event.attendees)
        if event.companies:
            companies_str = ", ".join(event.companies[:2])
            parts.append(f"Meeting with {attendee_count} attendee(s) from {companies_str}.")
        else:
            parts.append(f"Meeting with {attendee_count} attendee(s).")
        
        # Internal history (if any)
        if research.internal_results:
            parts.append(f"You have {len(research.internal_results)} previous interaction(s) on record.")
        
        return " ".join(parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing markdown and em dashes."""
        if not text:
            return ""
        
        # Remove em dashes
        text = text.replace("\u2014", ", ")  # em dash
        text = text.replace("\u2013", ", ")  # en dash
        text = text.replace(" - ", ", ")
        
        # Remove markdown headers
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                line = line.lstrip("#").strip()
            if line:
                cleaned.append(line)
        
        text = " ".join(cleaned)
        
        # Remove multiple spaces
        while "  " in text:
            text = text.replace("  ", " ")
        
        return text.strip()
    
    def _build_attendee_profiles(self, research: ResearchResults) -> List[AttendeeProfile]:
        """Build structured attendee profiles with links."""
        profiles = []
        
        for person in research.people:
            # Collect news mentions with URLs
            news_mentions = []
            for news in person.recent_news[:3]:
                news_mentions.append({
                    "title": news.title,
                    "url": news.url,
                })
            
            profile = AttendeeProfile(
                name=person.name,
                email=person.email,
                company=person.company,
                role=person.role,
                linkedin_url=person.linkedin_url,
                background=person.background,
                news_mentions=news_mentions,
            )
            profiles.append(profile)
        
        return profiles
    
    def _build_company_context(self, research: ResearchResults) -> List[CompanyContext]:
        """Build structured company context with deduplicated news links."""
        contexts = []
        
        for company in research.companies:
            # Collect recent news with URLs, deduplicated
            recent_news = []
            seen_urls: set = set()
            
            for news in company.recent_news[:5]:
                url = news.url or ""
                # Skip if URL is duplicate or near-duplicate
                if self._is_duplicate_url(url, seen_urls):
                    continue
                seen_urls.add(url)
                
                recent_news.append({
                    "title": news.title,
                    "url": url,
                    "summary": news.content[:200] if news.content else "",
                })
            
            ctx = CompanyContext(
                name=company.name,
                description=company.description,
                recent_news=recent_news[:3],  # Max 3 news per company
            )
            contexts.append(ctx)
        
        return contexts
    
    def _is_duplicate_url(self, url: str, seen_urls: set) -> bool:
        """Check if URL is a duplicate or near-duplicate."""
        if not url:
            return True
        
        url_clean = url.rstrip('/').lower()
        
        for seen in seen_urls:
            seen_clean = seen.rstrip('/').lower()
            if url_clean == seen_clean:
                return True
            # One is substring of the other
            if url_clean in seen_clean or seen_clean in url_clean:
                return True
        
        return False
    
    def _extract_recent_news(self, research: ResearchResults) -> List[NewsItem]:
        """Extract recent news items with deduplicated links."""
        news_items = []
        seen_urls: set = set()
        
        # Company news only (skip person news, usually noise)
        for company in research.companies:
            for news in company.recent_news[:3]:
                url = news.url or ""
                if not self._is_duplicate_url(url, seen_urls):
                    seen_urls.add(url)
                    news_items.append(NewsItem(
                        headline=f"{company.name}: {news.title}",
                        url=url,
                        source=news.source,
                        summary=news.content[:150] if news.content else None,
                    ))
        
        return news_items[:6]  # Limit to top 6
    
    def _generate_talking_points(
        self, 
        event: CalendarEvent, 
        research: ResearchResults
    ) -> List[str]:
        """Generate suggested talking points based on meeting agenda and research."""
        points = []
        
        # PRIORITY 1: Extract agenda items from meeting description
        agenda_items = self._extract_agenda_items(event.description)
        if agenda_items:
            points.extend(agenda_items)
        
        # PRIORITY 2: From internal context (if we have history)
        for result in research.internal_results[:2]:
            if result.source == "deals":
                points.append(f"Follow up on existing engagement: {result.title}")
            elif result.source == "meeting_notes":
                points.append(f"Reference previous discussion: {result.title[:50]}")
        
        # PRIORITY 3: Only add generic points if we don't have enough from agenda
        if len(points) < 3:
            title_lower = event.title.lower()
            if "review" in title_lower:
                points.append("Prepare metrics and progress updates for the review")
            if "kickoff" in title_lower:
                points.append("Establish clear goals, timelines, and success criteria")
            if "demo" in title_lower:
                points.append("Prepare demo environment and key features to highlight")
            if "partnership" in title_lower:
                points.append("Discuss mutual benefits and potential collaboration areas")
        
        # Only add defaults if still not enough
        if len(points) < 3:
            points.extend([
                "Understand their current priorities and challenges",
                "Establish clear next steps and follow-ups",
            ])
        
        return points[:7]
    
    def _extract_agenda_items(self, description: str) -> List[str]:
        """Extract agenda items from meeting description."""
        if not description:
            return []
        
        items = []
        
        # Clean up HTML
        desc = description.replace("<br>", "\n").replace("<br/>", "\n")
        desc = desc.replace("&nbsp;", " ")
        
        lines = desc.split("\n")
        in_agenda = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we're in an agenda section
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["agenda", "topics", "discussion points", "we will discuss"]):
                in_agenda = True
                continue
            
            # Check for numbered items (1. 2. 3. etc)
            if len(line) > 2 and line[0].isdigit() and line[1] in ".):":
                item = line[2:].strip().lstrip(".):- ")
                if item and len(item) > 3:
                    items.append(item)
                continue
            
            # Check for bullet points
            if line.startswith(("- ", "* ", "• ")):
                item = line[2:].strip()
                if item and len(item) > 3:
                    items.append(item)
                continue
            
            # If we're in agenda section, treat lines as items
            if in_agenda and len(line) > 5 and not line.endswith(":"):
                items.append(line)
        
        # Clean up items
        cleaned = []
        for item in items:
            # Remove em dashes
            item = item.replace("\u2014", ", ").replace("\u2013", ", ")
            # Skip if it looks like a header or instruction
            if item.lower().startswith(("please", "note:", "reminder")):
                continue
            if len(item) > 100:
                item = item[:100] + "..."
            cleaned.append(item)
        
        return cleaned[:6]  # Max 6 agenda items
    
    def _generate_questions(
        self, 
        event: CalendarEvent, 
        research: ResearchResults
    ) -> List[str]:
        """Generate potential questions based on meeting context."""
        questions = []
        
        # Internal history questions
        for result in research.internal_results[:2]:
            if result.source == "deals":
                questions.append("What's the current status of our previous discussions?")
                break
        
        # Meeting context questions
        title_lower = event.title.lower()
        if "partnership" in title_lower:
            questions.append("What does success look like for this partnership?")
            questions.append("What are the key milestones we should aim for?")
        elif "review" in title_lower:
            questions.append("What areas need the most attention going forward?")
            questions.append("What should we prioritize for next quarter?")
        elif "integration" in title_lower:
            questions.append("What's the timeline for the integration?")
            questions.append("What technical resources are needed?")
        else:
            # Default professional questions
            questions.extend([
                "What are your top priorities right now?",
                "What would make this meeting a success for you?",
                "What are the next steps after this meeting?",
            ])
        
        return questions[:4]
    
    def _summarize_internal_context(self, research: ResearchResults) -> str:
        """Summarize internal database findings."""
        if not research.internal_results:
            return ""
        
        summaries = []
        
        # Group by source
        by_source = {}
        for result in research.internal_results:
            if result.source not in by_source:
                by_source[result.source] = []
            by_source[result.source].append(result)
        
        for source, results in by_source.items():
            source_name = source.replace("_", " ").title()
            count = len(results)
            
            if results:
                # Get most recent/relevant item details
                top_result = results[0]
                content_preview = top_result.content[:150].replace('\n', ' ')
                summaries.append(f"{source_name} ({count} record(s)): {content_preview}")
        
        return " | ".join(summaries)
    
    def _collect_reference_links(self, research: ResearchResults) -> List[dict]:
        """Collect useful reference links, deduplicated."""
        links = []
        seen_urls: set = set()
        
        # LinkedIn profiles (always include)
        for person in research.people:
            url = person.linkedin_url
            if url and not self._is_duplicate_url(url, seen_urls):
                seen_urls.add(url)
                links.append({
                    "title": f"LinkedIn: {person.name}",
                    "url": url,
                })
        
        # Company news links (deduplicated)
        for company in research.companies:
            for news in company.recent_news[:2]:
                url = news.url
                if url and not self._is_duplicate_url(url, seen_urls):
                    seen_urls.add(url)
                    links.append({
                        "title": f"{company.name}: {news.title[:40]}",
                        "url": url,
                    })
        
        return links[:8]  # Limit to 8 links
    
    def _get_sources_used(self, research: ResearchResults) -> List[str]:
        """Get list of sources used in research."""
        sources = set()
        
        if research.internal_results:
            sources.add("Internal Database")
        
        if research.people:
            sources.add("Web Search (People)")
        
        if research.companies:
            sources.add("Web Search (Companies)")
        
        if research.external_results:
            sources.add("Web Search (Context)")
        
        return list(sources)

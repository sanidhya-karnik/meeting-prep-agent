"""
Calendar event watcher and processor.

Monitors calendar for upcoming meetings and triggers research/briefing generation.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Set, Callable, Optional

from models import CalendarEvent, PrepTask, MeetingBriefing
from config import get_settings
from .client import CalendarClient


class CalendarWatcher:
    """
    Watches calendar for upcoming meetings and processes them.
    
    Tracks which events have been processed to avoid duplicates.
    """
    
    def __init__(
        self,
        on_meeting_found: Optional[Callable[[CalendarEvent], None]] = None
    ):
        self.client = CalendarClient()
        self.settings = get_settings()
        self.processed_events: Set[str] = set()
        self.on_meeting_found = on_meeting_found
    
    def get_events_needing_prep(self) -> List[CalendarEvent]:
        """
        Get upcoming events that need preparation tasks.
        
        Filters out:
        - Already processed events
        - Events that already have prep tasks
        - All-day events
        - Events with no attendees (likely personal blocks)
        
        Returns:
            List of events needing preparation
        """
        events = self.client.get_upcoming_events()
        events_to_process = []
        
        for event in events:
            # Skip if already processed
            if event.event_id in self.processed_events:
                continue
            
            # Skip if no attendees (likely a personal event/block)
            if len(event.attendees) == 0:
                continue
            
            # Skip all-day events (no specific time)
            if event.start_time.hour == 0 and event.start_time.minute == 0:
                if event.end_time.hour == 0 and event.end_time.minute == 0:
                    continue
            
            # Skip if prep task already exists
            if self.client.check_prep_task_exists(event.event_id):
                self.processed_events.add(event.event_id)
                continue
            
            events_to_process.append(event)
        
        return events_to_process
    
    def calculate_prep_task_time(self, event: CalendarEvent) -> tuple[datetime, datetime]:
        """Calculate when to schedule the prep task."""
        now_utc = datetime.now(timezone.utc)
        
        event_start_utc = event.start_time
        if event.start_time.tzinfo is not None:
            event_start_utc = event.start_time.astimezone(timezone.utc)
        
        prep_minutes = self.settings.prep_task_minutes_before
        ideal_prep_start_utc = event_start_utc - timedelta(minutes=prep_minutes)
        
        if ideal_prep_start_utc <= now_utc:
            prep_start = now_utc
        else:
            prep_start = ideal_prep_start_utc
        
        prep_end = prep_start + timedelta(minutes=15)
        
        return prep_start, prep_end
    
    def create_prep_task_for_event(
        self, 
        event: CalendarEvent, 
        briefing: MeetingBriefing
    ) -> Optional[str]:
        """Create a preparation task on the calendar for a meeting."""
        prep_start, prep_end = self.calculate_prep_task_time(event)
        
        description = self._build_full_description(event, briefing)
        description += f"\n\n[PREP:{event.event_id}]"
        
        prep_task = PrepTask(
            event_id=event.event_id,
            title=f"Prep: {event.title}",
            description=description,
            start_time=prep_start,
            end_time=prep_end,
        )
        
        task_id = self.client.create_prep_task(prep_task)
        
        if task_id:
            self.processed_events.add(event.event_id)
        
        return task_id
    
    def _clean_text(self, text: str) -> str:
        """Clean text of em dashes and markdown."""
        if not text:
            return ""
        text = text.replace('\u2014', ', ').replace('\u2013', ', ')
        text = ' '.join(text.split())  # Normalize whitespace
        # Remove markdown headers
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                line = line.lstrip('#').strip()
            lines.append(line)
        return ' '.join(lines).strip()
    
    def _truncate_at_sentence(self, text: str, max_chars: int) -> str:
        """Truncate text at a sentence boundary."""
        if not text:
            return ""
        
        text = self._clean_text(text)
        
        if len(text) <= max_chars:
            return text
        
        truncated = text[:max_chars]
        
        # Find last sentence boundary
        last_period = truncated.rfind('. ')
        last_exclaim = truncated.rfind('! ')
        last_question = truncated.rfind('? ')
        
        last_boundary = max(last_period, last_exclaim, last_question)
        
        if last_boundary > max_chars * 0.4:
            return truncated[:last_boundary + 1].strip()
        
        # Truncate at last space
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space].strip() + "..."
        
        return truncated.strip() + "..."
    
    def _is_duplicate_url(self, url: str, seen_urls: Set[str]) -> bool:
        """Check if URL is a duplicate or near-duplicate."""
        if not url:
            return True
        
        url_clean = url.rstrip('/').lower()
        
        for seen in seen_urls:
            seen_clean = seen.rstrip('/').lower()
            if url_clean == seen_clean:
                return True
            # One is substring of the other (e.g., /newsroom vs /newsroom/news)
            if url_clean in seen_clean or seen_clean in url_clean:
                return True
        
        return False
    
    def _build_full_description(self, event: CalendarEvent, briefing: MeetingBriefing) -> str:
        """Build a comprehensive briefing directly in the task description."""
        lines = [
            "MEETING PREP",
            "=" * 40,
            "",
            f"Meeting: {event.title}",
            f"Time: {event.start_time.strftime('%I:%M %p on %B %d, %Y')}",
        ]
        
        if event.companies:
            lines.append(f"Companies: {', '.join(event.companies)}")
        
        lines.append("")
        
        # Agenda first (most important)
        if briefing.key_talking_points:
            lines.append("AGENDA")
            lines.append("-" * 30)
            for i, point in enumerate(briefing.key_talking_points[:6], 1):
                clean_point = self._truncate_at_sentence(point, 100)
                lines.append(f"{i}. {clean_point}")
            lines.append("")
        
        # Company Intel (more useful than generic summary)
        if briefing.company_context:
            lines.append("COMPANY INTEL")
            lines.append("-" * 30)
            seen_urls: Set[str] = set()
            
            for ctx in briefing.company_context[:2]:
                lines.append(ctx.name)
                if ctx.description:
                    desc = self._truncate_at_sentence(ctx.description, 200)
                    lines.append(f"  {desc}")
                
                # Add unique news links
                if ctx.recent_news:
                    news_added = 0
                    for news in ctx.recent_news:
                        url = news.get('url', '')
                        title = news.get('title', '')
                        
                        if title and url and not self._is_duplicate_url(url, seen_urls):
                            seen_urls.add(url)
                            # Truncate title cleanly
                            if len(title) > 50:
                                title = title[:47] + "..."
                            lines.append(f"  * {title}")
                            lines.append(f"    {url}")
                            news_added += 1
                            if news_added >= 2:
                                break
                lines.append("")
        
        # Attendee Info (simplified)
        if briefing.attendee_profiles:
            lines.append("ATTENDEES")
            lines.append("-" * 30)
            for profile in briefing.attendee_profiles[:3]:
                header = profile.name
                if profile.company:
                    header += f" ({profile.company})"
                lines.append(header)
                
                if profile.linkedin_url:
                    lines.append(f"  {profile.linkedin_url}")
                
                if profile.background and "No profile" not in profile.background:
                    bg = self._truncate_at_sentence(profile.background, 120)
                    lines.append(f"  {bg}")
            lines.append("")
        
        # Questions (fewer, more relevant)
        if briefing.potential_questions:
            lines.append("QUESTIONS")
            lines.append("-" * 30)
            for q in briefing.potential_questions[:3]:
                lines.append(f"* {q}")
            lines.append("")
        
        lines.append("=" * 40)
        lines.append("Generated by Kairo")
        
        return "\n".join(lines)
    
    def mark_as_processed(self, event_id: str):
        """Mark an event as processed to avoid re-processing."""
        self.processed_events.add(event_id)
    
    def clear_old_processed(self, max_age_hours: int = 48):
        """Clear old processed event IDs to prevent memory growth."""
        if len(self.processed_events) > 1000:
            self.processed_events = set(list(self.processed_events)[-500:])

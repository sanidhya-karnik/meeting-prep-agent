"""
Kairo Production - Main Entry Point

Automated meeting preparation system that:
1. Monitors Google Calendar for upcoming meetings
2. Performs internal + external research
3. Creates preparation tasks with full briefings in the description

Usage:
    python main.py
    python main.py --once  # Run once and exit (for testing)
"""

import sys
import logging
import argparse
from datetime import datetime
from typing import Optional
from pathlib import Path

import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import get_settings, internal_search_enabled
from calendar_client import CalendarWatcher
from research import ResearchOrchestrator
from models import CalendarEvent, MeetingBriefing


# Configure logging
def setup_logging():
    """Configure structured logging."""
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s",
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
                else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()


class KairoService:
    """
    Main service that orchestrates meeting preparation.
    
    Workflow:
    1. Poll calendar for upcoming meetings
    2. For each meeting without a prep task:
       a. Perform internal research (if database configured)
       b. Perform external research (Tavily)
       c. Generate briefing
       d. Create calendar prep task with full briefing in description
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.watcher = CalendarWatcher()
        self.researcher = ResearchOrchestrator()
        
        logger.info(
            "kairo_initialized",
            internal_search=internal_search_enabled(),
            poll_interval=self.settings.poll_interval_seconds,
            lookahead_hours=self.settings.calendar_lookahead_hours,
        )
    
    def process_upcoming_meetings(self):
        """
        Check for upcoming meetings and create prep tasks.
        
        This is the main job that runs on schedule.
        """
        logger.info("checking_calendar")
        
        try:
            # Get events needing preparation
            events = self.watcher.get_events_needing_prep()
            
            if not events:
                logger.info("no_events_to_process")
                return
            
            logger.info("events_found", count=len(events))
            
            for event in events:
                self._process_single_event(event)
            
            # Cleanup old processed events
            self.watcher.clear_old_processed()
            
        except Exception as e:
            logger.error("calendar_check_failed", error=str(e))
    
    def _process_single_event(self, event: CalendarEvent):
        """Process a single calendar event."""
        logger.info(
            "processing_event",
            event_id=event.event_id,
            title=event.title,
            start_time=event.start_time.isoformat(),
            attendees=len(event.attendees),
            companies=event.companies,
        )
        
        try:
            # Step 1: Research
            logger.info("starting_research", event_id=event.event_id)
            research = self.researcher.research_meeting(event)
            
            logger.info(
                "research_complete",
                event_id=event.event_id,
                internal_results=len(research.internal_results),
                people_researched=len(research.people),
                companies_researched=len(research.companies),
            )
            
            # Step 2: Generate briefing
            logger.info("generating_briefing", event_id=event.event_id)
            briefing = self.researcher.generate_briefing(event, research)
            
            logger.info(
                "briefing_generated",
                event_id=event.event_id,
                talking_points=len(briefing.key_talking_points),
                sources=briefing.sources_used,
            )
            
            # Step 3: Create prep task with full briefing in description
            logger.info("creating_prep_task", event_id=event.event_id)
            task_id = self.watcher.create_prep_task_for_event(event, briefing)
            
            if task_id:
                logger.info(
                    "prep_task_created",
                    event_id=event.event_id,
                    task_id=task_id,
                    meeting_title=event.title,
                )
            else:
                logger.error(
                    "prep_task_creation_failed",
                    event_id=event.event_id,
                )
            
        except Exception as e:
            logger.error(
                "event_processing_failed",
                event_id=event.event_id,
                error=str(e),
            )
            import traceback
            traceback.print_exc()
            # Mark as processed to avoid retry loop
            self.watcher.mark_as_processed(event.event_id)
    
    def run_once(self):
        """Run a single check (useful for testing)."""
        logger.info("running_single_check")
        self.process_upcoming_meetings()
        logger.info("single_check_complete")
    
    def run_scheduled(self):
        """Run on schedule indefinitely."""
        scheduler = BlockingScheduler()
        
        # Add the main job
        scheduler.add_job(
            self.process_upcoming_meetings,
            IntervalTrigger(seconds=self.settings.poll_interval_seconds),
            id="calendar_check",
            name="Check calendar for upcoming meetings",
            replace_existing=True,
        )
        
        logger.info(
            "scheduler_started",
            poll_interval_seconds=self.settings.poll_interval_seconds,
        )
        
        # Run immediately on start
        self.process_upcoming_meetings()
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("scheduler_stopped")


def verify_configuration():
    """Verify required configuration is present."""
    settings = get_settings()
    
    errors = []
    
    if not settings.tavily_api_key or settings.tavily_api_key == "your_tavily_api_key_here":
        errors.append("TAVILY_API_KEY is not configured")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease update your .env file with the required values.")
        sys.exit(1)
    
    # Warnings (not fatal)
    if not internal_search_enabled():
        print("Note: Internal database search is disabled (DATABASE_URL not set)")
    
    print("Configuration verified successfully.")
    print(f"  - Tavily API: Configured")
    print(f"  - Internal DB: {'Configured' if internal_search_enabled() else 'Disabled'}")
    print(f"  - Poll interval: {settings.poll_interval_seconds} seconds")
    print(f"  - Lookahead: {settings.calendar_lookahead_hours} hours")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Kairo - Automated Meeting Preparation"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify configuration and exit",
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_logging()
    
    print("=" * 50)
    print("  Kairo - Automated Meeting Preparation")
    print("=" * 50)
    print()
    
    # Verify configuration
    verify_configuration()
    
    if args.verify:
        print("Configuration verification complete.")
        return
    
    # Initialize and run
    service = KairoService()
    
    if args.once:
        service.run_once()
    else:
        print("Starting scheduler...")
        print("Press Ctrl+C to stop.")
        print()
        service.run_scheduled()


if __name__ == "__main__":
    main()

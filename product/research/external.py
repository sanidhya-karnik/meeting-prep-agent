"""
External web research using Tavily API.

Searches the web for information about meeting attendees,
companies, and relevant context.
"""

from typing import List, Optional, Set
from datetime import datetime

from tavily import TavilyClient

from config import get_settings
from models import (
    ExternalSearchResult, 
    PersonResearch, 
    CompanyResearch,
    CalendarEvent,
)


class ExternalResearcher:
    """
    Performs external web research using Tavily API.
    
    Searches for:
    - Person backgrounds and LinkedIn profiles
    - Company information and recent news
    - Industry context
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = TavilyClient(api_key=self.settings.tavily_api_key)
    
    def search(
        self, 
        query: str, 
        search_depth: str = "basic",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None
    ) -> List[ExternalSearchResult]:
        """
        Perform a general web search.
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            max_results: Maximum number of results
            include_domains: Limit search to these domains
            
        Returns:
            List of search results
        """
        try:
            kwargs = {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
            }
            if include_domains:
                kwargs["include_domains"] = include_domains
            
            response = self.client.search(**kwargs)
            
            results = []
            for item in response.get("results", []):
                results.append(ExternalSearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    source="web",
                    published_date=item.get("published_date"),
                    relevance_score=item.get("score", 0.0),
                ))
            
            return results
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def research_person(self, name: str, company: Optional[str] = None) -> PersonResearch:
        """
        Research a person's background.
        
        Args:
            name: Person's name
            company: Optional company name for context
            
        Returns:
            PersonResearch with gathered information
        """
        research = PersonResearch(name=name, company=company)
        
        # Search LinkedIn specifically with company context for better accuracy
        if company:
            # More specific query to find the right professional
            linkedin_query = f'"{name}" "{company}" site:linkedin.com/in'
        else:
            linkedin_query = f'"{name}" professional site:linkedin.com/in'
        
        # Search LinkedIn only
        linkedin_results = self.search(
            linkedin_query, 
            max_results=3,
            include_domains=["linkedin.com"]
        )
        
        # Find best LinkedIn match
        for result in linkedin_results:
            url_lower = result.url.lower()
            if "linkedin.com/in/" in url_lower:
                # Skip if it's clearly wrong (check if company mentioned in content)
                if company:
                    content_lower = (result.content or "").lower()
                    title_lower = (result.title or "").lower()
                    company_lower = company.lower()
                    # Check if company name appears in result
                    if company_lower in content_lower or company_lower in title_lower:
                        research.linkedin_url = result.url
                        research.background = self._truncate_at_sentence(result.content, 300)
                        break
                else:
                    research.linkedin_url = result.url
                    research.background = self._truncate_at_sentence(result.content, 300)
                    break
        
        # If no good LinkedIn match found, just note that
        if not research.linkedin_url:
            research.background = f"Professional at {company}" if company else "No profile found"
        
        # Skip news search for individuals - focus on company news instead
        
        return research
    
    def research_company(self, company_name: str) -> CompanyResearch:
        """
        Research a company.
        
        Args:
            company_name: Company name
            
        Returns:
            CompanyResearch with gathered information
        """
        research = CompanyResearch(name=company_name)
        
        # Search for company information on their official site
        info_query = f"{company_name} company about us"
        info_results = self.search(info_query, max_results=3)
        
        if info_results:
            # Get description, truncate at sentence boundary
            research.description = self._truncate_at_sentence(info_results[0].content, 250)
        
        # Search for recent news - be specific
        news_query = f"{company_name} news announcements 2026"
        news_results = self.search(news_query, search_depth="advanced", max_results=5)
        
        # Deduplicate news URLs
        seen_urls: Set[str] = set()
        unique_news = []
        for result in news_results:
            if not self._is_duplicate_url(result.url, seen_urls):
                seen_urls.add(result.url)
                unique_news.append(result)
        
        research.recent_news = unique_news[:4]  # Keep top 4 unique
        
        return research
    
    def _truncate_at_sentence(self, text: str, max_chars: int) -> str:
        """Truncate text at a sentence boundary, not mid-word."""
        if not text:
            return ""
        
        # Clean first
        text = text.replace('\u2014', ', ').replace('\u2013', ', ')
        text = ' '.join(text.split())  # Normalize whitespace
        
        if len(text) <= max_chars:
            return text
        
        # Find the last sentence boundary before max_chars
        truncated = text[:max_chars]
        
        # Look for sentence endings
        last_period = truncated.rfind('. ')
        last_exclaim = truncated.rfind('! ')
        last_question = truncated.rfind('? ')
        
        # Find the latest sentence boundary
        last_boundary = max(last_period, last_exclaim, last_question)
        
        if last_boundary > max_chars * 0.5:  # Only use if it's past halfway
            return truncated[:last_boundary + 1].strip()
        
        # Otherwise truncate at last space
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space].strip() + "..."
        
        return truncated.strip() + "..."
    
    def _is_duplicate_url(self, url: str, seen_urls: Set[str]) -> bool:
        """Check if URL is a duplicate or near-duplicate of seen URLs."""
        if not url:
            return True
        
        url_clean = url.rstrip('/').lower()
        
        # Exact match
        if url_clean in seen_urls:
            return True
        
        # Check if this URL is a prefix/suffix of existing URLs
        for seen in seen_urls:
            seen_clean = seen.rstrip('/').lower()
            # One is substring of the other
            if url_clean in seen_clean or seen_clean in url_clean:
                return True
        
        return False
    
    def research_event(self, event: CalendarEvent) -> dict:
        """
        Comprehensive research for a calendar event.
        
        Args:
            event: Calendar event to research
            
        Returns:
            Dictionary with research results organized by type
        """
        results = {
            "people": [],
            "companies": [],
            "context": [],
        }
        
        # Research each external attendee
        researched_names = set()
        for attendee in event.attendees:
            if attendee.is_organizer:
                continue  # Skip researching yourself
            
            name = attendee.name or attendee.email.split("@")[0]
            if name in researched_names:
                continue
            researched_names.add(name)
            
            # Get company from email domain
            company = None
            if attendee.email and "@" in attendee.email:
                domain = attendee.email.split("@")[1]
                if domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                    company = domain.split(".")[0].title()
            
            person_research = self.research_person(name, company)
            person_research.email = attendee.email
            results["people"].append(person_research)
        
        # Research each company
        researched_companies = set()
        for company in event.companies:
            if company in researched_companies:
                continue
            researched_companies.add(company)
            
            company_research = self.research_company(company)
            results["companies"].append(company_research)
        
        # Search for context based on meeting title (skip - focus on company/people)
        
        return results
    
    def get_quick_summary(self, query: str) -> Optional[str]:
        """
        Get a quick AI-generated summary for a query.
        
        Uses Tavily's context feature.
        
        Args:
            query: Search query
            
        Returns:
            Generated summary or None
        """
        try:
            response = self.client.get_search_context(
                query=query,
                max_tokens=500,
            )
            return response
        except Exception as e:
            print(f"Tavily context error: {e}")
            return None

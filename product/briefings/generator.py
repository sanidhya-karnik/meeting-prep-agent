"""
HTML Briefing Generator.

Generates professional, styled HTML pages for meeting briefings.
"""

import os
import hashlib
from datetime import datetime
from typing import List, Set
from pathlib import Path

from models.schemas import MeetingBriefing, AttendeeProfile, CompanyContext, NewsItem


BRIEFINGS_DIR = Path(__file__).parent / "pages"


def ensure_briefings_dir():
    """Ensure the briefings directory exists."""
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)


def generate_briefing_id(event_id: str) -> str:
    """Generate a short, unique briefing ID."""
    hash_obj = hashlib.md5(event_id.encode())
    return hash_obj.hexdigest()[:12]


def generate_html_briefing(briefing: MeetingBriefing) -> str:
    """
    Generate a professional HTML briefing page.
    
    Args:
        briefing: The meeting briefing data
        
    Returns:
        Path to the generated HTML file (relative)
    """
    ensure_briefings_dir()
    
    briefing_id = generate_briefing_id(briefing.event_id)
    html_content = _render_html(briefing)
    
    # Save to file
    file_path = BRIEFINGS_DIR / f"{briefing_id}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return briefing_id


def _render_html(briefing: MeetingBriefing) -> str:
    """Render the full HTML page."""
    
    # Deduplicate news items by URL
    seen_urls: Set[str] = set()
    unique_news: List[NewsItem] = []
    for news in briefing.recent_news:
        if news.url and news.url not in seen_urls:
            # Also skip if it's a substring of another URL we've seen
            is_duplicate = False
            for seen_url in seen_urls:
                if news.url in seen_url or seen_url in news.url:
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_urls.add(news.url)
                unique_news.append(news)
    
    # Build sections
    attendees_html = _render_attendees(briefing.attendee_profiles)
    companies_html = _render_companies(briefing.company_context)
    news_html = _render_news(unique_news)
    talking_points_html = _render_talking_points(briefing.key_talking_points)
    questions_html = _render_questions(briefing.potential_questions)
    references_html = _render_references(briefing.reference_links)
    internal_html = _render_internal_context(briefing.internal_context)
    
    # Format meeting time nicely
    meeting_time = briefing.event_time.strftime("%A, %B %d, %Y at %I:%M %p")
    generated_time = briefing.generated_at.strftime("%B %d, %Y at %I:%M %p UTC")
    
    # Clean executive summary (remove markdown artifacts, em dashes)
    exec_summary = _clean_text(briefing.executive_summary)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Prep: {_escape_html(briefing.event_title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: #1a1a2e;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 0.5rem;
        }}
        
        .header .meeting-time {{
            color: #6b7280;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .header .meeting-time svg {{
            width: 18px;
            height: 18px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .card h2 {{
            font-size: 1rem;
            font-weight: 600;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .card h2 svg {{
            width: 20px;
            height: 20px;
        }}
        
        .executive-summary {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid #0ea5e9;
        }}
        
        .executive-summary p {{
            font-size: 1.05rem;
            line-height: 1.7;
            color: #334155;
        }}
        
        .attendee {{
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 0.75rem;
        }}
        
        .attendee:last-child {{
            margin-bottom: 0;
        }}
        
        .attendee-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }}
        
        .attendee-name {{
            font-weight: 600;
            color: #1e293b;
            font-size: 1rem;
        }}
        
        .attendee-role {{
            color: #64748b;
            font-size: 0.875rem;
        }}
        
        .attendee-linkedin {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            color: #0077b5;
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        .attendee-linkedin:hover {{
            text-decoration: underline;
        }}
        
        .attendee-background {{
            color: #475569;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-top: 0.5rem;
        }}
        
        .company {{
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 0.75rem;
        }}
        
        .company:last-child {{
            margin-bottom: 0;
        }}
        
        .company-name {{
            font-weight: 600;
            color: #1e293b;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .company-description {{
            color: #475569;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }}
        
        .company-news {{
            margin-top: 0.5rem;
        }}
        
        .company-news-title {{
            font-size: 0.75rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}
        
        .news-item {{
            padding: 0.75rem;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }}
        
        .news-item:last-child {{
            margin-bottom: 0;
        }}
        
        .news-headline {{
            font-weight: 500;
            color: #1e293b;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }}
        
        .news-link {{
            color: #6366f1;
            text-decoration: none;
            font-size: 0.8rem;
            word-break: break-all;
        }}
        
        .news-link:hover {{
            text-decoration: underline;
        }}
        
        .news-summary {{
            color: #64748b;
            font-size: 0.8rem;
            line-height: 1.4;
            margin-top: 0.5rem;
        }}
        
        .list-item {{
            padding: 0.75rem 1rem;
            background: #f8fafc;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            color: #334155;
            line-height: 1.5;
        }}
        
        .list-item:last-child {{
            margin-bottom: 0;
        }}
        
        .numbered {{
            display: flex;
            gap: 0.75rem;
        }}
        
        .number {{
            flex-shrink: 0;
            width: 24px;
            height: 24px;
            background: #6366f1;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .reference-link {{
            display: block;
            padding: 0.75rem 1rem;
            background: #f8fafc;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            text-decoration: none;
            transition: background 0.2s;
        }}
        
        .reference-link:hover {{
            background: #e2e8f0;
        }}
        
        .reference-link:last-child {{
            margin-bottom: 0;
        }}
        
        .reference-title {{
            font-weight: 500;
            color: #1e293b;
            font-size: 0.9rem;
        }}
        
        .reference-url {{
            color: #6366f1;
            font-size: 0.8rem;
            word-break: break-all;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: rgba(255,255,255,0.8);
            font-size: 0.875rem;
        }}
        
        .footer strong {{
            color: white;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
        }}
        
        .internal-context {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
        }}
        
        .internal-context p {{
            color: #78350f;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{_escape_html(briefing.event_title)}</h1>
            <div class="meeting-time">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                {meeting_time}
            </div>
        </header>
        
        <div class="card executive-summary">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Executive Summary
            </h2>
            <p>{exec_summary}</p>
        </div>
        
        {internal_html}
        
        <div class="grid-2">
            <div>
                {attendees_html}
            </div>
            <div>
                {companies_html}
            </div>
        </div>
        
        {news_html}
        
        <div class="grid-2">
            <div>
                {talking_points_html}
            </div>
            <div>
                {questions_html}
            </div>
        </div>
        
        {references_html}
        
        <footer class="footer">
            <p>Generated by <strong>Kairo</strong> on {generated_time}</p>
        </footer>
    </div>
</body>
</html>'''
    
    return html


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))


def _clean_text(text: str) -> str:
    """Clean text by removing markdown artifacts and em dashes."""
    if not text:
        return ""
    
    # Remove em dashes
    text = text.replace("—", ", ")
    text = text.replace("–", ", ")
    
    # Remove markdown headers
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        cleaned_lines.append(line)
    
    text = " ".join(cleaned_lines)
    
    # Clean up multiple spaces
    while "  " in text:
        text = text.replace("  ", " ")
    
    return text.strip()


def _render_attendees(profiles: List[AttendeeProfile]) -> str:
    """Render attendees section."""
    if not profiles:
        return ""
    
    items = []
    for profile in profiles[:5]:
        name = _escape_html(profile.name)
        
        role_company = []
        if profile.role:
            role_company.append(_escape_html(profile.role))
        if profile.company:
            role_company.append(_escape_html(profile.company))
        role_text = " at ".join(role_company) if role_company else ""
        
        linkedin_html = ""
        if profile.linkedin_url:
            linkedin_html = f'''
                <a href="{_escape_html(profile.linkedin_url)}" target="_blank" class="attendee-linkedin">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                    LinkedIn
                </a>'''
        
        background_html = ""
        if profile.background:
            bg = _clean_text(profile.background)[:200]
            background_html = f'<div class="attendee-background">{_escape_html(bg)}</div>'
        
        items.append(f'''
            <div class="attendee">
                <div class="attendee-header">
                    <div>
                        <div class="attendee-name">{name}</div>
                        <div class="attendee-role">{role_text}</div>
                    </div>
                    {linkedin_html}
                </div>
                {background_html}
            </div>''')
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                Attendees
            </h2>
            {"".join(items)}
        </div>'''


def _render_companies(companies: List[CompanyContext]) -> str:
    """Render companies section."""
    if not companies:
        return ""
    
    items = []
    for company in companies[:3]:
        name = _escape_html(company.name)
        
        desc_html = ""
        if company.description:
            desc = _clean_text(company.description)[:200]
            desc_html = f'<div class="company-description">{_escape_html(desc)}</div>'
        
        news_html = ""
        if company.recent_news:
            # Deduplicate news for this company
            seen = set()
            news_items = []
            for news in company.recent_news[:3]:
                url = news.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    title = _escape_html(news.get("title", "")[:80])
                    news_items.append(f'''
                        <div class="news-item">
                            <div class="news-headline">{title}</div>
                            <a href="{_escape_html(url)}" target="_blank" class="news-link">{_escape_html(url[:60])}...</a>
                        </div>''')
            
            if news_items:
                news_html = f'''
                    <div class="company-news">
                        <div class="company-news-title">Recent News</div>
                        {"".join(news_items)}
                    </div>'''
        
        items.append(f'''
            <div class="company">
                <div class="company-name">{name}</div>
                {desc_html}
                {news_html}
            </div>''')
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
                Company Intelligence
            </h2>
            {"".join(items)}
        </div>'''


def _render_news(news_items: List[NewsItem]) -> str:
    """Render recent news section."""
    if not news_items:
        return ""
    
    items = []
    for news in news_items[:5]:
        headline = _escape_html(_clean_text(news.headline)[:100])
        url = _escape_html(news.url) if news.url else ""
        
        summary_html = ""
        if news.summary:
            summary = _clean_text(news.summary)[:150]
            summary_html = f'<div class="news-summary">{_escape_html(summary)}</div>'
        
        link_html = ""
        if url:
            link_html = f'<a href="{url}" target="_blank" class="news-link">{_escape_html(news.url[:70])}...</a>'
        
        items.append(f'''
            <div class="news-item">
                <div class="news-headline">{headline}</div>
                {link_html}
                {summary_html}
            </div>''')
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                </svg>
                Recent Developments
            </h2>
            {"".join(items)}
        </div>'''


def _render_talking_points(points: List[str]) -> str:
    """Render talking points section."""
    if not points:
        return ""
    
    items = []
    for i, point in enumerate(points[:6], 1):
        clean_point = _escape_html(_clean_text(point))
        items.append(f'''
            <div class="list-item numbered">
                <span class="number">{i}</span>
                <span>{clean_point}</span>
            </div>''')
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                Talking Points
            </h2>
            {"".join(items)}
        </div>'''


def _render_questions(questions: List[str]) -> str:
    """Render questions section."""
    if not questions:
        return ""
    
    items = []
    for q in questions[:5]:
        clean_q = _escape_html(_clean_text(q))
        items.append(f'<div class="list-item">{clean_q}</div>')
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Questions to Consider
            </h2>
            {"".join(items)}
        </div>'''


def _render_references(links: List[dict]) -> str:
    """Render reference links section."""
    if not links:
        return ""
    
    # Deduplicate links
    seen = set()
    items = []
    for ref in links[:10]:
        url = ref.get("url", "")
        if url and url not in seen:
            seen.add(url)
            title = _escape_html(ref.get("title", "Link")[:60])
            items.append(f'''
                <a href="{_escape_html(url)}" target="_blank" class="reference-link">
                    <div class="reference-title">{title}</div>
                    <div class="reference-url">{_escape_html(url[:80])}</div>
                </a>''')
    
    if not items:
        return ""
    
    return f'''
        <div class="card">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                Reference Links
            </h2>
            {"".join(items)}
        </div>'''


def _render_internal_context(context: str) -> str:
    """Render internal context section."""
    if not context:
        return ""
    
    clean_context = _escape_html(_clean_text(context))
    
    return f'''
        <div class="card internal-context">
            <h2>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
                Internal Context
            </h2>
            <p>{clean_context}</p>
        </div>'''

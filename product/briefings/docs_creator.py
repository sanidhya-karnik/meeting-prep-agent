"""
Google Docs creator for briefing pages.

Creates nicely formatted Google Docs for meeting briefings
that render perfectly on any device (phone, tablet, desktop).
"""

from typing import Optional, List, Set
from datetime import datetime

from googleapiclient.discovery import build

from calendar_client.auth import get_credentials
from models.schemas import MeetingBriefing, AttendeeProfile, CompanyContext, NewsItem


class DocsCreator:
    """
    Creates Google Docs for meeting briefings.
    
    Creates a 'Kairo Briefings' folder in Drive and creates
    formatted briefing documents there with public view access.
    """
    
    FOLDER_NAME = "Kairo Briefings"
    
    def __init__(self):
        self.credentials = get_credentials()
        self.drive_service = build("drive", "v3", credentials=self.credentials)
        self.docs_service = build("docs", "v1", credentials=self.credentials)
        self._folder_id: Optional[str] = None
    
    def get_or_create_folder(self) -> str:
        """Get or create the Kairo Briefings folder."""
        if self._folder_id:
            return self._folder_id
        
        # Search for existing folder
        query = f"name='{self.FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.drive_service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name)"
        ).execute()
        
        files = results.get("files", [])
        
        if files:
            self._folder_id = files[0]["id"]
            return self._folder_id
        
        # Create new folder
        folder_metadata = {
            "name": self.FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }
        
        folder = self.drive_service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()
        
        self._folder_id = folder["id"]
        return self._folder_id
    
    def create_briefing_doc(self, briefing: MeetingBriefing) -> Optional[str]:
        """
        Create a Google Doc for the meeting briefing.
        
        Args:
            briefing: The meeting briefing data
            
        Returns:
            Public viewable URL or None on failure
        """
        try:
            folder_id = self.get_or_create_folder()
            
            # Clean title for filename
            safe_title = "".join(c for c in briefing.event_title if c.isalnum() or c in " -_")[:50]
            doc_title = f"Meeting Prep: {safe_title}"
            
            # Check if doc already exists
            existing_id = self._find_existing_doc(doc_title, folder_id)
            
            if existing_id:
                # Delete and recreate (simpler than updating)
                self.drive_service.files().delete(fileId=existing_id).execute()
            
            # Create new doc
            doc_metadata = {
                "name": doc_title,
                "mimeType": "application/vnd.google-apps.document",
                "parents": [folder_id]
            }
            
            doc = self.drive_service.files().create(
                body=doc_metadata,
                fields="id"
            ).execute()
            
            doc_id = doc["id"]
            
            # Build and apply document content
            requests = self._build_doc_content(briefing)
            
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": requests}
                ).execute()
            
            # Make publicly viewable
            self._make_public(doc_id)
            
            # Return the shareable link
            return f"https://docs.google.com/document/d/{doc_id}/view"
            
        except Exception as e:
            print(f"Failed to create briefing doc: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _find_existing_doc(self, title: str, folder_id: str) -> Optional[str]:
        """Find an existing doc by title in the folder."""
        query = f"name='{title}' and '{folder_id}' in parents and trashed=false"
        results = self.drive_service.files().list(
            q=query,
            spaces="drive",
            fields="files(id)"
        ).execute()
        
        files = results.get("files", [])
        return files[0]["id"] if files else None
    
    def _make_public(self, file_id: str):
        """Make a file publicly viewable."""
        try:
            permission = {
                "type": "anyone",
                "role": "reader"
            }
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
        except Exception as e:
            print(f"Failed to set public permissions: {e}")
    
    def _build_doc_content(self, briefing: MeetingBriefing) -> List[dict]:
        """Build the document content as a list of requests."""
        requests = []
        index = 1  # Start after the implicit newline
        
        # Helper to add text
        def add_text(text: str, bold: bool = False, font_size: int = 11, 
                     heading: bool = False, color: tuple = None) -> int:
            nonlocal index
            
            # Insert text
            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": text
                }
            })
            
            end_index = index + len(text)
            
            # Style the text
            style = {
                "fontSize": {"magnitude": font_size, "unit": "PT"}
            }
            
            if bold:
                style["bold"] = True
            
            if color:
                style["foregroundColor"] = {
                    "color": {
                        "rgbColor": {
                            "red": color[0],
                            "green": color[1],
                            "blue": color[2]
                        }
                    }
                }
            
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": end_index},
                    "textStyle": style,
                    "fields": "fontSize,bold,foregroundColor"
                }
            })
            
            if heading:
                requests.append({
                    "updateParagraphStyle": {
                        "range": {"startIndex": index, "endIndex": end_index},
                        "paragraphStyle": {
                            "namedStyleType": "HEADING_2" if font_size > 14 else "HEADING_3"
                        },
                        "fields": "namedStyleType"
                    }
                })
            
            index = end_index
            return end_index
        
        def add_newline():
            nonlocal index
            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": "\n"
                }
            })
            index += 1
        
        def add_link(text: str, url: str):
            nonlocal index
            
            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": text
                }
            })
            
            end_index = index + len(text)
            
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": end_index},
                    "textStyle": {
                        "link": {"url": url},
                        "foregroundColor": {
                            "color": {"rgbColor": {"red": 0.26, "green": 0.52, "blue": 0.96}}
                        }
                    },
                    "fields": "link,foregroundColor"
                }
            })
            
            index = end_index
        
        # ===== TITLE =====
        add_text(f"{briefing.event_title}\n", bold=True, font_size=24, heading=True)
        
        # Meeting time
        meeting_time = briefing.event_time.strftime("%A, %B %d, %Y at %I:%M %p")
        add_text(f"{meeting_time}\n\n", font_size=12, color=(0.4, 0.4, 0.4))
        
        # ===== EXECUTIVE SUMMARY =====
        add_text("Executive Summary\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
        summary = self._clean_text(briefing.executive_summary)
        add_text(f"{summary}\n\n", font_size=11)
        
        # ===== AGENDA / TALKING POINTS =====
        if briefing.key_talking_points:
            add_text("Agenda\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
            for i, point in enumerate(briefing.key_talking_points[:6], 1):
                clean_point = self._clean_text(point)
                add_text(f"{i}. {clean_point}\n", font_size=11)
            add_newline()
        
        # ===== ATTENDEES =====
        if briefing.attendee_profiles:
            add_text("Attendees\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
            
            for profile in briefing.attendee_profiles[:5]:
                # Name and role
                name_text = profile.name
                if profile.role and profile.company:
                    name_text += f" - {profile.role} at {profile.company}"
                elif profile.company:
                    name_text += f" - {profile.company}"
                
                add_text(f"{name_text}\n", bold=True, font_size=11)
                
                # LinkedIn link
                if profile.linkedin_url:
                    add_text("  LinkedIn: ", font_size=10, color=(0.5, 0.5, 0.5))
                    add_link("View Profile", profile.linkedin_url)
                    add_newline()
                
                # Background
                if profile.background:
                    bg = self._clean_text(profile.background)[:200]
                    add_text(f"  {bg}\n", font_size=10, color=(0.4, 0.4, 0.4))
                
                add_newline()
        
        # ===== COMPANY INTELLIGENCE =====
        if briefing.company_context:
            add_text("Company Intelligence\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
            
            for ctx in briefing.company_context[:3]:
                add_text(f"{ctx.name}\n", bold=True, font_size=11)
                
                if ctx.description:
                    desc = self._clean_text(ctx.description)[:200]
                    add_text(f"{desc}\n", font_size=10, color=(0.4, 0.4, 0.4))
                
                # Recent news
                if ctx.recent_news:
                    seen_urls: Set[str] = set()
                    add_text("Recent News:\n", font_size=10, bold=True)
                    for news in ctx.recent_news[:3]:
                        url = news.get("url", "")
                        title = news.get("title", "")[:60]
                        
                        # Skip duplicates
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        add_text("  • ", font_size=10)
                        if url:
                            add_link(title, url)
                        else:
                            add_text(title, font_size=10)
                        add_newline()
                
                add_newline()
        
        # ===== QUESTIONS TO CONSIDER =====
        if briefing.potential_questions:
            add_text("Questions to Consider\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
            for q in briefing.potential_questions[:5]:
                add_text(f"• {q}\n", font_size=11)
            add_newline()
        
        # ===== REFERENCE LINKS =====
        if briefing.reference_links:
            add_text("Reference Links\n", bold=True, font_size=14, heading=True, color=(0.2, 0.4, 0.8))
            
            seen_urls: Set[str] = set()
            for ref in briefing.reference_links[:10]:
                url = ref.get("url", "")
                title = ref.get("title", "Link")[:50]
                
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                add_text("• ", font_size=10)
                add_link(title, url)
                add_newline()
            
            add_newline()
        
        # ===== FOOTER =====
        generated_time = briefing.generated_at.strftime("%B %d, %Y at %I:%M %p UTC")
        add_text(f"\nGenerated by Kairo on {generated_time}", font_size=9, color=(0.6, 0.6, 0.6))
        
        return requests
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing markdown and em dashes."""
        if not text:
            return ""
        
        # Remove em dashes
        text = text.replace("\u2014", ", ")
        text = text.replace("\u2013", ", ")
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

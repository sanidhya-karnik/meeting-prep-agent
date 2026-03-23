"""
Google Drive uploader for briefing pages.

Uploads HTML briefings to Google Drive and returns shareable links
that work from any device (phone, tablet, desktop).
"""

import io
from typing import Optional
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from calendar_client.auth import get_credentials


class DriveUploader:
    """
    Uploads HTML briefings to Google Drive for universal access.
    
    Creates a 'Kairo Briefings' folder in Drive and uploads
    briefing pages there with public view access.
    """
    
    FOLDER_NAME = "Kairo Briefings"
    
    def __init__(self):
        self.credentials = get_credentials()
        self.service = build("drive", "v3", credentials=self.credentials)
        self._folder_id: Optional[str] = None
    
    def get_or_create_folder(self) -> str:
        """Get or create the Kairo Briefings folder."""
        if self._folder_id:
            return self._folder_id
        
        # Search for existing folder
        query = f"name='{self.FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
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
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()
        
        self._folder_id = folder["id"]
        return self._folder_id
    
    def upload_briefing(self, briefing_id: str, html_content: str, title: str) -> Optional[str]:
        """
        Upload an HTML briefing to Google Drive.
        
        Args:
            briefing_id: Unique briefing identifier
            html_content: The HTML content to upload
            title: Meeting title for the filename
            
        Returns:
            Public viewable URL or None on failure
        """
        try:
            folder_id = self.get_or_create_folder()
            
            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:50]
            filename = f"{safe_title}_{briefing_id}.html"
            
            # Check if file already exists (update instead of create)
            existing_file_id = self._find_existing_file(filename, folder_id)
            
            # Prepare file content
            file_bytes = html_content.encode("utf-8")
            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype="text/html",
                resumable=True
            )
            
            if existing_file_id:
                # Update existing file
                file = self.service.files().update(
                    fileId=existing_file_id,
                    media_body=media
                ).execute()
                file_id = existing_file_id
            else:
                # Create new file
                file_metadata = {
                    "name": filename,
                    "parents": [folder_id],
                    "mimeType": "text/html"
                }
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()
                
                file_id = file["id"]
                
                # Make file publicly viewable
                self._make_public(file_id)
            
            # Return the direct view URL
            return f"https://drive.google.com/file/d/{file_id}/view"
            
        except Exception as e:
            print(f"Failed to upload briefing to Drive: {e}")
            return None
    
    def _find_existing_file(self, filename: str, folder_id: str) -> Optional[str]:
        """Find an existing file by name in the folder."""
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = self.service.files().list(
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
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
        except Exception as e:
            print(f"Failed to set public permissions: {e}")
    
    def delete_old_briefings(self, max_age_days: int = 30):
        """Delete briefings older than max_age_days."""
        from datetime import datetime, timedelta
        
        try:
            folder_id = self.get_or_create_folder()
            cutoff = datetime.utcnow() - timedelta(days=max_age_days)
            cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
            
            query = f"'{folder_id}' in parents and modifiedTime < '{cutoff_str}' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)"
            ).execute()
            
            for file in results.get("files", []):
                self.service.files().delete(fileId=file["id"]).execute()
                print(f"Deleted old briefing: {file['name']}")
                
        except Exception as e:
            print(f"Failed to delete old briefings: {e}")

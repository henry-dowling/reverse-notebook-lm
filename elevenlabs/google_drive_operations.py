"""
Google Drive and Google Docs operations module for the ElevenLabs API.
Handles authentication and CRUD operations for Google Drive files and Google Docs.
"""

import os
import json
import pickle
from typing import List, Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import logging

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Manages Google Drive API operations and authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, folder_name: str = "caplog"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.folder_name = folder_name
        self.folder_id = None
        self.credentials = None
        self.drive_service = None
        self.docs_service = None
        self.token_file = "google_token.pickle"
        
        # OAuth 2.0 scopes for Drive and Docs
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents'
        ]
    
    def load_credentials(self) -> bool:
        """Load saved credentials from file."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
                    
                # Refresh credentials if they're expired
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self.save_credentials()
                
                if self.credentials and self.credentials.valid:
                    self._build_services()
                    return True
            except Exception as e:
                logger.error(f"Error loading credentials: {str(e)}")
                
        return False
    
    def save_credentials(self):
        """Save credentials to file."""
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
    
    def get_auth_url(self) -> str:
        """Get the authorization URL for OAuth flow."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store flow configuration instead of the flow object itself
        flow_config = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes,
            "state": state
        }
        
        with open('oauth_flow_config.json', 'w') as f:
            json.dump(flow_config, f)
        
        return authorization_url
    
    def handle_auth_callback(self, authorization_code: str) -> bool:
        """Handle the OAuth callback and exchange code for tokens."""
        try:
            # Load flow configuration
            with open('oauth_flow_config.json', 'r') as f:
                flow_config = json.load(f)
            
            # Recreate the flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": flow_config["client_id"],
                        "client_secret": flow_config["client_secret"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [flow_config["redirect_uri"]]
                    }
                },
                scopes=flow_config["scopes"]
            )
            flow.redirect_uri = flow_config["redirect_uri"]
            
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            self.save_credentials()
            self._build_services()
            
            # Clean up the temporary flow configuration file
            if os.path.exists('oauth_flow_config.json'):
                os.remove('oauth_flow_config.json')
                
            return True
        except Exception as e:
            logger.error(f"Error handling auth callback: {str(e)}")
            return False
    
    def _build_services(self):
        """Build Google API service objects."""
        if self.credentials and self.credentials.valid:
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.docs_service = build('docs', 'v1', credentials=self.credentials)
            # Initialize the folder after building services
            self._ensure_folder_exists()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated and services are available."""
        return (self.credentials and self.credentials.valid and 
                self.drive_service is not None and self.docs_service is not None)
    
    def _ensure_folder_exists(self):
        """Ensure the target folder exists, create if it doesn't."""
        if not self.is_authenticated():
            return
        
        try:
            # Search for existing folder
            results = self.drive_service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # Use existing folder
                self.folder_id = folders[0]['id']
                logger.info(f"Using existing folder '{self.folder_name}' (ID: {self.folder_id})")
            else:
                # Create new folder
                folder_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.drive_service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.folder_id = folder.get('id')
                logger.info(f"Created new folder '{self.folder_name}' (ID: {self.folder_id})")
                
        except HttpError as error:
            logger.error(f"Error ensuring folder exists: {error}")
            raise Exception(f"Failed to ensure folder exists: {error}")
    
    # Drive operations
    def list_files(self, folder_id: Optional[str] = None, file_type: Optional[str] = None) -> List[Dict]:
        """List files in Google Drive."""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Drive")
        
        try:
            query_parts = []
            
            # Use the caplog folder by default if no folder_id specified
            target_folder_id = folder_id or self.folder_id
            if target_folder_id:
                query_parts.append(f"'{target_folder_id}' in parents")
            
            if file_type == "documents":
                query_parts.append("mimeType='application/vnd.google-apps.document'")
            elif file_type == "text":
                query_parts.append("mimeType='text/plain'")
            
            query_parts.append("trashed=false")
            query = " and ".join(query_parts) if query_parts else "trashed=false"
            
            results = self.drive_service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            
            return results.get('files', [])
        except HttpError as error:
            logger.error(f"Error listing files: {error}")
            raise Exception(f"Failed to list files: {error}")
    
    def get_file_content(self, file_id: str) -> str:
        """Get content of a file from Google Drive."""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Drive")
        
        try:
            # Get file metadata to determine type
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType')
            
            if mime_type == 'application/vnd.google-apps.document':
                # For Google Docs, use the Docs API
                return self._get_doc_content(file_id)
            else:
                # For other file types, export as plain text
                request = self.drive_service.files().export_media(
                    fileId=file_id, mimeType='text/plain'
                )
                file_io = io.BytesIO()
                downloader = MediaIoBaseDownload(file_io, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                return file_io.getvalue().decode('utf-8')
                
        except HttpError as error:
            logger.error(f"Error getting file content: {error}")
            raise Exception(f"Failed to get file content: {error}")
    
    def _get_doc_content(self, doc_id: str) -> str:
        """Get content from a Google Doc."""
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = []
            
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_element in paragraph.get('elements', []):
                        if 'textRun' in text_element:
                            content.append(text_element['textRun']['content'])
            
            return ''.join(content)
        except HttpError as error:
            logger.error(f"Error getting doc content: {error}")
            raise Exception(f"Failed to get document content: {error}")
    
    def create_file(self, filename: str, content: str, mime_type: str = 'text/plain') -> Dict:
        """Create a new file in Google Drive."""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Drive")
        
        try:
            if mime_type == 'application/vnd.google-apps.document':
                # Create a Google Doc
                return self._create_google_doc(filename, content)
            else:
                # Create a regular file in the caplog folder
                file_metadata = {
                    'name': filename,
                    'parents': [self.folder_id] if self.folder_id else []
                }
                media = MediaIoBaseUpload(
                    io.BytesIO(content.encode('utf-8')),
                    mimetype=mime_type
                )
                
                file = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name'
                ).execute()
                
                return file
                
        except HttpError as error:
            logger.error(f"Error creating file: {error}")
            raise Exception(f"Failed to create file: {error}")
    
    def _create_google_doc(self, title: str, content: str) -> Dict:
        """Create a new Google Doc with content."""
        try:
            # Create empty document
            doc = self.docs_service.documents().create(body={'title': title}).execute()
            doc_id = doc.get('documentId')
            
            # Move the document to the caplog folder if folder exists
            if self.folder_id:
                # Get current parents
                file = self.drive_service.files().get(fileId=doc_id, fields='parents').execute()
                previous_parents = ",".join(file.get('parents', []))
                
                # Move to caplog folder
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=self.folder_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
            
            # Add content to the document
            if content.strip():
                requests = [{
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }]
                
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
            
            return {'id': doc_id, 'name': title}
        except HttpError as error:
            logger.error(f"Error creating Google Doc: {error}")
            raise Exception(f"Failed to create Google Doc: {error}")
    
    def update_file(self, file_id: str, content: str) -> Dict:
        """Update an existing file in Google Drive."""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Drive")
        
        try:
            # Get file metadata to determine type
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType')
            
            if mime_type == 'application/vnd.google-apps.document':
                # Update Google Doc
                return self._update_google_doc(file_id, content)
            else:
                # Update regular file
                media = MediaIoBaseUpload(
                    io.BytesIO(content.encode('utf-8')),
                    mimetype=mime_type
                )
                
                file = self.drive_service.files().update(
                    fileId=file_id,
                    media_body=media,
                    fields='id, name, modifiedTime'
                ).execute()
                
                return file
                
        except HttpError as error:
            logger.error(f"Error updating file: {error}")
            raise Exception(f"Failed to update file: {error}")
    
    def _update_google_doc(self, doc_id: str, content: str) -> Dict:
        """Update content of a Google Doc."""
        try:
            # Get current document
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            
            # Clear existing content and insert new content
            end_index = doc.get('body', {}).get('content', [{}])[-1].get('endIndex', 1)
            
            requests = []
            if end_index > 1:
                # Delete existing content
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                })
            
            # Insert new content
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            })
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            return {'id': doc_id, 'name': doc.get('title')}
            
        except HttpError as error:
            logger.error(f"Error updating Google Doc: {error}")
            raise Exception(f"Failed to update Google Doc: {error}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive."""
        if not self.is_authenticated():
            raise Exception("Not authenticated with Google Drive")
        
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
        except HttpError as error:
            logger.error(f"Error deleting file: {error}")
            return False


# Global instance
google_drive_manager = None

def initialize_google_drive_manager(client_id: str, client_secret: str, redirect_uri: str, folder_name: str = "caplog") -> GoogleDriveManager:
    """Initialize the global Google Drive manager instance."""
    global google_drive_manager
    google_drive_manager = GoogleDriveManager(client_id, client_secret, redirect_uri, folder_name)
    return google_drive_manager

def get_google_drive_manager() -> Optional[GoogleDriveManager]:
    """Get the global Google Drive manager instance."""
    return google_drive_manager
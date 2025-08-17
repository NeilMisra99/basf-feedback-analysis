"""Azure Blob Storage service for managing audio files."""

import os
import logging
from typing import Optional
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from datetime import datetime, timedelta
from .base import BaseExternalService, ServiceResponse

logger = logging.getLogger(__name__)


class BlobStorageService(BaseExternalService):
    
    def __init__(self):
        super().__init__("Azure Blob Storage")
        self.connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = "audio-files"
        self.initialize()
    
    def _validate_credentials(self) -> bool:
        """Validate Azure Blob Storage credentials."""
        return bool(self.connection_string)
    
    def _initialize_client(self) -> bool:
        """Initialize Azure Blob Storage client."""
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            # Test connection and ensure container exists
            container_client = self.blob_service_client.get_container_client(self.container_name)
            try:
                container_client.get_container_properties()
            except Exception:
                # Container doesn't exist, create it
                container_client.create_container()
                logger.info(f"Created blob container: {self.container_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Blob Storage client: {str(e)}")
            return False
    
    def upload_audio_file(self, local_file_path: str, feedback_id: str) -> ServiceResponse:
        """
        Upload audio file to Blob Storage.
        
        Args:
            local_file_path: Path to local audio file
            feedback_id: Unique identifier for the feedback
            
        Returns:
            ServiceResponse with blob URL and metadata
        """
        if not self.is_available:
            return ServiceResponse(
                success=False,
                error="Blob Storage service not available",
                service_used="blob_storage"
            )
        
        try:
            blob_name = f"{feedback_id}.mp3"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload file with proper content type
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(
                    data, 
                    overwrite=True,
                    content_settings=ContentSettings(content_type="audio/mpeg")
                )
            
            # Get file size
            blob_properties = blob_client.get_blob_properties()
            file_size = blob_properties.size
            
            # Generate SAS URL for secure access (valid for 24 hours)
            sas_url = self.generate_sas_url(blob_name, hours_valid=24)
            
            logger.info(f"Audio file uploaded to blob: {blob_name} ({file_size} bytes)")
            
            return ServiceResponse(
                success=True,
                data={
                    'blob_url': blob_client.url,
                    'sas_url': sas_url,
                    'blob_name': blob_name,
                    'file_size': file_size,
                    'container_name': self.container_name
                },
                service_used="blob_storage"
            )
            
        except Exception as e:
            logger.error(f"Failed to upload audio file to blob storage: {str(e)}")
            return ServiceResponse(
                success=False,
                error=str(e),
                service_used="blob_storage"
            )
    
    def generate_sas_url(self, blob_name: str, hours_valid: int = 24) -> str:
        """
        Generate a SAS URL for secure blob access.
        
        Args:
            blob_name: Name of the blob
            hours_valid: Hours the SAS URL should be valid
            
        Returns:
            SAS URL string
        """
        try:
            # Extract account name and key from connection string
            # Format: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
            conn_parts = {}
            for item in self.connection_string.split(';'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    conn_parts[key] = value
            
            account_name = conn_parts.get('AccountName')
            account_key = conn_parts.get('AccountKey')
            
            if not account_name or not account_key:
                logger.error("Unable to extract account name/key from connection string")
                return ""
            
            # Generate SAS token with proper UTC datetime
            sas_token = generate_blob_sas(
                account_name=account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=hours_valid)
            )
            
            # Construct full SAS URL
            blob_url = f"https://{account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            return f"{blob_url}?{sas_token}"
            
        except Exception as e:
            logger.error(f"Failed to generate SAS URL: {str(e)}")
            return ""
    
    def get_blob_content(self, feedback_id: str) -> ServiceResponse:
        """
        Get blob content as bytes for streaming.
        
        Args:
            feedback_id: Unique identifier for the feedback
            
        Returns:
            ServiceResponse with blob content in data field
        """
        if not self.is_available:
            return ServiceResponse(
                success=False,
                error="Blob Storage service not available",
                service_used="blob_storage"
            )
        
        try:
            blob_name = f"{feedback_id}.mp3"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Download blob content
            blob_data = blob_client.download_blob().readall()
            
            return ServiceResponse(
                success=True,
                data=blob_data,
                service_used="blob_storage"
            )
            
        except Exception as e:
            logger.error(f"Failed to get blob content for {feedback_id}: {str(e)}")
            return ServiceResponse(
                success=False,
                error=f"Failed to retrieve blob content: {str(e)}",
                service_used="blob_storage"
            )
    
    def delete_audio_file(self, feedback_id: str) -> ServiceResponse:
        """
        Delete audio file from Blob Storage.
        
        Args:
            feedback_id: Unique identifier for the feedback
            
        Returns:
            ServiceResponse indicating success/failure
        """
        if not self.is_available:
            return ServiceResponse(
                success=False,
                error="Blob Storage service not available",
                service_used="blob_storage"
            )
        
        try:
            blob_name = f"{feedback_id}.mp3"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Audio file deleted from blob: {blob_name}")
            
            return ServiceResponse(
                success=True,
                data={'blob_name': blob_name},
                service_used="blob_storage"
            )
            
        except Exception as e:
            logger.error(f"Failed to delete audio file from blob storage: {str(e)}")
            return ServiceResponse(
                success=False,
                error=str(e),
                service_used="blob_storage"
            )
    
    def get_audio_url(self, feedback_id: str, download: bool = False) -> Optional[str]:
        """
        Get secure URL for audio file access.
        
        Args:
            feedback_id: Unique identifier for the feedback
            download: Whether URL should trigger download
            
        Returns:
            Secure SAS URL or None if not available
        """
        try:
            blob_name = f"{feedback_id}.mp3"
            sas_url = self.generate_sas_url(blob_name, hours_valid=1)  # Short-lived for access
            
            if download and sas_url:
                # Add download disposition to URL
                separator = "&" if "?" in sas_url else "?"
                sas_url += f"{separator}response-content-disposition=attachment%3B%20filename%3D{blob_name}"
            
            return sas_url
            
        except Exception as e:
            logger.error(f"Failed to get audio URL: {str(e)}")
            return None


_blob_singleton: Optional[BlobStorageService] = None


def get_blob_storage() -> BlobStorageService:
    """Process-wide singleton accessor for BlobStorageService."""
    global _blob_singleton
    if _blob_singleton is None:
        _blob_singleton = BlobStorageService()
    return _blob_singleton
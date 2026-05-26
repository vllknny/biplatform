
"""
Azure Blob Storage Data Upload Pipeline
Reads data from the local data folder and uploads it to Azure Blob Storage.

Requirements:
    pip install azure-storage-blob

Authentication:
    - For quick scripts/dev: Use connection string (see below)
    - For production: Use Azure Identity (DefaultAzureCredential) with Managed Identity or Service Principal
    
Large Files:
    For very large files, use streaming upload instead of reading entire file into memory.
"""

from azure.storage.blob import BlobServiceClient
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ Configuration ============
# Replace these with your Azure Storage credentials
CONNECTION_STRING = "YOUR_AZURE_STORAGE_CONNECTION_STRING"
CONTAINER_NAME = "YOUR_CONTAINER_NAME"
LOCAL_DATA_FOLDER = Path(__file__).parent.parent / "data"  # Points to ../data folder

# ============ Main Upload Function ============
def upload_data_to_azure(connection_string: str, container_name: str, local_folder: Path):
    """
    Upload all files from a local folder to Azure Blob Storage.
    
    Args:
        connection_string: Azure Storage connection string
        container_name: Target container name in Azure Blob Storage
        local_folder: Local folder path containing files to upload
    """
    try:
        # Initialize blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get or create container
        container_client = blob_service_client.get_container_client(container_name)
        
        # Upload all files from the local folder
        if not local_folder.exists():
            logger.error(f"Folder not found: {local_folder}")
            return
        
        uploaded_files = []
        for file_path in local_folder.iterdir():
            if file_path.is_file():
                blob_name = file_path.name
                
                try:
                    with open(file_path, "rb") as data:
                        container_client.upload_blob(name=blob_name, data=data, overwrite=True)
                    logger.info(f"✓ Uploaded: {blob_name}")
                    uploaded_files.append(blob_name)
                except Exception as e:
                    logger.error(f"✗ Failed to upload {blob_name}: {str(e)}")
        
        logger.info(f"\nTotal files uploaded: {len(uploaded_files)}")
        return uploaded_files
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise

# ============ Alternative: Read and Process Data ============
def read_local_data(local_folder: Path):
    """
    Read data files from local folder (for preprocessing before upload).
    
    Args:
        local_folder: Path to data folder
    
    Returns:
        Dictionary with file names and content
    """
    data = {}
    try:
        for file_path in local_folder.iterdir():
            if file_path.is_file():
                with open(file_path, "r") as f:
                    data[file_path.name] = f.read()
                logger.info(f"Read: {file_path.name}")
    except Exception as e:
        logger.error(f"Error reading data: {str(e)}")
    
    return data

# ============ Main Execution ============
if __name__ == "__main__":
    # TODO: Set your Azure Storage connection string and container name
    if CONNECTION_STRING == "YOUR_AZURE_STORAGE_CONNECTION_STRING":
        logger.error("Please set CONNECTION_STRING and CONTAINER_NAME in the script")
    else:
        # Upload data to Azure
        logger.info(f"Starting upload from: {LOCAL_DATA_FOLDER}")
        uploaded_files = upload_data_to_azure(CONNECTION_STRING, CONTAINER_NAME, LOCAL_DATA_FOLDER)
        logger.info(f"Upload completed. Files: {uploaded_files}")   
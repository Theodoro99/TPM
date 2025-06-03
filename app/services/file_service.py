import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from pathlib import Path
from dotenv import load_dotenv

"""File upload and management service.

This module handles file operations including:
- Saving uploaded files with size validation
- File deletion
- File path resolution
"""

# Load environment variables
load_dotenv()
"""Loads configuration from .env file."""

# Get upload directory from environment variables or use default
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./static/uploads")
"""Base directory for file uploads (configurable via environment)."""

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))# Default 10MB
"""Maximum allowed file upload size in bytes (default: 10MB)."""

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
"""Creates upload directory if it doesn't exist."""

async def save_upload_file(upload_file: UploadFile, entry_id: uuid.UUID) -> tuple[str, int]:
    """Save an uploaded file with chunked processing and size validation.

    Args:
        upload_file: FastAPI UploadFile object containing file data
        entry_id: UUID of associated logbook entry

    Returns:
        tuple: (relative_path, file_size) where:
            relative_path: Path relative to UPLOAD_DIR
            file_size: Size of saved file in bytes

    Raises:
        HTTPException: 413 if file exceeds size limit
        HTTPException: 500 if file cannot be saved
    """
    # Create directory for this entry if it doesn't exist
    entry_dir = os.path.join(UPLOAD_DIR, str(entry_id))
    Path(entry_dir).mkdir(exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(entry_dir, unique_filename)
    
    # Check file size
    file_size = 0
    try:
        # Move to start of file
        await upload_file.seek(0)
        
        # Read and save file in chunks to avoid loading large files into memory
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await upload_file.read(1024 * 1024)  # Read 1MB at a time
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > MAX_UPLOAD_SIZE:
                    # Delete the partially written file
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE / 1024 / 1024}MB"
                    )
                buffer.write(chunk)
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # Return the relative path from UPLOAD_DIR and file size
    relative_path = os.path.join(str(entry_id), unique_filename)
    return relative_path, file_size


def delete_file(file_path: str) -> bool:
    """Safely delete a file from the upload directory.

    Args:
        file_path: Relative path to file (from UPLOAD_DIR)

    Returns:
        bool: True if file was deleted or didn't exist,
              False if deletion failed
    """
    full_path = os.path.join(UPLOAD_DIR, file_path)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False


def get_file_path(file_path: str) -> str:
    """Resolve relative file path to absolute system path.

    Args:
        file_path: Relative path to file (from UPLOAD_DIR)

    Returns:
        str: Absolute filesystem path to the file
    """
    return os.path.join(UPLOAD_DIR, file_path)

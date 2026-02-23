import os
import re
import mimetypes
import magic

from typing import TYPE_CHECKING
from fastapi import HTTPException
from pathlib import Path

if TYPE_CHECKING:
    from db import FileDB


def validate_sql_identifier(identifier: str) -> str:
    """
    Validate and return a SQL identifier (table/column name) to prevent SQL injection.
    
    Args:
        identifier: The identifier to validate
        
    Returns:
        The validated identifier
        
    Raises:
        ValueError: If the identifier contains invalid characters
    """
    if not identifier:
        raise ValueError("SQL identifier cannot be empty")
    
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(
            f"Invalid SQL identifier '{identifier}'. "
            "Must start with a letter or underscore and contain only alphanumeric characters and underscores."
        )
    
    if len(identifier) > 64:
        raise ValueError(f"SQL identifier '{identifier}' is too long (max 64 characters)")
    
    return identifier


def detect_media_type(file_path: Path) -> str:
    # Use extensions as the media_type
    _, extension = os.path.splitext(file_path)
    if not extension:
        # If no extension, try to detect using magic
        media_type = magic.from_file(str(file_path), mime=True)
        extension = mimetypes.guess_extension(media_type) or ""
    media_type = extension.lstrip('.').lower()
    return media_type

def sanitize_extension(extension: str) -> str:
    # Keep alphanumerics plus _, -, and ., normalize case.
    cleaned = extension.strip().lstrip(".")
    return "".join(ch for ch in cleaned if ch.isalnum() or ch in {"_", "-", "."}).lower()

def delete_file_and_metadata(file_id: str, file_db: "FileDB", raise_if_not_found: bool = True):
    """Helper function to delete a file and its metadata from a file database."""
    metadata = file_db.get_file_metadata(file_id)
    if metadata is None:
        if raise_if_not_found:
            raise HTTPException(status_code=404, detail="File not found")
        else:
            return
    os.unlink(metadata['storage_path'])
    file_db.delete_file_metadata(file_id)
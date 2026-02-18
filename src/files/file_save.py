from db import FileDB
from fastapi import File, UploadFile
from pathlib import Path
import os
import uuid
import hashlib
import mimetypes
import magic
import shutil

class FileSave:
  STORAGE_DIR = "data/uploads"

  def __init__(self, file: UploadFile):
    self.db = FileDB()
    self.file = file
    self.uuid_str = str(uuid.uuid4())
    self.original_filename = file.filename
    self.file_extension = Path(self.original_filename).suffix
    self.unique_filename = f"{self.uuid_str}{self.file_extension}"
    os.makedirs(self.STORAGE_DIR, exist_ok=True)

  def save_file(self) -> dict:
    """
    Saves the uploaded file to disk, computes metadata, and stores metadata in the database. 

    Returns:
        metadata: metadata dictionary.
    """
    # Save uploaded file
    file_path = Path(self.STORAGE_DIR) / self.unique_filename
    with file_path.open("wb") as buffer:
      shutil.copyfileobj(self.file.file, buffer)
    # Compute file metadata
    file_size = file_path.stat().st_size
    sha256_checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
    
    # Use python-magic to detect media type based on file content
    media_type = magic.from_file(str(file_path), mime=True)
    
    # Determine filetype based on the extension if magic fails to detect the media type
    if media_type is None or media_type == "application/octet-stream":
      media_type, _ = mimetypes.guess_type(self.original_filename)
      if media_type is None:
        media_type = "application/octet-stream"
    
    # Store metadata in DB
    metadata = {
      "id": self.uuid_str,
      "storage_path": str(file_path),
      "original_filename": self.original_filename,
      "media_type": media_type,
      "extension": self.file_extension,
      "size_bytes": file_size,
      "sha256_checksum": sha256_checksum,
      "stored_as": self.unique_filename
    }
    self.db.insert_file_metadata(metadata)

    # Return metadata for response to user
    return metadata
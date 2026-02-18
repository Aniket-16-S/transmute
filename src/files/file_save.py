from db import FileDB
from fastapi import File, UploadFile
from pathlib import Path
import os
import uuid
import hashlib
import mimetypes
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
    # Save uploaded file
    file_path = Path(self.STORAGE_DIR) / self.unique_filename
    with file_path.open("wb") as buffer:
      shutil.copyfileobj(self.file.file, buffer)
    # Compute file metadata
    file_size = file_path.stat().st_size
    sha256_checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
    media_type = self.file.content_type or mimetypes.guess_type(self.original_filename)[0] or "application/octet-stream"
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
    return metadata
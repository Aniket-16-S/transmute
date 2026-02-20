import os
import mimetypes
import magic

from pathlib import Path


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
"""
File validation — MIME sniffing via puremagic (pure Python, no DLLs).
Never trust the client's Content-Type or file extension.
"""

from __future__ import annotations

import puremagic

from app.config import settings
from app.utils.errors import (
    UnsupportedMimeError,
    FileTooLargeError,
    ValidationError,
)

_MIME_ALIASES = {
    "application/x-pdf": "application/pdf",
    "application/acrobat": "application/pdf",
    "applications/vnd.pdf": "application/pdf",
    "text/pdf": "application/pdf",
    "text/x-pdf": "application/pdf",
    "image/jpg": "image/jpeg",
    "image/pjpeg": "image/jpeg",
}


def sniff_mime(content: bytes) -> str:
    """Detect MIME from first bytes. Falls back to octet-stream."""
    try:
        matches = puremagic.magic_string(content[:8192])
        if matches:
            mime = matches[0].mime_type or "application/octet-stream"
            return _MIME_ALIASES.get(mime, mime)
    except Exception:
        pass
    return "application/octet-stream"


def validate_upload(content: bytes, tier: str = "free") -> str:
    """Validate size + MIME. Returns the detected MIME."""
    if not content:
        raise ValidationError("Empty file.", hint="Choose a non-empty file.")

    max_bytes = settings.max_size_bytes(tier)
    if len(content) > max_bytes:
        mb = settings.free_max_file_mb if tier == "free" else settings.pro_max_file_mb
        raise FileTooLargeError(
            message=f"File exceeds {mb} MB.",
            hint=f"Upgrade to Pro for {settings.pro_max_file_mb} MB."
            if tier == "free"
            else "Split the file and try again.",
        )

    mime = sniff_mime(content)
    if mime not in settings.allowed_mime_list:
        raise UnsupportedMimeError(
            message=f"File type '{mime}' is not supported.",
            hint="Supported: PDF, JPG, PNG, WebP, DOCX, XLSX, PPTX.",
        )
    return mime
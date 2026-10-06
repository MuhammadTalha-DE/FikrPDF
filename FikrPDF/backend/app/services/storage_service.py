"""
Storage abstraction — local filesystem now, S3-compatible later.
All filenames are UUID-based to prevent path traversal (Gap 4).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone

from app.config import settings


class StorageService:
    def __init__(self, base_path: str | None = None):
        self.base = Path(base_path or settings.storage_path).resolve()
        self.uploads = self.base / "uploads"
        self.processed = self.base / "processed"
        self.tmp = self.base / "tmp"
        for d in (self.uploads, self.processed, self.tmp):
            d.mkdir(parents=True, exist_ok=True)

    # ----- public API -----

    def save_upload(self, content: bytes, original_name: str, ttl_hours: int) -> dict:
        """
        Save upload with a UUID filename.
        Returns metadata dict used by the router.
        """
        ext = self._safe_extension(original_name)
        file_uuid = uuid.uuid4()
        stored_name = f"{file_uuid.hex}{ext}"
        path = self.uploads / stored_name

        path.write_bytes(content)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        return {
            "id": file_uuid,
            "storage_path": str(path.relative_to(self.base)),
            "absolute_path": str(path),
            "size": len(content),
            "expires_at": expires_at,
        }

    def save_processed(self, content: bytes, ext: str = ".pdf") -> dict:
        file_uuid = uuid.uuid4()
        stored_name = f"{file_uuid.hex}{ext}"
        path = self.processed / stored_name
        path.write_bytes(content)
        return {
            "id": file_uuid,
            "storage_path": str(path.relative_to(self.base)),
            "absolute_path": str(path),
            "size": len(content),
        }

    def absolute(self, relative_path: str) -> Path:
        """Safely resolve a stored path — blocks traversal."""
        candidate = (self.base / relative_path).resolve()
        if self.base not in candidate.parents and candidate != self.base:
            raise ValueError("Invalid storage path")
        return candidate

    def delete(self, relative_path: str) -> bool:
        try:
            p = self.absolute(relative_path)
            if p.exists():
                p.unlink()
                return True
        except Exception:
            pass
        return False

    # ----- internal -----

    @staticmethod
    def _safe_extension(name: str) -> str:
        """Return a sanitized extension, default to ''."""
        if not name or "." not in name:
            return ""
        ext = "." + name.rsplit(".", 1)[-1].lower()
        # whitelist
        allowed = {
            ".pdf", ".jpg", ".jpeg", ".png", ".webp",
            ".docx", ".xlsx", ".pptx", ".zip",
        }
        return ext if ext in allowed else ""


storage_service = StorageService()
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    """
    Represents an uploaded or processed file.
    Gap 1 (file lifecycle): expires_at enforces auto-delete.
    """

    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Original client filename (display only — never used as storage path)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)

    # Detected MIME from magic bytes (Gap 4)
    mime: Mapped[str] = mapped_column(String(100), nullable=False)

    # Size in bytes (Gap 2)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Storage — uuid-based path (Gap 4: no user-supplied path traversal)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # Role: "upload" | "processed"
    kind: Mapped[str] = mapped_column(String(20), default="upload", nullable=False)

    # Gap 1 — when to delete
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User | None"] = relationship(back_populates="files")  # noqa: F821
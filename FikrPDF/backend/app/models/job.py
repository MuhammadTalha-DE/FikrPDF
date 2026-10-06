from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Job(Base):
    """
    Represents a PDF/image processing task.
    Status: queued | running | done | failed
    """

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    # Operation slug: "merge", "split", "compress", "image_to_pdf", ...
    operation: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Status (Gap 3 — errors captured in error_code/error_message)
    status: Mapped[str] = mapped_column(
        String(20), default="queued", nullable=False, index=True
    )

    # Input/output file references (null for multi-input ops like merge)
    input_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL")
    )
    output_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL")
    )

    # Flexible options (page ranges, order, DPI, etc.)
    options: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Error capture
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User | None"] = relationship(back_populates="jobs")  # noqa: F821
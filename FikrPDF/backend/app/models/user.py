from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tier: "free" | "pro" | "business"
    tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)

    # Usage counters (Gap 2) — reset daily via cron in Phase 29
    tasks_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    files: Mapped[list["File"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    jobs: Mapped[list["Job"]] = relationship(back_populates="user", cascade="all, delete-orphan")   # noqa: F821
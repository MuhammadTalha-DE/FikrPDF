"""
Cleanup service — deletes expired files (Gap 1).

Runs on a schedule via APScheduler. Each sweep:
  1. Finds files where expires_at < now()
  2. Deletes the disk file
  3. Deletes the DB row
  4. Logs totals
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from loguru import logger
from sqlalchemy import select

from app.database import SessionLocal
from app.models.file import File as FileModel
from app.services.storage_service import storage_service


def cleanup_expired_files() -> dict:
    """
    Sweep expired files. Safe to call repeatedly.
    Returns a summary dict for logging/testing.
    """
    started = datetime.now(timezone.utc)
    now = started

    deleted_disk = 0
    deleted_db = 0
    failed = 0

    db = SessionLocal()
    try:
        stmt = select(FileModel).where(FileModel.expires_at < now)
        expired = db.execute(stmt).scalars().all()

        for f in expired:
            # 1. Delete disk file
            try:
                if storage_service.delete(f.storage_path):
                    deleted_disk += 1
            except Exception as e:
                logger.warning("cleanup | disk_delete_failed | id={} | err={}", f.id, e)
                failed += 1

            # 2. Delete DB row
            try:
                db.delete(f)
                deleted_db += 1
            except Exception as e:
                logger.warning("cleanup | db_delete_failed | id={} | err={}", f.id, e)
                failed += 1

        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("cleanup | sweep_failed | err={}", e)
    finally:
        db.close()

    elapsed_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    summary = {
        "expired_found": len(expired) if 'expired' in locals() else 0,
        "deleted_disk": deleted_disk,
        "deleted_db": deleted_db,
        "failed": failed,
        "elapsed_ms": elapsed_ms,
    }
    if summary["expired_found"] > 0 or failed > 0:
        logger.info(
            "cleanup | found={} | disk={} | db={} | failed={} | {}ms",
            summary["expired_found"], deleted_disk, deleted_db, failed, elapsed_ms,
        )
    return summary
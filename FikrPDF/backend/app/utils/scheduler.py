"""
APScheduler bootstrap. Started from main.py.
Runs cleanup_expired_files() every N minutes.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.services.cleanup_service import cleanup_expired_files

_scheduler: BackgroundScheduler | None = None


def start_scheduler(interval_minutes: int = 15) -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")

    _scheduler.add_job(
        cleanup_expired_files,
        trigger="interval",
        minutes=interval_minutes,
        id="cleanup_expired_files",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info("scheduler | started | cleanup every {} min", interval_minutes)
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("scheduler | stopped")